# MTC Parameterization Guide

## Overview

The `get_sm_checkpoint_config` function has been parameterized to allow specification of S3 tier base path and MTC namespace through command-line arguments instead of hard-coded values.

## New Command-Line Arguments

### `--s3_tier_base_path`
- **Type**: String
- **Default**: `s3://sagemaker-checkpoints-842413447717-us-east-2/checkpoints`
- **Description**: S3 base path for MTC checkpoints
- **Example**: `--s3_tier_base_path=s3://my-bucket/my-checkpoints`

### `--mtc_namespace`
- **Type**: String  
- **Default**: `default-training-job`
- **Description**: Unique namespace/ID for MTC training job (alphanumeric, hyphens, underscores only)
- **Example**: `--mtc_namespace=llama3-1-8b-experiment-001`

## Usage in YAML Files

### Template Usage (with environment variables)
```yaml
command:
  - /fsdp/train.py
  # ... other arguments ...
  - '--s3_tier_base_path=${S3_TIER_BASE_PATH}'
  - '--mtc_namespace=${MTC_NAMESPACE}'
```

### Direct Usage
```yaml
command:
  - /fsdp/train.py
  # ... other arguments ...
  - '--s3_tier_base_path=s3://my-sagemaker-checkpoints/training-runs'
  - '--mtc_namespace=llama3-1-8b-production-run-001'
```

## Environment Variables for Templates

When using the template YAML files, set these environment variables:

```bash
export S3_TIER_BASE_PATH="s3://your-bucket/checkpoints"
export MTC_NAMESPACE="your-unique-job-id"
```

## Best Practices

1. **S3 Bucket**: Use a dedicated S3 bucket for checkpoints with appropriate IAM permissions
2. **Namespace**: Use descriptive, unique namespaces that include:
   - Model name/size
   - Experiment identifier
   - Date/version if needed
3. **Permissions**: Ensure the service account has read/write access to the S3 bucket
4. **Cleanup**: Consider S3 lifecycle policies for checkpoint cleanup

## Example Complete Configuration

```yaml
# In your YAML file
command:
  - /fsdp/train.py
  - '--model_type=llama_v3'
  - '--checkpoint_dir=/fsx/checkpoints'
  - '--s3_tier_base_path=s3://my-training-checkpoints/llama-experiments'
  - '--mtc_namespace=llama3-8b-c4-dataset-run-20241105'
  # ... other training arguments ...
```

## Migration from Hard-coded Values

If you were previously using the hard-coded values, the system will:
1. Use the new parameters if provided
2. Fall back to default values with warnings if not provided
3. Log the values being used for transparency

This ensures backward compatibility while encouraging migration to parameterized configuration.