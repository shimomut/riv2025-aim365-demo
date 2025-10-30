# Troubleshooting Guide

## Common Issues and Solutions

### NCCL and Communication Issues

#### NCCL Timeout Errors
**Symptoms:**
- Training hangs during initialization
- "NCCL timeout" errors in logs
- Jobs fail during collective operations

**Solutions:**
```bash
# Increase NCCL timeout
export NCCL_TIMEOUT=1800

# Enable detailed NCCL debugging
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=ALL

# Check network interface configuration
export NCCL_SOCKET_IFNAME=^docker,lo,veth,eth

# For EFA-enabled instances
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
```

#### EFA Configuration Issues
**Symptoms:**
- Poor multi-node performance
- Network-related errors
- Inconsistent training speeds

**Solutions:**
```bash
# Verify EFA driver installation
fi_info -p efa

# Check EFA interface availability
ibv_devinfo

# Configure EFA environment variables
export FI_EFA_USE_HUGE_PAGE=0
export FI_EFA_SET_CUDA_SYNC_MEMOPS=0
export FI_EFA_FORK_SAFE=1
```

### Memory Issues

#### Out of Memory (OOM) Errors
**Symptoms:**
- CUDA OOM errors
- Training crashes during forward/backward pass
- Inconsistent memory usage across GPUs

**Solutions:**
```python
# Reduce batch size
--train_batch_size=1

# Enable activation checkpointing
--activation_checkpointing=1

# Offload activations to CPU
--offload_activations=1

# Use CPU offloading for parameters
--cpu_offload=1

# Configure CUDA memory allocation
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

#### Memory Fragmentation
**Symptoms:**
- Inconsistent OOM errors
- Memory usage varies between runs
- Performance degradation over time

**Solutions:**
```python
# Use expandable memory segments
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Clear cache periodically
torch.cuda.empty_cache()

# Use gradient accumulation instead of larger batches
--gradient_accumulation_steps=4
```

### Checkpoint Issues

#### Checkpoint Loading Failures
**Symptoms:**
- "Checkpoint not found" errors
- Model state mismatch errors
- Training restarts from beginning

**Solutions:**
```python
# Verify checkpoint directory permissions
ls -la ./checkpoints/

# Check checkpoint file integrity
# Ensure consistent checkpoint naming

# For MTC checkpoints, verify S3 access
aws s3 ls s3://your-checkpoint-bucket/

# Use absolute paths for checkpoint directories
--checkpoint_dir=/fsx/checkpoints
--resume_from_checkpoint=/fsx/checkpoints
```

#### MTC Integration Issues
**Symptoms:**
- MTC checkpoints not saving
- S3 upload failures
- Inconsistent checkpoint recovery

**Solutions:**
```python
# Verify IAM permissions for S3 access
# Check MTC configuration in train.py
use_mtc = True
in_memory_checkpointing_freq = 10
s3_checkpointing_freq = 20

# Monitor MTC logs for errors
# Ensure sufficient local storage for in-memory checkpoints
```

### Dataset and Tokenizer Issues

#### HuggingFace Access Errors
**Symptoms:**
- "Repository not found" errors
- Authentication failures
- Slow dataset loading

**Solutions:**
```bash
# Set HuggingFace token
export HF_TOKEN=your_token_here

# Increase timeout for large clusters
export HF_HUB_ETAG_TIMEOUT=60

# Use local dataset cache
export HF_DATASETS_CACHE=/fsx/hf_cache

# For gated models, ensure token has appropriate permissions
```

#### Dataset Streaming Issues
**Symptoms:**
- Slow data loading
- Network timeouts during streaming
- Inconsistent batch loading

**Solutions:**
```python
# Increase dataset timeout
export HF_HUB_ETAG_TIMEOUT=120

# Use local dataset caching
--dataset_cache_dir=/fsx/dataset_cache

