import random
import os
import pickle


class QLearningAgent:
    def __init__(self, board_size, actions, rewards,
                 alpha=0.4, gamma=0.9, epsilon=0.99):
        """
        Initialise l'agent de Q-learning.
        :param board_size: Taille du plateau.
        :param actions: Liste des actions possibles [(0, 1), (0, -1), ...].
        :param rewards: Dictionnaire des récompenses.
        :param alpha: Taux d'apprentissage.
        :param gamma: Facteur de prediction pour les récompenses futures.
        :param epsilon: Probabilité d'exploration.
        """
        self.board_size = board_size
        self.actions = actions
        self.rewards = rewards
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}

    def get_global_state(self, vision):
        """
        Regroupe la vision de toutes les directions en
        une clé unique pour l'état global.
        La vision dans chaque direction s'arrête lorsqu'on
        rencontre un 'S' ou un 'G'.
        :param vision: Dictionnaire des visions par direction.
        :return: Tuple représentant l'état global.
        """
        state = []
        for direction in ["up", "down", "left", "right"]:
            cells = vision.get(direction, [])
            truncated = []
            for cell in cells:
                truncated.append(cell)
                if cell in ["S", "G", "W"]:
                    break
            state.append((direction, tuple(truncated)))
        return tuple(state)

    def get_resized_vision(self, vision, total_visible=9):
        """
        Redimensionne les visions opposées (up-down ou left-right)
        proportionnellement
        pour une taille fixe de vision (10x10) tout en respectant
        les proportions initiales.
        Ajoute un mur 'W' à la fin si nécessaire.

        :param vision: Dictionnaire des visions brutes avec
        les directions 'up', 'down', 'left', 'right'.
        :param total_visible: Nombre total de cases visibles entre
        deux directions opposées (par défaut 9).
        :return: Dictionnaire avec la vision redimensionnée.
        """
        resized_vision = {}
        directions_pairs = [("up", "down"), ("left", "right")]

        for dir1, dir2 in directions_pairs:
            # Extraire les visions brutes
            # print(dir1)
            # print(dir2)
            vision1 = vision[dir1]
            vision2 = vision[dir2]

            # Verrouiller les deux premières cases
            locked_dir1 = vision1[:2]
            locked_dir2 = vision2[:2]

            # Extraire les cases restantes
            remaining_dir1 = vision1[2:]
            remaining_dir2 = vision2[2:]

            # Vérifier si une pomme verte 'G' est visible dans la vision
            green_in_initial = "G" in (vision1 + vision2)

            # Calcul de la taille maximale de vision (sans la tête)
            # max_visible_per_direction = (self.board_size - 1) // 2 - 2

            # Calcul des proportions initiales
            dir1_visible = len([cell for cell
                                in remaining_dir1 if cell not in ["W"]])
            dir2_visible = len([cell for cell
                                in remaining_dir2 if cell not in ["W"]])
            combined_visible = dir1_visible + dir2_visible

            prop_dir1 = dir1_visible / max(1, combined_visible)
            prop_dir2 = dir2_visible / max(1, combined_visible)

            # Calcul des cases restantes à attribuer
            remaining_total_visible = (total_visible -
                                       len(locked_dir1) - len(locked_dir2))
            count_dir1 = max(0, round(prop_dir1 * remaining_total_visible))
            count_dir2 = max(0, remaining_total_visible - count_dir1)

            # Redimensionner séparément chaque direction
            resized_dir1 = [cell for cell
                            in remaining_dir1
                            if cell not in ["W"]][:count_dir1]
            resized_dir2 = [cell for cell
                            in remaining_dir2
                            if cell not in ["W"]][:count_dir2]

            # Construire les directions finales
            final_dir1 = locked_dir1 + resized_dir1
            final_dir2 = locked_dir2 + resized_dir2

            # Ajout des cases pour respecter total tout en maintenant les prop
            while len(final_dir1) + len(final_dir2) < total_visible:
                # Ajouter un '0' à la dir avec la proportion la plus basse
                if len(final_dir1) / max(1, len(final_dir1) +
                                         len(final_dir2)) < prop_dir1:
                    final_dir1.append("0")
                elif len(final_dir2) / max(1, len(final_dir1) +
                                           len(final_dir2)) < prop_dir2:
                    final_dir2.append("0")
                else:
                    # Si proportions égales, équilibrer les longueurs
                    if len(final_dir1) <= len(final_dir2):
                        final_dir1.append("0")
                    else:
                        final_dir2.append("0")

            # Réduire en cas de surplus
            while len(final_dir1) + len(final_dir2) > total_visible:
                if len(final_dir1) > len(final_dir2):
                    final_dir1.pop()
                else:
                    final_dir2.pop()

            # Ajouter un mur 'W' à la fin si nécessaire
            if "W" not in final_dir1:
                final_dir1.append("W")
            if "W" not in final_dir2:
                final_dir2.append("W")

            # Ajuster si des directions n'atteignent pas le total_visible
            while len(final_dir1) + len(final_dir2) < total_visible + 2:
                if len(final_dir1) >= len(final_dir2):
                    if "W" in final_dir1:
                        final_dir1.insert(-1, "0")
                    else:
                        final_dir1.append("0")
                else:
                    if "W" in final_dir2:
                        final_dir2.insert(-1, "0")
                    else:
                        final_dir2.append("0")

            # Si une pomme verte 'G' était visible dans la vision initiale
            # mais absente des directions finales
            if green_in_initial and "G" not in final_dir1 + final_dir2:
                if "G" in vision1:  # La pomme était dans la direction dir1
                    if "W" in final_dir1:
                        # Remplacer le dernier "0" avant le "W"
                        w_index = final_dir1.index("W")
                        for i in range(w_index - 1, -1, -1):
                            if final_dir1[i] == "0":
                                final_dir1[i] = "G"
                                break
                elif "G" in vision2:  # La pomme était dans la direction dir2
                    if "W" in final_dir2:
                        # Remplacer le dernier "0" avant le "W"
                        w_index = final_dir2.index("W")
                        for i in range(w_index - 1, -1, -1):
                            if final_dir2[i] == "0":
                                final_dir2[i] = "G"
                                break

            # Stocker les visions redimensionnées
            resized_vision[dir1] = final_dir1
            resized_vision[dir2] = final_dir2

        return resized_vision

    def choose_action(self, vision):  # , current_direction):
        """
        Choisit une action basée sur les Q-values de
        l'état global avec exploration.
        :param vision: Vision actuelle du serpent.
        :return: Une action valide
        (tuple représentant une direction, ex : (-1, 0)).
        """
        # Obtenir l'état global
        if self.board_size == 10:
            global_state = self.get_global_state(vision)
        else:
            new_vision = self.get_resized_vision(vision)
            global_state = self.get_global_state(new_vision)
        q_values = {}

        # Initialiser les Q-values pour chaque action si elles n'existent pas
        for action in self.actions:
            if (global_state, action) not in self.q_table:
                self.q_table[(global_state, action)] = 0  # Initialiser à 0
            q_values[action] = self.q_table[(global_state, action)]

        # direction_to_action = {
        #     "up": (-1, 0),
        #     "down": (1, 0),
        #     "left": (0, -1),
        #     "right": (0, 1)
        # }
        # action_to_direction = {v: k for k, v in direction_to_action.items()}

        # print("\nÉtat global:", global_state)
        # print("Q-values pour chaque direction:")
        # for action, q_value in q_values.items():
        #     direction = action_to_direction[action]
            # print(f"Direction: {direction}, "
            #       f"Action: {action}, Q-value: {q_value}")

        # Exploration vs exploitation
        if random.uniform(0, 1) < self.epsilon:  # Exploration
            # Filtrer les actions avec des Q-values au-dessus du seuil
            valid_actions = [
                action for action, (direction, state_key)
                in zip(self.actions, global_state)
                if not (state_key and state_key[0] in ["W", "S"])
            ]

            if valid_actions:
                # Choisir aléatoirement une action parmi celles valides
                action = random.choice(valid_actions)
            else:
                # Si aucune action valide, choisir une action aléatoire
                action = random.choice(self.actions)
        else:  # Exploitation
            # Choisir l'action avec la meilleure Q-value
            action = max(self.actions, key=lambda a: q_values[a])
            # opposite_direction = (-current_direction[0],
            #                       -current_direction[1])
            # action = max(
            #     (a for a in self.actions if a != opposite_direction),
            #     key=lambda a: q_values[a]
            # )
            # print(f"Exploitation choisie. Meilleure direction : "
            #       f"{action} avec Q-value : {q_values[action]}")

        return action

    def update_q_value(self, vision, action, reward, next_vision):
        """
        Met à jour la Q-value associée à l'état global et à l'action.
        :param vision: Vision actuelle (avant action).
        :param action: Action effectuée.
        :param reward: Récompense reçue.
        :param next_vision: Vision après action.
        """
        # Obtenir les états globaux avant et après
        current_state = self.get_global_state(vision)
        next_state = self.get_global_state(next_vision)

        # Initialiser les Q-values si nécessaires
        if (current_state, action) not in self.q_table:
            self.q_table[(current_state, action)] = 0
        for next_action in self.actions:
            if (next_state, next_action) not in self.q_table:
                self.q_table[(next_state, next_action)] = 0

        # Calculer la nouvelle Q-value
        current_q = self.q_table[(current_state, action)]
        max_future_q = max(self.q_table[(next_state, next_action)]
                           for next_action in self.actions)
        new_q = ((1 - self.alpha) * current_q +
                 self.alpha * (reward + self.gamma * max_future_q))

        # Mettre à jour la Q-value
        self.q_table[(current_state, action)] = new_q

    def decay_epsilon(self, min_epsilon=0.1, decay_rate=0.99):
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)

    def save_model(self, filename):
        os.makedirs("save", exist_ok=True)
        try:
            with open(f"save/{filename}", 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"Modèle sauvegardé dans {filename},"
                  f"nombre d'états : {len(self.q_table)}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def load_model(self, filename):
        try:
            with open(f"save/{filename}", 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Modèle chargé depuis {filename}, "
                  f"nombre d'états : {len(self.q_table)}")
        except FileNotFoundError:
            print(f"Erreur : Le fichier {filename} est introuvable. "
                  f"Nouvelle table initialisée.")
            self.q_table = {}  # Repartir de zéro
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            self.q_table = {}  # Repartir de zéro
