from collections import defaultdict
from dotenv import load_dotenv
from ollama import chat
from ollama import ChatResponse
from spotipy.oauth2 import SpotifyOAuth
import argparse
import json
import os
import requests
import spotipy
import time

load_dotenv()

AUDIO_DB_API = os.getenv(
    "AUDIO_DB_API", "https://www.theaudiodb.com/api/v1/json/123/search.php")

PROMPT_CONFIG_FILE_PATH = "prompts.json"

SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_PLAYLIST_IDS = os.getenv("SPOTIFY_PLAYLIST_IDS").split(",")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

if not SPOTIFY_REDIRECT_URI:
    raise ValueError('SPOTIFY_REDIRECT_URI is required')
if not SPOTIFY_CLIENT_ID:
    raise ValueError('SPOTIFY_CLIENT_ID is required')
if not SPOTIFY_CLIENT_SECRET:
    raise ValueError('SPOTIFY_CLIENT_SECRET is required')
if not SPOTIFY_PLAYLIST_IDS:
    raise ValueError('SPOTIFY_PLAYLIST_IDS is required')
if not OLLAMA_MODEL:
    raise ValueError('OLLAMA_MODEL is required')

if not os.path.exists(PROMPT_CONFIG_FILE_PATH):
    raise ValueError(
        f'A file named {PROMPT_CONFIG_FILE_PATH} must exist in the current directory. You can use prompts.json.example as a reference')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private playlist-modify-public playlist-modify-private",
))


def get_spotify_tracks(playlists, silent=False):
    raw_tracks = []

    for playlist_id in playlists:
        if not silent:
            print("Fetching songs from playlist: " + playlist_id)

        results = sp.playlist_items(playlist_id)

        raw_tracks_per_playlist = []
        raw_tracks_per_playlist.extend(results["items"])

        if not silent:
            print(f"Total songs in playlist: {results['total']}")

        while results["next"]:
            time.sleep(1)
            results = sp.next(results)
            raw_tracks_per_playlist.extend(results["items"])

        for item in raw_tracks_per_playlist:
            item["playlist_id"] = playlist_id

        raw_tracks.extend(raw_tracks_per_playlist)

        time.sleep(1)

    return raw_tracks


def load_prompts():
    with open(PROMPT_CONFIG_FILE_PATH, 'r') as file:
        return json.load(file)


def approved_by_ollama(track):

    try:
        prompt_config = load_prompts()
        messages = []

        if prompt_config["system"] != "":
            messages.append({
                "role": "system",
                "content": prompt_config["system"]
            })

        for prompt in prompt_config["user"]:
            messages.append({
                "role": "user",
                "content": prompt
            })

        messages.append({
            "role": "user",
            "content": json.dumps(track)
        })

        response: ChatResponse = chat(model=OLLAMA_MODEL, messages=messages)

        return "true" in response['message']['content'].strip().lower()

    except:
        return False


def determine_with_ia(tracks):
    tracks_approved = []
    tracks_not_approved = []

    for i, track in enumerate(tracks):
        is_approved = False
        if approved_by_ollama(track):
            tracks_approved.append(track)
            is_approved = True
        else:
            tracks_not_approved.append(track)
            is_approved = False

        print_log_progress(
            tracks, i,
            f"Song {'YES' if is_approved else 'NO'} meets model criteria: {track['name']} - {', '.join(track['artists'])}"
        )

    return tracks_approved, tracks_not_approved


def push_to_playlist(tracks, playlist_id):
    current_tracks = get_spotify_tracks([playlist_id], silent=True)

    current_track_ids = set(
        map(lambda track: track["id"], extract_relevant_data(current_tracks)))

    for i in range(0, len(tracks), 100):

        full_item_ids = list(map(lambda track: track["id"], tracks[i:i+100]))
        items = [item for item in full_item_ids if item not in current_track_ids]

        print(f"Adding unique songs to playlist {playlist_id}: {len(items)}")

        sp.playlist_add_items(
            playlist_id=playlist_id, items=items)


def remove_from_playlist(tracks):
    grouped = {}

    for item in tracks:
        playlist_id = item['playlist_id']
        if playlist_id not in grouped:
            grouped[playlist_id] = []
        grouped[playlist_id].append(item['id'])

    group_items = grouped.items()

    for i, (key, values) in enumerate(group_items):
        print_log_progress(
            group_items, i, f"Removing occurrences from playlist {key}: {len(values)}")
        sp.playlist_remove_all_occurrences_of_items(
            playlist_id=key, items=values)


def extract_relevant_data(raw_tracks):
    tracks = []

    for t in raw_tracks:
        name = t["item"]["name"]
        album = t["item"]["album"]["name"]
        artists = list(
            map(lambda artist: artist["name"], t["item"]["artists"]))

        tracks.append({
            "id": t["item"]["id"],
            "name": name,
            "album": album,
            "playlist_id": t["playlist_id"],
            "artists": artists
        })

    return tracks


