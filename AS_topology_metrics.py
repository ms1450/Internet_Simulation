import csv
import os
import re



if __name__ == '__main__':
    node_files = './Topology/Topology_Nodes_50.csv'
    link_files = './Topology/Topology_Links_50.csv'
    ipbgp_folder = './IP_BGP/Pre-Poisoning/'
    #ipbgp_folder = './IP_BGP/Post-Poisoning/30/30-1/'
    print("[+]\tReading topology...")
    ixp_nodes = get_ixp_nodes(node_files)
    links = topology_metrics(link_files)
    num_non_ixp_links = get_non_ixp_metrics(links, ixp_nodes)
    print(f'[+]\tComplete Topology Metrics\tNon-IXP Connections: {num_non_ixp_links}/{len(links)}')
    get_network_metrics(ipbgp_folder, ixp_nodes)




