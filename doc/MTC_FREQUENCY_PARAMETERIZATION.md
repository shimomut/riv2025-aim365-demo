# MTC Checkpoint Frequency Parameterization

## Overview

The MTC (Managed Tiered Checkpointing) checkpoint frequencies are now configurable via command-line arguments, allowing you to customize checkpoint behavior directly in your YAML deployment files.

## New Parameters

### `--in_memory_checkpointing_freq`
- **Type**: Integer
- **Default**: 10
- **Description**: Frequency (in steps) for in-memory checkpoints when using MTC
- **Purpose**: Fast local checkpoints for quick recovery from transient failures

### `--s3_checkpointing_freq`
- **Type**: Integer
- **Default**: 20
- **Description**: Frequency (in steps) for S3 checkpoints when using MTC
- **Purpose**: Durable S3 checkpoints for long-term recovery and fault tolerance

## Usage in YAML Files

Add these parameters to your HyperPodPyTorchJob command arguments:

```yaml
command:
  - hyperpodrun
  - '--tee=3'
  - '--log_dir=/tmp/hyperpod'
  - '--nproc_per_node=8'
  - '--nnodes=4'
  - /fsdp/train.py
  # ... other training parameters ...
  # MTC (Managed Tiered Checkpointing) configuration
  - '--s3_tier_base_path=s3://your-bucket/checkpoints'
  - '--mtc_namespace=your-job-name'
  - '--in_memory_checkpointing_freq=10'
  - '--s3_checkpointing_freq=20'
```

## Configuration Examples

### High-Frequency Checkpointing (for unstable environments)
```yaml
- '--in_memory_checkpointing_freq=5'   # Every 5 steps
- '--s3_checkpointing_freq=10'         # Every 10 steps
```

### Standard Checkpointing (default)
```yaml
- '--in_memory_checkpointing_freq=10'  # Every 10 steps
- '--s3_checkpointing_freq=20'         # Every 20 steps
```

### Low-Frequency Checkpointing (for stable, long-running jobs)
```yaml
- '--in_memory_checkpointing_freq=25'  # Every 25 steps
- '--s3_checkpointing_freq=50'         # Every 50 steps
```

### Cost-Optimized (minimize S3 writes)
```yaml
- '--in_memory_checkpointing_freq=10'  # Every 10 steps
- '--s3_checkpointing_freq=100'        # Every 100 steps
```

## Best Practices

### Frequency Selection
- **In-Memory Frequency**: Should be frequent enough to minimize lost work from transient failures (typically 5-25 steps)
- **S3 Frequency**: Should balance durability needs with S3 write costs (typically 2-5x the in-memory frequency)
- **Relationship**: S3 frequency should generally be a multiple of in-memory frequency

### Hardware Considerations

**P5 Instances (High Performance)**
```yaml
- '--in_memory_checkpointing_freq=10'
- '--s3_checkpointing_freq=25'
```
- Faster training means more frequent checkpoints are affordable
- Higher throughput justifies more S3 writes

**G5 Instances (Cost-Optimized)**
```yaml
- '--in_memory_checkpointing_freq=15'
- '--s3_checkpointing_freq=50'
```
- Slower training means less frequent checkpoints
- Minimize S3 costs with less frequent durable checkpoints

### Model Size Considerations

**Large Models (70B+)**
```yaml
- '--in_memory_checkpointing_freq=20'
- '--s3_checkpointing_freq=50'
```
- Larger checkpoint sizes mean longer save times
- Less frequent checkpoints to avoid training interruption

**Small Models (8B and below)**
```yaml
- '--in_memory_checkpointing_freq=5'
- '--s3_checkpointing_freq=15'
```
- Smaller checkpoint sizes enable more frequent saves
- Minimal impact on training throughput

## Migration from Hardcoded Values

### Previous Implementation
The checkpoint frequencies were hardcoded in `train.py`:
```python
in_memory_checkpointing_freq = 10
s3_checkpointing_freq = 20
```

### Current Implementation
Now configurable via command-line arguments with the same defaults:
```python
save_in_memory = total_steps % args.in_memory_checkpointing_freq == 0
save_s3 = total_steps % args.s3_checkpointing_freq == 0
```

### Backward Compatibility
- Default values remain unchanged (10 and 20)
- Existing deployments without these parameters will use the defaults
- No breaking changes to existing configurations

## Updated Files

1. **`FSDP/src/model_utils/arguments.py`**: Added new MTC frequency arguments
2. **`FSDP/src/train.py`**: Updated to use configurable frequencies from args
3. **`FSDP/kubernetes/fsdp-hpto-template.yaml`**: Added example parameters
4. **`FSDP/kubernetes/fsdp-hpto-g5.yaml`**: Added example parameters
5. **`FSDP/kubernetes/fsdp-hpto-p5.yaml`**: Added example parameters

## Monitoring Checkpoint Behavior

Check training logs to verify checkpoint frequency:
```bash
make logs-follow
```

Look for checkpoint save messages:
```
Saving in-memory checkpoint at step 10
Saving S3 checkpoint at step 20
```

## Troubleshooting

### Checkpoints Too Frequent
**Symptom**: Training throughput degraded
**Solution**: Increase both frequencies
```yaml
- '--in_memory_checkpointing_freq=20'
- '--s3_checkpointing_freq=50'
```

### Checkpoints Too Infrequent
**Symptom**: Too much work lost on failures
**Solution**: Decrease both frequencies
```yaml
- '--in_memory_checkpointing_freq=5'
- '--s3_checkpointing_freq=15'
```

### High S3 Costs
**Symptom**: Unexpected S3 storage/request costs
**Solution**: Increase S3 checkpoint frequency
```yaml
- '--in_memory_checkpointing_freq=10'
- '--s3_checkpointing_freq=100'
```

## Related Documentation

- [MTC Parameterization Guide](MTC_PARAMETERIZATION_GUIDE.md): Complete MTC configuration
- [Testing Guide](TESTING_GUIDE.md): Testing checkpoint functionality
- [Troubleshooting Guide](../tmp/README.md): Checkpoint-related issues
