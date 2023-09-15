
import requests

def abot_chat(msg: str, sender_id: str) -> dict:
    resp = requests.post("https://api.abot.phaidelta.com/chat", json={
        "text": msg,
        "sender_id": sender_id
    })
    resp.raise_for_status()

    return resp.json()
