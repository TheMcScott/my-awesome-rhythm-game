import json

def parse_song_file(filepath):
    with open(filepath, 'r') as f:
        notes = json.load(f)
    return notes