# Deployment Guidelines

## Kubernetes Deployment

### Prerequisites
- EKS cluster with GPU nodes (P4d, P5, G5)
- Kubeflow Training Operator installed
- EFA networking configured (for multi-node training)
- ECR repository for container images
- HuggingFace access token for gated models

### Container Image Management
```bash
# Build container image
docker build -f FSDP/Dockerfile -t ${REGISTRY}fsdp:pytorch2.7.1 .

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY
docker image push ${REGISTRY}fsdp:pytorch2.7.1
```

### Dataset Preparation
```bash
# Download C4 dataset
cd tools/dataset
pip install -r requirements.txt
python download_c4.py

# The dataset will be cached for training use
```

### Environment Variables
Required environment variables for Kubernetes deployment:
- `IMAGE_URI`: Container image URI
- `INSTANCE_TYPE`: EC2 instance type
- `NUM_NODES`: Number of training nodes
- `GPU_PER_NODE`: GPUs per node
- `EFA_PER_NODE`: EFA interfaces per node
- `HF_TOKEN`: HuggingFace access token

### PyTorchJob Configuration
- Use `HyperPodPyTorchJob` CRD for SageMaker HyperPod
- Configure elastic policy for fault tolerance
- Set appropriate resource requests and limits
- Mount shared storage for checkpoints

## HyperPod Testing Framework

### Prerequisites
- SageMaker HyperPod cluster with GPU nodes
- kubectl configured for cluster access
- AWS CLI configured with appropriate permissions
- Container images built and pushed to ECR

### Testing Framework Validation
```bash
# Validate testing framework setup
make validate-framework

# Check cluster connectivity and health
make validate-setup

# Verify all components are ready
make check-cluster
```

### End-to-End Testing
```bash
# Quick 1-minute validation test
make test-quick

# Comprehensive 5-minute test with monitoring
make test-cluster

# Performance testing
make perf-test
```

### Manual Deployment and Monitoring
```bash
# Deploy training job
make run

# Monitor job status
make check-job

# Follow training logs in real-time
make logs-follow

# Check pod status
make monitor-pods

# Clean up resources
make stop
```

### Local Development Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r FSDP/src/requirements.txt

# For dataset utilities
pip install -r tools/dataset/requirements.txt

# Download test datasets
cd tools/dataset
python download_c4.py
```

## Configuration Templates

### Model-Specific Configurations
Each model requires specific parameters:

**Llama 3.1 8B:**
- `hidden_width=4096`
- `num_layers=32`
- `num_heads=32`
- `intermediate_size=14336`
- `num_key_value_heads=8`

**Mistral 8x7B:**
- `hidden_width=4096`
- `num_layers=32`
- `num_heads=32`
- `intermediate_size=14336`
- `model_type=mixtral`

### Hardware-Specific Settings
**P5 Instances:**
- Comment out FI_* environment variables
- Use 8 GPUs per node
- Enable EFA networking

**G5 Instances:**
- Comment out EFA variables for single GPU instances
- Use 1-4 GPUs per node depending on instance size
- Adjust batch size accordingly

## Monitoring and Logging

### Job Monitoring
```bash
# Using make commands (recommended)
make check-job          # Job and pod status
make logs-follow        # Real-time log streaming
make logs-all          # Recent logs from all pods
make monitor-pods      # Watch pod status updates

# Direct kubectl commands
kubectl get hyperpodpytorchjob
kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto
kubectl logs -f <pod-name>

# Testing framework status
make test-status       # Get comprehensive job status
python3 tools/test_hyperpod_cluster.py --action status
```

### Performance Metrics
Monitor these key metrics:
- Training throughput (samples/sec)
- Loss convergence
- GPU utilization
- Memory usage
- Network bandwidth (for multi-node)

## Troubleshooting

### Common Issues
1. **NCCL Timeout**: Check EFA configuration and network connectivity
2. **OOM Errors**: Reduce batch size or enable activation checkpointing
3. **Checkpoint Loading**: Verify checkpoint directory permissions and paths
4. **HuggingFace Access**: Ensure HF_TOKEN is set correctly for gated models

### Debug Settings
Enable verbose logging:
```bash
export NCCL_DEBUG=INFO
export TORCH_DISTRIBUTED_DEBUG=DETAIL
export TORCH_NCCL_ENABLE_MONITORING=1
```