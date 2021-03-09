import os
import json
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import requests
import uuid
from random import randint
from math import floor

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

# config containing SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI
#   SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
with open('config.json') as f:
  config = json.load(f)

# list of 10000 words hosted by MIT
word_response = requests.get('https://www.mit.edu/~ecprice/wordlist.10000')
# store 10000 words in a list
WORDS = word_response.content.splitlines()

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=config['SPOTIPY_CLIENT_ID'],
        client_secret=config['SPOTIPY_CLIENT_SECRET'],
        redirect_uri=config['SPOTIPY_REDIRECT_URI'],
        scope='user-read-playback-state,user-modify-playback-state',
        cache_handler=cache_handler,
        show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('authorize.html', auth_url=auth_url)

    # Step 4. Signed in, ready to play random song
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # Shows playing devices
    res = spotify.devices()
    if res['devices']:
        # spotify.start_playback(uris=find_random_song(spotify))
        return render_template('index.html')
    else:
        return render_template('open_app.html')


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


def find_random_song(spotify):
    random_index = randint(0, 9999)
    search_result = spotify.search(q=WORDS[random_index].decode('utf-8'), limit=50, type='track')

    random_offset = randint(0, floor(search_result['tracks']['total'] / 50)) % 950
    search_result = spotify.search(q=WORDS[random_index].decode('utf-8'), limit=50, offset=random_offset, type='track')

    return [search_result['tracks']['items'][randint(0, len(search_result['tracks']['items']) - 1)]['uri']]