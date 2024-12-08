from json import loads as load_json
from requests import get as requests_get, post as requests_post
from datetime import datetime, timezone
from config.db import messages_collection, locations_collection
from fastapi import FastAPI, Request, HTTPException
from pytz import timezone as pytz_timezone
from models.arr import JellyseerrData, ProwlarrData, RadarrData, SonarrData
from models.bluebubbles import BluebubblesData
from models.change import ChangeData
from models.custom import CustomData
from models.uptime import UptimeKuma
from dotenv import load_dotenv
from os import getenv
from re import sub
from geopy.distance import geodesic

load_dotenv()

BB_ADDRESS = getenv("BB_URL", "http://127.0.0.1:1234")
BB_PASSWORD = getenv("BB_PASSWORD", "password")
MAUBOT_ADDRESS = getenv("MAUBOT_URL", "http://127.0.0.1:29316/_matrix/maubot/plugin/maubotwebhook/send")
AREA_CODE = getenv("AREA_CODE", "+1")
TIMEZONE = getenv("TIMEZONE", "America/New_York")
MATRIX_ID = getenv("MATRIX_ID")

app = FastAPI()

async def query_contact(handle):
    response = requests_get(f'{BB_ADDRESS}/api/v1/contact',
                            params={'password': BB_PASSWORD},
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

async def send_chat(message, room_id):
    if room_id == None or ":" not in room_id or "." not in room_id:
        raise HTTPException(status_code=400, detail="Invalid room_id")
    
    url = MAUBOT_ADDRESS
    room = room_id.lstrip("!")
    headers = {"Content-Type": "application/json"}
    body = {
        "message": message,
        "room_id": f"!{room}"
        }
    requests_post(url, headers=headers, json=body)

@app.post("/bluebubbles-webhook")
async def handle_bluebubbles_webhook(request: Request, data: BluebubblesData):
    if request.headers.get("Content-Type") != "application/json":
        raise HTTPException(status_code=400, detail="Invalid Content-Type")

    match data.type:
        case 'new-message':
            message_data = data.data
            message_guid = message_data.get("guid")
            message_text = message_data.get("guid")
            date_created = message_data.get("guid")
            self_message = message_data.get("guid")

            if self_message:
                return {"status": "ignored"}

            sender_handle = message_data.get("handle").get("address")

            conversation = await messages_collection.find_one({"sender_handle": sender_handle})
            
            if message_data.get("chats") is not None and "chat" in message_data["chats"][0].get("chatIdentifier"):
                group_chat = True
            else:
                group_chat = False
            
            if not conversation:
                await messages_collection.insert_one({
                    "sender_handle": sender_handle,
                    "messages": [
                        {
                            "guid": message_guid,
                            "text": message_text,
                            "timestamp": date_created,
                            "is_unsent": False,
                            "group_chat": group_chat
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
                        "group_chat": group_chat
                    }}}
                )

            return {"status": "ok"}

        case "updated-message":
            message_data = data.data
            self_message = message_data.get("isFromMe")

            if self_message:
                return {"status": "ignored"}
            
            message_guid = message_data.get("guid")
            message_text = message_data.get("text")
            date_unsent = message_data.get("dateEdited")
            sender_handle = message_data.get("handle").get("address")

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
                est_timezone = pytz_timezone(TIMEZONE)
                unsent_est_time = unsent_utc.astimezone(est_timezone)
                formatted_time = unsent_est_time.strftime("%I:%M %p")

                contact_name = await query_contact(sender_handle)
                original_text = message["text"]
                
                unsent_message = f'{contact_name} unsent "{original_text}" at {formatted_time}'
                
                if '"' in original_text and "'" not in original_text:
                    unsent_message = f"{contact_name} unsent '{original_text}' at {formatted_time}", MATRIX_ID
                
                await send_chat(unsent_message, MATRIX_ID)
                
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

        case "new-findmy-location":
            handle = data.data.get("handle")
            past_location = await locations_collection.find_one({"handle": handle},
                                                                {"_id": 1})
            last_updated = data.data.get("last_updated")
            coordinates = data.data.get("coordinates")
            latitude = coordinates[0]
            longitude = coordinates[1]

            if past_location is None:
                document = {
                    "handle": handle,
                    "location": [latitude, longitude],
                    "last_updated": last_updated
                    }
                await locations_collection.insert_one(document)
            else:
                await locations_collection.update_one(
                    {"handle": handle},
                    {"$set": {
                        "location": [latitude, longitude],
                        "last_updated": last_updated
                        }
                     }
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
            message = data.message
            await send_chat(message, MATRIX_ID)
            return {"status": "ok"}
        case "MEDIA_PENDING":
            username = data.request.requestedBy_username
            media = data.subject
            
            if username == None:
                username = "Someone"
                
            message = f"{username} requested {media}, pending approval"
            await send_chat(message, MATRIX_ID)
            return {"status": "ok"}
        case "MEDIA_AUTO_APPROVED":
            username = data.request.requestedBy_username
            media = data.subject
            
            if username == None:
                username = "Someone"
                
            message = f"{username} requested {media}"
            await send_chat(message, MATRIX_ID)
            return {"status": "ok"}
        case "MEDIA_AVAILABLE":
            media = data.subject
            message = f"{media} is now available"
            await send_chat(message, MATRIX_ID)
        case _:
            print(data)
            await send_chat("Something just happened within Jellyseerr, check logs!", MATRIX_ID)
            return {"status": "unknown type"}

@app.post("/radarr-webhook")
async def radarr_webhook(data: RadarrData):
    match data.eventType:
        case "Grab":
            title = data.movie.title
            year = data.movie.year
            quality = data.release.quality
            message = f"{title} ({year}) started downloading in {quality}"
            await send_chat(message, MATRIX_ID)
        case "Download":
            title = data.movie.title
            year = data.movie.year
            quality = data.movieFile.quality
            message = f"{title} ({year}) is now available in {quality}"
            await send_chat(message, MATRIX_ID)
        case _:
            print(data)
            message = "Something just happened within Radarr, check logs!"
            await send_chat(message, MATRIX_ID)
            return {"status": "unknown type"}

@app.post("/prowlarr-webhook")
async def prowlarr_webhook(data: ProwlarrData):
    match data.eventType:
        case "Health":
            message = f"Prowlarr: {data.message}"
            await send_chat(message, MATRIX_ID)
        case "HealthRestored":
            message = "Prowlarr indexer status restored"
            await send_chat(message, MATRIX_ID)
        case _:
            print(data)
            message = "Something just happened within Prowlarr, check logs!"
            await send_chat(message, MATRIX_ID)

@app.post("/sonarr-webhook")
async def sonarr_webhook(data: SonarrData):
    print(data)
    message = "Something just happened within Sonarr, check logs!"
    await send_chat(message, MATRIX_ID)

@app.post("/change-webhook")
async def change_webhook(data: ChangeData):
    changed_site = data.message
    message = f"{changed_site} changed!"
    await send_chat(message, MATRIX_ID)

@app.post("/uptime-webhook")
async def uptime_kuma(data: UptimeKuma):
    print(data)
    message = "Something just happened within Uptime Kuma, check logs!"
    await send_chat(message, MATRIX_ID)

@app.post("/custom-webhook")
async def custom_webhook(data: CustomData):
    if data.room_id is not None:
        send_chat(data.message, data.room_id)
    else:
        send_chat(data.message, MATRIX_ID)

@app.get("/bluebubbles-location/{handle}")
async def location_request(handle: str):
    past_location = await locations_collection.find_one({"handle": handle})
    if past_location is not None and past_location.get("last_updated") is not None:
        last_updated = past_location["last_updated"] / 1000
        last_updated_time = datetime.fromtimestamp(last_updated, tz=timezone.utc)
        current_time = datetime.now(tz=timezone.utc)
        if (current_time - last_updated_time).total_seconds() <= 60:
            return {
                "latitude": past_location["location"][0],
                "longitude": past_location["location"][1],
                "last_updated": past_location["last_updated"]
                }
    
    url = f"{BB_ADDRESS}/api/v1/icloud/findmy/friends?password={BB_PASSWORD}"
    request = requests_get(url)
    json_data = request.json()

    data = json_data.get("data")
    latitude = None
    longitude = None
    last_updated = None

    if data == None:
        raise HTTPException(status_code=504, detail="Data not found")
    
    for person in data:
        person_handle = person.get("handle")
        if handle == person_handle:
            coordinates = person.get("coordinates")
            latitude = coordinates[0]
            longitude = coordinates[1]
            last_updated = person.get("last_updated")

    if latitude == None or longitude == None:
        raise HTTPException(status_code=400, detail="Invalid handle")

    if past_location is None:
        document = {
            "handle": handle,
            "location": [latitude, longitude],
            "last_updated": last_updated
        }
        await locations_collection.insert_one(document)
    else:
        await locations_collection.update_one(
            {"handle": handle},
            {"$set": {
                "location": [latitude, longitude],
                "last_updated": last_updated
            }}
        )
    
    return {
        "latitude": latitude,
        "longitude": longitude,
        "last_updated": last_updated
    }
    
#distance between person and me
@app.get("/bluebubbles-distance")
async def person_distance(handle: str = "", id: str = ""):
    handle_location = await location_request(handle)
    if handle_location is None:
        raise HTTPException(status_code=400, detail="Invalid handle")
    
    handle_latitude = handle_location.get("latitude")
    handle_longitude = handle_location.get("longitude")
    handle_coordinates = (handle_latitude, handle_longitude)
    
    url = f"{BB_ADDRESS}/api/v1/icloud/findmy/devices?password={BB_PASSWORD}"
    request = requests_get(url)
    json_data = request.json()
    data = json_data.get("data")

    for device in data:
        name = device.get("name")
        if name == id:
            location = device.get("location")
            latitude = location.get("latitude")
            longitude = location.get("longitude")
        
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Invalid device")
    
    my_coordinates = (latitude, longitude)
                
    distance = geodesic(handle_coordinates, my_coordinates)
    distance_km = distance.km
    distance_miles = distance.miles
    
    return {
        "miles": distance_miles,
        "km": distance_km
    }