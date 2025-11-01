IMAGE_NAME=shell-tools

build:
	docker build --tag ${IMAGE_NAME} .

login:
	aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com

tag:
	docker tag ${IMAGE_NAME}:latest ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}:latest

push:
	docker push ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}:latest