# Verify network connectivity to HuggingFace
curl -I https://huggingface.co/datasets/allenai/c4
```

### Performance Issues

#### Poor Training Throughput
**Symptoms:**
- Low samples/second
- High GPU idle time
- Inconsistent performance across nodes

**Diagnostics:**
```bash
# Monitor GPU utilization
nvidia-smi -l 1

# Check network bandwidth
iperf3 -c <remote_node>

# Monitor NCCL performance
export NCCL_DEBUG=INFO
```

**Solutions:**
```python
# Optimize batch size for hardware
--train_batch_size=2  # Adjust based on GPU memory

# Use appropriate sharding strategy
--sharding_strategy=hybrid  # For very large models

# Enable mixed precision
--bf16=1

# Optimize data loading
--num_workers=4  # Adjust based on CPU cores
```

#### Convergence Issues
**Symptoms:**
- Loss not decreasing
- Unstable training
- NaN values in loss

**Solutions:**
```python
# Adjust learning rate
--lr=5e-5  # Lower learning rate

# Increase warmup steps
--warmup=0.01

# Use gradient clipping
--grad_clip=1.0

# Check for NaN values
torch.isnan(loss).any()
```

### Kubernetes-Specific Issues

#### Pod Scheduling Failures
**Symptoms:**
- Pods stuck in "Pending" state
- Resource allocation errors
- Node affinity issues

**Solutions:**
```bash
# Check node resources
kubectl describe nodes

# Verify resource requests
kubectl describe pod <pod-name>

# Check node selectors and taints
kubectl get nodes --show-labels
```

#### PyTorchJob Failures
**Symptoms:**
- Job stuck in "Running" state
- Worker pods failing
- Elastic scaling issues

**Solutions:**
```bash
# Check job status
kubectl describe pytorchjob <job-name>

# Review pod logs
kubectl logs <pod-name>

# Verify training operator status
kubectl get pods -n kubeflow
```

### Slurm-Specific Issues

#### Job Submission Failures
**Symptoms:**
- SBATCH errors
- Resource allocation failures
- Queue system issues

**Solutions:**
```bash
# Check cluster status
sinfo

# Verify job parameters
scontrol show job <job-id>

# Check resource availability
squeue -u $USER
```

#### Environment Setup Issues
**Symptoms:**
- Module loading failures
- Python environment errors
- Library version conflicts

**Solutions:**
```bash
# Verify virtual environment
source /fsx/venv/bin/activate
pip list

# Check module availability
module avail

# Verify container image
enroot list
```

## Debugging Tools and Commands

### NCCL Debugging
```bash
# Enable comprehensive NCCL logging
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=ALL
export TORCH_NCCL_ENABLE_MONITORING=1
export TORCH_NCCL_TRACE_BUFFER_SIZE=20000
export TORCH_NCCL_DUMP_ON_TIMEOUT=1
```

### PyTorch Debugging
```bash
# Enable distributed debugging
export TORCH_DISTRIBUTED_DEBUG=DETAIL
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1

# Memory debugging
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

### Performance Profiling
```python
# Use PyTorch profiler
with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA],
    record_shapes=True
) as prof:
    # Training step
    pass

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

### Log Analysis
```bash
# Monitor training logs in real-time
tail -f logs/training.log

# Search for specific errors
grep -i "error\|exception\|failed" logs/training.log

# Analyze NCCL performance
grep "NCCL" logs/training.log | grep "bandwidth"
```

## Prevention Strategies

### Pre-deployment Checks
1. Verify all environment variables are set
2. Test network connectivity between nodes
3. Validate checkpoint directory permissions
4. Confirm dataset accessibility
5. Check resource availability

### Monitoring Setup
1. Implement comprehensive logging
2. Set up performance monitoring
3. Configure alerting for failures
4. Monitor resource utilization
5. Track training metrics

### Best Practices
1. Use consistent naming conventions
2. Implement proper error handling
3. Test configurations on smaller scales first
4. Document environment-specific settings
5. Maintain backup checkpoint strategies