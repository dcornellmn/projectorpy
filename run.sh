#!/bin/sh

# set environment variables for configuration
# DON'T CHANGE THESE HERE, IT WILL BE OVERWRITTEN ON UPGRADES
# Instead, set the variables in your runtime environment and it will use them
if [ "x$PROJECTOR_SERIAL" = "x" ]; then
	PROJECTOR_SERIAL="/dev/ttyAMA0"
	export PROJECTOR_SERIAL
fi

# Prerequisites check
if [ ! -r ./api-venv/bin/activate ]; then 
	echo "Error: python3 virtual environment not found. Please run setup.sh first."
	exit -1
fi

# Launch the Flask-based projector API as a foreground application
source ./api-venv/bin/activate
python api.py $*
