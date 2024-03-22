import csv
import os
import pickle
import random


class AutonomousSystem:
    def __init__(self, as_id, as_type):
        # Initialize an Autonomous System with an ID and type
        self.as_id = as_id
        self.as_type = as_type
        # Initialize peer-to-peer connections
        self.p2p_connections = []
        self.p2p_connections_count = 0
        self.peers = []
        # Initialize provider-to-customer connections
        self.p2c_connections = []
        self.p2c_connections_count = 0
        self.providers = []
        self.customers = []
        # Initialize Internet Exchange Point connections
        self.ixps = []

    def assign_random_properties(self, p2p_range, p2c_range):
        # Assign random values for the count of p2p and p2c connections within specified ranges
        self.p2p_connections_count = random.randint(*p2p_range)
        self.p2c_connections_count = random.randint(*p2c_range)

    def __str__(self):
        # String representation of the AS including its ID, type, and connections
        return f"AS{self.as_id} ({self.as_type})\t- Peers: {[as_.as_id for as_ in self.peers]}\t- Providers: {[as_.as_id for as_ in self.providers]}\t- Customers: {[as_.as_id for as_ in self.customers]}\t- IXP: {[ixp.ixp_id for ixp in self.ixps]}"


class InternetExchangePoint:
    def __init__(self, ixp_id):
        # Initialize an IXP with an ID
        self.ixp_id = ixp_id
        self.ixp_connections = []

    def add_connection(self, AS):
        # Add an AS connection to the IXP
        self.ixp_connections.append(AS)

    def __str__(self):
        # String representation of the IXP including its ID and connected ASes
        return f"IXP{self.ixp_id}\t- Connections: {[as_.as_id for as_ in self.ixp_connections]}"


def create_ASes(stub_count, transit_count, tier1_count):
    # Create a specified number of ASes of each type
    list_of_ASes = []
    as_id = 1
    # Add Tier 1 ASes
    for _ in range(tier1_count):
        list_of_ASes.append(AutonomousSystem(as_id, "TIER1"))
        as_id += 1
    # Add Transit ASes
    for _ in range(transit_count):
        list_of_ASes.append(AutonomousSystem(as_id, "TRANSIT"))
        as_id += 1
    # Add Stub ASes
    for _ in range(stub_count):
        list_of_ASes.append(AutonomousSystem(as_id, "STUB"))
        as_id += 1
    return list_of_ASes


def assign_properties(list_of_ASes, p2p_range_stub, p2c_range_stub, p2p_range_transit, p2c_range_transit, p2c_range_tier1):
    # Assign random p2p and p2c properties to each AS based on its type
    for current_system in list_of_ASes:
        if current_system.as_type == 'STUB':
            current_system.assign_random_properties(p2p_range_stub, p2c_range_stub)
        elif current_system.as_type == 'TRANSIT':
            current_system.assign_random_properties(p2p_range_transit, p2c_range_transit)
        else:  # TIER1
            current_system.assign_random_properties((0, 0), p2c_range_tier1)


def get_as_as_list(list_of_ASes):
    # Categorize ASes into stubs, transits, and tier1s
    stub_ASes, transit_ASes, tier1_ASes = [], [], []
    for current_system in list_of_ASes:
        if current_system.as_type == 'STUB':
            stub_ASes.append(current_system)
        elif current_system.as_type == 'TRANSIT':
            transit_ASes.append(current_system)
        else:  # TIER1
            tier1_ASes.append(current_system)
    return stub_ASes, transit_ASes, tier1_ASes


def add_p2p_connection(current_as, peer_as):
    # Establish a bi-directional p2p connection between two ASes
    current_as.p2p_connections.append(peer_as)
    current_as.peers.append(peer_as)
    peer_as.p2p_connections.append(current_as)
    peer_as.peers.append(current_as)


def add_p2c_connection(provider_as, customer_as):
    # Establish a bi-directional p2c connection between provider and customer ASes
    provider_as.p2c_connections.append(customer_as)
    provider_as.customers.append(customer_as)
    customer_as.p2c_connections.append(provider_as)
    customer_as.providers.append(provider_as)


def add_ixp_connection(ixp, AS):
    # Add an AS connection to an IXP and vice versa
    ixp.ixp_connections.append(AS)
    AS.ixps.append(ixp)


