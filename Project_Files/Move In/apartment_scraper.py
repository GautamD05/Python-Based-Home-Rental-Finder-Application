# This script requires ChromeDriver to interact with Chrome.
# Ensure you've installed ChromeDriver and added it to your system's PATH or place it in the same directory as this script.
# Download from: https://sites.google.com/a/chromium.org/chromedriver/
# Also install requirements from requirements.txt before running the file

#Input Samples:
# Terminal 21, 5836 Beacon St, 5551 Darlington Rd, 5836 Alderson St, Walnut Towers at Frick Park, 7070 Forward Ave, 6350 Penn Ave

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import warnings
warnings.filterwarnings("ignore")

def start_browser():
    """Function to start the browser and return the driver."""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-agent=" + HEADERS['User-Agent'])
    chrome_options.add_argument("window-size=1920x1080")
    chrome_options.add_argument("headless")

    return webdriver.Chrome(options=chrome_options), HEADERS

def initiate_search(driver, search_term):
    """Function to navigate to apartments.com and initiate a search."""
    driver.get('https://www.apartments.com/')


    search_bar =WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "quickSearchLookup")))
    search_bar.clear()
    search_bar.send_keys(search_term)

    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'suggestItem'))
        WebDriverWait(driver, 5).until(element_present)
        driver.find_element(By.CLASS_NAME, 'suggestItem').click()
    except:
        search_button = driver.find_element(By.XPATH, "//button[@title='Search apartments for rent']")
        search_button.click()
    time.sleep(5)


def get_soup(url, headers):
    """Function to get the soup object from a URL"""
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error {response.status_code}: Unable to fetch webpage.")
        return None
    return BeautifulSoup(response.content, 'html.parser')


def scrape_listing(url, headers):
    soup = get_soup(url, headers)  # Assuming you have this function implemented

    unique_features = []
    all_amenities = []
    rating_info = None
    reviews = []

    if soup:
        # Extract unique features
        try:
            feature_div = soup.find('div', class_='uniqueFeatures')
            if feature_div:
                features_list = feature_div.find('ul')
                if features_list:
                    unique_features = [li.get_text(strip=True) for li in features_list.find_all('li', class_='specInfo uniqueAmenity')]
        except Exception as e:
            print(f"Error extracting unique features: {e}")

        try:
        # Extract apartment amenities
            amenities_label = [amenity.get_text(strip=True) for amenity in soup.find_all('p', class_='amenityLabel')]
            combined_amenities_list = soup.find('ul', class_='combinedAmenitiesList')
            combined_amenities = [amenity.get_text(strip=True) for amenity in combined_amenities_list.find_all('li', class_='specInfo')] if combined_amenities_list else []
            all_amenities = amenities_label + combined_amenities
        except Exception as e:
            print(f"Error extracting apartment amenities: {e}")

        try:
        # Extract rating information
            rating_wrapper = soup.find('div', class_='ratingBoxWrapper')
            if rating_wrapper:
                rating_value = rating_wrapper.find('div', class_='averageRating')
                rating_category = rating_wrapper.find('div', class_='ratingTitle')
                max_rating = rating_wrapper.find('div', class_='maxRating')
                if rating_value and rating_category and max_rating:
                    rating_info = {
                        "value": rating_value.get_text(strip=True),
                        "category": rating_category.get_text(strip=True),
                        "max": max_rating.get_text(strip=True).replace("Out of", "").strip()
                                    }
        except Exception as e:
            print(f"Error extracting rating information: {e}")

        try:
        # Extract reviews
            reviews_container = soup.find('div', class_='js-Reviews')
            if reviews_container:
                review_wrappers = reviews_container.find_all('div', class_='reviewContainerWrapper', limit=5)
                for review in review_wrappers:
                    date = review.find('span', class_='reviewDateContainer').get_text(strip=True)
                    title = review.find('h3', class_='reviewTitle').get_text(strip=True)
                    review_text = review.find('p', class_='reviewText reviewFullText').get_text(strip=True)
                    reviews.append({
                        "date": date,
                        "title": title,
                        "text": review_text
                    })
        except Exception as e:
            print(f"Error extracting review information: {e}")

    return unique_features, all_amenities, rating_info, reviews


def remove_duplicates(unique_features, apartment_features):
    # Convert the lists to sets for easy duplicate removal
    unique_set = set(unique_features)
    apartment_set = set(apartment_features)

    # Remove duplicates by taking the difference of the two sets
    unique_set -= apartment_set

    # Convert the sets back to lists for return
    unique_features = list(unique_set)
    apartment_features = list(apartment_set)

    return unique_features, apartment_features


