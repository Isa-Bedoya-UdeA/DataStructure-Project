from search_index import CharacterIndex  # ajusta el nombre del archivo donde está la clase
from collections import defaultdict

class DebugCharacterIndex(CharacterIndex):
    def load_index(self):
        characters = self._load_characters_for_debug()

        self.name_index = {c["name"].lower(): c for c in characters}
        prefix_map = defaultdict(list)

        for c in characters:
            name_lower = c["name"].lower()
            print(f"\nProcesando personaje: {name_lower}")

            for i in range(1, len(name_lower) + 1):
                prefix = name_lower[:i]
                prefix_map[prefix].append(c)
                print(f"  Prefijo '{prefix}' → {[p['name'] for p in prefix_map[prefix]]}")

        self.prefix_index = dict(prefix_map)
        print("\n✅ Índice de prefijos creado con éxito.")
        print(f"Total de prefijos almacenados: {len(self.prefix_index)}")

    def _load_characters_for_debug(self):
        # Llamamos a la función original sin modificar la clase base
        from utils import load_characters
        return load_characters()

if __name__ == "__main__":
    index = DebugCharacterIndex()
