# 🎧 Clasificador de canciones con Spotify + IA (Ollama)

Herramienta en Python para clasificar canciones de playlists de Spotify utilizando modelos de lenguaje ejecutados con Ollama.

Permite analizar múltiples playlists, aplicar criterios personalizados mediante prompts y opcionalmente crear o modificar playlists en base a los resultados.

---

## 🚀 Características

- Clasificación de canciones usando modelos de IA  
- Soporte para múltiples playlists de entrada  
- Prompts completamente configurables  
- Integración con la API de Spotify  
- Generación de logs detallados del proceso  
- Permite:
  - Analizar playlists sin modificarlas
  - Crear playlists con canciones clasificadas
  - Eliminar canciones desde playlists de origen

---

## 📦 Instalación

Se recomienda utilizar un entorno virtual:

```sh
python -m venv venv

# Linux / Mac  
source venv/bin/activate

# Windows  
venv\Scripts\activate
```

Instalar dependencias:

```sh
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### 1. Variables de entorno

```sh
cp .env.example .env
```

### 2. Descripción de variables de entorno

| Variable | Descripción | Opcional | Valor por defecto |
|---|---|---|---|
| `SPOTIFY_REDIRECT_URI` | Dirección URL para redireccionar el flujo de autenticación de Spotify | Obligatorio | `http://127.0.0.1:8888/callback` |
| `SPOTIFY_CLIENT_ID` | Identificador del cliente de Spotify | Obligatorio | (reemplazar con el ID real de tu aplicación) |
| `SPOTIFY_CLIENT_SECRET` | Secreto del cliente de Spotify | Obligatorio | (reemplazar con la clave secreta real de tu aplicación) |
| `SPOTIFY_PLAYLIST_IDS` | Lista de identificadores de las playlists de Spotify.<br>De donde se obtendran la lista de canciones para clasificar. | Obligatorio | (separados por comas) |
| `SPOTIFY_PLAYLIST_ID` | Identificador de la playlist de destino de Spotify.<br>En esta playlist se agregaran las canciones que cumplen el criterio del modelo.<br>Es requerida si se utiliza el flag `--push-to-playlist` | Opcional | (reemplazar con el ID de tu playlist) |
| `OLLAMA_MODEL` | Modelo de IA utilizado para clasificar las canciones | Obligatorio | (reemplazar con el nombre del modelo real de IA) |
| `AUDIO_DB_API` | API utilizada para obtener metadatos de artistas | Opcional | `https://www.theaudiodb.com/api/v1/json/123/search.php` |


---

### 3. Configuración del prompt

```sh
cp prompts.json.example prompts.json
```

Define en este archivo los criterios que utilizará el modelo para clasificar las canciones.

---

## ▶️ Uso

### 🔍 Modo análisis (por defecto)

```sh
python main.py
```

- No realiza ningún cambio en Spotify  
- Solo genera archivos de logs con los resultados de clasificación  

---

### ➕ Crear playlist con canciones clasificadas

Crear canciones en una playlist específica:

```sh
python main.py --spotify-playlist-id <playlist_id>
```

O usar la variable de entorno definida en `.env`:

```sh
python main.py --push-to-playlist
```

---

### ➖ Eliminar canciones de la playlist de origen

Eliminar canciones de la playlist de origen que cumplieron el criterio:

```sh
python main.py --remove-from-origin --spotify-playlist-id <playlist_id>
```

O:

```sh
python main.py --remove-from-origin --push-to-playlist
```

---

## 🧠 Funcionamiento

1. Carga las credenciales desde `.env`  
2. Carga el prompt desde `prompts.json`  
3. Obtiene canciones desde las playlists configuradas  
4. (Opcional) Enriquece los datos usando una API externa  
5. Ejecuta el modelo de IA con Ollama  
6. Clasifica cada canción  
7. Guarda resultados en archivos de salida  
8. (Opcional) Modifica playlists según flags utilizados  

---

## 📄 Logs generados

- `raw_tracks.log` → Información original de Spotify
- `tracks.log` → Listas de canciones que utiliza el modelo para la clasificación
- `tracks_approved.log` → Canciones aprobadas por el modelo
- `tracks_not_approved.log` → Canciones no aprobadas

---

## 🔌 Requisitos

- [Credenciales válidas de Spotify](http://developer.spotify.com/documentation/web-api/)
- Modelo disponible en Ollama  
- Archivo `prompts.json` configurado  
- IDs de playlists de entrada  

Opcional:

- API de [TheAudioDB](https://www.theaudiodb.com/free_music_api/) para enriquecer metadatos  

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT.

---

## 🧪 Nota

La calidad de la clasificación depende directamente de:
- El modelo utilizado en Ollama  
- El diseño del prompt  

Se recomienda experimentar con distintos prompts para obtener mejores resultados.
