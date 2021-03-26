import requests

route = "http://127.0.0.1:5000/api/user/"

response = requests.delete(route)

print(response.status_code)