from sc_google_maps_api import ScrapeitCloudClient 
import pandas as pd
import json
import re
import warnings
warnings.filterwarnings("ignore")


client = ScrapeitCloudClient(api_key='c2d6f4fe-1870-4625-b448-65113de48b51') 
response = client.scrape(params={"keyword": "grocery store in pittsburgh regent square", "country": "US", "domain": "com"}) 
res = response.json()

#print(len(res['scrapingResult']['locals']))
df = pd.DataFrame(res['scrapingResult']['locals'])
#df['longitude'] = df['gpsCoordinates'].apply(lambda x: x['longitude'])
#df['latitude'] = df['gpsCoordinates'].apply(lambda x: x['latitude'])
print(df.shape)
df.to_csv("grocery_store_regent_square.csv", index = False)

def flatten(x):
	# Define regular expressions to match latitude and longitude
	latitude_pattern = r"'latitude':\s*([\d.-]+)"
	longitude_pattern = r"'longitude':\s*([\d.-]+)"

	# Use re.findall to extract latitude and longitude values
	latitude = re.findall(latitude_pattern, x)
	longitude = re.findall(longitude_pattern, x)

	# Ensure the result is a list; you can access the first element if there's only one match
	if latitude:
	    latitude = float(latitude[0])
	if longitude:
	    longitude = float(longitude[0])

	return latitude, longitude

'''

df1 = pd.read_csv("grocery_store_squirrel_hill.csv")
df1['longitude'] = df1['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df1['latitude'] = df1['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df1['area'] = 'Squirrel Hill'

df2 = pd.read_csv("grocery_store_brookline.csv")
df2['longitude'] = df2['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df2['latitude'] = df2['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df2['area'] = 'Brookline'

df3 = pd.read_csv("grocery_store_lawrenceville.csv")
df3['longitude'] = df3['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df3['latitude'] = df3['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df3['area'] = 'Lawrenceville'

df4 = pd.read_csv("grocery_store_point_breeze.csv")
df4['longitude'] = df4['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df4['latitude'] = df4['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df4['area'] = 'Point Breeze'

df5 = pd.read_csv("grocery_store_north_shore.csv")
df5['longitude'] = df5['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df5['latitude'] = df5['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df5['area'] = 'North Shore'

df6 = pd.read_csv("grocery_store_shadyside.csv")
df6['longitude'] = df6['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df6['latitude'] = df6['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df6['area'] = 'Shadyside'

df7 = pd.read_csv("grocery_store_highland_park.csv")
df7['longitude'] = df7['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df7['latitude'] = df7['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df7['area'] = 'Highland Park'

df8 = pd.read_csv("grocery_store_regent_square.csv")
df8['longitude'] = df8['gpsCoordinates'].apply(lambda x: flatten(x)[1])
df8['latitude'] = df8['gpsCoordinates'].apply(lambda x: flatten(x)[0])
df8['area'] = 'Regent Square'

df = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8])
df.to_csv("Pittsburgh Grocery Stores.csv", index = False)


areas = ["Squirrel Hill", "Brookline", "Lawrenceville", "Point Breeze", "North Shore", "Shadyside", "Highland Park", "Regent Square"]
areasL = ["squirrel hill", "brookline", "lawrenceville", "point breeze", "north shore", "shadyside", "highland park", "regent square"]

agg = []
client = ScrapeitCloudClient(api_key='c2d6f4fe-1870-4625-b448-65113de48b51') 
for i in range(len(areas)):
	area = areasL[i]
	keyword = "restaurant in pittsburgh " + area
	response = client.scrape(params={"keyword": keyword, "country": "US", "domain": "com"}) 
	res = response.json()
	df = pd.DataFrame(res['scrapingResult']['locals'])
	df['longitude'] = df['gpsCoordinates'].apply(lambda x: x['longitude'])
	df['latitude'] = df['gpsCoordinates'].apply(lambda x: x['latitude'])
	df['area'] = area
	print(area, df.shape)
	agg.append(df)
df_a = pd.concat(agg)
df_a.to_csv("Pittsburgh Restaurants.csv", index = False)

