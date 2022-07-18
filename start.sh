#!/bin/bash
docker run \
    --rm -it \
    --name classbot-3.0 \
    --env-file .env \
    ghcr.io/azure-agst/classbot-3.0
