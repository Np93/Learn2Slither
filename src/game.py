# Gestion de la logique principale du jeu
import time
import pygame
from src.board import Board
from src.display import Display

class Game:
    def __init__(self, board_size=10, display=True, speed=1, victory_condition=10):
        self.board_size = board_size
        self.display_enabled = display
        self.speed = speed
        self.victory_condition = victory_condition

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

    def run(self):
        """Boucle principale du jeu."""
        clock = pygame.time.Clock()

        while self.running:
            # Gestion des événements
            if self.display_enabled:
                self.handle_events()

            # Déplacement du serpent
            result = self.board.move_snake(self.direction)
            if result == "green":
                self.score += 1  # Incrémente le score pour une pomme verte
            elif not result:  # Collision ou fin de partie
                print("Game Over!")
                self.running = False
                break

            # Vérifie la victoire
            if self.board.is_victory():
                print(f"Victoire ! Le serpent a atteint une longueur de {self.victory_condition} cellules.")
                self.running = False
                break

            # Affichage
            if self.display_enabled:
                self.screen.fill((0, 0, 0))  # Fond noir
                self.display.draw_board(self.board.get_state(), self.board.score)

            # Pause en fonction de la vitesse
            clock.tick(self.speed)