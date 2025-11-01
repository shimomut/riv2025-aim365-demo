# HyperPod FSDP Testing Guide

## Overview

This guide provides comprehensive testing methods for the FSDP training application on SageMaker HyperPod clusters using actual cluster resources.

## Quick Start

### 1. Validate Setup
```bash
make validate-setup
```

### 2. Run Quick Test
```bash
make test-quick
```

### 3. Monitor Training
```bash
make logs-follow
```

## Testing Framework

### Automated Testing Script
The `test_hyperpod_cluster.py` script provides comprehensive testing:

- **Pre-deployment checks**: Cluster connectivity, operator status, GPU nodes, storage
- **Job deployment**: Automated job submission and monitoring
- **Progress tracking**: Real-time training progress monitoring
- **Status reporting**: Detailed job and pod status information
- **Cleanup**: Automatic resource cleanup

### Available Test Commands

#### Basic Testing
```bash
# Full test with 5-minute monitoring
make test-cluster

# Quick test with 1-minute monitoring  
make test-quick

# Get current status
make test-status

# View recent logs
make test-logs

# Cleanup resources
make test-cleanup
```

#### Health Checks
```bash
# Complete cluster health check
make check-cluster

# Job-specific status
make check-job

# Validate entire setup
make validate-setup
```#### Perfo
rmance Testing
```bash
# 5-minute performance test
make perf-test

# 15-minute stress test
make stress-test
```

#### Monitoring Commands
```bash
# Watch pod status (updates every 5 seconds)
make monitor-pods

# Watch job status (updates every 10 seconds)
make monitor-job

# Follow training logs in real-time
make logs-follow

# View logs from all pods
make logs-all
```

#### Debug Commands
```bash
# Describe job details
make debug-describe

# View recent events
make debug-events

# List pods for manual debugging
make debug-pod
```

## Manual Testing Procedures

### 1. Pre-Deployment Validation

Check cluster connectivity:
```bash
kubectl cluster-info
```

Verify GPU nodes:
```bash
kubectl get nodes -l sagemaker.amazonaws.com/compute-type -o wide
```

Check HyperPod operator:
```bash
kubectl get pods -n kubeflow -l app=training-operator
```

Verify storage claims:
```bash
kubectl get pvc fsx-claim
```

### 2. Job Deployment Testing

Deploy the job:
```bash
make run
```

Monitor pod creation:
```bash
kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto -w
```

Check job status:
```bash
kubectl get hyperpodpytorchjob llama3-1-8b-fsdp-hpto
```

### 3. Training Progress Monitoring

View real-time logs:
```bash
kubectl logs -f llama3-1-8b-fsdp-hpto-pods-0
```

Check for training metrics:
```bash
kubectl logs llama3-1-8b-fsdp-hpto-pods-0 | grep "Loss:"
```

Monitor resource usage:
```bash
kubectl top pods -l job-name=llama3-1-8b-fsdp-hpto
```

### 4. Troubleshooting Commands

Describe pod for issues:
```bash
kubectl describe pod llama3-1-8b-fsdp-hpto-pods-0
```

Check events:
```bash
kubectl get events --sort-by=.metadata.creationTimestamp | tail -20
```

Access pod for debugging:
```bash
kubectl exec -it llama3-1-8b-fsdp-hpto-pods-0 -- /bin/bash
```

## Test Scenarios

### Scenario 1: Basic Functionality Test
1. Run `make validate-setup`
2. Deploy with `make run`
3. Monitor with `make logs-follow`
4. Verify training starts within 5 minutes
5. Check for loss values in logs
6. Cleanup with `make stop`

### Scenario 2: Multi-Node Communication Test
1. Deploy 8-node job
2. Monitor all pods reach Running state
3. Check NCCL initialization in logs
4. Verify distributed training coordination
5. Monitor for communication errors

### Scenario 3: Fault Tolerance Test
1. Deploy job and wait for training start
2. Manually delete one pod
3. Verify HyperPod operator restarts pod
4. Check training resumes from checkpoint
5. Monitor for successful recovery

### Scenario 4: Performance Validation
1. Run `make perf-test`
2. Monitor GPU utilization
3. Check training throughput (samples/sec)
4. Verify EFA network performance
5. Validate memory usage patterns

## Expected Results

### Successful Training Indicators
- All pods reach "Running" state within 5 minutes
- Training logs show decreasing loss values
- No NCCL timeout errors
- GPU utilization > 80%
- Checkpoints saved successfully

### Performance Benchmarks
- **Llama 3.1 8B on 8x G5.8xlarge**: ~2-3 samples/sec/GPU
- **Memory usage**: <32GB per GPU with activation checkpointing
- **Network bandwidth**: >10 Gbps between nodes with EFA

## Troubleshooting

### Common Issues and Solutions

**Pods stuck in Pending:**
```bash
kubectl describe pod <pod-name>
# Check node resources and scheduling constraints
```

**NCCL timeout errors:**
```bash
# Check EFA configuration in job spec
# Verify network connectivity between nodes
```

**Out of memory errors:**
```bash
# Reduce batch size in job configuration
# Enable activation checkpointing and offloading
```

**Checkpoint loading failures:**
```bash
# Verify FSx mount and permissions
# Check checkpoint directory structure
```

## Continuous Testing

### Automated Testing Pipeline
Set up regular testing with:
```bash
# Daily health check
0 9 * * * cd /path/to/project && make validate-setup

# Weekly performance test  
0 10 * * 1 cd /path/to/project && make perf-test
```

### Monitoring Integration
- Set up CloudWatch alarms for job failures
- Configure log aggregation for training metrics
- Implement alerting for performance degradation

## Best Practices

1. **Always validate setup** before running tests
2. **Monitor resource usage** during training
3. **Check logs regularly** for errors or warnings
4. **Use appropriate test duration** based on model size
5. **Clean up resources** after testing
6. **Document test results** for future reference
7. **Test different configurations** (batch sizes, node counts)
8. **Verify checkpoint functionality** regularly