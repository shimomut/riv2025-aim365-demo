# FSDP HyperPod Documentation

This directory contains comprehensive documentation for the FSDP training application on SageMaker HyperPod.

## Quick Start

1. **[Testing Guide](TESTING_GUIDE.md)** - Start here for basic testing procedures
2. **[Quick Reference](TESTING_QUICK_REFERENCE.md)** - Essential commands cheat sheet
3. **[HyperPod Testing Guide](HYPERPOD_TESTING_GUIDE.md)** - Detailed HyperPod-specific testing

## Documentation Index

### Testing Documentation
- **[Testing Guide](TESTING_GUIDE.md)** - Comprehensive testing procedures and workflows
- **[Testing Summary](TESTING_SUMMARY.md)** - Overview of the testing framework components
- **[Testing Quick Reference](TESTING_QUICK_REFERENCE.md)** - Command reference card
- **[HyperPod Testing Guide](HYPERPOD_TESTING_GUIDE.md)** - Detailed HyperPod-specific testing

### Setup Documentation  
- **[Local Dataset Setup](LOCAL_DATASET_SETUP.md)** - Dataset preparation instructions

## Getting Started

### 1. Validate Your Environment
```bash
make validate-setup
```

### 2. Run Quick Test
```bash
make test-quick
```

### 3. Deploy Training Job
```bash
make run
```

### 4. Monitor Training
```bash
make logs-follow
```

### 5. Stop Training
```bash
make stop
```

## Available Make Commands

Run `make help` to see all available commands:

**Basic Operations:**
- `make run` - Deploy FSDP training job
- `make stop` - Stop and cleanup training job
- `make list-pods` - List training pods

**Testing:**
- `make test-cluster` - Full cluster test (5 min monitoring)
- `make test-quick` - Quick test (1 min monitoring)
- `make test-status` - Get current job status
- `make test-logs` - Get recent training logs
- `make test-cleanup` - Cleanup test resources

**Health Checks:**
- `make check-cluster` - Check cluster health
- `make check-job` - Check job status
- `make validate-setup` - Validate complete setup

**Monitoring:**
- `make monitor-pods` - Watch pod status
- `make logs-follow` - Follow training logs
- `make logs-all` - View all recent logs

**Performance:**
- `make perf-test` - Performance test (5 min)

## Testing Framework Components

### Automated Testing Script
- **`tools/test_hyperpod_cluster.py`** - Comprehensive testing automation
- **`tools/validate_test_setup.py`** - Setup validation script

### Configuration Files
- **`FSDP/kubernetes/fsdp-hpto.yaml`** - HyperPodPyTorchJob configuration
- **`Makefile`** - Testing and deployment commands

## Support

For issues or questions:
1. Check the [Testing Guide](TESTING_GUIDE.md) for common solutions
2. Use the [Quick Reference](TESTING_QUICK_REFERENCE.md) for command help
3. Refer to the [HyperPod Testing Guide](HYPERPOD_TESTING_GUIDE.md) for detailed procedures