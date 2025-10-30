# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import re
import pickle
import statistics
import time
import warnings
from pathlib import Path

import torch
import torch.distributed as dist

# pylint: disable=import-error,no-name-in-module
import torch.distributed.checkpoint as dist_cp
from torch.distributed.checkpoint.optimizer import load_sharded_optimizer_state_dict
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.fully_sharded_data_parallel import StateDictType
from model_utils.train_utils import get_logger


logger = get_logger()


# for MTC
from amzn_sagemaker_checkpointing.config.sagemaker_checkpoint_config import SageMakerCheckpointConfig
from amzn_sagemaker_checkpointing.checkpointing.filesystem.filesystem import SageMakerTieredStorageWriter, SageMakerTieredStorageReader

# for MTC
class Globals:
    mtc_future = None

# for MTC
def get_sm_checkpoint_config(save_s3=False):

    config = SageMakerCheckpointConfig(
        # Unique ID for your training job 
        # Allowed characters in ID include: alphanumeric, hyphens, and underscores
        # FIXME: parameterize
        namespace="abcd1234",

        # Number of distributed processes/available GPUs
        world_size=dist.get_world_size(), 

        # Amazon S3 storage location, required for SageMakerTieredStorageReader for read fallbacks
        # Required for SageMakerTieredStorageWriter when save_to_s3 is True
        # FIXME: parameterize
        s3_tier_base_path="s3://sagemaker-checkpoints-535002850097-us-west-1/checkpoints"
    )

    if save_s3:
        config.save_to_s3=True

    return config


# for MTC
def save_checkpoint_mtc(model, optimizer, scheduler, user_content, root_dir, sub_dir, save_in_memory, save_s3, training_step):

    torch.cuda.empty_cache()

    sm_checkpoint_config = get_sm_checkpoint_config(save_s3=save_s3)

    # save_dir = os.path.join(root_dir, sub_dir)
    # if dist.get_rank() == 0:
    #     logger.info("Writing checkpoint to {0}.".format(save_dir))

    with FSDP.state_dict_type(
            model,
            StateDictType.SHARDED_STATE_DICT):

        state_dict = {
            "model": model.state_dict(),
            "optim": FSDP.optim_state_dict(model, optimizer),
            "scheduler": scheduler.state_dict(),
            "total_steps": user_content["total_steps"],
            "start_batch_index": user_content["start_batch_index"],
        }

        # Create storage writer for current step
        sm_storage_writer = SageMakerTieredStorageWriter(
            checkpoint_config=sm_checkpoint_config,
            step=training_step
        )

        # wait for previous checkpoint to get completed
        if  Globals.mtc_future is not None:
            exc = Globals.mtc_future.exception()
            if exc:
                print(f"Failure in saving previous checkpoint:{str(exc)}")
                #Handle failures as required
            else:
                result = Globals.mtc_future.result()
                #Process results from save, if required
        
        print(f"Starting async checkpoint save", flush=True)

        # Async save checkpoint using PyTorch DCP
        Globals.mtc_future = dist_cp.async_save(state_dict=state_dict, storage_writer=sm_storage_writer)

    dist.barrier()


def load_checkpoint_mtc(model, optimizer, scheduler, checkpoint_dir, model_type, device):

    print("Returning null checkpoint for testing", flush=True)
    return(
        model,
        optimizer,
        scheduler,
        0,
        0,
    )

    sm_checkpoint_config = get_sm_checkpoint_config(save_s3=True)

    with FSDP.state_dict_type(
            model,
            StateDictType.SHARDED_STATE_DICT,
        ):

        state_dict = {
            "model": model.state_dict(),
            "scheduler": scheduler.state_dict(),
            "total_steps": 0,
            "start_batch_index": 0,
            # cannot load the optimizer state_dict together with the model state_dict
        }

        # Load latest checkpoint
        sm_storage_reader = SageMakerTieredStorageReader(checkpoint_config=sm_checkpoint_config)

        dist_cp.load_state_dict(
            state_dict=state_dict,
            storage_reader=sm_storage_reader,
        )

        model.load_state_dict(state_dict["model"])
        scheduler.load_state_dict(state_dict["scheduler"])

        if dist.get_rank() == 0:
            logger.info("Loaded model state from disk")
            logger.info("Loading optimizer state from disk")

        optim_state = load_sharded_optimizer_state_dict(
            model_state_dict=state_dict["model"],
            optimizer_key="optim",
            storage_reader=sm_storage_reader,
        )
        if dist.get_rank() == 0:
            logger.info("Loaded and sharded optimizer state from disk")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            # UserWarning to replace all_gather_base with all_gather_into_tensor floods the logs
            flattened_osd = FSDP.optim_state_dict_to_load(
                model, optimizer, optim_state["optim"]
            )

        if dist.get_rank() == 0:
            logger.info("Converted optimizer state dict for FSDP")
        optimizer.load_state_dict(flattened_osd)
    
    dist.barrier()
    
    if dist.get_rank() == 0:
        logger.info("Checkpoint loaded from %s.", last_checkpoint)
    
    return (
        model,
        optimizer,
        scheduler,
        state_dict["total_steps"],
        state_dict["start_batch_index"],
    )



