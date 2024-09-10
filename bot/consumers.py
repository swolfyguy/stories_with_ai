# myapp/consumers.py
import json
import requests
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    headers = settings.TMDB_HEADERS
    base_url = settings.TMDB_BASE_URL

    async def get_top_rated_movies(self):
        region = ["IN", "US", "GB"]
        region = random.choice(region)
        page = random.randint(1, 20)
        movie = random.randint(1, 15)
        url = f"{self.base_url}/movie/top_rated?language=en-US&page={page}&region={region}"

        response = requests.get(url, headers=self.headers)
        resp = response.json()
        movie = resp.get("results")[movie]
        print("Resukt", movie)
        resp = """Hey there, welcome back, <br>Here is the today's movie recommndation<br><b>Title:</b> {} <br> <b>Ratings:</b> {} <br>
        <b>Overview:</b> {}""".format(
            movie.get("original_title"),
            movie.get("vote_average"),
            movie.get("overview"),
        )

        return resp

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send message to room group
        msg = await self.get_top_rated_movies()
        print("MSF", msg)
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": msg},
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat_message", "message": message}
        # )
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "get_response", "message": message}
        )

    def format_response(self, message):
        message = """<div class="alert alert-primary" role="alert"> <b>Bot:</b> {}</div>""".format(
            message
        )
        return message

    async def chat_message(self, event):
        message = event["message"]
        message = """<div class="alert alert-primary" role="alert"> <b>Bot:</b> {}</div>""".format(
            message
        )
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def get_response(self, event):
        from ollama import AsyncClient

        await self.send(
            text_data=json.dumps(
                {"message": self.format_response("<b>***Loading response...***</b>")}
            )
        )
        message = event["message"]
        print("Starting to send the response, message", message)

        message = {"role": "user", "content": f"Answer shortly about {message}"}
        content_out = ""
        async for part in await AsyncClient().chat(
            model="llama3", messages=[message], stream=True
        ):
            data = part["message"]["content"]
            print("DATA==>", data)
            if data in [".", "!", "?", "\n"]:
                await self.send(text_data=json.dumps({"message": content_out + data}))
                content_out = ""
            elif data == "DONE" or not data:
                await self.send(
                    text_data=json.dumps({"message": "<b>***Response completed***</b>"})
                )
                break
            else:
                content_out += data
