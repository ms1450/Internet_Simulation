#!/bin/bash

# Prompt for AS and POISON_AS
echo "AS Poisoning, Cleaning and Extracting Script"
read -p "[i] Enter AS: " AS
read -p "[i] Enter POISONED AS: " POISON_AS

declare -A neighbors
neighbors[14]="7,12"
neighbors[15]="11,13,43"
neighbors[16]="13"
neighbors[17]="5,49"
neighbors[18]="6,10"
neighbors[19]="10,12"
neighbors[20]="5,10,39"
neighbors[22]="8,9"
neighbors[24]="12,36"
neighbors[33]="9"

# Process only the specified AS
if [[ -n ${neighbors[$AS]} ]]; then
    IFS=',' read -r -a neighbor_ips <<< "${neighbors[$AS]}"
    echo "[+] Configuring AS ${AS}.."

    cmd="conf t
router bgp ${AS}
route-map ${POISON_AS}-POISON permit 10
set as-path prepend ${POISON_AS} ${AS}
end
conf t
router bgp ${AS}"

    for NEIGHBOR in "${neighbor_ips[@]}"; do
						 if (( NEIGHBOR > AS )); then
									NEIGHBOR_IP="179.${AS}.${NEIGHBOR}.${NEIGHBOR}"
						 else
									NEIGHBOR_IP="179.${NEIGHBOR}.${AS}.${NEIGHBOR}"
        fi
        cmd+="
neighbor ${NEIGHBOR_IP} route-map ${POISON_AS}-POISON out"
    done

    cmd+="
end
write file
"
echo "[+] Please verify the following commands:"
echo "${cmd}"
read -p "[+] Press enter to start BGP Poisoning..."
    docker exec "${AS}_RTRArouter" vtysh -c "$cmd"
else
    echo "[-] No predefined neighbors for AS ${AS}. Please manually configure the poisoning."
fi
echo "[+] BGP Poisoning completed."

# Wait for user input to proceed
read -p "[+] Press enter to continue with the Configuration Cleaner..."
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

# Extract IP BGP Paths
echo "[+] Extracting Configurations..."
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