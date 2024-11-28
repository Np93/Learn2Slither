import yaml
import pygame
from src.game import Game

def load_config(config_file="config.yaml"):
    """Charge la configuration depuis le fichier config.yaml."""
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def main():
    # Charger la configuration
    config = load_config()
    board_size = config.get("board_size", 10)
    speed = config.get("speed", 1)  # Cases par seconde
    display = config.get("display", True)
    victory_condition = config.get("victory_condition", 10)

    # Initialiser le jeu
    game = Game(board_size, display, speed, victory_condition)

    # Boucle principale
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nJeu interrompu.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()