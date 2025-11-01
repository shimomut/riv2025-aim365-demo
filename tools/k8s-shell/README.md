# Kubernetes Shell Pod

This directory contains a YAML configuration and Dockerfile for an interactive shell pod to help with debugging and development.

## Building the Shell Image

Build a custom image with additional tools (Python, AWS CLI, kubectl):

```bash
# Build the image
docker build -t shell-tools:latest tools/k8s-shell/

# Tag and push to your registry (optional)
docker tag shell-tools:latest your-registry/shell-tools:latest
docker push your-registry/shell-tools:latest
```

## Shell Pod (`shell-pod.yaml`)

A pod for debugging and testing with pre-installed development tools.

**Usage with default Ubuntu image:**
```bash
# Deploy the pod
kubectl apply -f tools/k8s-shell/shell-pod.yaml

# Connect to the shell
kubectl exec -it fsdp-shell -- bash

# Clean up
kubectl delete pod fsdp-shell
```

**Usage with custom shell image:**
```bash
# Set your custom image
export SHELL_IMAGE=your-registry/shell-tools:latest

# Deploy the pod
envsubst < tools/k8s-shell/shell-pod.yaml | kubectl apply -f -

# Connect to the shell
kubectl exec -it fsdp-shell -- bash

# Clean up
kubectl delete pod fsdp-shell
```

## Common Use Cases

### AWS Operations
```bash
# Inside the pod (with custom image)
aws s3 ls
aws sts get-caller-identity
```

### Python Development
```bash
# Inside the pod (with custom image)
python --version
pip list
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Kubernetes Operations
```bash
# Inside the pod (with custom image)
kubectl get pods
kubectl get nodes
```

### Network Testing
```bash
# Inside the pod
curl -I https://huggingface.co
nslookup kubernetes.default.svc.cluster.local
```

### File System Testing
```bash
# Inside the pod
ls -la /workspace
ls -la /fsx  # FSx Lustre mount
df -h
```

## Included Tools (Custom Image)

The custom Dockerfile includes:
- Python 3.11 with pip
- AWS CLI v2
- kubectl
- Common development tools (git, vim, curl, wget, jq, htop, tree)
- Python packages: boto3, requests, pyyaml, numpy, pandas, matplotlib, jupyter, ipython

## Notes

- The pod uses `sleep infinity` to stay running for interactive access
- Default Ubuntu 22.04 image or custom image with development tools
- Includes workspace volume and FSx Lustre mount at `/fsx`
- Memory allocation: 1-2GB with CPU limits
- Remember to clean up the pod when done to free cluster resources