import json
import requests
import base64

if __name__ == '__main__':

    # Dummy Inputs

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




    cont = requests.post('http://127.0.0.1:8000/', json=preferences)
    
    json_string = cont.content.decode('utf-8')

    print("2.) Got contnet... as string")


# Convert the JSON string to a Python dictionary
json_dict = json.loads(json_string)

json_dict = json.loads(json_dict)


with open('output.json', 'w') as json_file:
    json.dump(json_dict, json_file, indent=4)



print(json_dict)