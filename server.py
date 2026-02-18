from flask import Flask, send_from_directory, jsonify
import feedparser
import time
import os

app = Flask(__name__)

# --- CONFIG (you can edit these later safely) ---
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
}
MAX_ITEMS_PER_SOURCE = 6
CACHE_SECONDS = 60
# -----------------------------------------------

_cache = {"ts": 0, "items": []}

def fetch_news():
    items = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
            title = getattr(entry, "title", "").strip()
            if title:
                items.append({"source": source, "title": title})
    return items

@app.route("/")
def panel():
    return send_from_directory(".", "panel.html")

@app.route("/ticker")
def ticker():
    return send_from_directory(".", "ticker.html")

@app.route("/api/news")
def api_news():
    now = time.time()
    if (now - _cache["ts"]) > CACHE_SECONDS:
        _cache["items"] = fetch_news()
        _cache["ts"] = now
    return jsonify({
        "updated_epoch": int(_cache["ts"]),
        "items": _cache["items"],
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
