
export AWS_REGION=us-east-2
export AWS_DEFAULT_REGION=us-east-2

create-cluster:
	aws sagemaker create-cluster --cli-input-json file://./tools/cluster.json

update-kubeconfig:
	aws eks update-kubeconfig --name sagemaker-k8-demo-1-27d77433-eks


create-service-account:
	kubectl apply -f tools/service-account.yaml

create-pod-identity-assoc:
	aws eks create-pod-identity-association \
		--cluster-name sagemaker-k8-demo-1-27d77433-eks \
		--role-arn arn:aws:iam::842413447717:role/Riv2025-AIM365-Demo-Role \
		--namespace default \
		--service-account riv2025-aim365-demo-service-account

build:
	docker build -t ${REGISTRY}fsdp:pytorch2.5.1 ./FSDP

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

