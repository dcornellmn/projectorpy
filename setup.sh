#!/bin/sh

# Setup the Flask-based projector API

# Note: This preliminary version assumes installation into the current directory
# Creates a Python virtual environment named "api-venv" and invokes pip

if [ ! -r ./api.py -o ! -r ./projector.py ]; then
	echo "Error: Application not found.\nPlease invoke setup.sh from the same directory where you unpacked the API."
	exit -1
fi

# If a log file exists, we're probably updating, so rotate it
if [ -r projectorapi.log ]; then
	echo "Found existing log file. Rotating to projectorapi.log."
	if [ -r projectorapi.log.old ]; then
		mv -f projectorapi.log projectorapi.log.older
	fi
	mv -f projectorapi.log projectorapi.log.old
fi


# Setup virtual-environment and activate
python3 -m venv --clear api-venv
if [ -r "api-venv/bin/activate" ]; then
	source "./api-venv/bin/activate"
else
	echo "Error: python virtual environment could not be loaded. Exiting."
	exit -3
fi

# Install the prerequisite Python modules
if [ -r requirements.txt ]; then
	pip install -r requirements.txt
	if [ $? -ne 0 ]; then
		echo "PyPI (aka pip) returned an error status. Requirements may not have installed successfully."
		exit -2
else
	echo "Error: requirements.txt missing. Possible incomplete distribution package?"
	exit -1
fi

echo "Requirements satisfied. Invoke run.sh to launch the application."
