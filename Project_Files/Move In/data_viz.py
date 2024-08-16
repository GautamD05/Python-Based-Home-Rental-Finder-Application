import matplotlib.pyplot as plt
import pandas as pd
import re
import seaborn as sns
from collections import Counter
from matplotlib.gridspec import GridSpec

# Sample data for the serviceOptions chart
def extract(s):
    res = []
    s = s.split(",")
    for curr in s:
        if "[" in curr:
            curr = curr[2:-1]
        elif "]" in curr:
            curr = curr[1:-2]
        else:
            curr = curr[1:-1]
        curr = curr.replace("'", "")
        res.append(curr)
    return res

def create_image(area):
    df = pd.read_csv("Pittsburgh Grocery Stores.csv")
    df = df[df['area'] == area]
    df['serviceOptions'].replace('', pd.NA, inplace=True)
    # Drop rows where 'serviceOptions' is NaN
    df.dropna(subset=['serviceOptions'], inplace=True)
    df['serviceOptions'] = df['serviceOptions'].apply(lambda x: extract(x))
    serviceOptions = df['serviceOptions'].tolist()

    # Flatten the list of service options and count the occurrences
    flat_service_options = [item for sublist in serviceOptions for item in sublist]
    service_option_counts = Counter(flat_service_options)

    # Extract service options and their counts
    service_options = list(service_option_counts.keys())
    counts = list(service_option_counts.values())

    # Sample data for the restaurant rating chart
    df = pd.read_csv("Pittsburgh Restaurants.csv")
    rating = df['rating'][df['area'] == area.lower()].mean()  # Change this to the actual rating
    out_of = 5  # Maximum rating
    empty_rating = out_of - rating
    labels = [f'Out of {out_of - rating}', f'Rated {rating}']
    sizes = [empty_rating, rating]
    colors = ['#d3d3d3', '#2ca02c']

    # Sample data for the crime matrix chart
    crime_data = pd.read_csv("CrimeDataPitt.csv")
    crime_data['NEIGHBORHOOD'][crime_data['NEIGHBORHOOD'].isin(['SQUIRREL HILL SOUTH', 'SQUIRREL HILL NORTH'])] = 'SQUIRREL HILL'
    crime_data['NEIGHBORHOOD'][crime_data['NEIGHBORHOOD'].isin(['UPPER LAWRENCEVILLE', 'LOWER LAWRENCEVILLE', 'CENTRAL LAWRENCEVILLE'])] = 'SQUIRREL HILL'
    crime_data = crime_data[crime_data['NEIGHBORHOOD'].isin(['SQUIRREL HILL', 'BROOKLINE', 'LAWRENCEVILLE', 'POINT BREEZE', 'NORTH SHORE', 'SHADYSIDE', 'HIGHLAND PARK', 'REGENT SQUARE'])]

    # Create a 1x1 grid layout
    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(2, 2, width_ratios=[2, 2], height_ratios=[1, 1])

    # Service Options Chart (Bar Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.barh(service_options, counts, color='skyblue')
    ax1.set_title('Counts of Service Options')
    ax1.grid(axis='x', linestyle='--', alpha=0.6)

    # Restaurant Rating Chart (Pie Chart)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    center_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax2.add_artist(center_circle)
    ax2.set_title('Restaurant Rating')
    ax2.axis('equal')  # Equal aspect ratio ensures the pie chart is a circle

    # Matrix Chart
    ax3 = fig.add_subplot(gs[1, :])
    matrix_df = crime_data.pivot_table(index='NEIGHBORHOOD', columns='CALL_TYPE_FINAL', aggfunc='size', fill_value=0)
    sns.heatmap(matrix_df, cmap='coolwarm', annot=True, fmt='d', linewidths=0.5)
    ax3.set_title('Incident Matrix Chart')
    #ax3.set_xlabel('Call Type')
    ax3.set_ylabel('Neighborhood')
    ax3.tick_params(axis='x', rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Save the combined figure to a local image
    plt.savefig('combined_charts.png')
