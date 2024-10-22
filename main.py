import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import HumanMessage
from fastapi import FastAPI, Request
from collections import defaultdict
import time
import json
import requests

with open('config.json') as f:
    config = json.load(f)

USER = config["USER"]
GOOGLE_MAPS_KEY = config['GOOGLE_MAPS_KEY']
 

app = FastAPI()



#Get address to coords
def get_address_to_coords(address, API_KEY):

    # Google Geocoding API endpoint
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"

    # Send request
    response = requests.get(url)
    geocode_data = response.json()

    # Extract latitude and longitude from the response
    if geocode_data['status'] == 'OK':
        location = geocode_data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        print('Geocoding failed:', geocode_data['status'])



def get_todays_day():
    from datetime import datetime

    now = datetime.now()
    
    day = now.strftime("%A")

    day_idx = now.weekday()

    return day, day_idx



def get_restaurant_name_addr_timing(cuisine, API_KEY, my_latitude, my_longitude, radius, restaurant_cnt, place='restaurant'):

    search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'

    params = {
        'location': f'{my_latitude},{my_longitude}',
        'radius': radius,
        'type': place,
        'keyword': cuisine,
        'key': API_KEY
    }

    restaurant_details = {}
    cnt = 0
    while restaurant_cnt > 0:
        # Make the API request for nearby search
        response = requests.get(search_url, params=params)
        restaurants_data = response.json()

        if restaurants_data['status'] != 'OK':
            print(f"Error: {restaurants_data['status']}")
            break

        # Process each restaurant result
        for restaurant in restaurants_data.get('results', []):
            if restaurant_cnt <= 0:
                break  # Exit if the desired count is reached

            name = restaurant.get('name')
            address = restaurant.get('vicinity')
            place_id = restaurant.get('place_id')

            # Get detailed info about the restaurant
            details_params = {
                'place_id': place_id,
                'fields': 'name,opening_hours,formatted_address',
                'key': API_KEY
            }

            details_response = requests.get(details_url, params=details_params)
            details_data = details_response.json()

            if details_data['status'] == 'OK':
                restaurant_info = details_data['result']
                hours = restaurant_info.get('opening_hours', {}).get('weekday_text', 'No hours available')

                # Store restaurant details in dictionary
                restaurant_key = name if name not in restaurant_details else name + str(cnt)
                restaurant_details[restaurant_key] = {
                    'address': address,
                    'hours': hours
                }
                cnt += 1
                restaurant_cnt -= 1  # Decrement count after each restaurant

        # Check if there are more pages of results
        next_page_token = restaurants_data.get('next_page_token')
        if next_page_token and restaurant_cnt > 0:
            # Wait for a few seconds before making the next request (Google recommends a delay)
            time.sleep(2)
            # Update the parameters to include the next page token
            params['pagetoken'] = next_page_token
        else:
            # No more pages to process
            break

    return restaurant_details


