# Classe "Snake" pour gérer le serpent
class Snake:
    def __init__(self, initial_position, size):
        """
        Initialise le serpent avec une position de départ.
        :param initial_position: Liste de tuples représentant les segments du serpent [(x, y), ...].
        :param size: Taille du plateau (nombre de cases sur un côté, pour un plateau carré).
        """
        self.body = initial_position  # Corps du serpent, liste de tuples
        self.size = size  # Taille du plateau
        self.alive = True  # Indique si le serpent est vivant

    def move(self, direction, grow=False):
        """
        Déplace le serpent dans la direction donnée.
        :param direction: Tuple représentant la direction (dx, dy).
        :param grow: Booléen indiquant si le serpent doit grandir (True) ou non (False).
        """
        if not self.alive:
            return False

        # Calculer la nouvelle position de la tête
        head_x, head_y = self.body[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)
        # print(direction)

        # Vérifier les collisions avec le mur et le corps
        if new_head in self.body or not (0 <= new_head[0] < self.size and 0 <= new_head[1] < self.size):
            self.alive = False
            return False

        # Ajouter la nouvelle tête
        self.body.insert(0, new_head)

        # Retirer la queue si le serpent ne grandit pas
        if not grow:
            self.body.pop()

        return True

    def grow(self):
        """
        Le serpent grandit d'une case.
        """
        pass  # Rien à faire ici, la tête est déjà ajoutée dans move()

    def shrink(self):
        """
        Réduit la taille du serpent en supprimant la queue.
        """
        if len(self.body) > 1:
            self.body.pop()
        else:
            self.alive = False  # Si le serpent n'a plus de corps, il meurt
    
    def grow_at_tail(self):
        """
        Fait grandir le serpent à partir de sa queue.
        """
        if len(self.body) > 0:
            self.body.append(self.body[-1])

    def is_alive(self):
        """
        Retourne si le serpent est encore vivant.
        """
        return self.alive

    def get_body(self):
        """
        Retourne la liste des segments du serpent.
        """
        return self.body