#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Source the .env file
source .env

# Check if AWS_ACCOUNT_ID is set
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_ACCOUNT_ID environment variable is not set"
    exit 1
fi

# Check if AWS_REGION is set
if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS_REGION environment variable is not set"
    exit 1
fi

# Check AWS credentials and ECR access
echo "Checking AWS credentials and ECR access..."
if ! aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com > /dev/null 2>&1; then
    echo "Error: Unable to authenticate with AWS ECR. Please check your AWS credentials and permissions."
    exit 1
fi
echo "AWS credentials and ECR access verified."

# Get the current git hash
GIT_HASH=$(git rev-parse --short HEAD)

# AWS ECR repository URLs
ECR_REPO_REQUESTS="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/prop_backend_requests"
ECR_REPO_WORKER="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/prop_backend_worker"
ECR_REPO_CLUSTALW="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/prop_backend_clustalw"
ECR_REPO_MAFFT="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/prop_backend_mafft"

# Create .dockerignore file
cat <<EOF >./.dockerignore
.git
.cache
node_modules
.gitignore
frontend
EOF

# Stop and remove existing containers
echo "Stopping backend containers"
docker container stop $(docker container ls -q --filter name=prop_backend_) || true
echo "Deleting backend containers"
docker rm $(docker container ls -a -q --filter name=prop_backend_) || true

# Remove existing images
echo "Deleting backend images"
docker rmi $(docker images -q --filter=reference='prop_backend_*:*') || true

# Delete Docker volume
echo "Deleting Docker volume"
docker volume rm prop_docker_volume || true

# Prune Docker system
echo "Pruning leftover Docker layers and caches"
docker system prune -a --force

# Build Docker images
echo "Building Docker images"
docker compose -f compose.yml build

# Tag and push images to ECR
echo "Tagging and pushing images to ECR"

# Function to tag and push an image
tag_and_push() {
    local image_name=$1
    local ecr_repo=$2
    
    echo "Processing $image_name"
    
    # Tag with Git hash
    docker tag $image_name:latest $ecr_repo:$GIT_HASH
    docker push $ecr_repo:$GIT_HASH
    
    # Tag as latest
    docker tag $image_name:latest $ecr_repo:latest
    docker push $ecr_repo:latest
}

# Tag and push each image
tag_and_push prop_backend_requests $ECR_REPO_REQUESTS
tag_and_push prop_backend_worker $ECR_REPO_WORKER
tag_and_push prop_backend_clustalw $ECR_REPO_CLUSTALW
tag_and_push prop_backend_mafft $ECR_REPO_MAFFT

# Clean up
rm .dockerignore

echo "Build and upload process completed successfully"
echo "Images tagged with Git hash: $GIT_HASH and 'latest'"
