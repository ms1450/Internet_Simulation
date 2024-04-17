import pandas as pd

def calculate_statistics(df, as_range):
    """Calculate and return statistics for given AS range."""
    subset = df[df['IMPACTED AS'].between(*as_range)]
    stats = {
        'Visibility Change': subset['VISIBILITY CHANGE'].agg(['mean', 'max', 'min', 'std']),
        'Newly Discovered Connections': subset['NEW DISCOVERED CONNECTION COUNT'].agg(['mean', 'max', 'min', 'std']),
        'New P2P Connections': subset['NEW P2P CONNECTIONS DISCOVERED'].agg(['mean', 'max', 'min', 'std']),
        'New P2C Connections': subset['NEW P2C CONNECTIONS DISCOVERED'].agg(['mean', 'max', 'min', 'std']),
        'New IXP Connections': subset['NEW IXP CONNECTIONS DISCOVERED'].agg(['mean', 'max', 'min', 'std'])
    }
    return pd.DataFrame(stats)


if __name__ == '__main__':
    file_path = './IP_BGP/Results/Topology_Results.csv'
    data = pd.read_csv(file_path)
    filtered_data = data[data['POISONING AS'] != data['IMPACTED AS']]

    # Calculate statistics for different types of ASes
    tier1_stats = calculate_statistics(filtered_data, (1, 4))
    transit_stats = calculate_statistics(filtered_data, (5, 13))
    stub_stats = calculate_statistics(filtered_data, (14, 50))

    # Combine the results in a more readable format
    results = pd.concat({
        'Tier 1 AS': tier1_stats,
        'Transit AS': transit_stats,
        'Stub AS': stub_stats
    })

    # Print the results in a nicely formatted table
    print("Detailed Statistics by AS Type:")
    print(results.to_string())

    # Calculate and print total statistics for all ASes within range
    total_stats = calculate_statistics(filtered_data, (1, 50))
    print("\nTotal Statistics for AS Range 1-50:")
    print(total_stats.to_string())
