import os.path
import pickle

from AS_topology_generator import AutonomousSystem, InternetExchangePoint


# Print AS_config.txt
def print_AS_config(list_of_ASes, list_of_IXPs):
    with open('./Configuration/AS_config.txt', 'w', newline='\n') as file:
        for entry in list_of_ASes:
            if entry.as_id == 1:
                string = str(entry.as_id) + "\tAS\tConfig\tl3_routers_krill.txt\tl3_links.txt\tempty.txt\tempty.txt\tempty.txt\n"
            else:
                string = str(entry.as_id) + "\tAS\tConfig\tl3_routers.txt\tl3_links.txt\tempty.txt\tempty.txt\tempty.txt\n"
            file.write(string)
        for entry in list_of_IXPs:
            string = str(entry.ixp_id) + "\tIXP\tConfig\tN/A\tN/A\tN/A\tN/A\tN/A\n"
            file.write(string)


# Helper function for aslevel_links.txt
def get_ixp_connections(AS, IXP):
    connections = []
    for link in IXP.ixp_connections:
        if link != AS:
            connections.append(str(link.as_id))
    return ",".join(connections)


# Print aslevel_links.txt
def print_aslevel_links(list_of_ASes):
    with open('./Configuration/aslevel_links.txt', 'w', newline='\n') as file:
        completed = []
        for entry in list_of_ASes:
            completed.append(entry)
            for customer in entry.customers:
                if customer not in completed:
                    string = str(entry.as_id) + "\tRTRA\tProvider\t" + str(
                        customer.as_id) + "\tRTRA\tCustomer\t100000\t2.5ms\t50ms\t179." + str(entry.as_id) + "." + str(
                        customer.as_id) + ".0/24\n"
                    file.write(string)
            for peer in entry.peers:
                if peer not in completed:
                    string = str(entry.as_id) + "\tRTRA\tPeer\t" + str(
                        peer.as_id) + "\tRTRA\tPeer\t100000\t2.5ms\t50ms\t179." + str(entry.as_id) + "." + str(
                        peer.as_id) + ".0/24\n"
                    file.write(string)
            for ixp in entry.ixps:
                string = str(entry.as_id) + "\tRTRB\tPeer\t" + str(
                    ixp.ixp_id) + "\tNone\tPeer\t100000\t2.5ms\t50ms\t" + get_ixp_connections(entry, ixp) + "\n"
                file.write(string)


# Helper function for aslevel_links_students.txt
def get_smaller_connection(AS1, AS2):
    if AS1.as_id < AS2.as_id:
        return str(AS1.as_id) + "." + str(AS2.as_id) + "."
    else:
        return str(AS2.as_id) + "." + str(AS1.as_id) + "."


# Print as_level_links_students.txt
def print_aslevel_links_students(list_of_ASes, list_of_IXPs):
    with open('./Configuration/aslevel_links_students.txt', 'w', newline='\n') as file:
        for entry in list_of_ASes:
            for customer in entry.customers:
                string = str(entry.as_id) + "\tRTRA\tProvider\t" + str(
                    customer.as_id) + "\tRTRA\tCustomer\t179." + str(entry.as_id) + "." + str(
                    customer.as_id) + "." + str(entry.as_id) + "/24\n"
                file.write(string)
            for provider in entry.providers:
                string = str(entry.as_id) + "\tRTRA\tCustomer\t" + str(
                    provider.as_id) + "\tRTRA\tProvider\t179." + str(provider.as_id) + "." + str(
                    entry.as_id) + "." + str(entry.as_id) + "/24\n"
                file.write(string)
            for peer in entry.peers:
                string = str(entry.as_id) + "\tRTRA\tPeer\t" + str(
                    peer.as_id) + "\tRTRA\tPeer\t179." + get_smaller_connection(entry, peer) + str(
                    entry.as_id) + "/24\n"
                file.write(string)
            for ixp in entry.ixps:
                string = str(entry.as_id) + "\tRTRB\tPeer\t" + str(
                    ixp.ixp_id) + "\tNone\tPeer\t180." + str(ixp.ixp_id) + ".0." + str(
                    entry.as_id) + "/24\n"
                file.write(string)

        for ixp in list_of_IXPs:
            for connection in ixp.ixp_connections:
                string = str(ixp.ixp_id) + "\tNone\tPeer\t" + str(
                    connection.as_id) + "\tRTRB\tPeer\t180." + str(
                    ixp.ixp_id) + ".0." + str(ixp.ixp_id) + "/24\n"
                file.write(string)


# Print l3_routers.txt
def print_l3_routers():
    with open('./Configuration/l3_routers.txt', 'w', newline='\n') as file:
        file.write("RTRA\tDNS\thost:miniinterneteth/d_host\tvtysh\n")
        file.write("RTRB\tN/A\thost:miniinterneteth/d_host\tvtysh\n")


# Print l3_routers_krill.txt
def print_l3_routers_krill():
    with open('./Configuration/l3_routers_krill.txt', 'w', newline='\n') as file:
        file.write("RTRA\tDNS\tkrill:miniinterneteth/d_host\tvtysh\n")
        file.write("RTRB\tN/A\thost:miniinterneteth/d_host\tvtysh\n")


# Print l3_links.txt
def print_l3_links():
    with open('./Configuration/l3_links.txt', 'w', newline='\n') as file:
        file.write("RTRA\tRTRB\t100000\t10ms\t50ms\n")
        file.write("RTRB\tRTRA\t100000\t10ms\t50ms\n")


if __name__ == "__main__":
    as_file_name = '.\Topology\Topology_ASes_50.pkl'
    ixp_file_name = '.\Topology\Topology_IXPs_50.pkl'
    ASes = []
    IXPs = []
    if os.path.exists(as_file_name) and os.path.exists(ixp_file_name):
        print("[+]\tLoading AS and IXP files...")
        with open(as_file_name, 'rb') as as_file:
            ASes = pickle.load(as_file)
            print(f'[+]\t\tLoaded {len(ASes)} ASes')
        with open(ixp_file_name, 'rb') as ixp_file:
            IXPs = pickle.load(ixp_file)
            print(f'[+]\t\tLoaded {len(IXPs)} IXPs')
            print("[+]\tCreating Configuration files...")
            print_AS_config(ASes, IXPs)
            print_aslevel_links(ASes)
            print_aslevel_links_students(ASes, IXPs)
            print_l3_routers()
            print_l3_routers_krill()
            print_l3_links()
            print("[+]\tCompleted")
    else:
        print("[-]\tAS and IXP files not found.")

