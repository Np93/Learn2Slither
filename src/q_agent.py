import random
import os
import pickle

class QLearningAgent:
    def __init__(self, board_size, actions, rewards, alpha=0.1, gamma=0.9, epsilon=1.0):
        """
        Initialise l'agent de Q-learning.
        :param board_size: Taille du plateau.
        :param actions: Liste des actions possibles [(0, 1), (0, -1), ...].
        :param rewards: Dictionnaire des récompenses.
        :param alpha: Taux d'apprentissage.
        :param gamma: Facteur de discount pour les récompenses futures.
        :param epsilon: Probabilité d'exploration.
        """
        self.board_size = board_size
        self.actions = actions
        self.rewards = rewards
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}  # Q-table dynamique

    def get_state_key(self, vision):
        """Convertit la vision du serpent en clé pour la Q-table."""
        return tuple(tuple(row) for row in vision.values())

    def choose_action(self, state_key):
        """Choisit une action basée sur une stratégie epsilon-greedy."""
        if random.uniform(0, 1) < self.epsilon:  # Exploration
            return random.choice(self.actions)
        else:  # Exploitation
            if state_key not in self.q_table:
                self.q_table[state_key] = {action: 0 for action in self.actions}
            return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def update_q_value(self, state_key, action, reward, next_state_key):
        """Met à jour la valeur Q pour une action donnée."""
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0 for action in self.actions}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {action: 0 for action in self.actions}

        current_q = self.q_table[state_key][action]
        max_future_q = max(self.q_table[next_state_key].values())
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)
        self.q_table[state_key][action] = new_q

    def save_model(self, filename):
        """Sauvegarde la Q-table dans un fichier."""
        os.makedirs("save", exist_ok=True)  # Crée le dossier si nécessaire
        with open(f"save/{filename}", 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_model(self, filename):
        """Charge une Q-table à partir d'un fichier."""
        with open(f"save/{filename}", 'rb') as f:
            self.q_table = pickle.load(f)