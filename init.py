import os
import json

with open('config.json') as f:
  config = json.load(f)

print(config["SPOTIPY_CLIENT_ID"])
