# Webhook

Track unsent iMessages.
Get notified for pending or successful Jellyseerr requests.
Receive notifications when Radarr downloads start or are completed.
Alerts when Prowlarr proxies disconnect or are restored.


Webhook is still in active development, but I use it every day!

## Pre-requisites
- A Maubot instance with the [Webhook plugin](https://github.com/jkhsjdhjs/maubot-webhook) installed
- A working [BlueBubbles Server](https://bluebubbles.app/downloads/server/) to track unsent messages (optional)
- A MongoDB collection (optional, only needed for tracking unsent messages)
    - You can create a free MongoDB account and configure a shared instance, or self- host.
-  Docker and Docker Compose for easier deployment
    - Alternatively, you can deploy the application manually. I will not be able to offer support for alternative deployment, but you can find instructions provided by FastAPI for [cloud deployment](https://fastapi.tiangolo.com/deployment/cloud/) or [running a server manually](https://fastapi.tiangolo.com/deployment/manually/).
    - Python 3.12 is required for manual deployment.
- If you use Coolify and link this repository, you can skip steps 2, 3, 5, and 6. It will also automatically update. This is the option I recommend the most!
## Installation
1. Set up `maubotwebhook` to use the configuration below. We'll leave authentication blank since we won't be exposing the Maubot instance.

    ```
    path: /send
    method: POST
    room: '{{ json.room_id }}'
    message: '{{ json.message }}'
    message_format: plaintext
    auth_type:
    auth_token:
    force_json: true
    ignore_empty_messages: true
    ```

2. Clone the repository
    ```
    git clone https://github.com/mehapps/webhook
    ```

3. Navigate into the repository
    ```
    cd webhook
    ```

4. Create a `.env` file with:
    - `ATLAS_URI` (this should be your MongoDB connection string, and should be URL encoded)
    - `MAUBOT_URL` (this should be your base URL)
    - `MATRIX_ID` (this should be your Matrix room ID)
    - `BB_URL` (optional - this should be your BlueBubbles base URL, needed if you're using BlueBubbles)
    - `BB_PASSWORD` (optional - this should be your BlueBubbles password, needed if you're using BlueBubbles)
    - `AREA_CODE` (this is optional and will default to +1, only needed if you're using BlueBubbles)
    - `TIMEZONE` (this is optional and will default to America/New_York, only needed if you're using BlueBubbles)  

    Here is an example:
    ```
    AREA_CODE=+1
    ATLAS_URI=mongodb+srv:/your_url
    MATRIX_ID=room:homeserver.tld
    BB_PASSWORD=password
    BB_URL=http://127.0.0.1:1234
    MAUBOT_URL=http://127.0.0.1:29316/_matrix/maubot/plugin/maubotwebhook/send
    TIMEZONE=America/New_York
    ```

5. Build the Docker image:
    ```
    docker compose --pull --env-file .env build .
    ```

6. Start the Docker container:
    ```
    docker compose --env-file .env up -d
    ```

7. If you're using BlueBubbles, create a new Webhook in the `API & Webhooks` section of the BlueBubbles Server settings. Enter the server address and port, followed by `bluebubbles-webhook`. Then make sure to select `New Messages` and `Message Updates`.

    ![Server configuration](./assets/SCR-20241204-200837.png)


## Issues & Suggestions

If you have any issues running the server or have any suggestions, feel free to create an issue and I'll do my best to help you!
I especially want to know what services you'd like to use to receive notifications, so please open an issue/feature request for that!