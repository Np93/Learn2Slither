import yaml
import pygame
from src.game import Game
from src.q_agent import QLearningAgent

def load_config(config_file="config.yaml"):
    """Charge la configuration depuis config.yaml."""
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def show_lobby(screen, config):
    """
    Affiche le lobby interactif pour choisir le mode et modifier les paramètres.
    Permet aussi de modifier directement le nom du modèle et de gérer les boutons + et -.
    """
    font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 72)

    # Copie des paramètres pour modifications temporaires
    local_config = config.copy()
    local_config["rewards"] = config["rewards"].copy()  # Copie des récompenses pour éviter les conflits

    # Zone de texte pour model_name
    input_active = False  # Suivi de l'état actif/inactif de la zone de texte
    model_name = local_config["model"]["name"]

    def draw_lobby():
        """Dessine le lobby avec les paramètres actuels."""
        screen.fill((0, 0, 0))  # Fond noir

        # Titre
        title_text = title_font.render("Snake RL - Lobby", True, (255, 255, 255))
        screen.blit(title_text, (200, 20))

        # Paramètres affichés
        param_labels = [
            f"Board Size: {local_config['board_size']}",
            f"Speed: {local_config['speed']}",
            f"Victory Length: {local_config['victory_condition']}",
            f"Sessions: {local_config['training']['sessions']}",
            f"Green Apple Reward: {local_config['rewards']['green_apple']}",
            f"Red Apple Reward: {local_config['rewards']['red_apple']}",
            f"Collision Penalty: {local_config['rewards']['collision']}",
            f"Move Penalty: {local_config['rewards']['move_without_eating']}",
            f"Display: {'ON' if local_config['display'] else 'OFF'}"
        ]
        param_positions = [100 + i * 50 for i in range(len(param_labels))]

        # Boutons pour chaque paramètre
        buttons = []
        for i, label in enumerate(param_labels):
            text = font.render(label, True, (255, 255, 255))
            screen.blit(text, (100, param_positions[i]))

            # Boutons "+" et "-"
            minus_button = pygame.Rect(500, param_positions[i], 50, 30)
            plus_button = pygame.Rect(560, param_positions[i], 50, 30)
            pygame.draw.rect(screen, (255, 0, 0), minus_button)
            pygame.draw.rect(screen, (0, 255, 0), plus_button)

            minus_text = font.render("-", True, (255, 255, 255))
            plus_text = font.render("+", True, (255, 255, 255))
            screen.blit(minus_text, (515, param_positions[i] + 5))
            screen.blit(plus_text, (575, param_positions[i] + 5))

            buttons.append((minus_button, plus_button))

        # Affichage du paramètre Display avec un bouton unique
        display_label = font.render(param_labels[-1], True, (255, 255, 255))
        screen.blit(display_label, (100, param_positions[-1]))
        display_button = pygame.Rect(500, param_positions[-1], 110, 30)
        pygame.draw.rect(screen, (0, 255, 255), display_button)  # Cyan pour différencier
        button_text = font.render("ON/OFF", True, (0, 0, 0))
        text_rect = button_text.get_rect(center=display_button.center)  # Centrer le texte
        screen.blit(button_text, text_rect)

        # Zone de texte pour model_name
        model_label = font.render("Model Name:", True, (255, 255, 255))
        screen.blit(model_label, (100, 550))

        # Zone interactive
        input_box = pygame.Rect(250, 550, 300, 36)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2 if input_active else 1)
        model_text = font.render(model_name, True, (255, 255, 255))
        screen.blit(model_text, (input_box.x + 10, input_box.y + 5))

        # Boutons principaux (Play, Train, Model, Quit)
        play_button = pygame.Rect(100, 600, 150, 50)
        train_button = pygame.Rect(270, 600, 150, 50)
        model_button = pygame.Rect(440, 600, 150, 50)
        quit_button = pygame.Rect(610, 600, 150, 50)

        pygame.draw.rect(screen, (0, 255, 0), play_button)
        pygame.draw.rect(screen, (0, 0, 255), train_button)
        pygame.draw.rect(screen, (255, 255, 0), model_button)
        pygame.draw.rect(screen, (255, 0, 0), quit_button)

        screen.blit(font.render("Play", True, (0, 0, 0)), (130, 615))
        screen.blit(font.render("Train", True, (0, 0, 0)), (300, 615))
        screen.blit(font.render("Model", True, (0, 0, 0)), (475, 615))
        screen.blit(font.render("Quit", True, (0, 0, 0)), (640, 615))

        pygame.display.flip()

        return buttons, input_box, display_button, play_button, train_button, model_button, quit_button

    # Dessiner le lobby initial
    buttons, input_box, display_button, play_button, train_button, model_button, quit_button = draw_lobby()

    # Gestion des interactions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si on clique dans la zone de texte
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                # Vérifier les boutons de modification des paramètres
                for i, (minus, plus) in enumerate(buttons):
                    if minus and minus.collidepoint(event.pos):
                        modify_config(local_config, i, decrement=True)
                        buttons, input_box, display_button, play_button, train_button, model_button, quit_button = draw_lobby()
                    elif plus and plus.collidepoint(event.pos):
                        modify_config(local_config, i, decrement=False)
                        buttons, input_box, display_button, play_button, train_button, model_button, quit_button = draw_lobby()

                # Vérifier le bouton Display
                if display_button.collidepoint(event.pos):
                    local_config["display"] = not local_config["display"]
                    buttons, input_box, display_button, play_button, train_button, model_button, quit_button = draw_lobby()

                # Vérifier les boutons principaux
                if play_button.collidepoint(event.pos):
                    local_config["model"]["name"] = model_name
                    return "player", local_config
                elif train_button.collidepoint(event.pos):
                    local_config["model"]["name"] = model_name
                    return "train", local_config
                elif model_button.collidepoint(event.pos):
                    local_config["model"]["name"] = model_name
                    return "model", local_config
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

            if event.type == pygame.KEYDOWN and input_active:
                # Gestion des entrées clavier pour le model_name
                if event.key == pygame.K_BACKSPACE:
                    model_name = model_name[:-1]  # Supprimer un caractère
                else:
                    model_name += event.unicode  # Ajouter le caractère saisi

                # Redessiner le lobby après modification
                buttons, input_box, display_button, play_button, train_button, model_button, quit_button = draw_lobby()


