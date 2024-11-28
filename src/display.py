# Classe ou fonctions pour gérer l'affichage (Pygame)
import pygame

class Display:
    def __init__(self, board_size=10, cell_size=50):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = 200  # Espace pour le score
        self.screen = pygame.display.set_mode((board_size * cell_size + self.margin, board_size * cell_size))
        pygame.display.set_caption("Snake RL")
        self.font = pygame.font.SysFont(None, 36)  # Police pour afficher le score

    def draw_board(self, board, score):
        """
        Dessine le plateau de jeu et affiche le score.
        :param board: État du plateau.
        :param score: Score actuel.
        """
        self.screen.fill((0, 0, 0))  # Fond noir

        # Dessin de la grille
        for x in range(len(board)):
            for y in range(len(board[x])):
                color = (255, 255, 255)  # Blanc pour les cases vides
                if board[x][y] == "S":
                    color = (0, 0, 255)  # Bleu pour le serpent
                elif board[x][y] == "G":
                    color = (0, 255, 0)  # Vert pour les pommes vertes
                elif board[x][y] == "R":
                    color = (255, 0, 0)  # Rouge pour les pommes rouges

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size)
                )

        # Affichage du score
        score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.board_size * self.cell_size + 20, 20))  # Score affiché à droite

        pygame.display.flip()