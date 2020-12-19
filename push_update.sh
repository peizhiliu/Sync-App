#!/bin/bash

#this script first detects changes in the directory above
#recursively and then updates the files in the server

while true; do 
	inotifywait -qr -t 1 --exclude '/sync_app' -e modify,move,delete,create ../ | 
	while read events; do 
	echo "starting push"
	python3 push_sync.py
	echo "done"
	sleep 1
	done
done
