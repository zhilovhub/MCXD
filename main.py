import requests

with open("index.html", "w", encoding="utf-8") as f:
    f.write(requests.get("https://garantex.io/trading/usdtrub").text)
