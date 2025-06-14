import requests
import datetime
import os

SURFLINE_URL = "https://services.surfline.com/kbyg/spots/forecasts/wave"
SPOT_ID = "584204204e65fad6a7709aaf"
DAYS = 3
THRESHOLDS = {"wave": 0.6, "period": 6, "score": 1}

IFTTT_KEY = os.getenv("IFTTT_KEY")
IFTTT_EVENT = "surf_alert"

def fetch_forecast():
    params = {
        "spotId": SPOT_ID,
        "days": DAYS,
        "intervalHours": 6,
        "maxHeights": "false"
    }
    res = requests.get(SURFLINE_URL, params=params)
    res.raise_for_status()
    return res.json()

def find_good_slots(data):
    good = []
    for item in data.get("data", {}).get("wave", []):
        wave_max = item["surf"]["raw"]["max"]
        score = item["surf"]["optimalScore"]
        period_ok = any(s.get("period", 0) > THRESHOLDS["period"] for s in item["swells"])
        if wave_max > THRESHOLDS["wave"] and score > THRESHOLDS["score"] and period_ok:
            t = datetime.datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M")
            good.append(f"{t}: 🌊 {wave_max:.2f}m | period > 6s | score {score}")
    return good

def send_ifttt(good_slots):
    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}"
    body = {"value1": "\n".join(good_slots)}
    r = requests.post(url, json=body)
    print("✅ Alert sent" if r.ok else f"❌ Failed: {r.status_code}")

def main():
    try:
        forecast = fetch_forecast()
        good = find_good_slots(forecast)
        if good:
            send_ifttt(good)
        else:
            print("No good conditions today.")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()