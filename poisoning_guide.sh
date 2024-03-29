#!/bin/bash

# Prompt for AS and POISON_AS
read -p "Enter AS: " AS
read -p "Enter POISON_AS: " POISON_AS

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
    read -p "Enter Neighbor_$counter (leave empty to stop): " neighbor
    if [ -z "$neighbor" ]; then
        break
    fi
    output+="neighbor $neighbor route-map $POISON_AS-POISON out\n"
    ((counter++))
done

output+="end\nwrite file"

# Display the output
echo -e "$output"