def create_p2c_connections(list_of_ASes, stub_to_tier1_probability=0.1):
    # Obtain lists of stub, transit, and tier1 ASes
    available_stubs, available_transits, available_tier1s = get_as_as_list(list_of_ASes)

    # Establish P2C connections for stub ASes
    for stub in available_stubs:
        # Keep adding connections until the stub reaches its desired connection count
        while len(stub.p2c_connections) < stub.p2c_connections_count:
            # Potential providers are initially set to transits not already connected to the stub
            potential_providers = [as_ for as_ in list_of_ASes if as_.as_type == 'TRANSIT' and as_ != stub and
                                   len(as_.p2c_connections) < as_.p2c_connections_count and as_ not in
                                   stub.p2c_connections]

            # With a certain probability, add tier1 ASes as potential providers
            if random.random() < stub_to_tier1_probability:
                potential_providers += [as_ for as_ in list_of_ASes if as_.as_type == 'TIER1' and as_ != stub and
                                        len(as_.p2c_connections) < as_.p2c_connections_count and as_ not in
                                        stub.p2c_connections]

            # Select a random provider from the potential list and establish a P2C connection
            if potential_providers:
                provider = random.choice(potential_providers)
                add_p2c_connection(provider, stub)
            else:
                # If no potential providers are found, stop trying to add more connections
                print(f'[-]\tNo more Potential P2C Providers for Stub: {stub}')
                stub.p2c_connections_count = len(stub.p2c_connections)
                break

    # Establish P2C connections for transit ASes to tier1 ASes
    for transit in available_transits:
        # Ensure each transit AS has at least one tier1 provider
        if not any(as_.as_type == 'TIER1' for as_ in transit.p2c_connections):
            tier1_providers = [as_ for as_ in available_tier1s if as_ != transit and as_ not in transit.p2c_connections]
            if tier1_providers:
                provider = random.choice(tier1_providers)
                add_p2c_connection(provider, transit)
            else:
                print(f'[-]\tNo TIER1 providers available for Transit: {transit}')

        # Add additional P2C connections to tier1 ASes as needed
        while len(transit.p2c_connections) < transit.p2c_connections_count:
            potential_providers = [as_ for as_ in available_tier1s if as_ != transit and
                                   len(as_.p2c_connections) < as_.p2c_connections_count and as_ not in
                                   transit.p2c_connections]
            if potential_providers:
                provider = random.choice(potential_providers)
                add_p2c_connection(provider, transit)
            else:
                print(f'[-]\tNo more Potential P2C Providers for Transit: {transit}')
                transit.p2c_connections_count = len(transit.p2c_connections)
                break

    # Adjust the connection count for tier1 ASes if necessary
    for tier1 in available_tier1s:
        if tier1.p2c_connections_count > len(tier1.p2c_connections):
            tier1.p2c_connections_count = len(tier1.p2c_connections)


def create_p2p_connections(list_of_ASes, stub_to_transit_probability=0.1):
    # Obtain lists of stub, transit, and tier1 ASes
    available_stubs, available_transits, available_tier1s = get_as_as_list(list_of_ASes)

    # Establish P2P connections among tier1 ASes
    connected = []
    for tier1 in available_tier1s:
        connected.append(tier1)
        for pending in available_tier1s:
            if pending not in connected:
                add_p2p_connection(tier1, pending)

    # Establish P2P connections for stub ASes
    for stub in available_stubs:
        # Keep adding connections until the stub reaches its desired connection count
        while len(stub.p2p_connections) < stub.p2p_connections_count:
            # Potential peers are initially set to other stubs not already connected
            potential_peers = [as_ for as_ in available_stubs if as_ != stub and
                               len(as_.p2p_connections) < as_.p2p_connections_count and as_ not in stub.p2p_connections]

            # With a certain probability, add transits as potential peers
            if random.random() < stub_to_transit_probability:
                potential_peers += [as_ for as_ in available_transits if as_ != stub and
                                    len(as_.p2p_connections) < as_.p2p_connections_count and as_ not in
                                    stub.p2p_connections]

            # Select a random peer from the potential list and establish a P2P connection
            if potential_peers:
                peer = random.choice(potential_peers)
                add_p2p_connection(stub, peer)
            else:
                # If no potential peers are found, stop trying to add more connections
                print(f'[-]\tNo more potential P2P Peers for Stub: {stub}')
                stub.p2p_connections_count = len(stub.p2p_connections)
                break

    # Establish P2P connections for transit ASes
    for transit in available_transits:
        # Keep adding connections until the transit reaches its desired connection count
        while len(transit.p2p_connections) < transit.p2p_connections_count:
            # Potential peers are other transits not already connected
            potential_peers = [as_ for as_ in available_transits if as_ != transit and
                               len(as_.p2p_connections) < as_.p2p_connections_count and as_ not in transit.p2p_connections]

            # Select a random peer from the potential list and establish a P2P connection
            if potential_peers:
                peer = random.choice(potential_peers)
                add_p2p_connection(transit, peer)
            else:
                # If no potential peers are found, stop trying to add more connections
                print(f'[-]\tNo more potential P2P Peers for Transit: {transit}')
                transit.p2p_connections_count = len(transit.p2p_connections)
                break


