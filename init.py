import os
import json

with open('config.json') as f:
  config = json.load(f)

os.system('set FLASK_APP=app.py')
os.system('set SPOTIPY_CLIENT_ID=' + config['SPOTIPY_CLIENT_ID'])
os.system('set SPOTIPY_CLIENT_SECRET=' + config['SPOTIPY_CLIENT_SECRET'])
os.system('set SPOTIPY_REDIRECT_URI=' + config['SPOTIPY_REDIRECT_URI'])