def get_distance_between_addresses(address1, address2, API_KEY):

    distance_matrix_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    params = {
        'origins': address1,
        'destinations': address2,
        'key': API_KEY,
        'units': 'metric',
    }

    response = requests.get(distance_matrix_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        distance_in_km = data['rows'][0]['elements'][0]['distance']['text']
        duration = data['rows'][0]['elements'][0]['duration']['text']

        return distance_in_km, duration
    else:
        print(f"Error: {data['status']}")


@app.post("/")
async def reservation(request: Request):

    # 1) Get User FRiends and similar cuisine

    req_data = await request.json()

    user_pref = req_data[USER]   #alice pref

    peeps = [req_data[i] for i in req_data if i != USER]


    user_friends = []
    common_cuisine = set()


    for i in peeps:

        get_user_cuisine = set(user_pref["cuisines"].split(", "))
        get_i_curr_cuisine = set(i["cuisines"].split(", "))

        if USER in i["friend's name"]:

            if get_user_cuisine.intersection(get_i_curr_cuisine):
                    common_cuisine.update(get_user_cuisine.intersection(get_i_curr_cuisine))
                    user_friends.append(i)


    # 2) Get name, addr, time of restaurants (based on cuisines, location and radius)


    Radius = 3000
    Restaurant_cnt = 5

    user_latitute, user_longitude = get_address_to_coords(user_pref["Address"], GOOGLE_MAPS_KEY)




    day, day_idx = get_todays_day()


    restaurant_details = {}
    for cuisine in common_cuisine:
        temp_restaurant_details = get_restaurant_name_addr_timing(cuisine=cuisine,API_KEY= GOOGLE_MAPS_KEY, my_latitude=user_latitute, my_longitude=user_longitude, radius=Radius, restaurant_cnt=Restaurant_cnt)
        restaurant_details.update(temp_restaurant_details)


    for restaurant, details in restaurant_details.items():

        details['hours'] = details['hours'][day_idx].replace('\u2009', " ").replace('\u202f', "")


    # 3) Get Distance B/w frnds and restaurant addresses


    get_distance = defaultdict(list)
    for i in user_friends:
        for j in restaurant_details:
            dist_in_km, duration = get_distance_between_addresses(address1=restaurant_details[j]['address'], address2=i["Address"], API_KEY=GOOGLE_MAPS_KEY)
            
            get_distance[i['name']].append({'name' : j, 'dist_in_km' : dist_in_km, 'time' : duration})



    user_detail = user_pref


    #User's name, cuisines, preferred time

    prompt_user = """"""
    for i in user_detail:
        if i == 'Address' or i == "friend's name" : continue
        prompt_user += f"{i} : {user_detail[i]}\n"



    #Friend's name, cuisines, preferred time
    prompt_frnds = """"""
    cnt = 1
    for i in user_friends:
        prompt_frnds += f"Friend {cnt} ->\n"
        for j in i:
            if j == 'Address' or j == "friend's name" : continue
            prompt_frnds += f"{j} : {i[j]}\n"
        prompt_frnds += '\n'
        cnt += 1



    #Rest Timing, name, distance from frnd to restaurant
    prompt_distance_to_user_frnds = """"""
    for i in get_distance:
        prompt_distance_to_user_frnds += f"\nFriend Name : {i} =>\n"
        for j in get_distance[i]:
            prompt_distance_to_user_frnds += ' ' *10 + f"Restaurant name : {j['name']}, Timings : {restaurant_details[j['name']]['hours']}, Distance from {i} to Restaurant : {j['dist_in_km']}\n"



    prpt = f""" 
    Given the user's preferences and their friends' preferences, identify suitable restaurant matches for the user and their friends based on cuisine, preferred dining time, and the distance from each friend's location to the restaurant.

        User Information:
            {prompt_user}

        Friends' Information:
            {prompt_frnds}

        Distance Information:
            {prompt_distance_to_user_frnds}

    Please note that multiple friends may choose the same restaurant, and the user's name should not appear in the list of friends. Do not attempt to include all friends; only select matches that can be recommended for the best restaurant experience. Additionally, include a key indicating whether the recommendation is for a group or just one friend.

    Using the provided information, Generate the output as a single JSON string containing the following key-value pairs. Inside the JSON string, it may include one or more JSON objects for matches based on the provided information. No comments should be included, the term "json" should not be mentioned, and no additional content should be present other than the specified content:

        friends: A list of friends that match with the user.
        restaurant_name: The name of the restaurant.
        timing: The timing of the restaurant.
        reason_for_this_match: A concise explanation detailing why this restaurant aligns with the user's preferences. Highlight how the restaurant's offerings cater to the user's chosen cuisines and preferred dining times, ensuring a satisfying experience. Mention how it complements the overall atmosphere and quality that the user seeks, making it an excellent choice for their outing.
        group_or_friend: A key indicating whether the recommendation is for a group or just one friend.
    """



    GEMINI_API = config['GEMINI_API']




    os.environ['GOOGLE_API_KEY'] = GEMINI_API

    llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro') #, temperature=0.9, top_p=0.85

    prompt = HumanMessage(content=prpt)
    response = llm([prompt])

    content = response.content.replace('json', '').replace('`', '')

    return content


if __name__ == "__main__":

    preferences = {
        'Alice': {
            'name': 'Alice',
            "cuisines": "Indian, Mexican",
            "preferred time": "Weekends, brunch time",
            "friend's name": ["Bob", "Charlie"],
            "Address": "Jubilee Hills Rd, Hyderabad, Telangana 500033"
        },
        'Bob': {
            'name': 'Bob',
            "cuisines": "Indian",
            "preferred time": "Weekdays, lunch time",
            "friend's name": ["Alice", "Charlie"],
            "Address": "Banjara Hills Rd, Hyderabad, Telangana 500034"
        },
        'Charlie': {
            'name': 'Charlie',
            "cuisines": "Korean, Indian",
            "preferred time": "Evenings, after 6 PM",
            "friend's name": ["Alice", "Bob"],
            "Address": "Madhapur Main Rd, Hyderabad, Telangana 500081"
        },
        'Dave': {
            'name': 'Dave',
            "cuisines": "Italian, Indian",
            "preferred time": "Weekends, dinner time",
            "friend's name": ["Alice", "Charlie"],
            "Address": "Hitech City, Hyderabad, Telangana 500081"
        },
        'Eve': {
            'name': 'Eve',
            "cuisines": "Mexican, Chinese",
            "preferred time": "Weekdays, lunch time",
            "friend's name": ["Bob"],
            "Address": "Gachibowli, Hyderabad, Telangana 500032"
        },
        'Frank': {
            'name': 'Frank',
            "cuisines": "Thai, Indian",
            "preferred time": "Weekdays, dinner time",
            "friend's name": ["Alice", "Eve"],
            "Address": "Kondapur, Hyderabad, Telangana 500084"
        },
        'Grace': {
            'name': 'Grace',
            "cuisines": "Italian, Mexican",
            "preferred time": "Weekends, lunch time",
            "friend's name": ["Charlie", "Bob"],
            "Address": "Manikonda, Hyderabad, Telangana 500089"
        }
    }

    print(reservation(preferences))