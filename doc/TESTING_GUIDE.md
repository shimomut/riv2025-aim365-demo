# HyperPod FSDP Testing Guide

## Quick Start

### 1. Validate Your Setup
```bash
make validate-setup
```

### 2. Run a Quick Test
```bash
make test-quick
```

### 3. Monitor Training
```bash
make logs-follow
```

## Testing Commands

### Basic Testing Workflow
```bash
# 1. Check cluster health
make check-cluster

# 2. Deploy and test (1 minute monitoring)
make test-quick

# 3. View logs
make logs-all

# 4. Clean up
make test-cleanup
```

### Full Testing Suite
```bash
# Run comprehensive 5-minute test
make test-cluster

# Performance test
make perf-test
```

### Manual Job Control
```bash
# Deploy job
make run

# Check status
kubectl get hyperpodpytorchjob
kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto

# Follow logs
make logs-follow

# Stop job
make stop
```

## Expected Results

### Success Indicators
- ✅ All pods reach "Running" state within 5 minutes
- ✅ Training logs show "Loss:" values decreasing
- ✅ No NCCL timeout errors
- ✅ GPU utilization > 80%
- ✅ Checkpoints save to /fsx/checkpoints

### Performance Benchmarks
- **Llama 3.1 8B on 8x G5.8xlarge**: ~2-3 samples/sec/GPU
- **Memory usage**: <32GB per GPU with activation checkpointing
- **Network**: EFA should show >10 Gbps between nodes

## Troubleshooting

### Common Issues
```bash
# Pods stuck in Pending
kubectl describe pod <pod-name>

# NCCL timeout errors
kubectl logs <pod-name> | grep NCCL

# Out of memory
kubectl top pods -l job-name=llama3-1-8b-fsdp-hpto

# Debug job details
make debug-describe
make debug-events
```

### Access Pod for Debugging
```bash
kubectl exec -it llama3-1-8b-fsdp-hpto-pods-0 -- /bin/bash
```

## Test Scenarios

### Scenario 1: Basic Functionality
1. `make validate-setup` - Check prerequisites
2. `make run` - Deploy job
3. Wait 5 minutes for pods to start
4. `make logs-follow` - Verify training starts
5. `make stop` - Clean up

### Scenario 2: Multi-Node Communication
1. Deploy 8-node job
2. Monitor all pods reach Running
3. Check NCCL initialization in logs
4. Verify no communication timeouts

### Scenario 3: Fault Tolerance
1. Start training job
2. Delete one pod manually
3. Verify HyperPod restarts it
4. Check training resumes from checkpoint

## Available Commands Reference

Run `make help` to see all available commands:
- **Basic**: run, stop, list-pods
- **Testing**: test-cluster, test-quick, test-status
- **Health**: check-cluster, check-job, validate-setup
- **Monitoring**: monitor-pods, logs-follow, logs-all
- **Debug**: debug-describe, debug-events