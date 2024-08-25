import pygame

class playsfx:
    def sfxplayer(self, mp3_file, volume=100, nofreezeteak=False):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_file)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(volume)
            if not nofreezeteak:
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)  # Check every 10 milliseconds
        except Exception as e:
            print(f"Error occurred: {str(e)}")