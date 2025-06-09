#!/bin/zsh
# Script to run the Streamlit app for PDF Lab Report Extraction

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if required packages are installed
if ! pip show streamlit &> /dev/null; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Run the Streamlit app
echo "Starting Streamlit app..."
streamlit run streamlit_app.py
