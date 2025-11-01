# Local Dataset Setup for FSx Lustre

This document describes the modifications made to support training with JSONL datasets stored on FSx Lustre filesystem.

## Changes Made

### 1. Modified `FSDP/src/model_utils/train_utils.py`

- Enhanced `create_streaming_dataloader()` function to support local JSONL files
- Added automatic detection of local vs remote datasets (paths starting with `/` or `./`)
- Added comprehensive error handling and logging
- Support for split-specific files (e.g., `*train*.jsonl`, `*validation*.jsonl`)

### 2. Modified `FSDP/src/model_utils/arguments.py`

- Added `--local_dataset_path` argument to specify local dataset directory
- This argument overrides `--dataset` when provided

### 3. Modified `FSDP/src/train.py`

- Updated to use local dataset path when provided
- Added logging to show which dataset source is being used

### 4. Updated YAML Configuration Files

- Modified `FSDP/kubernetes/fsdp-hpto-template.yaml` and `FSDP/kubernetes/fsdp-hpto.yaml`
- Replaced `--dataset=allenai/c4` and `--dataset_config_name=en` with `--local_dataset_path=/fsx/c4_subset`

## Dataset Format Requirements

### Directory Structure
```
/fsx/c4_subset/
├── train.jsonl          # Training data (or files matching *train*.jsonl)
├── validation.jsonl     # Validation data (or files matching *validation*.jsonl)
└── *.jsonl             # Additional JSONL files (used if no split-specific files found)
```

### JSONL Format
Each line in the JSONL files must be a valid JSON object with a `text` field:

```json
{"text": "This is a sample text for training the language model."}
{"text": "Another example text with different content for diversity."}
```

## Usage

### Command Line Arguments

**Using local dataset:**
```bash
python train.py \
    --local_dataset_path=/fsx/c4_subset \
    --tokenizer=hf-internal-testing/llama-tokenizer \
    --max_steps=1000 \
    # ... other arguments
```

**Using remote dataset (original behavior):**
```bash
python train.py \
    --dataset=allenai/c4 \
    --dataset_config_name=en \
    --tokenizer=hf-internal-testing/llama-tokenizer \
    --max_steps=1000 \
    # ... other arguments
```

### Kubernetes Deployment

The YAML files have been updated to use the local dataset by default:

```yaml
command:
  - hyperpodrun
  - '--tee=3'
  - '--log_dir=/tmp/hyperpod'
  - '--nproc_per_node=$GPU_PER_NODE'
  - '--nnodes=$NUM_NODES'
  - /fsdp/train.py
  - '--local_dataset_path=/fsx/c4_subset'  # Uses local dataset
  # ... other arguments
```

## Dataset Preparation

### 1. Verify Dataset Location
```bash
# Check if dataset directory exists
ls -la /fsx/c4_subset/

# Check JSONL files
ls -la /fsx/c4_subset/*.jsonl
```

### 2. Validate Dataset with HyperPod Testing
Use the HyperPod testing framework to validate your dataset:

```bash
# Deploy a test job to validate dataset access
make run

# Check if training starts successfully (indicates dataset is accessible)
make logs-follow

# Stop the test job
make stop
```

This will:
- Deploy a real training job on the HyperPod cluster
- Verify FSx storage is mounted and accessible
- Check if the dataset can be loaded by the training script
- Validate the complete end-to-end pipeline

## Features

### Automatic Split Detection
The loader automatically detects training and validation splits:

1. **Training split**: Looks for files matching `*train*.jsonl`
2. **Validation split**: Looks for files matching `*validation*.jsonl`
3. **Fallback**: Uses all `*.jsonl` files if no split-specific files found

### Error Handling
- Comprehensive error messages for missing directories or files
- Graceful handling of malformed JSON lines
- Detailed logging of dataset loading progress
- Validation of required `text` field in JSON objects

### Performance Optimizations
- Streaming data loading (doesn't load entire dataset into memory)
- Efficient file iteration
- Proper resource cleanup

## Troubleshooting

### Common Issues

1. **"No JSONL files found"**
   - Check that files have `.jsonl` extension
   - Verify the directory path is correct
   - Ensure files are readable

2. **"Missing 'text' field"**
   - Each JSON object must have a `text` field
   - Manually inspect a few lines of your JSONL files to verify format

3. **"JSON decode error"**
   - Ensure each line is valid JSON
   - Check for trailing commas or malformed objects
   - Use `head -10 /fsx/c4_subset/train.jsonl` to inspect file format

4. **No batches generated**
   - Text samples might be too short after tokenization
   - Increase `max_context_width` or use longer text samples
   - Check tokenizer configuration

### Debugging

Enable verbose logging by setting environment variables:
```bash
export TORCH_DISTRIBUTED_DEBUG=DETAIL
export NCCL_DEBUG=INFO
```

Check the training logs for dataset loading messages:
```bash
tail -f logs/training.log | grep -i "dataset\|loading\|jsonl"
```

## Migration from Remote to Local Dataset

To migrate from using remote HuggingFace datasets to local FSx datasets:

1. **Prepare your JSONL files** in the correct format
2. **Copy files to FSx**: `cp your_data/*.jsonl /fsx/c4_subset/`
3. **Update YAML configuration**: Replace `--dataset` with `--local_dataset_path`
4. **Test the setup**: Use the provided test scripts
5. **Deploy**: Apply the updated Kubernetes configuration

## Performance Considerations

- **FSx Lustre** provides high-performance parallel filesystem access
- **Streaming loading** prevents memory issues with large datasets
- **Multiple workers** can be used for data loading parallelism
- **Caching** is handled automatically by the tokenizer and dataset libraries

## Backward Compatibility

The changes are fully backward compatible:
- If `--local_dataset_path` is not provided, the original remote dataset behavior is used
- All existing command-line arguments continue to work
- No changes required for remote dataset usage