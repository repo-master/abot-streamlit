import streamlit as st
import numpy as np
import json
import time
from typing import TypedDict, Optional
from concurrent.futures import Future, ThreadPoolExecutor
import requests
import random
from uuid import uuid4
import plotly
from abot_client import abot_chat


B1_CIPLA_TEMP_CHART = "temp_chart.json"
B1_CIPLA_RH_CHART = "rh_chart.json"


CAPABILITIES = """Here are my capabilities:

- List of warehouses
- Warehouse summary
- Units summary in a warehouse
- Warehouse unit list
- Warehouse sensor status
- Unit-level sensor status
- Sensor data value aggregation [Min, Max, etc.] in given time range
- Sensor data chart/report
- Report download [PDF/XLSX]
- List sensors in warehouse
- List of units that are normal/out
- List of sensors that are normal/out
- Count of units in a warehouse that are normal/out
- Count of sensors in a warehouse/unit/overall that are normal/out

Let me know if there's anything specific you would like to know or any task you would like me to perform.
"""

UNIT_SUMMARY = """Here is the summary of units in the warehouse:

- Unit: B2 FF Back
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B2 Basement
  - Number of out_of_range sensors: 2
  - Status: OUT_OF_RANGE

- Unit: B2 GF Back
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B2 FF Front
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B1 Lupin
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B1 Cipla
  - Number of out_of_range sensors: 2
  - Status: OUT_OF_RANGE

- Unit: B2 GF Front
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B3 NAC
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: B3 AC
  - Number of out_of_range sensors: 1
  - Status: OUT_OF_RANGE

- Unit: CR2
  - Number of out_of_range sensors: 0
  - Status: NORMAL

- Unit: CR1
  - Number of out_of_range sensors: 0
  - Status: NORMAL
"""


OOR_UNITS = """- B1 Cipla (OUT_OF_RANGE)
- B3 AC (OUT_OF_RANGE)
- B2 Basement (OUT_OF_RANGE)
"""


class Message(TypedDict):
    msg_id: str = None
    role: str = "human"
    message: Optional[str]
    kwargs: dict = {}


if st.session_state.get("tpe") is None:
    st.session_state["tpe"] = ThreadPoolExecutor()

if st.session_state.get("sent_msg") is None:
    st.session_state["sent_msg"] = None

if st.session_state.get("chat_message_history") is None:
    st.session_state["chat_message_history"] = []

if st.session_state.get("sess_id")  is None:
    st.session_state["sess_id"] = uuid4().hex

if len(st.session_state["chat_message_history"]) == 0:
    st.session_state["chat_message_history"].append(Message(
        role="ai",
        message="Hi! I am Abot! Ask me anything!"
    ))


def _msg_api(msg: str) -> Message:
    msg = msg.lower()
    time.sleep(random.randint(50, 200) / 100)
    match msg:
        case "hello":
            return Message(
                role="ai",
                message="Hello! How can I assist you today?",
                kwargs={"buttons": ["What can you do?"]}
            )
        case "what can you do?":
            return Message(
                role="ai",
                message=CAPABILITIES
            )
        case "list of warehouses":
            return Message(
                role="ai",
                message="- Warehouse: Verna",
                kwargs={"buttons": ["Verna warehouse status", "List inactive warehouses"]}
            )
        case "status of verna":
            return Message(
                role="ai",
                message="""Status of Warehouse Verna:
- Emergencies: Normal
- Metrics Out of Range: 8
- Power Consumption: 5410.0 KWH (Normal)
- Attendance: Normal""",
                kwargs={"buttons": ["Number of units", "Inactive unit list"]}
            )
        case "any units out?":
            return Message(
                role="ai",
                message="""The following units in the warehouse have sensors that are out of range:

- Unit: B2 Basement
  - Number of out_of_range sensors: 2
  - Status: OUT_OF_RANGE

- Unit: B1 Cipla
  - Number of out_of_range sensors: 2
  - Status: OUT_OF_RANGE

- Unit: B3 AC
  - Number of out_of_range sensors: 1
  - Status: OUT_OF_RANGE""",
                kwargs={"buttons": ["Number of out of range units"]}
            )
        case "b1 cipla temperature sensor status":
            return Message(
                role="ai",
                message="""Status of Temperature sensors in Unit B1 Cipla:
- Sensor Name: B1 Cipla 1_temp
  - Status: NORMAL
  - Last Value: 27.1°C""",
                kwargs={"buttons": ["Chart", "Sensor trends"]}
            )
        case "and rh?":
            return Message(
                role="ai",
                message="""Status of Relative Humidity (RH) sensors in Unit B1 Cipla:
- Sensor Name: B1 Cipla 1_rh
  - Status: NORMAL
  - Last Value: 56.2%""",
                kwargs={"buttons": ["Chart", "Sensor trends"]}
            )
        case "b1 cipla temperature sensor chart for yesterday, 1h interval":
            return Message(
                role="ai",
                message="Report: Temperature for B1 Cipla 1_temp [2023-08-02 00:00:00 till 2023-08-02 23:59:59, 1H interval]",
                kwargs={"chart": open(B1_CIPLA_TEMP_CHART).read(), "buttons": [
                    "Download PDF",
                    "Download XLSX"
                ]}
            )
        case "rh sensor in same unit":
            return Message(
                role="ai",
                message="Report: Humidity for B1 Cipla 1_rh [2023-08-02 00:00:00 till 2023-08-02 23:59:59, 1H interval]",
                kwargs={"chart": open(B1_CIPLA_RH_CHART).read(), "buttons": [
                    "Download PDF",
                    "Download XLSX"
                ]}
            )
        case "download xlsx":
            return Message(
                role="ai",
                message="Report ready for download: B1 Cipla 1_rh [2023-08-02 00:00:00 till 2023-08-02 23:59:59, 1H interval]",
                kwargs={"buttons": [(":page_facing_up:", "View attachment")]}
            )
        case "b2 basement temperature":
            return Message(
                role="ai",
                message="""B2 Basement 1_temp:
  - Status: NORMAL
  - Last value: 22.7°C""",
                kwargs={"buttons": ["Get sensor max", "Get sensor min", "Get sensor average"]}
            )
        case "get sensor max":
            return Message(
                role="ai",
                message="Maximum value: 22.9°C",
                kwargs={"buttons": ["Get sensor min", "Get sensor average", "Get unit status"]}
            )
        case "get unit status":
            return Message(
                role="ai",
                message="Status: OUT_OF_RANGE",
                kwargs={"buttons": ["Out of range unit list", "Get sensors min", "Get sensors max"]}
            )
        case "out of range unit list":
            return Message(
                role="ai",
                message=OOR_UNITS,
                kwargs={"buttons": ["Normal units", "Inactive units", "Warehouse info"]}
            )

    return Message(
        role="ai",
        message="Unknown message for this demo :("
    )