def write_logs(data, filename):
    print(f"Saving logfile to: {filename}")
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def print_log_progress(data_list, current_index, text):
    n_digits = len(str(len(data_list)))
    t_size = len(data_list)
    print(f"[ {current_index+1:0{n_digits}d}/{t_size:0{n_digits}d} ] {text}")


def encode_artist_name(artist):
    safe_param = ""

    try:
        safe_param = artist.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, AttributeError) as e:
        try:
            safe_param = requests.utils.quote(artist, safe=' ')
        except Exception as e2:
            safe_param = artist

    return safe_param


def inject_artists_metadata(tracks):
    unique_artists = {
        artist for track in tracks for artist in track["artists"]}

    artist_genres = defaultdict(list)
    artist_country = defaultdict(list)

    print(f"Total artists: {len(unique_artists)}")

    for i, artist in enumerate(unique_artists):
        print_log_progress(unique_artists, i,
                           f"Fetching artist metadata: {artist}")

        if artist in artist_genres and artist_genres[artist]:
            # print(f"Géneros para {artist} ya obtenidos previamente.")
            continue

        try:
            safe_param = encode_artist_name(artist)
            response = requests.get(
                f"{AUDIO_DB_API}?s={safe_param}", timeout=2)
            data = response.json()

            if data.get("artists"):
                artist_data = data["artists"][0]
                _gender = artist_data.get("strGenre")
                _style = artist_data.get("strStyle")
                _country = artist_data.get("strCountry")

                if _gender:
                    artist_genres[artist].append(_gender)
                if _style:
                    artist_genres[artist].append(_style)

                if _country:
                    artist_country[artist].append(_country)

            else:
                print(f"No metadata found for artist: {artist}")

        except Exception:
            print(f"Error fetching metadata for artist: {artist}")

        time.sleep(1)

    # Asignar géneros a los tracks
    for track in tracks:
        _artists_genres = set()
        _artists_country = set()
        for artist in track["artists"]:
            if artist_genres[artist]:
                _artists_genres.update(artist_genres[artist])
            if artist_country[artist]:
                _artists_country.update(artist_country[artist])

        track["artists_genres"] = list(_artists_genres)
        track["artists_country"] = list(_artists_country)

    return tracks


def elapsed_time_str(elapsed_time):
    minutes = elapsed_time // 60
    hours = elapsed_time // 3600
    if elapsed_time < 3600:
        return f"{minutes:.0f} m, {elapsed_time % 60:.2f} s."
    else:
        return (
            f"{hours:.0f} h, "
            f"{(elapsed_time % 3600) // 60:.0f} m, "
            f"{elapsed_time % 60:.2f} s."
        )


def main():

    parser = argparse.ArgumentParser(
        description="Song classifier using LLM model")

    parser.add_argument("--spotify-playlist-id", type=str,
                        help="Playlist ID where classified songs will be added",
                        default=SPOTIFY_PLAYLIST_ID)
    parser.add_argument("--push-to-playlist", action="store_true",
                        help="Add classified songs to the playlist")
    parser.add_argument("--remove-from-origin", action="store_true",
                        help="Remove classified songs from original playlists")

    args = parser.parse_args()

    if args.push_to_playlist and args.spotify_playlist_id is None:
        raise ValueError(
            "When using --push-to-playlist you must provide --spotify-playlist-id or set SPOTIFY_PLAYLIST_ID")

    # -----------------------

    print("Starting song classification process...")
    start_time = time.time()

    raw_tracks = get_spotify_tracks(SPOTIFY_PLAYLIST_IDS)
    tracks = extract_relevant_data(raw_tracks)

    print(f"Total songs: {len(tracks)}")

    tracks = inject_artists_metadata(tracks)
    tracks_approved, tracks_not_approved = determine_with_ia(tracks)

    if args.push_to_playlist:
        push_to_playlist(tracks_approved, args.spotify_playlist_id)

    if args.remove_from_origin:
        remove_from_playlist(tracks_approved)

    end_time = time.time()

    print("--- Logs ---")
    elapsed = end_time - start_time
    print(f"Total approved by model: {len(tracks_approved)}")
    print(f"Total not approved by model: {len(tracks_not_approved)}")
    print(f"Execution time: {elapsed_time_str(elapsed)}")

    write_logs(raw_tracks, "./raw_tracks.log")
    write_logs(tracks, "./tracks.log")
    write_logs(tracks_approved, "./tracks_approved.log")
    write_logs(tracks_not_approved, "./tracks_not_approved.log")


if __name__ == "__main__":
    main()