def save_checkpoint(model, optimizer, scheduler, user_content, root_dir, sub_dir):
    torch.cuda.empty_cache()

    save_dir = os.path.join(root_dir, sub_dir)
    if dist.get_rank() == 0:
        logger.info("Writing checkpoint to {0}.".format(save_dir))
    
    with FSDP.state_dict_type(
            model, 
            StateDictType.SHARDED_STATE_DICT):
        state_dict = {
            "model": model.state_dict(),
            "optim": FSDP.optim_state_dict(model, optimizer),
            "scheduler": scheduler.state_dict(),
            "total_steps": user_content["total_steps"],
            "start_batch_index": user_content["start_batch_index"],
        }
        dist_cp.save_state_dict(
                    state_dict=state_dict,
                    storage_writer=dist_cp.FileSystemWriter(save_dir)
                )
    dist.barrier()
    if dist.get_rank() == 0:
        logger.info("Completed checkpoint.")

def get_last_checkpoint(checkpoint_paths, model_type):
    steps = [int(re.findall(r'\d+steps', checkpoint.stem)[0].replace('steps','')) \
         for checkpoint in checkpoint_paths]
    checkpoints = sorted([(step, path) for step,path in zip(steps, checkpoint_paths)])
    
    # find last checkpoint, skipping incomplete ones 
    for step, path in reversed(checkpoints):
        metadata_path = path.joinpath(".metadata")
        if not metadata_path.exists():
            logger.warn(f"{metadata_path} not found. Skipping this incomplete checkpoint")
            continue
        return path.as_posix()
    else:
        return None
    
def load_checkpoint(model, optimizer, scheduler, checkpoint_dir, model_type, device):
    checkpoint_paths = list(Path(checkpoint_dir).glob(f"{model_type}-*steps"))
    last_checkpoint = get_last_checkpoint(checkpoint_paths, model_type)
    if last_checkpoint is None:
        if dist.get_rank() == 0:
            logger.info("No Checkpoints Found")
        return(
            model,
            optimizer,
            scheduler,
            0,
            0,
        )
    if dist.get_rank() == 0:
        logger.info("Loading checkpoint from %s ...", last_checkpoint)
    with FSDP.state_dict_type(
            model,
            StateDictType.SHARDED_STATE_DICT,
        ):
        state_dict = {
            "model": model.state_dict(),
            "scheduler": scheduler.state_dict(),
            "total_steps": 0,
            "start_batch_index": 0,
            # cannot load the optimizer state_dict together with the model state_dict
        }
        dist_cp.load_state_dict(
            state_dict=state_dict,
            storage_reader=dist_cp.FileSystemReader(last_checkpoint),
        )
        model.load_state_dict(state_dict["model"])
        scheduler.load_state_dict(state_dict["scheduler"])
        if dist.get_rank() == 0:
            logger.info("Loaded model state from disk")
            logger.info("Loading optimizer state from disk")
        optim_state = load_sharded_optimizer_state_dict(
            model_state_dict=state_dict["model"],
            optimizer_key="optim",
            storage_reader=dist_cp.FileSystemReader(last_checkpoint),
        )
        if dist.get_rank() == 0:
            logger.info("Loaded and sharded optimizer state from disk")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            # UserWarning to replace all_gather_base with all_gather_into_tensor floods the logs
            flattened_osd = FSDP.optim_state_dict_to_load(
                model, optimizer, optim_state["optim"]
            )

        if dist.get_rank() == 0:
            logger.info("Converted optimizer state dict for FSDP")
        optimizer.load_state_dict(flattened_osd)
    dist.barrier()
    if dist.get_rank() == 0:
        logger.info("Checkpoint loaded from %s.", last_checkpoint)
    return (
        model,
        optimizer,
        scheduler,
        state_dict["total_steps"],
        state_dict["start_batch_index"],
    )
