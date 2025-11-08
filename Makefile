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

run: run-p5
stop: stop-p5

run-g5:
	kubectl apply -f FSDP/kubernetes/fsdp-hpto-g5.yaml

stop-g5:
	kubectl delete -f FSDP/kubernetes/fsdp-hpto-g5.yaml

run-p5:
	kubectl apply -f FSDP/kubernetes/fsdp-hpto-p5.yaml

stop-p5:
	kubectl delete -f FSDP/kubernetes/fsdp-hpto-p5.yaml

list-pods:
	kubectl get pods -A | grep llama

watch:
	stern llama3-1-8b-fsdp-hpto-pods-0

# Testing Commands
test-cluster:
	python3 tools/test_hyperpod_cluster.py --action full-test --monitor-duration 300

test-quick:
	python3 tools/test_hyperpod_cluster.py --action full-test --monitor-duration 60

test-status:
	python3 tools/test_hyperpod_cluster.py --action status

test-logs:
	python3 tools/test_hyperpod_cluster.py --action logs

test-cleanup:
	python3 tools/test_hyperpod_cluster.py --action cleanup

# Health Checks
check-cluster:
	@echo "🔍 Checking cluster health..."
	kubectl cluster-info
	@echo "\n📊 Node status:"
	kubectl get nodes -o wide
	@echo "\n🎯 GPU nodes:"
	kubectl get nodes -l sagemaker.amazonaws.com/compute-type -o wide
	@echo "\n💾 Storage claims:"
	kubectl get pvc
	@echo "\n🔧 HyperPod operator:"
	kubectl get pods -n kubeflow -l app=training-operator

check-job:
	@echo "📊 Job Status:"
	kubectl get hyperpodpytorchjob
	@echo "\n🏃 Pod Status:"
	kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto -o wide
	@echo "\n📋 Recent Events:"
	kubectl get events --sort-by=.metadata.creationTimestamp | tail -10

validate-setup:
	@echo "✅ Validating HyperPod setup..."
	@echo "1. Checking cluster connectivity..."
	@kubectl cluster-info > /dev/null && echo "   ✅ Cluster accessible" || echo "   ❌ Cluster not accessible"
	@echo "2. Checking HyperPod operator..."
	@kubectl get pods -n kubeflow -l app=training-operator | grep -q Running && echo "   ✅ HyperPod operator running" || echo "   ❌ HyperPod operator not running"
	@echo "3. Checking GPU nodes..."
	@kubectl get nodes -l sagemaker.amazonaws.com/compute-type | grep -q Ready && echo "   ✅ GPU nodes available" || echo "   ❌ No GPU nodes ready"
	@echo "4. Checking storage..."
	@kubectl get pvc fsx-claim | grep -q Bound && echo "   ✅ FSx storage bound" || echo "   ❌ FSx storage not bound"
	@echo "5. Checking service account..."
	@kubectl get serviceaccount riv2025-aim365-demo-service-account > /dev/null && echo "   ✅ Service account exists" || echo "   ❌ Service account missing"

# Monitoring
monitor-pods:
	watch -n 5 'kubectl get pods -l job-name=llama3-1-8b-fsdp-hpto -o wide'

logs-follow:
	kubectl logs -f -l job-name=llama3-1-8b-fsdp-hpto

logs-all:
	kubectl logs -l job-name=llama3-1-8b-fsdp-hpto --tail=100

# Debug
debug-describe:
	kubectl describe hyperpodpytorchjob llama3-1-8b-fsdp-hpto

debug-events:
	kubectl get events --field-selector involvedObject.name=llama3-1-8b-fsdp-hpto --sort-by=.metadata.creationTimestamp

# Performance Testing
perf-test:
	@echo "🚀 Running performance test (5 minutes)..."
	python3 tools/test_hyperpod_cluster.py --action full-test --monitor-duration 300

# Framework Validation
validate-framework:
	python3 tools/validate_test_setup.py

# Help
help:
	@echo "HyperPod FSDP Testing Commands:"
	@echo ""
	@echo "Basic Operations:"
	@echo "  make run              - Deploy FSDP training job"
	@echo "  make stop             - Stop and cleanup training job"
	@echo "  make list-pods        - List training pods"
	@echo ""
	@echo "Testing:"
	@echo "  make test-cluster     - Full cluster test (5 min monitoring)"
	@echo "  make test-quick       - Quick test (1 min monitoring)"
	@echo "  make test-status      - Get current job status"
	@echo "  make test-logs        - Get recent training logs"
	@echo "  make test-cleanup     - Cleanup test resources"
	@echo ""
	@echo "Health Checks:"
	@echo "  make check-cluster    - Check cluster health"
	@echo "  make check-job        - Check job status"
	@echo "  make validate-setup   - Validate complete setup"
	@echo "  make validate-framework - Validate testing framework"
	@echo ""
	@echo "Monitoring:"
	@echo "  make monitor-pods     - Watch pod status"
	@echo "  make logs-follow      - Follow training logs"
	@echo "  make logs-all         - View all recent logs"
	@echo ""
	@echo "Performance:"
	@echo "  make perf-test        - Performance test (5 min)"

