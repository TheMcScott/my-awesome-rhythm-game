import pygame
import sys
from song_parser import parse_song_file

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NOTE_HEIGHT = 50  # Increased height to reflect leniency
NOTE_SPEED = 5
HIT_WINDOW = 50  # Increased leniency for hit detection
FLASH_DURATION = 100  # Flash duration in milliseconds
COLLECTOR_FLASH_DURATION = 200  # Collector flash duration in milliseconds

# Colors
COLOR_BACKGROUND = (63, 0, 63)
COLOR_NOTE = (255, 128, 255)
COLOR_HIT = (255, 255, 255)
COLOR_MISS = (255, 0, 0)
COLOR_OUTLINE = (255, 0, 0)
COLOR_FLASH = (75, 0, 75)
COLOR_COLLECTOR_FLASH = (0, 0, 255)  # Color for lane collector flash

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rhythm Game")

# List of songs and their note files
songs = [
    {'title': 'Song 1', 'file': 'Tough Times - Jeremy Korpas.mp3', 'notes': 'notes_song1.json'},
    {'title': 'Song 2', 'file': 'song2.mp3', 'notes': 'notes_song2.json'},
    {'title': 'Song 3', 'file': 'song3.mp3', 'notes': 'notes_song3.json'}
]

# Note class
class Note:
    def __init__(self, lane, y):
        self.lane = lane
        self.y = y
        self.hit = False
        self.hit_time = None

    def update(self, current_time):
        self.y += NOTE_SPEED
        if self.hit and current_time - self.hit_time > FLASH_DURATION:
            self.hit = False

    def draw(self, screen, width, height, current_time):
        lane_width = width // 4
        x = self.lane * lane_width
        color = COLOR_HIT if self.hit else COLOR_NOTE
        pygame.draw.rect(screen, color, (x, self.y, lane_width, NOTE_HEIGHT))

    def is_active(self, height):
        return self.y < height

# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True
    in_menu = True
    selected_song = 0
    notes = []
    score = 0
    hit_feedback = None
    feedback_time = 500  # Feedback display time in milliseconds
    last_feedback_time = 0
    flash_time = 0
    collector_flash_times = [0, 0, 0, 0]  # Flash times for each lane collector

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if in_menu:
                    if event.key == pygame.K_DOWN:
                        selected_song = (selected_song + 1) % len(songs)
                    elif event.key == pygame.K_UP:
                        selected_song = (selected_song - 1) % len(songs)
                    elif event.key == pygame.K_RETURN:
                        note_file = songs[selected_song]['notes']
                        notes_data = parse_song_file(note_file)
                        notes = [Note(lane, -NOTE_HEIGHT) for lane, beat_time in notes_data]
                        current_time_slice = 0
                        last_beat_time = current_time  # Get the current time in milliseconds
                        score = 0

                        # Calculate the beat interval based on BPM (using a default BPM for now)
                        BPM = 120  # Default BPM, you can adjust this or retrieve it from the song analysis
                        beat_interval = 60000 / BPM  # Calculate the interval between beats in milliseconds

                        in_menu = False
                else:
                    if event.key == pygame.K_a:
                        score, hit_feedback, flash_time = check_hit(0, notes, score, screen.get_height(), current_time)
                        collector_flash_times[0] = current_time
                    elif event.key == pygame.K_s:
                        score, hit_feedback, flash_time = check_hit(1, notes, score, screen.get_height(), current_time)
                        collector_flash_times[1] = current_time
                    elif event.key == pygame.K_d:
                        score, hit_feedback, flash_time = check_hit(2, notes, score, screen.get_height(), current_time)
                        collector_flash_times[2] = current_time
                    elif event.key == pygame.K_f:
                        score, hit_feedback, flash_time = check_hit(3, notes, score, screen.get_height(), current_time)
                        collector_flash_times[3] = current_time
                    elif event.key == pygame.K_ESCAPE:
                        in_menu = True
                    last_feedback_time = current_time

        if not in_menu:
            # Game logic goes here
            if current_time_slice < len(notes) and current_time - last_beat_time >= beat_interval:
                notes[current_time_slice].y = 0
                current_time_slice += 1
                last_beat_time = current_time

            # Update notes
            for note in notes:
                note.update(current_time)

            # Remove inactive notes
            notes = [note for note in notes if note.is_active(screen.get_height())]

        # Draw everything
        if current_time - flash_time < FLASH_DURATION:
            screen.fill(COLOR_FLASH)  # Flash the screen
        else:
            screen.fill(COLOR_BACKGROUND)  # Clear screen with black
        width, height = screen.get_size()
        lane_width = width // 4

        if in_menu:
            font = pygame.font.Font(None, 36)
            title_text = font.render("Select a Song", True, (255, 255, 255))
            screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 100))
            for index, song in enumerate(songs):
                color = (255, 255, 255) if index == selected_song else (100, 100, 100)
                song_text = font.render(song['title'], True, color)
                screen.blit(song_text, (width // 2 - song_text.get_width() // 2, 150 + index * 40))
        else:
            # Draw target outlines
            for lane in range(4):
                x = lane * lane_width
                if current_time - collector_flash_times[lane] < COLLECTOR_FLASH_DURATION:
                    collector_color = COLOR_COLLECTOR_FLASH
                else:
                    collector_color = COLOR_OUTLINE
                pygame.draw.rect(screen, collector_color, (x, height - NOTE_HEIGHT, lane_width, NOTE_HEIGHT), 2)

            # Draw notes
            for note in notes:
                note.draw(screen, width, height, current_time)

            # Display hit/miss feedback
            if hit_feedback and current_time - last_feedback_time < feedback_time:
                feedback_color = COLOR_HIT if hit_feedback == "Hit" else COLOR_MISS
                feedback_text = hit_feedback
                font = pygame.font.Font(None, 36)
                text = font.render(feedback_text, True, feedback_color)
                screen.blit(text, (10, 10))  # Display feedback at the top-left corner

        pygame.display.flip()  # Update the display

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

def check_hit(lane, notes, score, screen_height, current_time):
    for note in notes:
        if note.lane == lane and screen_height - NOTE_HEIGHT - HIT_WINDOW <= note.y <= screen_height:
            note.hit = True
            note.hit_time = current_time
            score += 100
            print(f"Hit! Score: {score}")
            return score, "Hit", current_time  # Return current time for flash
    score -= 50  # Penalty for miss
    print(f"Miss! Score: {score}")
    return score, "Miss", 0  # Return 0 for no flash

if __name__ == "__main__":
    main()