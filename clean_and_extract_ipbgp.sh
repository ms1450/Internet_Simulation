#!/bin/bash

echo "Configuration Cleaner and Extractor"
# Ask for a number and read it into a variable
echo -n "[i] Enter AS: "
read num_zip
base_dir=/home/student/Desktop/Simulation/
ipbgp_dir="${base_dir}/IP_BGP_Path/"

# Global variable for the number of Autonomous Systems, set to 50 by default
num=50

# Create the directory if it does not exist
mkdir -p "${ipbgp_dir}"

# First loop: Clear IP BGP sessions for each router
echo "[+] Cleaning IP BGP sessions for each AS"
for ((current=1; current<=num; current++))
do
    echo "[+] Cleaning ${current}.."
    # Execute the command in the docker container for each router
    docker exec "${current}_RTRArouter" vtysh -c 'clear ip bgp *'
done
echo "[+] Cleaning Completed"

# Second loop: Check the size of looking_glass.txt files and move them if conditions are met
echo "[+] Moving IP BGP Paths"
for ((current=1; current<=num; current++))
do
    src_file="${base_dir}/platform/groups/g${current}/RTRA/looking_glass.txt"
    dest_file="${ipbgp_dir}/${current}.txt"

    while true; do
        if [[ -f "$src_file" && $(stat --printf="%s" "$src_file") -ge 4000 ]]; then
            mv "$src_file" "$dest_file"
            echo "[+] Moved $src_file to $dest_file"
            break
        else
            echo "[-] File $src_file is smaller than 4000 bytes. Waiting..."
            sleep 3
        fi
    done
done

echo "[+] Completed Moving files processed. Zipping..."

# Go to the IPBGP directory
cd "${ipbgp_dir}"

# Create a zip archive with all the .txt files
zip "${num_zip}.zip" *.txt
echo "[+] Completed Packaging ${num_zip}.zip"

# Cleaning temporary txt files
rm -f *.txt
echo "[+] Completed, Goodbye!"
