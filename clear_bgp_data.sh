#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

DIRECTORY="$1"

source "${DIRECTORY}"/config/subnet_config.sh

# read AS configurations
readarray groups < "${DIRECTORY}"/config/AS_config.txt

for group_info in "${groups[@]}"; do
    read -r group_number group_as group_router_config <<< "${group_info}"

    if [ "${group_as}" != "IXP" ]; then
        readarray routers < "${DIRECTORY}"/config/$group_router_config

        for router_info in "${routers[@]}"; do
            read -r rname <<< "${router_info}"

            container="${group_number}_${rname}router"

            # Clear IP BGP paths
            echo "Clearing BGP session for router: ${container}"
            # Uncomment the following line to execute the BGP clear command
            # docker exec ${container} vtysh -c 'clear ip bgp *'
            echo "sudo ./setup/bgp_clear.sh . ${group_number} ${rname}"

            # Wait for 5 seconds before moving to the next router
            sleep 5
        done
    fi
done