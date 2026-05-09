#!/usr/bin/env bash
set -o errexit

# Install setuptools and wheel first before other packages
pip install --upgrade setuptools wheel pip

# Install requirements
pip install -r requirements.txt
