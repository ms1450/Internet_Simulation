import csv
import os
import re


# Get List of IXPs
def get_ixp_nodes(topology_file):
    connections = []
    # Read the edge data
    with open(topology_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            if row[1] == "IXP":
                numbers = re.findall(r'\d+', row[0])
                connections.append(int(numbers[0]) if numbers else None)
    return connections


# Extract Network Data (Subnet, Next_Hop, and Path) from the filepath
def extract_network_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    raw_data = []
    for line in lines:
        if line[0] == '*':
            values = line[3:].split(' ')
            cleaned = [value.strip() for value in values if value.strip()]
            raw_data.append(cleaned)

    current_network = ""  # To keep track of network
    data = []
    AS_number = ''
    for data_value in raw_data:
        path = []
        if '/' in data_value[0]:
            current_network = data_value[0]
            subnet = data_value[0]
        else:
            subnet = current_network
        if '/' not in data_value[0]:
            next_hop = data_value[0]
        else:
            next_hop = data_value[1]
        if next_hop != '0.0.0.0':
            reversed_value = data_value[::-1]
            start_index = len(data_value) - reversed_value.index('0', reversed_value.index('i') + 1) - 1
            path = data_value[start_index + 1: len(data_value) - 1]
        else:
            AS_number = current_network.split('.', 1)[0]
        data.append([subnet, next_hop, path])
    return AS_number, data


# Parse Links File Metrics
def topology_metrics(links_file):
    connections = []
    # Read the edge data
    with open(links_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            pair = tuple(sorted(((row[2]), (row[3]))))
            numeric_pair = tuple(sorted(
                (int(''.join(i for i in row[2] if i.isdigit())), int(''.join(i for i in row[3] if i.isdigit())))))
            connections.append(numeric_pair)
        return connections


# Form connections from network data
def form_network_connections(AS, network_data):
    connections = []
    for values in network_data:
        if len(values[2]) == 1:
            pair = tuple(sorted((int(AS), int(values[2][0]))))
            if pair not in connections and AS != values[2][0]:
                connections.append(pair)
        elif len(values[2]) > 1:
            first_pair = tuple(sorted((int(AS), int(values[2][0]))))
            if first_pair not in connections and AS != values[2][0]:
                connections.append(first_pair)
            for i in range(len(values[2]) - 1):
                next_pair = tuple(sorted((int(values[2][i]), int(values[2][i + 1]))))
                if next_pair not in connections and values[2][i] != values[2][i + 1]:
                    connections.append(next_pair)
    return connections


# Print Topology Metrics
def get_non_ixp_metrics(connections, IXPs):
    count = 0
    for connection in connections:  # connection is a tuple like (1, 2)
        # Check if neither end of the connection is an IXP
        if not any(node in IXPs for node in connection):
            count += 1
    return count


def get_network_metrics(folder_path, ixp_nodes, num_links):
    files = os.listdir(folder_path)
    sorted_files = sorted(files, key=lambda x: int(re.search(r'(\d+)', x).group()) if re.search(r'(\d+)', x) else float('inf'))
    for filename in sorted_files:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            AS, network_data = extract_network_data(file_path)
            ipbgp_connections = form_network_connections(AS, network_data)
            num_non_ixp_connections = get_non_ixp_metrics(ipbgp_connections, ixp_nodes)
            print(f'[+]\t\t{filename}\t\tAS: {AS}\tNon-IXP Connections: {num_non_ixp_connections}/{len(ipbgp_connections)}(~{int((num_non_ixp_connections/num_non_ixp_links)*100)}%)\tEntries: {len(network_data)}')


if __name__ == '__main__':
    node_files = './Topology/Topology_Nodes_50.csv'
    link_files = './Topology/Topology_Links_50.csv'
    ipbgp_folder = './IP_BGP/Pre-Poisoning/'
    #ipbgp_folder = './IP_BGP/Post-Poisoning/50-2/'
    print("[+]\tReading topology...")
    ixp_nodes = get_ixp_nodes(node_files)
    links = topology_metrics(link_files)
    num_non_ixp_links = get_non_ixp_metrics(links, ixp_nodes)
    print(f'[+]\tComplete Topology Metrics\tNon-IXP Connections: {num_non_ixp_links}/{len(links)}')
    get_network_metrics(ipbgp_folder, ixp_nodes, num_non_ixp_links)




