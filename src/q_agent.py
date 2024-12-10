import random
import os
import pickle
from collections import deque

class QLearningAgent:
    def __init__(self, board_size, actions, rewards, alpha=0.4, gamma=0.9, epsilon=0.99):
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
        Regroupe la vision de toutes les directions en une clé unique pour l'état global.
        La vision dans chaque direction s'arrête lorsqu'on rencontre un 'S' ou un 'G'.
        :param vision: Dictionnaire des visions par direction.
        :return: Tuple représentant l'état global.
        """
        state = []
        for direction in ["up", "down", "left", "right"]:
            cells = vision.get(direction, [])
            truncated = []
            for cell in cells:
                truncated.append(cell)
                if cell in ["S", "G"]:
                    break
            state.append((direction, tuple(truncated))) 
        return tuple(state)

    def choose_action(self, vision):
        """
        Choisit une action basée sur les Q-values de l'état global avec exploration.
        :param vision: Vision actuelle du serpent.
        :return: Une action valide (tuple représentant une direction, ex : (-1, 0)).
        """
        # Obtenir l'état global
        global_state = self.get_global_state(vision)
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
        #     print(f"  Direction: {direction}, Action: {action}, Q-value: {q_value}")

        # Exploration vs exploitation
        if random.uniform(0, 1) < self.epsilon:  # Exploration
            # Filtrer les actions avec des Q-values au-dessus du seuil
            valid_actions = [
                action for action, (direction, state_key) in zip(self.actions, global_state)
                if not (state_key and state_key[0] in ["W", "S"])  # Exclure si le premier élément est "W" ou "S"
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
            # print(f"Exploitation choisie. Meilleure direction : {action} avec Q-value : {q_values[action]}")
        
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
        max_future_q = max(self.q_table[(next_state, next_action)] for next_action in self.actions)
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)

        # Mettre à jour la Q-value
        self.q_table[(current_state, action)] = new_q

    def decay_epsilon(self, min_epsilon=0.1, decay_rate=0.99):
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