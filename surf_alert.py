import requests
from datetime import datetime
import os

# --- Configuration ---
LAT = 31.958336
LON = 34.625015
IFTTT_KEY = os.getenv("IFTTT_KEY")  # Set in GitHub Actions or .env
IFTTT_EVENT = "surf_alert"
WAVE_MIN = 0.6       # meters
PERIOD_MIN = 6       # seconds

def fetch_forecast():
    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={LAT}&longitude={LON}"
        "&hourly=wave_height,swell_wave_period"
        "&timezone=auto"
    )
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def find_good_times(data):
    times = data["hourly"]["time"]
    heights = data["hourly"]["wave_height"]
    periods = data["hourly"]["swell_wave_period"]

    good = []
    for t, h, p in zip(times, heights, periods):
        if h > WAVE_MIN and p > PERIOD_MIN:
            local_time = datetime.fromisoformat(t).strftime("%a %H:%M")
            good.append(f"{local_time} — 🌊 {h:.2f}m, ⏱ {p:.1f}s")
    return good

def send_ifttt_alert(messages):
    if not messages:
        print("No good surf conditions found.")
        return

    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}"
    body = {"value1": "\n".join(messages)}
    res = requests.post(url, json=body)
    if res.status_code == 200:
        print("✅ IFTTT alert sent!")
    else:
        print(f"❌ IFTTT error: {res.status_code}\n{res.text}")

def main():
    try:
        forecast = fetch_forecast()
        good_slots = find_good_times(forecast)
        send_ifttt_alert(good_slots)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()