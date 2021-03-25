import requests

user_api = "http://127.0.0.1:5000/api/user/"

print("Adding a user: uyqn")
user_id = "uyqn"
# http://127.0.0.1:5000/api/user/uyqn
post_request = requests.post(user_api + user_id, {"Name": "Uy Quoc Nguyen", "Age": 29, "Email": "uy@email.com"})
print(post_request.json())

print("Get all users:")
get_all_request = requests.get(user_api + 'all')
print(get_all_request.json())

print("Adding a new user: panders")
user_id = "panders"
post_request = requests.post(user_api + user_id, {"Name": "Anders Ottersland", "Age": 21, "Email": "anders@email.com"})
print(post_request.json())

print("Get all users again:")
get_all_request = requests.get(user_api + 'all')
print(get_all_request.json())

print("Adding a new user: torresso")
user_id = "torresso"
post_request = requests.post(user_api + user_id, {"Name": "Andreas Torres Hansen", "Age": 21, "Email": "andreas@google.com"})
print(post_request.json())

print("Get all users for the third time:")
get_all_request = requests.get(user_api + 'all')
print(get_all_request.json())