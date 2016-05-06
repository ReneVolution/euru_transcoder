# eurucamp_transcoder #

euru_transcoder is a simple (limited) configurable transcoding application which makes heavily use of FFMPEG - hyper fast audio and video encoder :]

### Prerequisites ####

- FFmpeg binary

### Example usage ###

```
#!bash

python transcode.py http://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4 encoded/ profiles/eurucamp_profiles_mp4hls_only.json
```