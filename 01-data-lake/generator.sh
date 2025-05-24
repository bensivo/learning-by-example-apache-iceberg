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

cd generator

$CONTAINER_CMD build -t generator -f ./generator.dockerfile .
$CONTAINER_CMD run --network=lbe-iceberg generator
