import requests

response = requests.post("http://127.0.0.1:5000/api/users", {'username': 'uyqn'})
response2 = requests.get("http://127.0.0.1:5000/api/user/uyqn", {'requester': 'uyqn'})
print(response2.json())