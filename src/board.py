# Classe "Board" pour gérer le plateau
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
            "repeat_penalty": -5,
            "exploration": 5,
        }
        self.snake, self.direction = self.generate_snake()
        self.green_apples = []
        self.red_apples = []
        self.score = 0
        self.generate_apples()
        self.recent_positions = []

    def is_valid_head_position(self, x, y):
        """Vérifie que la position de la tête n'est pas contre un mur avec un Game Over immédiat."""
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
        Génère la position initiale du serpent et retourne également la direction initiale.
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
        occupied_positions = set(tuple(pos) for pos in self.snake.get_body())  # Convertit explicitement chaque segment en tuple
        free_positions = list(all_positions - occupied_positions)

        self.green_apples = random.sample(free_positions, 2)
        free_positions = list(set(free_positions) - set(self.green_apples))
        self.red_apples = random.sample(free_positions, 1)

    def generate_apple(self, apple_type):
        """
        Génère une pomme unique sur une case libre, uniquement pour remplacer la pomme mangée.
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
            new_apple = random.choice(free_positions)  # Choisir une position libre
            if apple_type == "green":
                self.green_apples.append(new_apple)  # Ajouter une nouvelle pomme verte
            elif apple_type == "red":
                self.red_apples.append(new_apple)

    def move_snake(self, direction):
        """
        Déplace le serpent, gère les collisions et les interactions avec les pommes.
        """
        # print(f"direction avant self.dir...{self.direction}")
        self.direction = direction
        # print(f"direction apres self.dir...{self.direction}")
        head = self.snake.get_body()[0]  # Tête actuelle
        self.snake.move(direction, grow=False)
        # print(f"direction apres mouvement {self.direction}")

        if not self.snake.is_alive():
            print("Game Over!")
            # print(f"Tête après mouvement : {self.snake.get_body()[0]}")
            return False

        new_head = self.snake.get_body()[0]
        # Enregistrer les 9 dernières positions
        self.recent_positions.append(new_head)
        if len(self.recent_positions) > 15:
            self.recent_positions.pop(0)

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
        # print(f"Tête après mouvement : {self.snake.get_body()[0]}")
        return True

    def get_state(self):
        """
        Retourne l'état actuel du plateau (serpent et pommes).
        """
        state = [[" " for _ in range(self.size)] for _ in range(self.size)]

        for x, y in self.snake.get_body():
            if 0 <= x < self.size and 0 <= y < self.size:  # Vérifie que les indices sont valides
                state[x][y] = "S"
        for x, y in self.green_apples:
            if 0 <= x < self.size and 0 <= y < self.size:  # Vérifie que les indices sont valides
                state[x][y] = "G"
        for x, y in self.red_apples:
            if 0 <= x < self.size and 0 <= y < self.size:  # Vérifie que les indices sont valides
                state[x][y] = "R"

        return state

    def get_vision(self):
        """
        Détermine ce que le serpent voit dans les 4 directions depuis sa tête.
        Chaque direction est explorée jusqu'à ce qu'un mur soit rencontré.
        Retourne un dictionnaire indiquant la vision complète dans chaque direction.
        """
        vision = {"up": [], "down": [], "left": [], "right": []}
        head_x, head_y = self.snake.get_body()[0]  # Tête du serpent

        directions = {
            "up": (-1, 0),    # Vers le haut
            "down": (1, 0),   # Vers le bas
            "left": (0, -1),  # Vers la gauche
            "right": (0, 1)   # Vers la droite
        }

        for dir_name, (dx, dy) in directions.items():
            x, y = head_x, head_y
            while True:
                x += dx
                y += dy
                # Vérifier les limites du plateau
                if not (0 <= x < self.size and 0 <= y < self.size):
                    vision[dir_name].append("W")  # Mur rencontré
                    break
                # Vérifier si c'est une pomme verte
                elif (x, y) in self.green_apples:
                    vision[dir_name].append("G")  # Continue après la pomme verte
                # Vérifier si c'est une pomme rouge
                elif (x, y) in self.red_apples:
                    vision[dir_name].append("R")  # Continue après la pomme rouge
                # Vérifier si c'est une partie du corps
                elif (x, y) in self.snake.get_body():
                    vision[dir_name].append("S")  # Continue après le corps
                else:
                    vision[dir_name].append("0")  # Case vide
        # print(f"Vision calculée : {vision}")
        return vision

    def calculate_reward(self, action_result):
        """
        Calcule la récompense en fonction du résultat de l'action.
        :param action_result: Résultat de l'action ("green", "red", None ou False).
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

        # Pénalité pour revisite récente
        current_position = self.snake.get_body()[0]
        if self.recent_positions.count(current_position) > 1:
            penalty = self.rewards["repeat_penalty"]
            reward += penalty
            # print("repete penality")
        else:
            reward += self.rewards["exploration"]

        head = self.snake.get_body()[0]
        center_min = self.size // 4
        center_max = 3 * (self.size // 4)

        # Si la tête est en dehors de la zone centrale
        if not (center_min <= head[0] <= center_max and center_min <= head[1] <= center_max):
            reward += self.rewards.get("exploration", 10)

        return reward

    def is_victory(self):
        """
        Vérifie si la longueur du serpent atteint la condition de victoire (10 cellules).
        :return: True si victoire, sinon False.
        """
        return len(self.snake.get_body()) >= self.victory_condition

    def update_direction(self, new_direction):
        """Met à jour la direction uniquement si elle ne correspond pas à un demi-tour."""
        self.direction = new_direction