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
docker build -f Dockerfile -t ${REGISTRY}fsdp:pytorch2.7.1 .

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY
docker image push ${REGISTRY}fsdp:pytorch2.7.1
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

## Slurm Deployment

### Prerequisites
- Slurm cluster with GPU nodes
- Shared FSx for Lustre filesystem
- Python virtual environment or container runtime
- EFA drivers installed
- HuggingFace access token

### Environment Setup
```bash
# Create virtual environment
./create_venv.sh

# Or use container
enroot import -o pytorch-fsdp.sqsh dockerd://fsdp:pytorch2.7.1
```

### Job Submission
```bash
# Submit training job
sbatch llama3_1_8b-training.sbatch
```

### SBATCH Configuration
- Set appropriate node count and GPU allocation
- Configure EFA environment variables
- Set up shared filesystem mounts
- Include auto-resume for HyperPod clusters

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
# Kubernetes
kubectl get pytorchjob
kubectl logs -f <pod-name>

# Slurm
squeue
tail -f logs/<job-name>_<job-id>.out
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