#!/usr/bin/env bash
set -o errexit

# Upgrade pip, setuptools, wheel before anything else
pip install --upgrade pip setuptools wheel

# Install all requirements
pip install -r requirements.txt
