from requests import get

response = get("http://127.0.0.1:5000/api/room/general", {'requester': 'uyqn'})
room_info = response.json()
room_info.pop('messages')

print(room_info)