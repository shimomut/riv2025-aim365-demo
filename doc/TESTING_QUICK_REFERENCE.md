# HyperPod Testing Quick Reference

## Essential Commands

### Setup Validation
```bash
# Validate entire testing framework
make validate-framework

# Check cluster health
make validate-setup

# Check specific components
make check-cluster
make check-job
```

### Basic Testing Workflow
```bash
# 1. Quick test (1 minute)
make test-quick

# 2. Full test (5 minutes)  
make test-cluster

# 3. Monitor training
make logs-follow

# 4. Check status
make test-status

# 5. Cleanup
make test-cleanup
```

### Manual Job Control
```bash
# Deploy job
make run

# Monitor pods
kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto -w

# Get logs
kubectl logs -f llama3-1-8b-fsdp-hpto-pods-0

# Stop job
make stop
```

### Troubleshooting
```bash
# Describe job details
make debug-describe

# Check recent events
make debug-events

# Access pod shell
kubectl exec -it llama3-1-8b-fsdp-hpto-pods-0 -- /bin/bash

# View all logs
make logs-all
```

### Performance Monitoring
```bash
# Watch resource usage
kubectl top pods -l job-name=llama3-1-8b-fsdp-hpto

# Monitor job status
make monitor-job

# Performance test
make perf-test
```

## Key Files

- `test_hyperpod_cluster.py` - Main testing framework
- `FSDP/kubernetes/fsdp-hpto.yaml` - Job configuration
- `Makefile` - Testing commands
- `doc/HYPERPOD_TESTING_GUIDE.md` - Detailed guide

## Success Indicators

✅ All pods reach "Running" state  
✅ Training logs show "Loss:" values  
✅ No NCCL timeout errors  
✅ GPU utilization > 80%  
✅ Checkpoints save successfully  

## Common Issues

❌ **Pods Pending**: Check node resources  
❌ **NCCL Timeout**: Verify EFA configuration  
❌ **OOM Errors**: Reduce batch size  
❌ **No Logs**: Check pod status and events