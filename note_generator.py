import librosa
import numpy as np
import json


def analyze_song(song_path):
    # Load the song
    y, sr = librosa.load(song_path)

    # Extract BPM and beat frames
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Convert beat frames to time
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    return tempo, beat_times


def map_beats_to_notes(beat_times, lanes=4):
    # Create a list of notes
    notes = []

    for beat_time in beat_times:
        # Randomly assign a lane for each beat
        lane = np.random.randint(0, lanes)
        notes.append((lane, beat_time))

    return notes


def save_notes_to_file(notes, output_file):
    with open(output_file, 'w') as f:
        json.dump(notes, f)


def generate_note_path(song_path, output_file):
    tempo, beat_times = analyze_song(song_path)
    notes = map_beats_to_notes(beat_times)
    save_notes_to_file(notes, output_file)
    print(f"Generated note path for {song_path} and saved to {output_file}")


if __name__ == "__main__":
    song_path = "Tough Times - Jeremy Korpas.mp3"
    output_file = "notes_song1.json"
    generate_note_path(song_path, output_file)