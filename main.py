from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os

app = FastAPI()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REPLIT_BACKEND_URL = os.getenv("REPLIT_BACKEND_URL")

@app.get("/login")
def login():
    print("@@@@ [Render] login @@@@")
    redirect_url = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=auto&scope=activity:read"
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

    if not access_token:
        return {"error": "Failed to get access token"}

    # Replit 백엔드로 토큰 전달 (POST)
    send_res = requests.post(REPLIT_BACKEND_URL, json={"access_token": access_token})

    if send_res.status_code != 200:
        return {"error": "Failed to send token to backend"}

    # 프론트엔드로 리다이렉트 (예: 로그인 성공 페이지)
    frontend_url = "https://your-frontend-url.com/strava-success"
    return RedirectResponse(frontend_url)
