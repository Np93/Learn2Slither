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
        self.board.snake, self.direction = self.board.generate_snake()
        self.score = 0

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
                new_direction = None
                if event.key == pygame.K_UP:
                    new_direction = (-1, 0)  # Haut
                elif event.key == pygame.K_DOWN:
                    new_direction = (1, 0)  # Bas
                elif event.key == pygame.K_LEFT:
                    new_direction = (0, -1)  # Gauche
                elif event.key == pygame.K_RIGHT:
                    new_direction = (0, 1)  # Droite

                # Vérification des demi-tours uniquement pour les joueurs
                if new_direction and self.board.direction:
                    # Calculer si c'est un demi-tour
                    is_reverse = tuple(map(lambda x, y: x + y, self.board.direction, new_direction)) == (0, 0)
                    if not is_reverse:
                        self.board.update_direction(new_direction)
                    else:
                        print("Tentative de demi-tour évitée pour le joueur.")

    def draw_score(self):
        """Affiche le score à côté du terrain."""
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_position = (self.board_size * self.cell_size + 20, 20)
        self.screen.blit(score_text, score_position)

    def run(self, agent=None, train=False, current_session=None, total_sessions=None):
        """
        Boucle principale du jeu.
        :param agent: Agent Q-learning si en mode `train` ou `model`.
        :param train: Indique si le jeu est en mode `train` (True) ou `model` (False).
        :param current_session: Numéro de la session actuelle (utilisé en mode train).
        :param total_sessions: Nombre total de sessions (utilisé en mode train).
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
                vision = self.board.get_vision()  # Obtenir la vision actuelle
                action = agent.choose_action(
                    vision=vision,
                )
                self.board.update_direction(action)

            else:
                action = self.board.direction

            # Effectuer l'action et obtenir le résultat
            result = self.board.move_snake(action)

            # Récompenser ou punir en mode train
            if agent:
                reward = self.board.calculate_reward(result)
                if train:
                    next_vision = self.board.get_vision()
                    agent.update_q_value(vision, action, reward, next_vision)

            if result == "green":
                self.score += 1  # Incrémente le score pour une pomme verte
            # Vérifier la fin de partie
            if not result:  # Collision
                print("Game Over!")
                self.running = False
                self.handle_end_screen(
                    title="Game Over",
                    reason="Collision",
                    elapsed_time=elapsed_time
                )
                break

            # Vérifier la victoire
            if self.board.is_victory():
                print("Victoire !")
                self.running = False
                self.handle_end_screen(
                    title="Victory",
                    reason="Length achieved",
                    elapsed_time=elapsed_time
                )
                break
            
            # self.print_action(action)
            # self.board.get_vision()

            # Affichage
            if self.display_enabled:
                self.display.draw_board(
                    self.board.get_state(),
                    score=self.score,
                    elapsed_time=elapsed_time,
                    snake_length=len(self.board.snake.get_body()),
                    current_session=current_session,
                    total_sessions=total_sessions
                )
            if self.display_enabled:
                clock.tick(self.speed)

    @staticmethod
    def print_action(action):
        direction_to_action = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        action_to_direction = {v: k for k, v in direction_to_action.items()}
        direction = action_to_direction[action]
        print(direction)

    def handle_end_screen(self, title, reason, elapsed_time):
        """
        Gère l'affichage de l'écran de fin ou des messages dans la console.
        :param title: "Victory" ou "Game Over".
        :param reason: La raison de la fin ("Length achieved" ou "Collision").
        :param elapsed_time: Temps écoulé en secondes.
        """
        if self.display_enabled and self.display:
            self.display.show_end_screen(
                title=title,
                score=self.score,
                elapsed_time=elapsed_time,
                snake_length=len(self.board.snake.get_body()),
                reason=reason
            )
        else:
            # Afficher les informations dans la console si l'affichage est désactivé
            print(f"{title}!")
            print(f"Reason: {reason}")
            print(f"Score: {self.score}")
            print(f"Time elapsed: {elapsed_time:.1f}s")
            print(f"Snake length: {len(self.board.snake.get_body())}")
    
    def reset(self):
        """
        Réinitialise l'état du jeu pour une nouvelle session d'entraînement.
        """
        # Réinitialiser le plateau en utilisant Board
        self.board = Board(size=self.board_size, victory_condition=self.victory_condition)
        
        # Récupérer le serpent et la direction initiale depuis le Board
        self.board.snake, self.direction = self.board.snake, self.board.direction
        
        # Réinitialiser le score
        self.score = 0

        # Si l'affichage est activé, remettre l'écran à zéro
        if self.display_enabled and self.display:
            self.display.screen.fill((0, 0, 0))
            pygame.display.flip()

        # Réactiver l'état de jeu
        self.running = True