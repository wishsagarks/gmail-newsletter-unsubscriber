#!/bin/bash

# Simple launcher for the Streamlit app

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run Streamlit
streamlit run Home.py
