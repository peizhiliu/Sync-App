#!/bin/bash

#this script runs the pull_sync python script every 30 seconds
#which checks the server for any changes


while true; do
	echo "starting pull"
	python3 pull_sync.py
	echo "done"
	sleep 30
done
