#!/bin/bash

# Ask for a number and read it into a variable
echo -n "Enter AS: "
read num_zip

# Global variable for the number of Autonomous Systems, set to 50 by default
num=50

# Create the directory if it does not exist
mkdir -p /home/student/Desktop/IPBGP/

# First loop: Clear IP BGP sessions for each router
for ((current=1; current<=num; current++))
do
    # Execute the command in the docker container for each router
    docker exec "${current}_RTRArouter" vtysh -c 'clear ip bgp *'
done

# Second loop: Check the size of looking_glass.txt files and move them if conditions are met
for ((current=1; current<=num; current++))
do
    src_file="/home/student/Desktop/Simulation/platform/groups/g${current}/RTRA/looking_glass.txt"
    dest_file="/home/student/Desktop/IPBGP/${current}.txt"

    while true; do
        if [[ -f "$src_file" && $(stat --printf="%s" "$src_file") -ge 4000 ]]; then
            mv "$src_file" "$dest_file"
            echo "Moved $src_file to $dest_file"
            break
        else
            echo "File $src_file is smaller than 4000 bytes. Waiting..."
            sleep 3
        fi
    done
done

echo "All files processed. Zipping..."

# Go to the IPBGP directory
cd /home/student/Desktop/IPBGP/

# Create a zip archive with all the .txt files
zip "${num_zip}.zip" *.txt

echo "Completed Packaging into ${num_zip}.zip"
