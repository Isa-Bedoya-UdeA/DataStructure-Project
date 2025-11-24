from bplustree import BPlusTree
from utils import load_characters
from typing import Dict


def create_characters_bptrees() -> Dict[str, BPlusTree]:
    """
    Creates three B+ trees:
      - 'class' -> indexes characters by class (exact)
      - 'race'  -> indexes characters by race (exact)
      - 'name'  -> indexes characters by name (supports prefix search)
    All keys are stored normalized (lowercase) by the B+ tree implementation.
    """
    characters: list = load_characters()

    class_tree = BPlusTree(5)
    race_tree = BPlusTree(5)
    name_tree = BPlusTree(5)

    for char in characters:
        # Insert by class
        class_tree.insert(char["class"], char)
        # Insert by race
        race_tree.insert(char["race"], char)
        # Insert by name (for prefix searching)
        name_tree.insert(char["name"], char)

    return {"class": class_tree, "race": race_tree, "name": name_tree}


def search_by_class(class_tree: BPlusTree, in_class: str):
    return class_tree.search(in_class)


def search_by_race(race_tree: BPlusTree, in_race: str):
    return race_tree.search(in_race)


def search_by_name_prefix(name_tree: BPlusTree, prefix: str):
    return name_tree.search_prefix(prefix)


if __name__ == "__main__":
    trees = create_characters_bptrees()
    res = search_by_class(trees["class"], "Nigromante")
    print("By class:", res)
    res2 = search_by_race(trees["race"], "Elfo")
    print("By race:", res2)
    res3 = search_by_name_prefix(trees["name"], "Al")
    print("By name prefix 'Al':", res3)
