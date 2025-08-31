import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

from .path import get_path

# Initialize pygame mixer
pygame.mixer.init()

# Load beep sound if file exists
sound_path = get_path("app/static/sounds/beep.wav")
sound = None

if os.path.exists(sound_path):
    try:
        sound = pygame.mixer.Sound(sound_path)
    except Exception as e:
        print(f"Error loading sound: {e}")
        sound = None
else:
    print(f"Sound file not found: {sound_path}")


async def beep():
    """
    Plays a simple beep sound.
    """
    if sound is not None:
        try:
            sound.play()
        except Exception:
            # Silent failure if unable to play sound
            pass
