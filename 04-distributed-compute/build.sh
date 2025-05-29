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

echo "Building Spark docker images"
$CONTAINER_CMD build -t spark-base . -f ./spark-base.dockerfile
$CONTAINER_CMD build -t spark-master . -f ./spark-master.dockerfile
$CONTAINER_CMD build -t spark-worker . -f ./spark-worker.dockerfile
