#!/bin/bash

# Check if podman is installed; otherwise use docker
if command -v podman &> /dev/null; then
    echo "Using Podman"
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    echo "Using Docker"
    CONTAINER_CMD="docker"
else
    echo "Neither podman nor docker is installed. Please install one of them."
    exit 1
fi


$CONTAINER_CMD network create lbe-iceberg

cd minio
mkdir ./data

echo "Building mino-init docker image"
$CONTAINER_CMD build -t minio-init -f ./minio/minio-init.dockerfile ./minio

$CONTAINER_CMD compose up -d

open http://localhost:9001