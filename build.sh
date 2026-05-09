#!/usr/bin/env bash
set -o errexit

# Upgrade pip, setuptools, wheel first
pip install --upgrade pip setuptools wheel

# Install requirements with only binary wheels (no source compilation)
pip install --only-binary :all: -r requirements.txt
