import pygame


class Display:
    def __init__(self, board_size=10, cell_size=50):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = 200  # Espace pour le score
        self.screen = pygame.display.set_mode((board_size * cell_size +
                                               self.margin, board_size *
                                               cell_size))
        pygame.display.set_caption("Snake RL")
        self.font = pygame.font.SysFont(None, 30)  # Police pour le score

    def draw_board(self, board, score, elapsed_time, snake_length,
                   current_session=None, total_sessions=None,
                   means_score=None, means_length=None):
        """
        Dessine le plateau de jeu et affiche le score.
        :param board: État du plateau.
        :param score: Score actuel.
        :param elapsed_time: Temps écoulé en secondes.
        :param snake_length: Longueur actuelle du serpent.
        :param current_session: Numéro de la session actuelle (optionnel).
        :param total_sessions: Nombre total de sessions (optionnel).
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
                    pygame.Rect(y * self.cell_size, x *
                                self.cell_size, self.cell_size,
                                self.cell_size)
                )

        # Affichage des informations supplémentaires
        self.draw_info(score, elapsed_time, snake_length,
                       current_session, total_sessions,
                       means_score, means_length)

        pygame.display.flip()

    def draw_info(self, score, elapsed_time, snake_length,
                  current_session=None, total_sessions=None,
                  means_score=None, means_length=None):
        """
        Affiche les informations supplémentaires à côté du terrain.
        :param score: Score actuel.
        :param elapsed_time: Temps écoulé en secondes.
        :param snake_length: Longueur actuelle du serpent.
        :param current_session: Numéro de la session actuelle (optionnel).
        :param total_sessions: Nombre total de sessions (optionnel).
        """
        max_text_width = self.margin - 40
        # Affiche le score
        score_text = self.font.render(f"Score: "
                                      f"{score}", True, (255, 255, 255))
        self.screen.blit(score_text,
                         (self.board_size * self.cell_size + 20, 20))

        # Affiche le temps écoulé
        time_text = self.font.render(f"Time: {elapsed_time:.1f}s",
                                     True, (255, 255, 255))
        self.screen.blit(time_text,
                         (self.board_size * self.cell_size + 20, 60))

        # Affiche la longueur du serpent
        length_text = self.font.render(f"Length: "
                                       f"{snake_length}",
                                       True, (255, 255, 255))
        self.screen.blit(length_text,
                         (self.board_size * self.cell_size + 20, 100))

        # Affiche la session actuelle si en mode entraînement
        if current_session is not None and total_sessions is not None:
            session_text = self.font.render(f"Session: "
                                            f"{current_session}/"
                                            f"{total_sessions}",
                                            True, (255, 255, 255))
            self.screen.blit(session_text,
                             (self.board_size * self.cell_size + 20, 140))

        if means_score is not None and means_length is not None:
            means_score_text = self.render_text_clipped(f"Mean Score: "
                                                        f"{means_score}",
                                                        max_text_width)
            self.screen.blit(means_score_text,
                             (self.board_size * self.cell_size + 20, 180))
            means_length_text = self.render_text_clipped(f"Mean Length: "
                                                         f"{means_length}",
                                                         max_text_width)
            self.screen.blit(means_length_text,
                             (self.board_size * self.cell_size + 20, 220))

    def render_text_clipped(self, text, max_width):
        font_size = 36
        font = pygame.font.SysFont(None, font_size)
        while font.size(text)[0] > max_width:  # Réduire taille de la police
            font_size -= 2
            if font_size < 10:  # Taille minimale pour éviter l'invisibilité
                break
            font = pygame.font.SysFont(None, font_size)
        return font.render(text, True, (255, 255, 255))

    def show_end_screen(self, title, score, elapsed_time,
                        snake_length, reason):
        """
        Affiche un écran de fin avec les statistiques et un message.
        :param title: Titre de l'écran (e.g., "Victory", "Game Over").
        :param score: Score final.
        :param elapsed_time: Temps écoulé en secondes.
        :param snake_length: Longueur finale du serpent.
        :param reason: Raison de la fin de partie.
        """
        self.screen.fill((0, 0, 0))  # Fond noir

        # Police plus grande pour le titre
        title_font = pygame.font.SysFont(None, 72)  # Police plus grande
        title_color = (0, 255, 0) if title == "Victory" else (255, 0, 0)
        title_text = title_font.render(title, True, title_color)

        # Calcul pour centrer le titre
        title_rect = title_text.get_rect(center=(self.board_size *
                                                 self.cell_size // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Raison de la fin
        reason_text = self.font.render(f"Reason: {reason}",
                                       True, (255, 255, 255))
        self.screen.blit(reason_text,
                         (self.board_size * self.cell_size // 2 - 100, 200))

        # Score final
        score_text = self.font.render(f"Score: {score}",
                                      True, (255, 255, 255))
        self.screen.blit(score_text,
                         (self.board_size * self.cell_size // 2 - 100, 250))

        # Temps écoulé
        time_text = self.font.render(f"Time: {elapsed_time:.1f}s",
                                     True, (255, 255, 255))
        self.screen.blit(time_text,
                         (self.board_size * self.cell_size // 2 - 100, 300))

        # Longueur finale
        length_text = self.font.render(f"Length: {snake_length}",
                                       True, (255, 255, 255))
        self.screen.blit(length_text,
                         (self.board_size * self.cell_size // 2 - 100, 350))

        # Met à jour l'affichage
        pygame.display.flip()

        # Pause pour permettre au joueur de lire les informations
        pygame.time.wait(5000)
