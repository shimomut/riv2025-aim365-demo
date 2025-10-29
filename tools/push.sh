# Create registry if needed
REGISTRY_COUNT=$(aws ecr describe-repositories | grep "fsdp" | wc -l)
if [ "$REGISTRY_COUNT" -eq 0 ]; then
    aws ecr create-repository --repository-name fsdp
fi

# Login to registry
echo "Logging in to $REGISTRY ..."
aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY

# Push image to registry
docker image push ${REGISTRY}fsdp:pytorch2.5.1