def add_ixp_connections(list_of_ASes, probability_of_same_connection=0.1, probability_of_cross_connection=0.05):
    # Initialize a list to hold all IXPs
    list_of_IXPs = []
    ixp_id = 81
    stubs, transits, tier1s = get_as_as_list(list_of_ASes)

    # Create IXP between Tier 1
    if tier1s:
        ixp_tier1 = InternetExchangePoint(ixp_id)
        list_of_IXPs.append(ixp_tier1)
        for AS in tier1s:
            add_ixp_connection(ixp_tier1, AS)
            # Create IXP between Tier 1 and their customers
            ixp_id += 1
            ixp_between_tier1_customers = InternetExchangePoint(ixp_id)
            list_of_IXPs.append(ixp_between_tier1_customers)
            add_ixp_connection(ixp_between_tier1_customers, AS)
            for customer in AS.customers:
                add_ixp_connection(ixp_between_tier1_customers, customer)

            # Create Random IXP between Tier 1 and Transits/Stubs
            if random.random() < probability_of_same_connection:
                ixp_id += 1
                ixp_tier1_random = InternetExchangePoint(ixp_id)
                new_connections = []
                for potential_AS in transits + stubs:
                    if random.random() < probability_of_cross_connection:
                        add_ixp_connection(ixp_tier1_random, potential_AS)
                        new_connections.append(potential_AS)
                if new_connections:
                    add_ixp_connection(ixp_tier1_random, AS)
                    list_of_IXPs.append(ixp_tier1_random)
                else:
                    ixp_id -= 1

    # Create IXP between Transits
    if transits:
        # Create IXP between Transit and their customers
        for AS in transits:
            ixp_id += 1
            ixp_between_transit_customers = InternetExchangePoint(ixp_id)
            list_of_IXPs.append(ixp_between_transit_customers)
            add_ixp_connection(ixp_between_transit_customers, AS)
            for customer in AS.customers:
                add_ixp_connection(ixp_between_transit_customers, customer)

            # Random IXP between Transits
            if random.random() < probability_of_same_connection:
                ixp_id += 1
                ixp_transit_random = InternetExchangePoint(ixp_id)
                new_connections = []
                for potential_AS in transits:
                    if potential_AS != AS:
                        add_ixp_connection(ixp_transit_random, potential_AS)
                        new_connections.append(potential_AS)
                if new_connections:
                    add_ixp_connection(ixp_transit_random, AS)
                    list_of_IXPs.append(ixp_transit_random)
                else:
                    ixp_id -= 1

                # Random IXP between Transit and Stubs
                new_connections = []
                ixp_id += 1
                ixp_transit_stub_random = InternetExchangePoint(ixp_id)
                for potential_AS in stubs:
                    if random.random() < probability_of_cross_connection:
                        add_ixp_connection(ixp_transit_stub_random, potential_AS)
                        new_connections.append(potential_AS)
                if new_connections:
                    add_ixp_connection(ixp_transit_stub_random, AS)
                    list_of_IXPs.append(ixp_transit_stub_random)
                else:
                    ixp_id -= 1

    # Create IXP between Stubs
    if stubs:
        for AS in stubs:
            # Random IXP between Stubs
            if random.random() < probability_of_same_connection:
                new_connections = []
                ixp_id += 1
                ixp_stub_random = InternetExchangePoint(ixp_id)
                for potential_AS in stubs:
                    if potential_AS != AS and random.random() < probability_of_cross_connection:
                        add_ixp_connection(ixp_stub_random, potential_AS)
                        new_connections.append(potential_AS)
                if new_connections:
                    add_ixp_connection(ixp_stub_random, AS)
                    list_of_IXPs.append(ixp_stub_random)
                else:
                    ixp_id -= 1
    return list_of_IXPs


