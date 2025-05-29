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


$CONTAINER_CMD run \
    --network lbe-iceberg \
    -v $PWD:/app \
    -it \
    spark-base /opt/spark/bin/spark-submit --master spark://spark-master:7077 /app/$1