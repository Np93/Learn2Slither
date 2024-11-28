# Gestion de la logique principale du jeu
import time
import pygame
from src.board import Board
from src.display import Display

class Game:
    def __init__(self, board_size=10, display=True, speed=1, victory_condition=10, mode="player"):
        self.board_size = board_size
        self.display_enabled = display
        self.speed = speed
        self.victory_condition = victory_condition
        self.mode = mode

        # Génération du plateau et récupération du serpent et de la direction initiale
        self.board = Board(size=board_size, victory_condition=victory_condition)
        self.board.snake, self.direction = self.board.generate_snake()  # Correctement récupéré ici
        self.score = 0 # Initialisation du score

        if self.display_enabled:
            pygame.init()
            self.display = Display(board_size=board_size)
            self.cell_size = 50
            self.margin = 200  # Espace pour le score
            window_width = board_size * self.cell_size + self.margin
            window_height = board_size * self.cell_size
            self.screen = pygame.display.set_mode((window_width, window_height))
            pygame.display.set_caption("Snake RL")
            self.font = pygame.font.SysFont(None, 36)  # Police pour le score
        else:
            self.display = None

        self.running = True

    def handle_events(self):
        """Gère les événements clavier pour changer la direction du serpent."""
        if self.mode == "model":
            return  # Pas de gestion des événements clavier en mode modèle

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Vérifie uniquement si la direction est opposée
                if event.key == pygame.K_UP and self.direction != (1, 0):  # Pas de demi-tour vers le bas
                    self.direction = (-1, 0)  # Haut
                elif event.key == pygame.K_DOWN and self.direction != (-1, 0):  # Pas de demi-tour vers le haut
                    self.direction = (1, 0)  # Bas
                elif event.key == pygame.K_LEFT and self.direction != (0, 1):  # Pas de demi-tour vers la droite
                    self.direction = (0, -1)  # Gauche
                elif event.key == pygame.K_RIGHT and self.direction != (0, -1):  # Pas de demi-tour vers la gauche
                    self.direction = (0, 1)  # Droite

    def draw_score(self):
        """Affiche le score à côté du terrain."""
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_position = (self.board_size * self.cell_size + 20, 20)  # Affichage sur la droite
        self.screen.blit(score_text, score_position)

    def run(self, agent=None, train=False):
        """
        Boucle principale du jeu.
        :param agent: Agent Q-learning si en mode `train` ou `model`.
        :param train: Indique si le jeu est en mode `train` (True) ou `model` (False).
        """
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()

        while self.running:
            # Si en mode joueur, gérer les événements clavier
            if self.display_enabled and agent is None:
                self.handle_events()

            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000

            # Déterminer l'action
            if agent:
                state_key = agent.get_state_key(self.board.get_vision())
                action = agent.choose_action(state_key)
            else:
                action = self.direction

            # Effectuer l'action et obtenir le résultat
            result = self.board.move_snake(action)

            # Récompenser ou punir en mode train
            if agent:
                reward = self.board.calculate_reward(result)
                if train:
                    next_state_key = agent.get_state_key(self.board.get_vision())
                    agent.update_q_value(state_key, action, reward, next_state_key)

            if result == "green":
                self.score += 1  # Incrémente le score pour une pomme verte
            # Vérifier la fin de partie
            if not result:  # Collision
                print("Game Over!")
                self.running = False
                self.display.show_end_screen(
                    title="Game Over",
                    score=self.score,
                    elapsed_time=elapsed_time,
                    snake_length=len(self.board.snake.get_body()),
                    reason="Collision"
                )
                break

            # Vérifier la victoire
            if self.board.is_victory():
                print("Victoire !")
                self.running = False
                self.display.show_end_screen(
                    title="Victory",
                    score=self.score,
                    elapsed_time=elapsed_time,
                    snake_length=len(self.board.snake.get_body()),
                    reason="Length achieved"
                )
                break

            # Affichage
            if self.display_enabled:
                self.display.draw_board(
                    self.board.get_state(),
                    score=self.score,
                    elapsed_time=elapsed_time,
                    snake_length=len(self.board.snake.get_body())
                )

            clock.tick(self.speed)
    
    # def run(self):
    #     """Boucle principale du jeu."""
    #     clock = pygame.time.Clock()
    #     start_time = pygame.time.get_ticks()

    #     while self.running:
    #         # Gestion des événements
    #         if self.display_enabled:
    #             self.handle_events()

    #         elapsed_time = (pygame.time.get_ticks() - start_time) / 1000

    #         # Récupérer ce que le serpent voit
    #         # vision = self.board.get_vision()
    #         # print(f"Vision du serpent : {vision}")  # Debug

    #         # Mode modèle : déplace automatiquement le serpent
    #         if self.mode == "model":
    #             # Exemple simple : garder la direction actuelle
    #             # (Vous pouvez remplacer cette logique par un modèle plus intelligent)
    #             pass  # Ajoutez la logique ici

    #         # Déplacement du serpent
    #         result = self.board.move_snake(self.direction)
    #         if result == "green":
    #             self.score += 1  # Incrémente le score pour une pomme verte
    #         elif not result:  # Collision ou fin de partie
    #             print("Game Over!")
    #             self.display.show_end_screen(
    #                 title="Game Over",
    #                 score=self.score,
    #                 elapsed_time=elapsed_time,
    #                 snake_length=len(self.board.snake.get_body()),
    #                 reason="Collision"
    #             )
    #             break

    #         # Vérifie la victoire
    #         if self.board.is_victory():
    #             print("Victoire !")
    #             self.display.show_end_screen(
    #                 title="Victory",
    #                 score=self.score,
    #                 elapsed_time=elapsed_time,
    #                 snake_length=len(self.board.snake.get_body()),
    #                 reason="Length achieved"
    #             )
    #             break

    #         # Affichage
    #         if self.display_enabled:
    #             self.display.draw_board(
    #                 self.board.get_state(),
    #                 score=self.score,
    #                 elapsed_time=elapsed_time,
    #                 snake_length=len(self.board.snake.get_body())
    #             )

    #         # Pause en fonction de la vitesse
    #         clock.tick(self.speed)