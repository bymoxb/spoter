# 🎧 Song Classifier with Spotify + AI (Ollama)

A Python tool to classify songs from Spotify playlists using language models running with Ollama.

It allows analyzing multiple playlists, applying custom criteria through prompts, and optionally creating or modifying playlists based on the results.

---

## 🚀 Features

- Song classification using AI models
- Support for multiple input playlists
- Fully configurable prompts
- Integration with the Spotify API
- Detailed process logging
- Allows:
  - Analyzing playlists without modifying them
  - Creating playlists with classified songs
  - Removing songs from source playlists

---

## 📦 Installation

It is recommended to use a virtual environment:

```sh
python -m venv venv

# Linux / Mac  
source venv/bin/activate

# Windows  
venv\Scripts\activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment variables

```sh
cp .env.example .env
```

### 2. Environment variables description

| Variable                | Description                                                                                                               | Optional | Default value                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------- |
| `SPOTIFY_REDIRECT_URI`  | URL used for Spotify authentication redirect flow                                                                         | Required | `http://127.0.0.1:8888/callback`                        |
| `SPOTIFY_CLIENT_ID`     | Spotify client ID                                                                                                         | Required | (replace with your app's real ID)                       |
| `SPOTIFY_CLIENT_SECRET` | Spotify client secret                                                                                                     | Required | (replace with your app's real secret)                   |
| `SPOTIFY_PLAYLIST_IDS`  | List of Spotify playlist IDs.<br>Used as input sources for songs to classify.                                             | Required | (comma-separated)                                       |
| `SPOTIFY_PLAYLIST_ID`   | Destination Spotify playlist ID.<br>Approved songs will be added here.<br>Required if using the `--push-to-playlist` flag | Optional | (replace with your playlist ID)                         |
| `OLLAMA_MODEL`          | AI model used for song classification                                                                                     | Required | (replace with actual model name)                        |
| `AUDIO_DB_API`          | API used to fetch artist metadata                                                                                         | Optional | `https://www.theaudiodb.com/api/v1/json/123/search.php` |

---

### 3. Prompt configuration

```sh
cp prompts.json.example prompts.json
```

Define in this file the criteria that the model will use to classify songs.

---

## ▶️ Usage

### 🔍 Analysis mode (default)

```sh
python main.py
```

- Does not make any changes in Spotify
- Only generates log files with classification results

---

### ➕ Create playlist with classified songs

Create songs in a specific playlist:

```sh
python main.py --spotify-playlist-id <playlist_id>
```

Or use the environment variable defined in `.env`:

```sh
python main.py --push-to-playlist
```

---

### ➖ Remove songs from source playlist

Remove songs from the source playlist that met the criteria:

```sh
python main.py --remove-from-origin --spotify-playlist-id <playlist_id>
```

Or:

```sh
python main.py --remove-from-origin --push-to-playlist
```

---

## 🧠 How it works

1. Loads credentials from `.env`
2. Loads the prompt from `prompts.json`
3. Retrieves songs from configured playlists
4. (Optional) Enriches data using an external API
5. Runs the AI model with Ollama
6. Classifies each song
7. Saves results into output files
8. (Optional) Modifies playlists based on used flags

---

## 📄 Generated logs

- `raw_tracks.log` → Original Spotify data
- `tracks.log` → Songs used by the model for classification
- `tracks_approved.log` → Songs approved by the model
- `tracks_not_approved.log` → Songs not approved

---

## 🔌 Requirements

- Valid Spotify credentials
- Model available in Ollama
- Configured `prompts.json` file
- Input playlist IDs

Optional:

- TheAudioDB API to enrich metadata

---

## 📜 License

This project is licensed under the MIT License.

---

## 🧪 Note

The classification quality directly depends on:
- The model used in Ollama
- The prompt design

It is recommended to experiment with different prompts to achieve better results.
