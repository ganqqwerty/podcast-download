#!/bin/bash

# Check if the directory is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 directory"
    exit 1
fi

DIRECTORY="$1"

# Check if exiftool is installed
if ! command -v exiftool &> /dev/null; then
    echo "exiftool could not be found"
    exit 1
fi

# Calculate total duration
total_duration=$(exiftool -q -p '$Duration#' -r -ext mp3 "$DIRECTORY" | awk '{s+=$1} END {print s}')

total_hours=$(echo "scale=2; $total_duration / 3600" | bc)
echo "Total duration: $total_duration seconds ($total_hours hours)"