def _msg_abot_chat(msg: str) -> Message:
    try:
        response = abot_chat(msg, st.session_state.get("sess_id"))
        msg = response[0]
        print(response)
        attachments = []

        if msg.get("attachment") is not None:
            attachments.append({
                "label": ":page_facing_up: View attachment",
                "url": msg.get("attachment")
            })

        return Message(
            role="ai",
            message=msg["text"],
            kwargs={
                "buttons": [*[
                    btn['title'] for btn in (msg.get("buttons") or [])
                ], *attachments],
                **(msg.get("custom", {}) or {})
            }
        )
    except requests.HTTPError as ex:
        return Message(
            role="ai",
            message=f'Error: {ex.response.json()["detail"]}',
            kwargs={"color": "red"}
        )
    return Message(
        role="ai",
        message="Error: No response received"
    )


def submit_msg(msg: str, history) -> Future:
    return st.session_state["tpe"].submit(_msg_abot_chat, msg)


"# ABOT"

msg = st.chat_input()


def send_message(msg: str):
    user_msg = Message(
        msg_id=uuid4().hex,
        role="human",
        message=msg
    )
    st.session_state["chat_message_history"].append(user_msg)
    with st.spinner():
        st.session_state["sent_msg"] = submit_msg(msg, st.session_state["chat_message_history"])


# Send message
if msg is not None:
    send_message(msg)


def open_url(url: str):
    pass


# All messages
for message in st.session_state["chat_message_history"]:
    if message is None: continue
    with st.chat_message(message["role"], avatar="abot-chat.png" if message["role"] == "ai" else None):
        if message["message"]:
            st.write(message["message"])

        if message.get("kwargs") is not None:
            addt = message["kwargs"]
            if addt.get("chart") is not None:
                if addt["chart"]:
                    fig = plotly.io.from_json(json.dumps(addt["chart"]))
                    fig.update_layout({
                        'plot_bgcolor': 'rgba(16,24,24,0.6)',
                    })
                    st.plotly_chart(fig, use_container_width=True)
            if addt.get("buttons"):
                for btn in addt["buttons"]:
                    if isinstance(btn, dict):
                        from urllib.parse import quote_plus
                        btn_label = btn["label"]
                        btn_url = btn["url"].replace(" ", "%20")
                        st.markdown(f"[{btn_label}]({btn_url})")
                    else:
                        if isinstance(btn, str):
                            btn_label = btn
                        elif isinstance(btn, tuple):
                            btn_label = " ".join(btn)
                        st.button(btn_label, key=btn_label+message.get("msg_id", ""), on_click=send_message, args=(btn_label,))

# Sending message spinner
if st.session_state["sent_msg"] is not None:
    with st.chat_message("ai", avatar="abot-chat.png"):
        with st.spinner(text=""):
            new_msg = st.session_state["sent_msg"].result()
            new_msg["msg_id"] = uuid4().hex
            st.session_state["chat_message_history"].append(new_msg)
            st.session_state["sent_msg"] = None
            st.experimental_rerun()