def modify_config(config, index, decrement):
    """
    Modifie un paramètre dans la configuration locale.
    """
    if index == 0:  # Board Size
        config['board_size'] = max(5, min(40, config['board_size'] - 1 if decrement else config['board_size'] + 1))
    elif index == 1:  # Speed
        config['speed'] = max(1, min(20, config['speed'] - 1 if decrement else config['speed'] + 1))
    elif index == 2:  # Victory Condition
        config['victory_condition'] = max(5, min(50, config['victory_condition'] - 1 if decrement else config['victory_condition'] + 1))
    elif index == 3:  # Sessions
        config['training']['sessions'] = max(1, config['training']['sessions'] - 1 if decrement else config['training']['sessions'] + 1)
    elif index == 4:  # Green Apple Reward
        config['rewards']['green_apple'] += -1 if decrement else 1
    elif index == 5:  # Red Apple Reward
        config['rewards']['red_apple'] += -1 if decrement else 1
    elif index == 6:  # Collision Penalty
        config['rewards']['collision'] += -10 if decrement else 10
    elif index == 7:  # Move Penalty
        config['rewards']['move_without_eating'] += -1 if decrement else 1

def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 700))

    # Charger la configuration
    config = load_config()

    # Afficher le lobby et récupérer le mode choisi et les paramètres locaux
    mode, local_config = show_lobby(screen, config)

    # Lire les paramètres locaux
    print(local_config['board_size'])
    board_size = local_config.get("board_size", 10)
    print(board_size)
    speed = local_config.get("speed", 1)
    display = local_config.get("display", True)
    victory_condition = local_config.get("victory_condition", 10)
    rewards = local_config["rewards"]
    training_sessions = local_config["training"]["sessions"]
    model_name = local_config["model"]["name"]

    # Initialiser les actions et l'agent
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    agent = QLearningAgent(board_size, actions, rewards)

    # Initialiser le jeu
    game = Game(board_size, display, speed, victory_condition, mode)

    if mode == "player":
        game.run()
    elif mode == "train":
        # Charger l'état actuel si disponible
        try:
            agent.load_model(model_name)
            print("Modèle chargé à partir de la sauvegarde actuelle.")
        except FileNotFoundError:
            print("Aucun modèle actuel trouvé, démarrage à partir de zéro.")

        # Boucle d'entraînement
        for session in range(1, training_sessions + 1):
            game.reset()
            print(f"Début de la session {session}/{training_sessions}")
            game.run(agent=agent, train=True, current_session=session, total_sessions=training_sessions)

            # Sauvegarder le modèle pour la session actuelle
            agent.save_model(model_name)

            # Sauvegarder les modèles spécifiques pour les sessions importantes
            if session in {1, 10, 100}:
                agent.save_model(f"{model_name}_{session}_sessions.pkl")
            agent.decay_epsilon()
            print(f"\nSession terminée. Nouvelle valeur d'epsilon : {agent.epsilon}\n")
    elif mode == "model":
        agent.epsilon = 0.0
        try:
            agent.load_model(model_name)
            print(f"Modèle {model_name} chargé.")
        except FileNotFoundError:
            print(f"Erreur : Modèle {model_name} introuvable.")
            return

        game.run(agent=agent, train=False)
    else:
        print("Mode invalide.")

if __name__ == "__main__":
    main()