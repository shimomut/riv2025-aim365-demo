# FSDP Training Application Project Overview

## Project Description

This project provides a comprehensive FSDP (Fully Sharded Data Parallel) training application designed for SageMaker HyperPod environments. The application supports distributed training of large language models including Llama 2, Llama 3.x, Mistral, and Mathstral models using PyTorch FSDP.

## Key Technologies

- **PyTorch FSDP**: Fully Sharded Data Parallel for distributed training
- **SageMaker HyperPod**: AWS managed training infrastructure
- **HyperPod Training Operator**: Kubernetes-based training orchestration using "HyperPodPyTorchJob" CRD
- **Managed Tiered Checkpointing (MTC)**: Advanced checkpointing library for fault tolerance
- **Container Orchestration**: Support for both Kubernetes and Slurm deployment

## Project Structure

```
FSDP/
├── src/                    # Core training code
│   ├── train.py           # Main training script
│   └── model_utils/       # Utility modules
├── kubernetes/            # Kubernetes deployment manifests
├── slurm/                # Slurm job scripts
└── models/               # Model configuration files
```

## Supported Models

- Llama 2 (7B, 13B, 70B)
- Llama 3.1 (8B, 70B) 
- Llama 3.2 (1B, 3B)
- Mistral 8x7B
- Mistral Mathstral 7B

## Deployment Platforms

1. **Kubernetes with HyperPod Training Operator**
2. **Slurm with SageMaker HyperPod**
3. **Amazon EKS**

## Core Features

- Multi-node distributed training
- Automatic checkpointing and resume
- Mixed precision training (BF16)
- Activation checkpointing for memory optimization
- Streaming dataset support (HuggingFace datasets)
- EFA (Elastic Fabric Adapter) support for high-performance networking