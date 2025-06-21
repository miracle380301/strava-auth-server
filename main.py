from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import requests
import os

app = FastAPI()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REPLIT_BACKEND_URL = os.getenv("REPLIT_BACKEND_URL")
REPLIT_FRONT_URL = os.getenv("REPLIT_FRONT_URL")

@app.get("/login")
def login():
    print("@@@@ [Render] login @@@@")
    redirect_url = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=auto&scope=activity:read"
    print(f"@@@@ [Render] : {redirect_url}")
    return RedirectResponse(
        url= redirect_url
    )

@app.get("/callback")
def callback(code: str):
    print("@@@@ [Render] callback @@@@")
    token_res = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    })
    token_data = token_res.json()
    access_token = token_data.get("access_token")
    athlete_id = None
    if "athlete" in token_data:
        athlete_id = token_data["athlete"].get("id")    
    print(f"@@@@ [Render] : access_token :  {access_token}")
    print(f"@@@@ [Render] : athlete_id :  {athlete_id}")

    if not access_token:
        return {"error": "Failed to get access token"}

    # Replit 백엔드로 토큰 전달 (POST)
    send_res = requests.post(REPLIT_BACKEND_URL, json={"access_token": access_token, "athlete_id": athlete_id})

    if send_res.status_code != 200:
        return {"error": "Failed to send token to backend"}

    params = urlencode({"athlete_id": athlete_id})
    redirect_url_with_param = f"{REPLIT_FRONT_URL}?{params}"


    # 프론트엔드로 리다이렉트 (예: 로그인 성공 페이지)
    return RedirectResponse(redirect_url_with_param)
