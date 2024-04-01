#!/bin/bash

# Prompt for AS and POISON_AS
read -p "[i] Enter AS: " AS
read -p "[i] Enter POISONED AS: " POISON_AS

declare -A neighbors
neighbors[15]="43,11,13"
neighbors[16]="13"
neighbors[17]="49,5"
neighbors[18]="6,10"
neighbors[20]="39,5,10"
neighbors[24]="36,12"
neighbors[28]="12,7"
neighbors[29]="30,12,7"
neighbors[32]="11,10"
neighbors[36]="24,4"
neighbors[40]="46,9"
neighbors[42]="6,1"
neighbors[43]="15,11,5"
neighbors[44]="13,2"
neighbors[46]="40,8,10"
neighbors[49]="17,3"

# Process only the specified AS
if [[ -n ${neighbors[$AS]} ]]; then
    IFS=',' read -r -a neighbor_ips <<< "${neighbors[$AS]}"
    echo "[+] Configuring AS ${AS}.."

    cmd="conf t
router bgp ${AS}
route-map ${POISON_AS}-POISON permit 10
set as-path prepend ${POISON_AS}"

    for NEIGHBOR in "${neighbor_ips[@]}"; do
        NEIGHBOR_IP="179.${NEIGHBOR}.${AS}.${NEIGHBOR}"
        cmd+="
neighbor ${NEIGHBOR_IP} route-map ${POISON_AS}-POISON out"
    done

    cmd+="
end
write file"

echo "CHECK THE FOLLOWING: "
read -p "${cmd}"
    docker exec "${AS}_RTRArouter" vtysh -c "$cmd"
else
    echo "No predefined neighbors for AS ${AS}. Please manually configure the poisoning."
fi


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