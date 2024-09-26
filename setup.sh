#!/bin/bash
echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing Pillow..."
pip install --only-binary=:all: pillow