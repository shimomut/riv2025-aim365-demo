# SageMaker HyperPod Integration Guidelines

## HyperPod Training Operator

### Overview
The HyperPod Training Operator extends Kubeflow's PyTorchJob with SageMaker-specific features:
- Managed Tiered Checkpointing (MTC) integration
- Automatic fault tolerance and job recovery
- Deep health checks for training jobs
- Integration with SageMaker monitoring and logging

### HyperPodPyTorchJob CRD
Use the `HyperPodPyTorchJob` Custom Resource Definition instead of standard PyTorchJob:

```yaml
apiVersion: "sagemaker.aws.com/v1"
kind: HyperPodPyTorchJob
metadata:
  name: llama-training-job
spec:
  elasticPolicy:
    rdzvBackend: c10d
    minReplicas: 1
    maxReplicas: 64
    maxRestarts: 100
  pytorchReplicaSpecs:
    Worker:
      replicas: 4
      template:
        spec:
          containers:
          - name: pytorch
            # Container configuration
```

## Managed Tiered Checkpointing (MTC)

### Integration in Training Code
The training script includes MTC integration:

```python
# MTC configuration
use_mtc = True
in_memory_checkpointing_freq = 10
s3_checkpointing_freq = 20

# Checkpoint saving logic
if use_mtc:
    save_in_memory = total_steps % in_memory_checkpointing_freq == 0
    save_s3 = total_steps % s3_checkpointing_freq == 0
    
    if save_in_memory or save_s3:
        save_checkpoint_mtc(
            model, optimizer, lr_scheduler, user_content,
            args.checkpoint_dir, sub_dir, save_in_memory, save_s3, total_steps
        )
```

### MTC Benefits
- **Tiered Storage**: In-memory checkpoints for fast recovery, S3 for durability
- **Automatic Management**: Handles checkpoint lifecycle automatically
- **Fault Tolerance**: Seamless recovery from node failures
- **Cost Optimization**: Reduces storage costs through intelligent tiering

### Configuration Best Practices
- Set `in_memory_checkpointing_freq` for frequent local saves (every 10 steps)
- Set `s3_checkpointing_freq` for durable saves (every 20 steps)
- Use consistent checkpoint directory structure
- Include comprehensive metadata in checkpoints

## Auto-Resume Functionality

### Kubernetes Integration
For HyperPod Kubernetes clusters, use the HyperPodPyTorchJob CRD with auto-resume capabilities built into the training operator.

### Checkpoint Resume Logic
```python
if args.resume_from_checkpoint:
    if use_mtc:
        model, optimizer, lr_scheduler, total_steps, start_batch_index = load_checkpoint_mtc(
            model, optimizer, lr_scheduler, args.resume_from_checkpoint, 
            args.model_type, device
        )
    else:
        model, optimizer, lr_scheduler, total_steps, start_batch_index = load_checkpoint(
            model, optimizer, lr_scheduler, args.resume_from_checkpoint,
            args.model_type, device
        )
```

## Health Checks and Monitoring

### Deep Health Checks
HyperPod provides enhanced health monitoring:
- GPU utilization tracking
- Memory usage monitoring
- Network connectivity checks
- Training progress validation

### Integration with CloudWatch
- Automatic metric collection
- Custom metric publishing
- Alarm configuration for job failures
- Log aggregation and analysis

## Resource Management

### Node Selection
Configure node selectors for optimal resource allocation:

```yaml
nodeSelector:
  node.kubernetes.io/instance-type: "p5.48xlarge"
  sagemaker.aws.com/node-health: "healthy"
```

### Resource Requests and Limits
```yaml
resources:
  requests:
    nvidia.com/gpu: 8
    vpc.amazonaws.com/efa: 32
    memory: "400Gi"
  limits:
    nvidia.com/gpu: 8
    vpc.amazonaws.com/efa: 32
    memory: "400Gi"
```

## Best Practices

### Job Configuration
- Use elastic policies for automatic scaling
- Configure appropriate restart policies
- Set resource quotas to prevent resource exhaustion
- Use priority classes for job scheduling

### Monitoring and Alerting
- Monitor training metrics through CloudWatch
- Set up alerts for job failures or performance degradation
- Use HyperPod dashboards for job visualization
- Implement custom health checks for training validation

### Cost Optimization
- Use spot instances where appropriate
- Implement intelligent checkpointing strategies
- Monitor resource utilization and right-size instances
- Use MTC for cost-effective checkpoint storage

### Security
- Use IAM roles for service authentication
- Encrypt data in transit and at rest
- Implement network policies for pod communication
- Use secrets management for sensitive configuration