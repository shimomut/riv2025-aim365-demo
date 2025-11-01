# FSDP Training Application Project Overview

## Project Description

This project provides a comprehensive FSDP (Fully Sharded Data Parallel) training application designed for SageMaker HyperPod environments. The application supports distributed training of large language models including Llama 2, Llama 3.x, Mistral, and Mathstral models using PyTorch FSDP.

## Key Technologies

- **PyTorch FSDP**: Fully Sharded Data Parallel for distributed training
- **SageMaker HyperPod**: AWS managed training infrastructure
- **HyperPod Training Operator**: Kubernetes-based training orchestration using "HyperPodPyTorchJob" CRD
- **Managed Tiered Checkpointing (MTC)**: Advanced checkpointing library for fault tolerance
- **Container Orchestration**: Support for both Kubernetes and Slurm deployment

## Project Structure

```
FSDP/
├── src/                    # Core training code
│   ├── train.py           # Main training script
│   ├── requirements.txt   # Python dependencies
│   └── model_utils/       # Utility modules
│       ├── arguments.py   # Command-line argument parsing
│       ├── checkpoint.py  # Checkpointing functionality
│       ├── train_utils.py # Training utilities
│       └── concat_dataset.py # Dataset utilities
├── kubernetes/            # Kubernetes deployment manifests
│   ├── *.yaml            # Model-specific training configurations
│   └── templates/        # Configuration templates
├── Dockerfile            # Container image definition
└── README.md            # FSDP module documentation

tools/
├── test_hyperpod_cluster.py # Comprehensive HyperPod testing framework
├── validate_test_setup.py   # Testing framework validation
├── dataset/              # Dataset utilities
│   ├── download_c4.py   # C4 dataset download script
│   └── requirements.txt # Dataset tool dependencies
├── internal/            # Internal environment scripts
├── k8s-shell/           # Kubernetes shell utilities
├── cluster.json         # Cluster configuration
├── policy.json         # IAM policy configuration
├── push.sh             # Container push script
└── service-account.yaml # Kubernetes service account

doc/                     # Comprehensive documentation
├── README.md           # Documentation index
├── TESTING_GUIDE.md    # Testing procedures
├── VERIFICATION_RESULTS.md # Verified test results
└── [other guides...]   # Additional documentation

data/                    # Dataset storage (empty by default)
logs/                   # Training logs
Makefile                # Testing and deployment commands
```

## Supported Models

- Llama 2 (7B, 13B, 70B)
- Llama 3.1 (8B, 70B) 
- Llama 3.2 (1B, 3B)
- Mistral 8x7B
- Mistral Mathstral 7B

## Deployment Platforms

1. **Kubernetes with HyperPod Training Operator**
2. **Amazon EKS**
3. **Standard Kubernetes clusters**

## Core Features

- Multi-node distributed training
- Automatic checkpointing and resume
- Mixed precision training (BF16)
- Activation checkpointing for memory optimization
- Streaming dataset support (HuggingFace datasets)
- EFA (Elastic Fabric Adapter) support for high-performance networking
- Dataset download utilities (C4 dataset support)
- Container-based deployment with Docker
- **Comprehensive Testing Framework**: Verified HyperPod cluster testing
- **One-Command Operations**: `make run`, `make stop`, `make test-quick`
- **Automated Validation**: Framework and cluster health checks
- **Real-time Monitoring**: Training progress and resource monitoring

## Testing and Validation

The project includes a comprehensive testing framework that has been verified on actual HyperPod clusters:

### Quick Start Commands
```bash
make validate-framework  # Validate testing framework
make validate-setup     # Check cluster connectivity
make test-quick        # 1-minute end-to-end test
make run              # Deploy training job
make logs-follow      # Monitor training progress
make stop            # Clean up resources
```

### Testing Framework Components
- **`tools/test_hyperpod_cluster.py`**: Comprehensive cluster testing automation
- **`tools/validate_test_setup.py`**: Framework validation and prerequisites check
- **Makefile**: Standardized commands for all operations
- **Documentation**: Complete guides in `doc/` directory