from json import loads as load_json
from requests import get as requests_get, post as requests_post
from datetime import datetime, timezone
from config.db import messages_collection
from fastapi import FastAPI, Request, HTTPException
from pytz import timezone as pytz_timezone
from models.arr import JellyseerrData, ProwlarrData, RadarrData, SonarrData
from models.bluebubbles import BluebubblesData
from models.change import ChangeData
from models.custom import CustomData
from models.uptime import UptimeKuma
from os import getenv
from re import sub

server_address = getenv("BB_URL")
maubot_address = f"{getenv('MAUBOT_URL')}/_matrix/maubot/plugin/maubotwebhook/send"
server_password = getenv("BB_PASSWORD")
AREA_CODE = getenv("AREA_CODE", "+1")
tz = getenv("TIMEZONE", "America/New_York")
MATRIX_ID = getenv("MATRIX_ID")

app = FastAPI()

async def query_contact(handle):
    response = requests_get(f'{server_address}/api/v1/contact',
                            params={'password': server_password},
                            headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        handle = sub(r"[ ()-]", "", handle)
        contacts = load_json(response.text)
        contact = contacts.get("data")
        for i in contact:
            try:
                phone_number = i.get("phoneNumbers")[0].get("address")
                phone_number = sub(r"[ ()-]", "", phone_number)
                
                if len(phone_number) == 10:
                    phone_number = AREA_CODE + phone_number
                if len(handle) == 10:
                    handle = AREA_CODE + handle
                if phone_number == handle:
                    try:
                        first = i.get("firstName")
                        return first
                    except Exception:
                        pass
            except Exception:
                pass
        return "Someone"
    else:
        return "Someone"


async def send_chat(message):
    print(message)
    url = maubot_address
    headers = {"Content-Type": "application/json"}
    body = {
        "message": message,
        "room_id": f"!{MATRIX_ID}"
        }
    requests_post(url, headers=headers, json=body)


@app.post("/bluebubbles-webhook")
async def handle_bluebubbles_webhook(request: Request, data: BluebubblesData):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400, detail="Invalid Content-Type")

    match data.type:
        case 'new-message':
            message_data = data.data
            message_guid = message_data.guid
            message_text = message_data.text
            date_created = message_data.dateCreated
            self_message = message_data.isFromMe

            if self_message:
                return {"status": "ignored"}

            sender_handle = message_data.handle.get("address")

            conversation = await messages_collection.find_one({"sender_handle": sender_handle})

            if not conversation:
                await messages_collection.insert_one({
                    "sender_handle": sender_handle,
                    "messages": [
                        {
                            "guid": message_guid,
                            "text": message_text,
                            "timestamp": date_created,
                            "is_unsent": False,
                        }
                    ]
                })
            else:
                await messages_collection.update_one(
                    {"sender_handle": sender_handle},
                    {"$push": {"messages": {
                        "guid": message_guid,
                        "text": message_text,
                        "timestamp": date_created,
                        "is_unsent": False,
                    }}}
                )

            return {"status": "ok"}

        case "updated-message":
            message_data = data.data
            message_guid = message_data.guid
            message_text = message_data.text
            date_unsent = message_data.dateEdited
            self_message = message_data.isFromMe

            if self_message:
                return {"status": "ignored"}

            sender_handle = message_data.handle.get("address")

            conversation = await messages_collection.find_one({"sender_handle": sender_handle})

            if not conversation:
                await messages_collection.insert_one({
                    "sender_handle": sender_handle,
                    "messages": []
                })

                return {"status": "ignored"}
            
            message = None
            messages = conversation.get("messages")

            if isinstance(messages, list):
                for msg in messages:
                    if msg.get("guid") == message_guid:
                        message = msg
                        break

            if not message:
                return {"status": "ignored"}

            if message_text is None:
                unsent_time = date_unsent / 1000
                unsent_utc = datetime.fromtimestamp(unsent_time, tz=timezone.utc)
                est_timezone = pytz_timezone(tz)
                unsent_est_time = unsent_utc.astimezone(est_timezone)
                formatted_time = unsent_est_time.strftime("%I:%M %p")

                contact_name = await query_contact(sender_handle)
                original_text = message["text"]

                await send_chat(f'{contact_name} unsent "{original_text}" at {formatted_time}')
                
                await messages_collection.update_one(
                    {"sender_handle": sender_handle, "messages.guid": message_guid},
                    {"$set": {
                        "messages.$.is_unsent": True
                    }}
                )
            else:
                await messages_collection.update_one(
                    {"sender_handle": sender_handle, "messages.guid": message_guid},
                    {"$set": {
                        "messages.$.text": message_text,
                        "messages.$.timestamp": date_unsent
                    }}
                )

            return {"status": "ok"}

        case _:
            raise HTTPException(status_code=400, detail="Unknown event type")


@app.post("/jellyseerr-webhook")
async def handle_jellyseerr_webhook(request: Request, data: JellyseerrData):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400, detail="Invalid Content-Type")
    
    match data.notification_type:
        case "TEST_NOTIFICATION":
            await send_chat(data.message)
            return {"status": "ok"}
        case "MEDIA_PENDING":
            username = data.request.get("requestedBy_username", "Someone")
            message = f"{username} requested {data.subject}, pending approval"
            await send_chat(message)
            return {"status": "ok"}
        case "MEDIA_AUTO_APPROVED":
            username = data.request.get("requestedBy_username", "Someone")
            message = f"{username} requested {data.subject}"
            await send_chat(message)
            return {"status": "ok"}
        case _:
            print(data)
            await send_chat("Something just happened within Jellyseerr, check logs!")
            return {"status": "unknown type"}

@app.post("/radarr-webhook")
async def radarr_webhook(request: Request, data: RadarrData):
    match data.eventType:
        case "Grab":
            await send_chat(f"{data.movie.get('title')}, {data.movie.get('year')} started downloading in {data.release.get('quality')}")
        case _:
            print(data)
            await send_chat("Something just happened within Radarr, check logs!")
            return {"status": "unknown type"}
    
@app.post("/prowlarr-webhook")
async def prowlarr_webhook(request: Request, data: ProwlarrData):
    print(data)
    match data.eventType:
        case "Health":
            await send_chat(f"Prowlarr: {data.message}")
        case "HealthRestored":
            await send_chat("Indexer status restored")
        case _:
            await send_chat("Something just happened within Prowlarr, check logs!")
    
@app.post("/sonarr-webhook")
async def sonarr_webhook(request: Request, data: SonarrData):
    print(data)
    await send_chat("Something just happened within Sonarr, check logs!")

@app.post("/change-webhook")
async def change_webhook(data: ChangeData):
    await send_chat(f"{data.message} changed!")

@app.post("/uptime-webhook")
async def uptime_kuma(data: UptimeKuma):
    print(data)
    await send_chat("Something just happened within Uptime Kuma, check logs!")
    
@app.post("/custom-webhook")
async def custom_webhook(data: CustomData):
    print(data.message)