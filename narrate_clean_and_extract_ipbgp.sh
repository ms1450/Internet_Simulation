#!/bin/bash

# Prompt for AS and POISON_AS
read -p "[i] Enter AS: " AS
read -p "[i] Enter POISONED AS: " POISON_AS

# Initialize the configuration output
output="conf t\n"
output+="router bgp $AS\n"
output+="route-map $POISON_AS-POISON permit 10\n"
output+="set as-path prepend $POISON_AS\n"
output+="end\n"
output+="conf t\n"
output+="router bgp $AS\n"

# Read neighbor inputs
counter=1
while true; do
    read -p "[i] Enter NEIGHBOUR $counter (leave empty to stop): " neighbor
    if [ -z "$neighbor" ]; then
        break
    fi
    output+="neighbor $neighbor route-map $POISON_AS-POISON out\n"
    ((counter++))
done

output+="end\nwrite file"

# Display the output
echo -e "$output"

# Wait for user input to proceed
read -p "Press enter to continue with the Configuration Cleaner and Extractor script..."
echo "Configuration Cleaner and Extractor"
base_dir=/home/student/Desktop/Simulation/
ipbgp_dir="${base_dir}/IP_BGP_Path/"

# Global variable for the number of Autonomous Systems, set to 50 by default
num=50

# Create the directory if it does not exist
mkdir -p "${ipbgp_dir}"

# Clear IP BGP sessions for each router
echo "[+] Cleaning IP BGP sessions for each AS"
for ((current=1; current<=num; current++))
do
    echo "[+] Cleaning ${current}.."
    docker exec "${current}_RTRArouter" vtysh -c 'clear ip bgp *'
done
echo "[+] Cleaning Completed"
echo "[~] Sleeping for 20 Seconds to let BGP messages propagate..."
sleep 20

# Copy IP BGP Paths
echo "[+] Copying IP BGP Paths"
for ((current=1; current<=num; current++))
do
    src_file="${base_dir}/platform/groups/g${current}/RTRA/looking_glass_json.txt"
    dest_file="${ipbgp_dir}/${current}.txt"

    while true; do
        cp "$src_file" "$dest_file"

        if [[ -f "$dest_file" && $(stat --printf="%s" "$dest_file") -ge 20000 ]]; then
            echo "[+] Copied $src_file"
            break
        else
            echo "[~] $dest_file was smaller than 20,000 bytes. Waiting 3 seconds..."
            sleep 3
        fi
    done
done

echo "[+] Completed copying files. Zipping..."

cd "${ipbgp_dir}"
zip "${AS}-${POISON_AS}.zip" *.txt
echo "[+] Completed Packaging ${AS}-${POISON_AS}.zip"

rm -f *.txt
echo "[+] Completed, Goodbye!"