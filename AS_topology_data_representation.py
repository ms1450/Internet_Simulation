import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

if __name__ == '__main__':
    file_path = './IP_BGP/Results/Topology_Results.csv'
    data = pd.read_csv(file_path)

    # Define the neighbor relationships based on the provided list
    neighbors_dict = {
        14: [7, 12],
        15: [11, 13, 43],
        16: [13],
        17: [5, 49],
        18: [6, 10],
        19: [10, 12],
        20: [5, 10, 39],
        21: [6, 7],
        24: [8, 9],
        27: [6],
        30: [12, 29],
        33: [9],
        37: [9, 12],
        41: [9, 13]
    }

    filtered_data = data[data['POISONING AS'] != data['IMPACTED AS']]

    # Define a function to check if an IMPACTED AS is a neighbor of the POISONING AS
    # def is_neighbor(poisoning_as, impacted_as):
    #     neighbors = neighbors_dict.get(poisoning_as, [])
    #     return impacted_as in neighbors

    #
    # # Apply the function to the dataset to determine if each entry is a neighbor or not
    # filtered_data['IS_NEIGHBOR'] = filtered_data.apply(
    #     lambda row: is_neighbor(row['POISONING AS'], row['IMPACTED AS']), axis=1
    # )

    # # Split the data into two separate DataFrames
    # neighbor_results_df = filtered_data[filtered_data['IS_NEIGHBOR']]
    # non_neighbor_results_df = filtered_data[~filtered_data['IS_NEIGHBOR']]

    def calculate_statistics(df, as_range):
        subset = df[df['IMPACTED AS'].between(*as_range)]
        visibility_stats = subset['VISIBILITY CHANGE'].agg(['mean', 'max', 'min', 'std'])
        connection_stats = subset['NEW DISCOVERED CONNECTION COUNT'].agg(['mean', 'max', 'min', 'std'])
        p2p_stats = subset['NEW P2P CONNECTIONS DISCOVERED'].agg(['mean'])
        p2c_stats = subset['NEW P2C CONNECTIONS DISCOVERED'].agg(['mean'])
        ixp_stats = subset['NEW IXP CONNECTIONS DISCOVERED'].agg(['mean'])
        return pd.concat([visibility_stats, connection_stats, p2p_stats, p2c_stats, ixp_stats])
    #
    #
    # # Calculate statistics for Tier 1, Transit, and Stub ASes
    # tier1_stats = calculate_statistics(neighbor_results_df, (1, 4))
    # transit_stats = calculate_statistics(neighbor_results_df, (5, 13))
    # stub_stats = calculate_statistics(neighbor_results_df, (14, 50))
    # #
    # # # Combine the results
    # results = pd.DataFrame({'Tier 1 AS': tier1_stats, 'Transit AS': transit_stats, 'Stub AS': stub_stats})
    #print(results)


    print("------------")
    # # Calculate statistics for Tier 1, Transit, and Stub ASes
    tier1_stats = calculate_statistics(filtered_data, (1, 4))
    transit_stats = calculate_statistics(filtered_data, (5, 13))
    stub_stats = calculate_statistics(filtered_data, (14, 50))
    #
    # # Combine the results
    results = pd.DataFrame({'Tier 1 AS': tier1_stats, 'Transit AS': transit_stats, 'Stub AS': stub_stats})
    print(results)

    # print("------------")
    # # # Calculate statistics for Tier 1, Transit, and Stub ASes
    # tier1_stats = calculate_statistics(filtered_data_stub, (1, 4))
    # transit_stats = calculate_statistics(filtered_data_stub, (5, 13))
    # stub_stats = calculate_statistics(filtered_data_stub, (14, 50))
    # #
    # # # Combine the results
    # results = pd.DataFrame({'Tier 1 AS': tier1_stats, 'Transit AS': transit_stats, 'Stub AS': stub_stats})
    # print(results)
    total_stats = calculate_statistics(filtered_data, (1,50))
    print(total_stats)