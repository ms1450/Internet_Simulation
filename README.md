# BGP Poisoning for AS-Level Topology Mapping

> By Mehul Sen

This project investigates the effectiveness of BGP poisoning techniques for mapping AS-level Internet topologies. It features a sophisticated simulation environment designed to mimic real-world Internet structures, enabling the study of hidden network pathways. The project employs a unique topology generation algorithm and focuses on a network configuration of 50 Autonomous Systems (ASes), analyzing how BGP poisoning impacts network paths when applied to Tier-1 and Transit ASes.

## Prerequisites

- Python 3.0 or higher
- Access to the Mini-Internet project on Github: [Mini-Internet](https://github.com/nsg-ethz/mini_internet_project)

## Installation

1. **Clone the repository and prepare the environment:** Ensure the Mini Internet project and its prerequisites are set up before beginning.

```
./Root/
|--- /Internet_Simulation/ (this repository)
`--- /platform/ (from Mini-Internet repository)
```

2. **Modify Mini-Internet project files:** Navigate to the platform directory and make the following changes:
   - Disable Measurement, SSH, MPLS, RPKI, and Throughput setups by commenting out the specified lines in `dns_setup.sh` and `startup.sh`.

```
./platform/setup/dns_setup.sh
- Comment lines 112-116 (Remove Measurement Elements)
./platform/startup.sh
- Comment lines 145-148 (Remove SSH setup)
- Comment lines 226-238 (Remove MPLS and RPKI setup)
- Comment lines 250-252 (RPKI Webserver setup)
- Comment lines 265-267 (Throughput setup)
- Comment lines 285-287 (Hijack setup)
```

3. **Install dependencies:** Inside the `/Internet_Simulation/` directory, run:

```bash
./Internet_Simulation/
sudo pip -r requirements.txt
```

4. **Configure simulation files:** Transfer configuration files from `/Internet_Simulation/Configuration/` to `/platform/config/`.

```
./Internet_Simulation/Configuration/ > /platform/config/
|---AS_config.txt
|---aslevel_links_students.txt
|---aslevel_links.txt
|---l3_links.txt
|---l3_routers_krill.txt
`---l3_routers.txt
```

5. **Initialize the simulation:** Execute `startup.sh` from the platform directory.
6. **Prepare the BGP script:** Make the BGP script executable:

```bash
./Internet_Simulation/
sudo chmod +x ipbgp_script.sh
```

## Usage

### Simulation Setup

Through the installation, you should be able to run the default 50 AS simulation. However if you would like to further customize the configuration or perform other operations, you can use the python scripts provided in /Internet_Simulation/ to do so. A brief description and usage of each script is provided below.

1. `AS_topology_generator.py`

This script is designed to simulate and manage a complex network topology involving Autonomous Systems (ASes), Internet Exchange Points (IXPs), and various connection types among them. It provides a framework for generating, serializing, and documenting network structures, making it a useful tool for educational purposes, network research, and simulation.

The following are default parameters that can be modified between lines 378 - 390:

```python
random.seed(42) # Random Seed for reproducibility

total_as = 50  # Total Number of ASes
num_stub = 37  # Number of Stub ASes
num_transit = 9  # Number of Transit ASes
num_tier1 = 4  # Number of Tier-1 ASes

p2p_range_stub = (0, 1)  # Range of P2P connections on Stub AS
p2c_range_stub = (1, 2)  # Range of P2C connections on Stub AS
p2p_range_transit = (2, 3)  # Range of P2P connections on Transit AS
p2c_range_transit = (5, 10)  # Range of P2C connections on Transit AS
p2c_range_tier1 = (6, 10)  # Range of P2C connections on Tier-1 AS
```

On running, it will generate a topology based on the provided parameters and save it in `/Internet_Simulation/Topology/`

2. `AS_topology_config_creator.py`

This script generates various configuration files necessary for setting up network simulations or educational environments that mimic real-world Internet routing scenarios.

Ensure that the following files created by `AS_topology_generator.py` exist:

```
./Internet_Simulation/Topology/
|---Topology_ASes_50.pkl
`---Topology_IXPs_50.pkl
```

On running, it will generate the new configuration files in `/Internet_Simulation/Configuration/` that can be placed in `/platform/config/` to run the new topology.

3. `AS_topology_visualize.py`

This script creates visualizations of network graphs. It depict relationships between Autonomous Systems (ASes) and Internet Exchange Points (IXPs) based on data provided in CSV files.

Ensure that the following files created by `AS_topology_generator.py` exist, if not modify lines 74 - 75 to get the topology node and link information:

```
./Internet_Simulation/Topology/
|---Topology_Nodes_50.csv
`---Topology_Links_50.csv
```

On running, it will generates two PNG images within the `/Internet_Simulation/Topology/`:

- `Topology_Complete_Landscape.png`: Depicts the entire network graph with ASes, IXPs, and all connections.
- `Topology_ASes_Landscape.png`: Depicts the network graph showcasing only ASes and their connections (IXPs excluded).

4. `ipbgp_script.sh`

NOTE: Ensure you gather the `looking_glass_json.txt` from the routers before poisoning once to establish a baseline. The pre-poisoning data should be stored in `./Internet_Simulation/IP_BGP/Pre-Poisoning/`. The baseline for the default configuration is already located at this location.

This script automates the process of performing AS poisoning, cleaning BGP configurations, and extracting IP BGP paths in a simulated network environment.

This should be run after the Internet simulation is configured and running on the host machine, and it requires sudo permissions. Modify the neighbors dictionary between lines 10-19 and add any additional neighbors based on the new topology design. Modify line 63 to the total number of ASes.

It will request a target AS and the AS to be poisoned on runtime, and will generate and conduct BGP poisoning based on the neighbors dictionary. It will clear all existing IP BGP sessions for each router in the simulated network (AS1 to AS50 by default). It extracts routing information from each router's `looking_glass_json.txt` file located within the simulation directory structure. Finally it zips and extracts all data files into a single archive at the following location:

```
./Root/IP_BGP_Path/
`---{AS}-{POISON_AS}.zip
```

### Data Parsing

The zip files from the simulation can be extracted and placed within /Internet_Simulation/IP_BGP/ folder through following structure:

```
./Internet_Simulation/IP_BGP/
|---/Results/ (contains the results of AS_topology_tracker.py)
|---/Pre-Poisoning/ (contains the baseline data without poisoning the topology)
|---/Post-Poisoning/ (contains the poisoned data)
	`---/{AS} (contains the ASes that were poisoned)
		`---/{AS}-{POISON_AS} (contains the data from AS poisoning POISONED_AS)
```

### Data Analysis

5. `AS_topology_tracker.py`

This script analyzes the impact of BGP poisoning on network visibility in a simulated environment. It parses ground truth, validates BGP data, performs pre-poisoning analysis, poisoning impact analysis and stores the result in a CSV file.

Ensure that the following files created by `AS_topology_generator.py` exist, if not modify lines 201 - 205 to get the topology node and link information:

```
./Internet_Simulation/Topology/
|---Topology_50.txt
|---Topology_Nodes_50.csv
`---Topology_Links_50.csv

./Internet_Simuation/IP_BGP/
|---/Pre-Poisoning/
`---/Post-Poisoning/
```

Uncomment lines 210 - 223, or add additional lines based on the poisoning performed and the subdirectories available in `./Internet_Simulation/IP_BGP/Post-Poisoning/`. It will parse the data and create 

the `./Internet_Simulation/IP_BGP/Results/Topology_Results.csv` file.

6. `AS_topology_data_representation.py`

This script is designed to analyze the impact of changes in network topology on Autonomous Systems (ASes) based on data from BGP poisoning experiments.

Ensure that the `./Internet_Simulation/IP_BGP/Results/Topology_Results.csv` file exists. Modify lines 22 - 24, and 38 to customize the AS distribution. This does not need to be changed for the default configuration.

This script will output a table that lists calculated statistics for Tier 1 ASes, Transit ASes, and Stub ASes separately. It will also provides aggregated statistics for all ASes in the specified range.

## Contributing

Contributions are encouraged. Please fork the repository, make your changes, and submit a pull request for review.

## License and Support

This project is open-sourced. While I will not maintain the repository or monitor changes to the Mini-Internet project continuously, I am available to answer questions or offer assistance as needed.

