
import requests

def abot_chat(msg: str) -> dict:
    requests.post("https://api.abot.phaidelta.com/chat", json={
        "text": msg
    }).json()
