from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os

app = FastAPI()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://127.0.0.1/callback")

@app.get("/login")
def login():
    print("@@@@ here login @@@@")
    return RedirectResponse(
        url=f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=auto&scope=activity:read"
    )

@app.get("/callback")
def callback(request: Request, code: str):
    # Strava에 토큰 요청
    token_res = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    })
    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return JSONResponse(content={"error": "Failed to get access token"}, status_code=400)

    # 30일 전 타임스탬프 계산
    thirty_days_ago = datetime.now() - timedelta(days=30)
    after_timestamp = int(thirty_days_ago.timestamp())

    # 활동 정보 요청 (30일 이후)
    activities_res = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            "after": after_timestamp
        }
    )

    activities = activities_res.json()

    print(f"@@ activities : {activities}")

    return JSONResponse(content={"activities": activities})
