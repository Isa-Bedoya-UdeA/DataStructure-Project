from bplustree import BPlusTree
from utils import load_characters
from typing import Dict


def create_characters_bptrees() -> Dict[str, BPlusTree]:
    """
    Creates two B+ trees:
      - 'class' -> exact search
      - 'race'  -> exact search
    """
    characters = load_characters()

    class_tree = BPlusTree(5)
    race_tree = BPlusTree(5)

    for char in characters:
        class_tree.insert(char["class"], char)
        race_tree.insert(char["race"], char)

    return {"class": class_tree, "race": race_tree}


def search_by_class(class_tree: BPlusTree, in_class: str):
    return class_tree.search(in_class)


def search_by_race(race_tree: BPlusTree, in_race: str):
    return race_tree.search(in_race)
