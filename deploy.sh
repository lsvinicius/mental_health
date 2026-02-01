#!/bin/bash
set -e

IMAGE_NAME="my-local-image"
IMAGE_TAG="1.0"
K8S_VERSION="v1.35.0"
PHYSICAL_CPUS=$(lscpu | grep "Core(s) per socket" | awk '{print $4}')

command -v minikube >/dev/null || { echo "minikube not installed"; exit 1; }
command -v terraform >/dev/null || { echo "terraform not installed"; exit 1; }
command -v docker >/dev/null || { echo "docker not installed"; exit 1; }

minikube status || minikube start --cpus="$PHYSICAL_CPUS" --memory=4g --kubernetes-version="$K8S_VERSION" --driver=docker

eval $(minikube docker-env)

docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

cd local_infra
terraform init -upgrade
terraform apply -auto-approve
