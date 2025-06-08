# test_client.py (local testing script)
import base64
import requests

url = "http://localhost:8000/process/"
data = {"url": "https://en.wikipedia.org/wiki/Natural_language_processing"}
response = requests.post(url, json=data)

if response.ok:
    result = response.json()
    for topic_id, img_data in result['wordclouds'].items():
        with open(f"wordcloud_{topic_id}.png", "wb") as f:
            f.write(base64.b64decode(img_data))
else:
    print("Error:", response.text)