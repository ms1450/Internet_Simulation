import csv
import os
import re
import json


# Get the Topology direct links, and IXP links
def parse_ground_truth(link_file, ixp_file):
    p2p_links = []
    p2c_links = []
    ixp_links = []
    print("[+]\tParsing Links from Ground Truth - Topology Links")
    connections = []

    with open(link_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            current = int(''.join([c for c in row[2] if c.isdigit()]))
            connection = int(''.join([c for c in row[3] if c.isdigit()]))
            pair = tuple(sorted((current, connection)))

            # Only consider AS - AS connections
            if pair not in connections:
                if row[1] != 'IXP':
                    if row[1] == 'P2P':
                        p2p_links.append(pair)
                    elif row[1] == 'P2C':
                        p2c_links.append(pair)
                    connections.append(pair)

    print("[+]\tParsing Links from Ground Truth - IXP")
    with open(ixp_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('IXP'):
                parts = line.split('Connections: ')
                # Assuming the connections part is a list-like string
                ixp_connections = eval(parts[1])  # Better to replace eval with a safer parsing method
                tuples = [(a, b) for i, a in enumerate(ixp_connections) for b in ixp_connections[i + 1:]]
                sorted_tuples = [tuple(sorted(t)) for t in tuples]
                for pair in sorted_tuples:
                    if pair not in connections:
                        ixp_links.append(pair)
                        connections.append(pair)
    return connections, p2p_links, p2c_links, ixp_links


# Check ground truth with the discovered connections
def validate_connections(discovered_connections):
    valid_connections = 0
    invalid_connections = []
    for connection in discovered_connections:
        if connection in ground_truth[0]:
            valid_connections += 1
        else:
            invalid_connections.append(connection)
    if invalid_connections:
        return invalid_connections
    else:
        return invalid_connections


# Reads the Extracted JSON data and returns an array with Network/Subnet, Next_Hop, Local Preference, and Path
def read_bgp_data(json_file):
    # Load the file content as JSON
    with open(json_file, 'r') as file:
        data = json.load(file)
    # Initialize a list to hold the extracted data
    extracted_data = []
    # Iterate over each route in the 'routes' dictionary
    for network, routes in data.get('routes', {}).items():
        for route in routes:
            # For each route, extract the desired fields
            network = route.get('network')
            locPrf = route.get('locPrf')
            path = route.get('path')
            # Next_Hop needs to be extracted from the 'nexthops' list
            next_hops = [nexthop.get('ip') for nexthop in route.get('nexthops', [])]
            # Add the extracted details to our list
            for next_hop in next_hops:
                extracted_data.append([network, next_hop, locPrf, path])
    return extracted_data


# Establishes links between ASes based on BGP data
def establish_links(AS, bgp_data):
    connections = []
    for network, next_hop, local_pref, path in bgp_data:
        path_values = path.split(' ')
        # Empty Path
        if len(path_values) == 0:
            continue

        # Single AS Path
        if len(path_values) == 1 and path_values[0] != '':
            pair = tuple(sorted((AS, int(path_values[0]))))
            if pair not in connections and AS != int(path_values[0]):
                connections.append(pair)

        # Several AS Path
        elif len(path_values) > 1 and path_values[0] != '':
            first_pair = tuple(sorted((AS, int(path_values[0]))))
            if first_pair not in connections and AS != int(path_values[0]):
                connections.append(first_pair)
            for i in range(len(path_values) - 1):
                if path_values[i+1] != '':
                    next_pair = tuple(sorted((int(path_values[i]), int(path_values[i + 1]))))
                    if next_pair not in connections and path_values[i] != path_values[i + 1]:
                        connections.append(next_pair)
    return connections


# Checks the validity and visibility of each AS connections
def check_validity(folder_path, ignore_link=None):
    connection_validity = dict()
    if ignore_link is None:
        ignore_link = []
    files = os.listdir(folder_path)
    sorted_files = sorted(files,
                          key=lambda x: int(re.search(r'(\d+)', x).group()) if re.search(r'(\d+)', x) else float('inf'))
    for filename in sorted_files:
        as_name = filename.split('.')[0]
        discovered_connections = establish_links(int(as_name), read_bgp_data(folder_path + filename))
        invalid_connections = validate_connections(discovered_connections)
        invalid_connections = [connection for connection in invalid_connections if connection not in ignore_link]
        if invalid_connections:
            print(f'[+]\t\t{as_name} - {str(invalid_connections)}')
        connection_validity[as_name] = invalid_connections
    return connection_validity


def store_prepoisoned_data(folder_path):
    prepoisoned_dictionary = dict()
    for filename in os.listdir(folder_path):
        as_name = filename.split('.')[0]
        discovered_connections = establish_links(int(as_name), read_bgp_data(folder_path + filename))
        visibility = round(len(discovered_connections) / len(ground_truth[0]) * 100, 2)
        prepoisoned_dictionary[as_name] = discovered_connections, visibility
    return prepoisoned_dictionary


def check_poisoning_data(folder_path, poisoned_link, prepoisoned_dictionary, poisoned_invalid_links_dict):
    files = os.listdir(folder_path)
    sorted_files = sorted(files,
                          key=lambda x: int(re.search(r'(\d+)', x).group()) if re.search(r'(\d+)', x) else float('inf'))
    for filename in sorted_files:
        as_name = filename.split('.')[0]
        invalid_links = poisoned_invalid_links_dict[as_name] + poisoned_link
        # Get all the connections
        discovered_connections = establish_links(int(as_name), read_bgp_data(folder_path + filename))
        # Get all the valid connections
        discovered_valid_connections = [connection for connection in discovered_connections if connection not in invalid_links]
        # Get all the prepoisoned connections
        prepoisoned_connections = prepoisoned_dictionary[as_name][0]
        # Get all the new connections
        new_connections = [connection for connection in discovered_valid_connections if connection not in prepoisoned_connections]
        visibility = round(len(discovered_valid_connections) / len(ground_truth[0]) * 100, 2)
        prepoisoned_visibility = prepoisoned_dictionary[as_name][1]
        count_from_p2p = sum(link in ground_truth[1] for link in new_connections)
        count_from_p2c = sum(link in ground_truth[2] for link in new_connections)
        count_from_ixp = sum(link in ground_truth[3] for link in new_connections)
        print(f'[+]\t\tAS {as_name} ({round(visibility - prepoisoned_visibility, 2)}%) - {len(new_connections)} new (P2P({count_from_p2p}), P2C({count_from_p2c}), IXP({count_from_ixp}))')
        #print(f'[+]\t\tAS {as_name} ({new_connections}')


if __name__ == '__main__':
    node_files = './Topology/Topology_Nodes_50.csv'
    link_files = './Topology/Topology_Links_50.csv'
    topology_file = './Topology/Topology_50.txt'
    pre_poisoning_folder = './IP_BGP/Pre-Poisoning/'

    ground_truth = parse_ground_truth(link_files, topology_file)
    #check_validity(pre_poisoning_folder)
    prepoisoned_dict = store_prepoisoned_data(pre_poisoning_folder)

    post_poisoning_folder = './IP_BGP/Post-Poisoning/21/21-11/'
    print('[+]\tInvalid Paths Created:')
    poisoned_invalid_links = check_validity(post_poisoning_folder, [(11, 21)])
    print('[+]\tComparison of BGP Data with Pre-Poisoned Data:')
    check_poisoning_data(post_poisoning_folder, [(11, 21)], prepoisoned_dict, poisoned_invalid_links)