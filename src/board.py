from src.snake import Snake
import random

class Board:
    def __init__(self, size=10, victory_condition=10, rewards=None):
        self.size = size
        self.victory_condition = victory_condition
        self.rewards = rewards or {
            "green_apple": 10,
            "red_apple": -5,
            "move_without_eating": -1,
            "collision": -50,
        }
        self.snake, self.direction = self.generate_snake()
        self.green_apples = []
        self.red_apples = []
        self.score = 0
        self.generate_apples()
        self.recent_positions = []

    def is_valid_head_position(self, x, y):
        """Vérifie que la position de la tête n'est pas 
        contre un mur avec un Game Over immédiat."""
        # Directions possibles : haut, bas, gauche, droite
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_moves = 0

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                valid_moves += 1

        return valid_moves > 2  # Au moins deux directions possibles

    def generate_snake(self):
        """
        Génère la position initiale du serpent et 
        retourne également la direction initiale.
        """
        while True:
            x = random.randint(1, self.size - 2)
            y = random.randint(1, self.size - 2)

            if self.is_valid_head_position(x, y):
                directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                random.shuffle(directions)

                for direction in directions:
                    snake_body = [(x, y), (x + direction[0], y + direction[1]), (x + 2 * direction[0], y + 2 * direction[1])]

                    if all(0 <= sx < self.size and 0 <= sy < self.size for sx, sy in snake_body):
                        direction_from_tail = (
                            snake_body[0][0] - snake_body[1][0],  # x1 - x2
                            snake_body[0][1] - snake_body[1][1]   # y1 - y2
                        )
                        return Snake(snake_body, self.size), direction_from_tail

    def generate_apples(self):
        """
        Génère des pommes sur des cases libres.
        """
        all_positions = set((x, y) for x in range(self.size) for y in range(self.size))
        occupied_positions = set(tuple(pos) for pos in self.snake.get_body())
        free_positions = list(all_positions - occupied_positions)

        self.green_apples = random.sample(free_positions, 2)
        free_positions = list(set(free_positions) - set(self.green_apples))
        self.red_apples = random.sample(free_positions, 1)

    def generate_apple(self, apple_type):
        """
        Génère une pomme unique sur une case libre, uniquement 
        pour remplacer la pomme mangée.
        :param apple_type: Le type de la pomme à générer ("green" ou "red").
        """
        # Générer toutes les positions possibles du plateau
        all_positions = set((x, y) for x in range(self.size) for y in range(self.size))
        
        # Positions occupées par le serpent et les pommes existantes
        occupied_positions = set(self.snake.get_body() + self.green_apples + self.red_apples)
        
        # Cases libres
        free_positions = list(all_positions - occupied_positions)
        
        # Vérifier qu'il reste des cases libres
        if free_positions:
            new_apple = random.choice(free_positions)
            if apple_type == "green":
                self.green_apples.append(new_apple)
            elif apple_type == "red":
                self.red_apples.append(new_apple)

    def move_snake(self, direction):
        """
        Déplace le serpent, gère les collisions et 
        les interactions avec les pommes.
        """
        self.direction = direction
        self.snake.move(direction, grow=False)

        if not self.snake.is_alive():
            # print("Game Over!")
            return False

        # Gestion des pommes
        new_head = self.snake.get_body()[0]
        if new_head in self.green_apples:
            print("Pomme verte mangée.")
            self.green_apples.remove(new_head)
            self.snake.grow_at_tail()
            # self.snake.move(direction, grow=True)  # Le serpent grandit
            self.generate_apple("green")  # Générer une nouvelle pomme verte
            return "green"
        elif new_head in self.red_apples:
            print("Pomme rouge mangée.")
            self.red_apples.remove(new_head)
            self.snake.shrink()  # Rétrécit
            if not self.snake.is_alive():
                print("Le serpent est mort après avoir mangé une pomme rouge.")
                return False
            self.generate_apple("red")  # Générer une nouvelle pomme rouge
            return "red"
        return True

    def get_state(self):
        """
        Retourne l'état actuel du plateau (serpent et pommes).
        """
        state = [[" " for _ in range(self.size)] for _ in range(self.size)]

        for x, y in self.snake.get_body():
            if 0 <= x < self.size and 0 <= y < self.size:
                state[x][y] = "S"
        for x, y in self.green_apples:
            if 0 <= x < self.size and 0 <= y < self.size:
                state[x][y] = "G"
        for x, y in self.red_apples:
            if 0 <= x < self.size and 0 <= y < self.size:
                state[x][y] = "R"

        return state

    def get_vision(self):
        """
        Détermine ce que le serpent voit dans les 4 directions depuis sa tête.
        Chaque direction est explorée jusqu'à ce qu'un mur soit rencontré.
        Retourne un dictionnaire indiquant 
        la vision complète dans chaque direction.
        """
        vision = {"up": [], "down": [], "left": [], "right": []}
        head_x, head_y = self.snake.get_body()[0]

        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }

        for dir_name, (dx, dy) in directions.items():
            x, y = head_x, head_y
            while True:
                x += dx
                y += dy
                # Vérifier les limites du plateau
                if not (0 <= x < self.size and 0 <= y < self.size):
                    vision[dir_name].append("W")
                    break
                # Vérifier si c'est une pomme verte
                elif (x, y) in self.green_apples:
                    vision[dir_name].append("G")
                # Vérifier si c'est une pomme rouge
                elif (x, y) in self.red_apples:
                    vision[dir_name].append("R")
                # Vérifier si c'est une partie du corps
                elif (x, y) in self.snake.get_body():
                    vision[dir_name].append("S")
                else:
                    vision[dir_name].append("0")  # Case vide
        # self.print_vision(vision)
        return vision

    @staticmethod
    def print_vision(vision):
        """
        Affiche la vision dans le terminal dans un format 
        structuré avec la tête au centre.
        :param vision: Dictionnaire contenant la vision pour 
        chaque direction.
        """
        # Préparer les directions
        up_vision = vision["up"]
        down_vision = vision["down"]
        left_vision = vision["left"]
        right_vision = vision["right"]

        # Déterminer la hauteur maximale entre "up" et "down" 
        # pour l'alignement vertical
        max_vertical = max(len(up_vision), len(down_vision))

        # Préparer des espaces vides pour compléter les directions courtes
        up_padding = [" "] * (max_vertical - len(up_vision))
        down_padding = [" "] * (max_vertical - len(down_vision))

        # Combiner les visions "up" et "down"
        vertical_view = up_padding + list(reversed(up_vision)) + ["H"] + down_vision + down_padding

        # Déterminer la longueur maximale entre "left" et "right" 
        # pour l'alignement horizontal
        max_horizontal = max(len(left_vision), len(right_vision))
        left_padding = [" "] * (max_horizontal - len(left_vision))
        right_padding = [" "] * (max_horizontal - len(right_vision))

        # Compléter les visions "left" et "right"
        left_view = left_padding + list(reversed(left_vision))
        right_view = right_vision + right_padding

        # Combiner la vue horizontale (ligne contenant "H")
        horizontal_line = "".join(left_view) + "H" + "".join(right_view)

        # Affichage final
        # print("\nVision du serpent :")
        for i in range(len(vertical_view)):
            if i < len(up_padding):
                print(" " * len(horizontal_line))
            elif i < len(up_padding) + len(up_vision):
                print(" " * (len(left_view)) + vertical_view[i])
            elif i == len(up_padding) + len(up_vision):
                print(horizontal_line)
            else:
                print(" " * (len(left_view)) + vertical_view[i])

    def calculate_reward(self, action_result):
        """
        Calcule la récompense en fonction du résultat de l'action.
        :param action_result: Résultat de l'action 
        ("green", "red", None ou False).
        :return: Récompense associée.
        """
        reward = 0

        # Récompenses existantes
        if action_result == "green":
            reward += self.rewards["green_apple"]
        elif action_result == "red":
            reward += self.rewards["red_apple"]
        elif action_result is False:  # Collision
            reward += self.rewards["collision"]
        else:
            reward += self.rewards["move_without_eating"]

        return reward

    def is_victory(self):
        """
        Vérifie si la longueur du serpent atteint 
        la condition de victoire (10 cellules).
        :return: True si victoire, sinon False.
        """
        return len(self.snake.get_body()) >= self.victory_condition

    def update_direction(self, new_direction):
        """Met à jour la direction uniquement si elle ne 
        correspond pas à un demi-tour."""
        self.direction = new_direction