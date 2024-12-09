import random
import os
import pickle
from collections import deque

class QLearningAgent:
    def __init__(self, board_size, actions, rewards, alpha=0.3, gamma=0.7, epsilon=0.90):
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
        self.q_table = {}  # Q-table dynamique

    def get_state_keys(self, vision):
        """
        Extrait les états directionnels indépendamment des directions spécifiques.
        :param vision: Dictionnaire des visions par direction.
        :return: Dictionnaire des états par direction.
        """
        states = {}
        for direction, cells in vision.items():
            # L'état est uniquement basé sur ce qui est vu dans cette direction
            state = []
            for i, cell in enumerate(cells):
                state.append(cell)
                if cell in ["G", "S", "W"]:  # Arrête au premier obstacle ou objet pertinent
                    if cell == "G" and i + 1 < len(cells):  # Si c'est un "G", inclure une case supplémentaire
                        state.append(cells[i + 1])
                    break
            states[direction] = tuple(state)
        return states

    def choose_action(self, vision):
        """
        Choisit une action basée sur les Q-values des états directionnels avec exploration.
        :param vision: Vision actuelle du serpent (dictionnaire retourné par get_vision).
        :return: Une action valide (tuple représentant une direction, ex : (-1, 0)).
        """
        # Obtenir les états directionnels depuis la vision
        states = self.get_state_keys(vision)  # Récupérer les états directionnels
        q_values = {}  # Stocker les Q-values pour chaque direction

        # Obtenir les Q-values pour chaque direction
        for direction, state_key in states.items():
            key = (state_key, direction)  # Inclure la direction dans la clé
            if key not in self.q_table:
                self.q_table[key] = 0  # Initialiser la Q-value si absente
            q_values[direction] = self.q_table[key]

        # print(f"Q-values directionnelles : {q_values}")
        # print(vision)
        THRESHOLD = -50
        # Exploration vs exploitation
        if random.uniform(0, 1) < self.epsilon:  # Exploration
            # Filtrer les actions dangereuses
            # valid_actions = [
            #     (action, direction) for action, (direction, state_key) in zip(self.actions, states.items())
            #     if state_key[0] not in ["S", "W"]  # Exclure les états avec "S" ou "W" au premier élément
            # ]
            valid_actions = [
                (action, direction)
                for action, (direction, state_key) in zip(self.actions, states.items())
                if self.q_table.get((state_key, direction), 0) > THRESHOLD  # Vérifiez la Q-value
            ]

            if valid_actions:
                action, chosen_direction = random.choice(valid_actions)  # Choisir aléatoirement une action valide
                # print(f"Exploration choisie. Direction aléatoire sûre : {chosen_direction}")
            else:
                # Si aucune direction sûre, choisir une action aléatoire non filtrée
                action, chosen_direction = random.choice(list(zip(self.actions, states.keys())))
                # print(f"Exploration choisie. Aucune direction sûre, direction aléatoire : {chosen_direction}")
        else:  # Exploitation
            chosen_direction = max(q_values, key=q_values.get)  # Direction avec la meilleure Q-value
            action = self.actions[["up", "down", "left", "right"].index(chosen_direction)]
            # print(f"Exploitation choisie. Meilleure direction : {chosen_direction} avec Q-value : {q_values[chosen_direction]}")

        # Traduire la direction en action
        # direction_to_action = {
        #     "up": (-1, 0),
        #     "down": (1, 0),
        #     "left": (0, -1),
        #     "right": (0, 1)
        # }

        # Imprimer les informations complètes pour le débogage
        # print(f"Vision : {vision}")
        # print(f"Direction choisie : {chosen_direction}, Action : {action}")

        # Retourner uniquement l'action
        return action

    def update_q_value(self, vision, action, reward, next_vision):
        """
        Met à jour la Q-value associée à l'état directionnel (vision par direction).
        :param vision: Vision actuelle (avant action).
        :param action: Action effectuée.
        :param reward: Récompense reçue.
        :param next_vision: Vision après action.
        """
        # Récupérer les états directionnels avant et après
        states = self.get_state_keys(vision)
        next_states = self.get_state_keys(next_vision)

        # Identifier l'état et la direction associés à l'action
        action_to_direction = {
            (-1, 0): "up",
            (1, 0): "down",
            (0, -1): "left",
            (0, 1): "right"
        }
        current_direction = action_to_direction[action]
        current_state = states[current_direction]
        next_state = next_states[current_direction]

        # Clés de la Q-table
        current_key = (current_state, current_direction)
        next_key = (next_state, current_direction)

        # Initialiser les Q-values si nécessaire
        if current_key not in self.q_table:
            self.q_table[current_key] = 0
        if next_key not in self.q_table:
            self.q_table[next_key] = 0

        # Calculer la nouvelle Q-value
        current_q = self.q_table[current_key]
        if "G" in current_state:
            max_future_q = 0
        else:
            max_future_q = max(
                self.q_table.get((next_state, dir_), 0) for dir_ in ["up", "down", "left", "right"]
            )
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)

        # Mise à jour de la Q-value
        self.q_table[current_key] = new_q
        # print(f"Update Q-value | État : {current_state} | Direction : {current_direction} | Récompense : {reward} "
        #     f"| Ancienne Q : {current_q:.2f} | Nouvelle Q : {new_q:.2f} | Max future Q : {max_future_q:.2f}")


    def decay_epsilon(self, min_epsilon=0.1, decay_rate=0.98):
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)

    def save_model(self, filename):
        os.makedirs("save", exist_ok=True)
        try:
            with open(f"save/{filename}", 'wb') as f:
                pickle.dump(self.q_table, f)
            # print(f"Modèle sauvegardé dans {filename}, nombre d'états : {len(self.q_table)}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def load_model(self, filename):
        try:
            with open(f"save/{filename}", 'rb') as f:
                self.q_table = pickle.load(f)
            # print(f"Modèle chargé depuis {filename}, nombre d'états : {len(self.q_table)}")
        except FileNotFoundError:
            # print(f"Erreur : Le fichier {filename} est introuvable. Nouvelle table initialisée.")
            self.q_table = {}  # Repartir de zéro
        except Exception as e:
            # print(f"Erreur lors du chargement : {e}")
            self.q_table = {}  # Repartir de zéro