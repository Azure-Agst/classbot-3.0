#!/bin/bash

# If requesting to run for real...
if [[ $* == *--prod* ]]; then

    docker run \
        --rm -dt \
        --name classbot-3.0 \
        --env-file .env \
        ghcr.io/azure-agst/classbot-3.0

# If dev flag specified...
elif [[ $* == *--dev* ]]; then

    docker run \
        --rm -it \
        --name classbot-3.0 \
        --env-file .env \
        -w /usr/app/src \
        -v $(pwd):/usr/app/src \
        python:3.10.5-slim-bullseye \
        sh -c "\
            pip install -r requirements.txt && \
            python -m fsu-classbot \
        "

else

    # if nothing was defined, print help and leave
    echo -e "\n\e[36m============================================"
    echo -e "  start.sh"
    echo -e "  (c) 2022 Andrew \"Azure-Agst\" Augustine"
    echo -e "============================================\e[0m\n"
    echo -e "Usage: ./_start.sh \e[33m[ --prod | --dev ]\e[0m\n"
    echo -e "\e[33m--prod\e[0m: Starts the server in prebuilt Docker image"
    echo -e "\e[33m --dev\e[0m: Starts the server in development image, using bind mounts"

fi

exit 0