def export_to_csv(filename, unique_features, apartment_features, rating_info, reviews):
    # Ensure the filename is filesystem-friendly
    filename = ''.join(e for e in filename if e.isalnum() or e in (' ',)).replace(' ', '_')

    # Create or overwrite the CSV file
    with open(filename + '.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write unique features to CSV
        writer.writerow(["Unique Features"])
        if unique_features:
            for feature in unique_features:
                writer.writerow(["-", feature])
        else:
            writer.writerow(["No information available for Unique Features."])

        writer.writerow([])  # Empty row

        # Write apartment features to CSV
        writer.writerow(["Apartment Features"])
        if apartment_features:
            for amenity in apartment_features:
                writer.writerow(["-", amenity])
        else:
            writer.writerow(["No information available for Apartment Features."])

        writer.writerow([])  # Empty row

        # Write rating info to CSV
        writer.writerow(["Rating Information"])
        if rating_info:
            writer.writerow([
                                f"This place is rated {rating_info['value']} out of {rating_info['max']} and is marked {rating_info['category']}."])
        else:
            writer.writerow(["No information available for Rating Information."])

        writer.writerow([])  # Empty row

        # Write reviews to CSV
        writer.writerow(["Reviews"])
        if reviews:
            writer.writerow(["Top 5 Reviews:"])
            for review in reviews:
                writer.writerow(["Date:", review["date"]])
                writer.writerow(["Title:", review["title"]])
                writer.writerow(["Review:", review["text"]])
                writer.writerow([])  # Empty row
        else:
            writer.writerow(["No reviews available."])

def main(search_term):
    try:
        driver, headers = start_browser()
        initiate_search(driver, search_term)
        current_url = driver.current_url
        unique_features, all_amenities, rating_info, reviews = scrape_listing(current_url, headers)
        refined_unique_features, refined_apartment_features = remove_duplicates(unique_features, all_amenities)
        if not refined_unique_features:
            refined_unique_features = ['']
        if not refined_apartment_features:
            refined_apartment_features = ['']
        if not rating_info:
            rating_info = {'value': 0, 'max': 0, 'category': 'NA'}
        return refined_unique_features, refined_apartment_features, rating_info
    except Exception as error:
        print(error)
        return [''], [''], {'value': 0, 'max': 0, 'category': 'NA'}


'''
def main():

    while True:
        # Read the search address from the user
        search_term = input("Enter the address you want to search for or type exit: ")
        if search_term.lower() == 'exit':  # If user types 'exit', break the loop
            break
        driver, headers = start_browser()
        initiate_search(driver, search_term)

        current_url = driver.current_url
        print(f"\nYour choice of place: {search_term}")

        unique_features, all_amenities, rating_info, reviews = scrape_listing(current_url, headers)
        refined_unique_features, refined_apartment_features = remove_duplicates(unique_features, all_amenities)

        # Print unique features
        if refined_unique_features:
            print("\n" + "=" * 40)
            print("Unique Features")
            print("=" * 40 + "\n")
            for feature in refined_unique_features:
                print("-", feature)
        else:
            print("\nNo information available for Unique Features.")

        # Print apartment features
        if refined_apartment_features:
            print("\n" + "=" * 40)
            print("Apartment Features")
            print("=" * 40 + "\n")
            for amenity in refined_apartment_features:
                print("-", amenity)
        else:
            print("\nNo information available for Apartment Features.")

        # Print rating information
        if rating_info:
            print("\n" + "=" * 40)
            print("Rating Information")
            print("=" * 40 + "\n")
            print(f"This place is rated {rating_info['value']} out of {rating_info['max']} and is marked {rating_info['category']}.")
        else:
            print("\nNo information available for Rating Information.")

        # Print reviews
        if reviews:
            print("\n" + "=" * 40)
            print("Reviews")
            print("=" * 40 + "\n")
            print("Top 5 Reviews:")
            for review in reviews:
                print("-" * 30)
                print("Date:", review["date"])
                print("Title:", review["title"])
                print("Review:", review["text"])
        else:
            print("\nNo reviews available.")
        print("-" * 30)
        export_to_csv(search_term, refined_unique_features, refined_apartment_features, rating_info, reviews)
        print("Search completed. You can search again or type 'exit' to quit.\n")

        driver.quit()


if __name__ == "__main__":
    main()

# *********** OUTPUT SAMPLE *****************

#Enter the address you want to search for or type exit: Terminal 21

Your choice of place: Terminal 21

========================================
Unique Features
========================================

- City View
- Yoga Studio
- Duckpin Bowling
- Bike Storage with Repair Stn
- Coffee/Tea Bar
- Large Windows
- 3rd Floor Decrease
- New Kitchens
- Concrete Floors
- Laundry Rooms on Each Floor
- 9th Floor Increase
- City & River Views
- Pet friendly
- River View
- 7th Floor Increase
- Speakeasy Lounge
- Near Public Transit
- Arcade
- Renovated Bathrooms
- Online Resident Portal
- Sound Proof Studio
- Soundproof Rehearsal Studios
- Co-Working Lounge
- Community Kitchen
- Makers Room
- 8th Floor Increase
- Yoga Lounge
- Stainless Steel Appliances
- Microwave
- Short Term Leases Available
- High Score from walkscore.com
- Internet Ready
- Laundry In Unit
- 6th Floor Increase
- Near Try Street Terminal Bld
- Online Maintenance Requests
- Private Full Bathrooms
- Speak Easy
- Markers Room
- Onsite Management Office
- WiFi Enabled Common Areas
- 6 minute walk to nearby uni
- Minutes to Historic District

========================================
Apartment Features
========================================

- Lounge
- On-Site Retail
- Bicycle Storage
- Controlled Access
- Dishwasher
- Washer/Dryer
- Laundry Facilities
- Air Conditioning
- Granite Countertops
- Maintenance on site
- Multi Use Room
- Gameroom
- Fitness Center

========================================
Rating Information
========================================

This place is rated 4.8 out of 5 and is marked Great.

========================================
Reviews
========================================

Top 5 Reviews:
------------------------------
Date: 12/8/22
Title: WORST EXPERIENCE EVER!!!!
Review: I was treated great at first. found it odd you could never reach anyone...I was told my co- signer was denied...a month later I get an email saying I owe them over a 1000 dollars for an apartment I never leased or even had access to, I never even got keys. I've tried calling repeatedly, just getting no answer and no way to leave a VM...total BS!!!
------------------------------
Date: 10/19/22
Title: Incompetent Building Management
Review: Prior to this property being acquired by Aion management, it was a great place to live. The new management has minimal concern for residents. Don’t expect timely responses to inquiries or satisfying resolutions to any maintenance issues.
------------------------------
Date: 8/12/20
Title: Very impressive
Review: Great layouts with modern amenities and fantastic social areas! Definitely at the top of my search list. Just toured today with Derrick who is an awesome agent. It feels like a good fit for me.
------------------------------
Search completed. You can search again or type 'exit' to quit.

Enter the address you want to search for or type exit: 7070 Forward Ave

Your choice of place: 7070 Forward Ave

========================================
Unique Features
========================================

- Individual Climate Control
- Cable/Internet ready
- Lobby Lounge
- Updated Appliances
- Large Windows
- Extra Storage
- Refrigerator
- Convenient Location
- Online Service and Rent Payments
- Carpeting
- Furnished Units Available
- Smoke Free Building
- Package and Mail Room
- Recycling
- Advanced Key Card Access on Exterior Doors
- Walnut Perks Discounts
- Wood-Inspired Flooring
- View
- Electronic Thermostat
- Dryer
- Central Air
- Recreation Room

========================================
Apartment Features
========================================

- Disposal
- Dishwasher
- Elevator
- Washer/Dryer
- Laundry Facilities
- Maintenance on site
- High Speed Internet Access
- Fitness Center

========================================
Rating Information
========================================

This place is rated 4.8 out of 5 and is marked Great.

========================================
Reviews
========================================

Top 5 Reviews:
------------------------------
Date: 6/10/23
Title: Verified Renter
Review: I love the towers I’ve been cleaning it off and on for 8yrs the staff is great I love all the doggies and the ppl that live there are really nice any issues are taken care of very quickly!!
------------------------------
Date: 2/28/23
Title: Verified Renter
Review: I've been looking for that dream apartment where I'd be content while saving for a house of my own. Walnut Towers is my dream apartment community, I consider myself lucky to be able to reside here.
------------------------------
Date: 10/4/22
Title: Verified Renter
Review: This property was the perfect choice for my first apartment. I got a safe, clean, spacious, and well laid out apartment for great value, and I love the location in Squirrel Hill! The maintenance and management teams are excellent and reliable, and you can tell that they value their residents!
------------------------------
Date: 9/29/22
Title: Verified Renter
Review: As a Maryland native in Pittsburgh, I typically move once a year at the end of my rental lease. I renewed at Walnut Towers for another year this past March thanks to the wonderful fellow residents, extremely attentive maintenance staff, and excellent building amenities. For once in the last decade in this city, I don't plan on moving any time soon!
------------------------------
Date: 7/26/22
Title: Verified Renter
Review: The experience before, during, and after move in have all been a breeze compared to other rental companies in Pittsburgh.
------------------------------
Search completed. You can search again or type 'exit' to quit.

Enter the address you want to search for or type exit: exit
'''