# Extract Connections to later be stored as CSV
def extract_connections(ases):
    connections = []
    for as_ in ases:
        # P2P Connections
        for peer in as_.peers:
            sorted_ids = sorted([as_.as_id, peer.as_id])
            connection = (f"AS{sorted_ids[0]} - AS{sorted_ids[1]}", "P2P", f"AS{sorted_ids[0]}", f"AS{sorted_ids[1]}")
            if connection not in connections:
                connections.append(connection)
        # P2C Connections
        for customer in as_.customers:
            connection = (f"AS{as_.as_id} - AS{customer.as_id}", "P2C", f"AS{as_.as_id}", f"AS{customer.as_id}")
            if connection not in connections:
                connections.append(connection)
        # IXP Connections
        for ixp in as_.ixps:
            connection = (f"AS{as_.as_id} - IXP{ixp.ixp_id}", "IXP", f"AS{as_.as_id}", f"IXP{ixp.ixp_id}")
            if connection not in connections:
                connections.append(connection)
    return connections


# Write Connections to CSV File
def write_connections_to_csv(connections, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Type', 'Current', 'Connection'])
        for conn in connections:
            writer.writerow(conn)


# Create a CSV of Nodes
def write_nodes_to_csv(ases, ixps, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Node', 'Type'])

        # Write ASes with their types
        for as_ in ases:
            as_type = as_.as_type
            if as_type == 'TIER1':
                node_type = 'Tier 1 AS'
            elif as_type == 'TRANSIT':
                node_type = 'Transit AS'
            else:  # 'STUB'
                node_type = 'Stub AS'
            writer.writerow([f"AS{as_.as_id}", node_type])
        # Write IXPs
        for ixp in ixps:
            writer.writerow([f"IXP{ixp.ixp_id}", "IXP"])


if __name__ == "__main__":
    # Initialize random seed for reproducibility
    random.seed(42)

    # Example usage to demonstrate the creation and connection of ASes and IXPs
    total_as = 50
    num_stub = 37
    num_transit = 9
    num_tier1 = 4
    ASes = create_ASes(num_stub, num_transit, num_tier1)
    assign_properties(ASes, (0, 1), (1, 2), (2, 3), (5, 10), (6, 10))
    create_p2c_connections(ASes)
    create_p2p_connections(ASes)
    IXPs = add_ixp_connections(ASes)

    configuration_file_name = './Topology/Topology_' + str(total_as) + '.txt'
    as_file_name = './Topology/Topology_ASes_' + str(total_as) + '.pkl'
    ixp_file_name = './Topology/Topology_IXPs_' + str(total_as) + '.pkl'
    csv_connections_file_name = './Topology/Topology_Links_' + str(total_as) + '.csv'
    csv_nodes_file_name = './Topology/Topology_Nodes_' + str(total_as) + '.csv'

    print("[+]\tConfiguring Topology: ", configuration_file_name)
    with open(configuration_file_name, 'w') as file:
        # Print details of ASes and IXPs
        for as_system in ASes:
            file.write(f"{as_system}\n")
        for ixp in IXPs:
            file.write(f"{ixp}\n")

    if not os.path.exists(as_file_name) and not os.path.exists(ixp_file_name):
        print("[+]\tCreating Dataset of ASes...")
        with open(as_file_name, 'wb') as as_file:
            pickle.dump(ASes, as_file)
            print(f"[+]\t\tSaved {as_file_name}")
        print("[+]\tCreating Dataset of IXPs...")
        with open(ixp_file_name, 'wb') as ixp_file:
            pickle.dump(IXPs, ixp_file)
            print(f"[+]\t\tSaved {ixp_file_name}")
    if not os.path.exists(csv_nodes_file_name):
        print("[+]\tCreating Nodes...")
        write_nodes_to_csv(ASes, IXPs, csv_nodes_file_name)
    if not os.path.exists(csv_connections_file_name):
        print("[+]\tCreating Links between Nodes...")
        connections = extract_connections(ASes)
        write_connections_to_csv(connections, csv_connections_file_name)
    print("[+]\tCompleted")
