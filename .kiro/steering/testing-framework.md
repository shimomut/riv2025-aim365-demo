# HyperPod Testing Framework Guidelines

## Overview

The project includes a comprehensive, verified testing framework for SageMaker HyperPod FSDP training applications. This framework has been tested on actual HyperPod clusters and provides reliable validation of the complete training pipeline.

## Testing Framework Components

### Core Scripts
- **`tools/test_hyperpod_cluster.py`**: Comprehensive HyperPod testing automation
- **`tools/validate_test_setup.py`**: Testing framework validation and prerequisites
- **`Makefile`**: Standardized commands for all testing operations
- **`doc/`**: Complete documentation and guides

### Key Features
- **Verified on Real Clusters**: Tested on actual HyperPod infrastructure
- **End-to-End Validation**: Complete pipeline testing from deployment to cleanup
- **Automated Monitoring**: Real-time progress tracking and status reporting
- **Comprehensive Diagnostics**: Detailed job status and troubleshooting information
- **One-Command Operations**: Simple make commands for all operations

## Standard Testing Workflow

### 1. Framework Validation
```bash
make validate-framework
```
**Purpose**: Validates that the testing framework is properly set up
**Checks**: Required files, script executability, kubectl availability, make commands

### 2. Cluster Health Check
```bash
make validate-setup
```
**Purpose**: Verifies cluster connectivity and component health
**Checks**: Cluster access, GPU nodes, storage claims, service accounts

### 3. Quick Validation Test
```bash
make test-quick
```
**Purpose**: 1-minute end-to-end validation test
**Process**: Deploy job → Wait for pods → Monitor briefly → Cleanup

### 4. Comprehensive Testing
```bash
make test-cluster
```
**Purpose**: 5-minute comprehensive test with detailed monitoring
**Process**: Full validation → Extended monitoring → Performance metrics → Cleanup

### 5. Performance Testing
```bash
make perf-test
```
**Purpose**: Performance validation and benchmarking
**Process**: Extended monitoring → Throughput analysis → Resource utilization

## Manual Operations

### Job Deployment
```bash
make run                # Deploy training job
make check-job         # Check job and pod status
make logs-follow       # Monitor training progress
make stop             # Clean up resources
```

### Monitoring and Debugging
```bash
make monitor-pods      # Watch pod status updates
make logs-all         # View recent logs from all pods
make debug-describe   # Get detailed job configuration
make debug-events     # View recent cluster events
make test-status      # Get comprehensive status JSON
```

## Testing Best Practices

### Development Workflow
1. **Always validate framework first**: `make validate-framework`
2. **Check cluster health**: `make validate-setup`
3. **Run quick test for validation**: `make test-quick`
4. **Use comprehensive testing for thorough validation**: `make test-cluster`
5. **Monitor real deployments**: `make run` → `make logs-follow` → `make stop`

### Continuous Integration
```bash
# CI/CD pipeline integration
make validate-framework  # Framework validation
make validate-setup     # Cluster connectivity
make test-quick        # Quick validation for PRs
make test-cluster      # Comprehensive testing for releases
```

### Troubleshooting Workflow
```bash
# Systematic troubleshooting
make validate-framework  # Ensure tools work
make validate-setup     # Check cluster health
make check-job         # Current job status
make debug-describe    # Job configuration details
make debug-events      # Recent cluster events
make logs-all         # Training logs analysis
```

## Expected Results and Benchmarks

### Success Indicators
- ✅ All pods reach "Running" state within 5 minutes
- ✅ Training logs show "Loss:" values decreasing
- ✅ No NCCL timeout errors in logs
- ✅ GPU utilization > 80%
- ✅ Checkpoints save successfully to `/fsx/checkpoints`

### Performance Benchmarks
- **Llama 3.1 8B on 8x G5.8xlarge**: ~2-3 samples/sec/GPU
- **Memory usage**: <32GB per GPU with activation checkpointing
- **Network bandwidth**: >10 Gbps between nodes with EFA
- **Pod startup time**: <5 minutes for all 8 pods
- **NCCL initialization**: <2 minutes for multi-node setup

### Common Test Results
```json
{
  "timestamp": "2025-11-01T03:15:20.376849",
  "job_exists": true,
  "job_status": {
    "conditions": [
      {"type": "Created", "status": "True"},
      {"type": "PodsRunning", "status": "True"},
      {"type": "Running", "status": "True"}
    ],
    "masterAddr": "10.2.8.64",
    "masterPort": "1234"
  }
}
```

## Integration with Development

### Code Changes Validation
```bash
# After code changes
make validate-framework  # Ensure framework still works
make test-quick         # Quick validation of changes
```

### Pre-deployment Validation
```bash
# Before production deployment
make validate-setup     # Cluster readiness
make test-cluster      # Comprehensive validation
make perf-test        # Performance validation
```

### Production Monitoring
```bash
# Production job monitoring
make run              # Deploy production job
make monitor-pods     # Watch deployment progress
make logs-follow      # Monitor training progress
make check-job       # Regular status checks
```

## Advanced Usage

### Direct Script Usage
```bash
# Framework validation
python3 tools/validate_test_setup.py

# Comprehensive testing with custom duration
python3 tools/test_hyperpod_cluster.py --action full-test --monitor-duration 600

# Status checking
python3 tools/test_hyperpod_cluster.py --action status

# Log retrieval
python3 tools/test_hyperpod_cluster.py --action logs

# Cleanup
python3 tools/test_hyperpod_cluster.py --action cleanup
```

### Custom Test Scenarios
```bash
# Test different model configurations
# Edit FSDP/kubernetes/fsdp-hpto.yaml
make test-quick

# Test with different hardware
# Update node selectors in job configuration
make validate-setup
make test-cluster

# Performance testing with monitoring
make perf-test
kubectl top pods -l job-name=llama3-1-8b-fsdp-hpto
```

## Documentation References

- **`doc/TESTING_GUIDE.md`**: Comprehensive testing procedures
- **`doc/TESTING_QUICK_REFERENCE.md`**: Command reference card
- **`doc/VERIFICATION_RESULTS.md`**: Verified test results and evidence
- **`doc/TESTING_SUMMARY.md`**: Framework overview and components
- **`doc/TOOLS_REORGANIZATION.md`**: Tools organization and structure

## Support and Troubleshooting

For issues with the testing framework:
1. Check `doc/TESTING_GUIDE.md` for detailed procedures
2. Review `doc/VERIFICATION_RESULTS.md` for expected behavior
3. Use `make debug-describe` and `make debug-events` for diagnostics
4. Refer to the troubleshooting guide for common issues and solutions

The testing framework provides a reliable, production-ready approach to validating FSDP training on HyperPod clusters.