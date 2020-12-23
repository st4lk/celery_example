#!/usr/bin/env bash

PROJECT_PATH=/app

VENV_NAME=venv_`awk -F= '$1=="ID" { print $2 ;}' /etc/os-release | tr -d '"'`

# create virtualenv if it doesn't exist
if [ ! -d ${PROJECT_PATH}/${VENV_NAME} ]; then
    python3 -m venv ${PROJECT_PATH}/${VENV_NAME}
    ${PROJECT_PATH}/${VENV_NAME}/bin/pip install -U pip
fi

. ${PROJECT_PATH}/${VENV_NAME}/bin/activate
cd ${PROJECT_PATH}

ENV=${VENV_NAME} exec "$@"
