import yaml
import pygame
from src.game import Game
from src.q_agent import QLearningAgent

def load_config(config_file="config.yaml"):
    """Charge la configuration depuis le fichier config.yaml."""
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    board_size = config.get("board_size", 10)
    speed = config.get("speed", 1)
    display = config.get("display", True)
    victory_condition = config.get("victory_condition", 10)
    mode = config.get("mode", "player")
    rewards = config["rewards"]
    training_sessions = config["training"]["sessions"]
    model_name = config["model"]["name"]

    # Initialiser les actions et l'agent
    actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    agent = QLearningAgent(board_size, actions, rewards)

    # Initialiser le jeu
    game = Game(board_size, display, speed, victory_condition, mode)

    if mode == "player":
        game.run()
    elif mode == "train":
        for session in range(1, training_sessions + 1):
            game.reset()
            game.run(agent=agent, train=True)
            if session in {1, 10, 100}:
                agent.save_model(f"{model_name}_{session}_sessions.pkl")
    elif mode == "model":
        agent.load_model(model_name)
        game.run(agent=agent, train=False)
    else:
        print("Mode invalide.")

# def main():
#     # Charger la configuration
#     config = load_config()
#     board_size = config.get("board_size", 10)
#     speed = config.get("speed", 1)  # Cases par seconde
#     display = config.get("display", True)
#     victory_condition = config.get("victory_condition", 10)
#     mode = config.get("mode", "player")

#     # Initialiser le jeu
#     game = Game(board_size, display, speed, victory_condition, mode)

#     # Boucle principale
#     try:
#         game.run()
#     except KeyboardInterrupt:
#         print("\nJeu interrompu.")
#     finally:
#         pygame.quit()

if __name__ == "__main__":
    main()