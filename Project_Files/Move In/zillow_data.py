import json
import httpx
import pandas as pd
from parsel import Selector
import apartment_scraper as apt
import warnings
warnings.filterwarnings("ignore")

def parse_property(data: dict) -> dict:
    """parse zillow property"""
    # zillow property data is massive, let's take a look just
    # at the basic information to keep this tutorial brief:
    return data

def flatten(x):
    res = ''
    for i in range(len(x)):
        res += x[i]['price'] + '/' + x[i]['beds'] + ' bed(s)' + ';'
    return res[:-1]

def zillow_data_collect(area):
    BASE_HEADERS = {
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    url = "https://www.zillow.com/{0}-pittsburgh-pa/rentals/".format(area)
    with httpx.Client(http2=False, headers=BASE_HEADERS, follow_redirects=True) as client:
        resp = client.get(url)
    sel = Selector(text=resp.text)
    data = json.loads(sel.css("script#__NEXT_DATA__::text").get())
    res = parse_property(data)

    df = pd.json_normalize(res, sep='_')

    #print(df.to_dict(orient='records')[0].keys())

    # props_pageProps_searchPageState_cat1_searchResults_listResults
    r = res['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
    df = pd.DataFrame(r)
    df = df[['imgSrc', 'latLong', 'units', 'address', 'buildingName', 'isBuilding', 'addressZipcode', 'propertyStatusCd', 'price']]
    df['latitude'] = df['latLong'].apply(lambda x: 0.000 if 'latitude' not in x else x['latitude'])
    df['longitude'] = df['latLong'].apply(lambda x: 0.000 if 'longitude' not in x else x['longitude'])
    df['price'] = df['price'].astype(str)
    a = df.loc[0].units
    df['price'][df['isBuilding'] == True] = ""
    df['price'][df['isBuilding'] == True] = df['units'][df['isBuilding'] == True].apply(lambda x: flatten(x))
    df['propertyStatusCd'][df['propertyStatusCd'].isnull()] = "Apartment"
    df['address'] = df['address'].apply(lambda x: x.split(",")[0])
    del df['isBuilding']
    del df['units']

    df = df.iloc[:5]
    l1, l2, l3, l4 = [], [], [], []
    for address in list(df['address']):
        refined_unique_features, refined_apartment_features, rating_info = apt.main(address)
        rating_value, rating_category = rating_info['value'], rating_info['category']
        l1.append(refined_unique_features)
        l2.append(refined_apartment_features)
        l3.append(rating_value)
        l4.append(rating_category)
    df['unique_features'] = l1
    df['apartment_features'] = l2
    df['rating_value'] = l3
    df['rating_category'] = l4
    return df