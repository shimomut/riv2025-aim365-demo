create-cluster:
	aws sagemaker create-cluster --cli-input-json file://./tools/cluster.json

create-service-account:
	kubectl apply -f tools/service-account.yaml

create-pod-identity-assoc:
	aws eks create-pod-identity-association \
		--cluster-name ${EKS_CLUSTER_NAME} \
		--role-arn ${SERVICE_ACCOUNT_IAMROLE_ARN} \
		--namespace default \
		--service-account riv2025-aim365-demo-service-account

build:
	docker build -t ${REGISTRY}riv2025-aim365-demo:pytorch2.5.1 ./FSDP

build-x:
	docker buildx build --platform linux/amd64 -t ${REGISTRY}riv2025-aim365-demo:pytorch2.5.1 ./FSDP

push:
	bash tools/push.sh

apply:
	kubectl apply -f FSDP/kubernetes/fsdp-hpto.yaml

delete:
	kubectl delete -f FSDP/kubernetes/fsdp-hpto.yaml

list-pods:
	kubectl get pods -A | grep llama

logs:
	stern llama | grep -v "200 OK"

