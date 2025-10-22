from utils import load_characters
from collections import defaultdict

class CharacterIndex:
    def __init__(self):
        self.name_index = {} # Búsqueda exacta
        self.prefix_index = {} # Búsqueda por prefijo
        self.load_index()

    def load_index(self): # Construye los índices hash y de prefijos.
        characters = load_characters()
        self.name_index = {c["name"].lower(): c for c in characters}

        prefix_map = defaultdict(list)
        for c in characters:
            name_lower = c["name"].lower()
            for i in range(1, len(name_lower) + 1):
                prefix = name_lower[:i]
                prefix_map[prefix].append(c)
        self.prefix_index = dict(prefix_map)

    def search_exact(self, name: str): # Búsqueda exacta por nombre.
        return self.name_index.get(name.lower())

    def search_prefix(self, prefix: str): # Búsqueda por prefijo (case-insensitive).
        return self.prefix_index.get(prefix.lower(), [])

    def reload(self): # Recarga el índice (por si se agregan personajes nuevos).
        self.load_index()
