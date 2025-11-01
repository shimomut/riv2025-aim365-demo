# FSDP Training on SageMaker HyperPod

This project provides a comprehensive FSDP (Fully Sharded Data Parallel) training application designed for SageMaker HyperPod environments. It supports distributed training of large language models including Llama 2, Llama 3.x, Mistral, and Mathstral models using PyTorch FSDP.

## Quick Start

### 1. Validate Setup
```bash
make validate-setup
```

### 2. Run Training
```bash
make run
```

### 3. Monitor Progress
```bash
make logs-follow
```

### 4. Stop Training
```bash
make stop
```

## Documentation

📚 **Complete documentation is available in the [`doc/`](doc/) directory:**

- **[Testing Guide](doc/TESTING_GUIDE.md)** - Comprehensive testing procedures
- **[Quick Reference](doc/TESTING_QUICK_REFERENCE.md)** - Essential commands
- **[Verification Results](doc/VERIFICATION_RESULTS.md)** - Proof of functionality
- **[Documentation Index](doc/README.md)** - Full documentation overview

## Key Features

- ✅ **Verified Working** - Tested on actual HyperPod clusters
- 🚀 **One-Command Deployment** - `make run` to start training
- 📊 **Comprehensive Testing** - Automated test suite with monitoring
- 🔧 **Easy Debugging** - Built-in troubleshooting commands
- 📈 **Performance Monitoring** - Real-time metrics and logging
- 🛡️ **Fault Tolerance** - HyperPod auto-recovery integration

## Supported Models

- Llama 2 (7B, 13B, 70B)
- Llama 3.1 (8B, 70B) 
- Llama 3.2 (1B, 3B)
- Mistral 8x7B
- Mistral Mathstral 7B

## Project Structure

```
├── FSDP/                    # Core training code
│   ├── src/                 # Training scripts and utilities
│   └── kubernetes/          # HyperPod job configurations
├── doc/                     # Documentation
├── tools/                   # Utilities and scripts
│   ├── test_hyperpod_cluster.py # Testing framework
│   └── validate_test_setup.py   # Setup validation
└── Makefile                 # Testing and deployment commands
```

## Requirements

- SageMaker HyperPod cluster with GPU nodes
- kubectl configured for cluster access
- AWS CLI configured
- Container images built and pushed to ECR

## Getting Help

Run `make help` to see all available commands, or check the [documentation](doc/) for detailed guides.