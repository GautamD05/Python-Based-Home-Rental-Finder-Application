import pandas as pd
import numpy as np
import zillow_data as zlw
import CrimeSearch as cs
import re
import warnings
warnings.filterwarnings("ignore")

def find_street(s):
	# Regular expression pattern to match street/avenue names
	pattern = r'\d+\s+(?:\w+\s+)*(\w+\s+\w+(?:\s+\w+)*)'

	match = re.search(pattern, s)
	if match:
		street_name = match.group(1)
		return street_name
	else:
		return ""

def find_apartments(area):
	df = zlw.zillow_data_collect(area)

	grocery = pd.read_csv("Pittsburgh Grocery Stores.csv")
	grocery = grocery[grocery['area'] == area]

	coordinates_grocery = grocery[['longitude', 'latitude']].values
	coordinates_apt = df[['longitude', 'latitude']].values

	# Calculate the pairwise Euclidean distances
	distances = np.linalg.norm(coordinates_apt[:, np.newaxis, :] - coordinates_grocery, axis=2)

	# Calculate the mean distance for each apartment
	mean_distances = np.mean(distances, axis=1)
	sorted_indices = np.argsort(mean_distances)  # Get the indices that would sort mean_distances
	ranks = np.argsort(sorted_indices) + 1  # Add 1 to make ranks start from 1

	df['grocery_rank'] = ranks

	area = area.lower()
	restaurant = pd.read_csv("Pittsburgh Restaurants.csv")
	restaurant = restaurant[restaurant['area'] == area]

	info_restaurant = restaurant[['longitude', 'latitude', 'rating']].values

	# Calculate the pairwise Euclidean distances between apartments and restaurants
	distances = np.linalg.norm(coordinates_apt[:, np.newaxis, :] - info_restaurant[:, :2], axis=2)

	# Find the indices of the five closest restaurants for each apartment
	closest_indices = np.argsort(distances, axis=1)[:, :5]

	# Get the ratings of the closest restaurants
	closest_ratings = info_restaurant[closest_indices, 2]

	# Calculate the mean rating of the closest restaurants for each apartment
	mean_ratings = np.mean(closest_ratings, axis=1)

	sorted_indices = np.argsort(mean_ratings)  # Get the indices that would sort mean_distances
	ranks = np.argsort(sorted_indices) + 1  # Add 1 to make ranks start from 1
	df['restaurant_rank'] = ranks


	df['street'] = df['address'].apply(lambda x: find_street(x))
	df['safety'] = df['address'].apply(lambda x: cs.find_safety_level(find_street(x)))
	df['safety_level'] = 1
	df['safety_level'][df['safety'] == 'safe'] = 1
	df['safety_level'][df['safety'] == 'moderately safe'] = 2/3
	df['safety_level'][df['safety'] == 'moderately unsafe'] = 1/3
	df['safety_level'][df['safety'] == 'unsafe'] = 0
	df['safety_level'][df['safety'] == 'NA'] = 0
	df['safety_level'][df['safety'] == ''] = 0

	df['rating_value'], df['grocery_rank'], df['restaurant_rank'], df['safety_level'] = df['rating_value'].astype(float), df['grocery_rank'].astype(float), df['restaurant_rank'].astype(float), df['safety_level'].astype(float)
	df['Total Score'] = 0.25 * (df['rating_value'] + df['grocery_rank'] + df['restaurant_rank'] + df['safety_level'])
	selected = df.nlargest(4, 'Total Score')
	return selected
