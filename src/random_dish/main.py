import os
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .google_maps_wrapper import GoogleMap

app = FastAPI()

gmaps = GoogleMap()

try:
    port: str = os.environ["PORT"]
    print(port)
except KeyError:
    print("API_KEY doesn't exist")
    raise KeyError

# CORS setting
origins = [
    # Add 100 to env.port by using `heroku local`
    f"http://localhost:{int(port)+100}",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/apikey")
async def get_api() -> dict:
    apikey: str = GoogleMap.get_apikey()
    return {"apikey": apikey}


@app.get("/geolocate")
async def get_geolocate() -> dict:
    result = gmaps.get_current_locate()
    return result["location"]


@ app.get("/places/nearby")
async def get_search_nearby_result(
        lat: float, lng: float, radius: int = 1000, open_now: bool = False
):
    fields = {
        "location": tuple([lat, lng]),
        "radius": radius,
        "open_now": open_now
    }
    result = gmaps.search_nearby(fields)

    selected_places = random.sample(result, 2)

    places = []
    for place in selected_places:
        place_detail = gmaps.get_place_detail(place["place_id"])
        place_detail["photos"] = [
            "data:image/jpeg;base64,"
            f"{gmaps.get_place_photo(photo['photo_reference'])}"
            for photo in place_detail["photos"][0:3]
        ]
        places.append(place_detail)

    return {"results": places}