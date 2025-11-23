from bplustree import BPlusTree
from utils import load_characters


def create_characters_bptree():
    characters: list = load_characters()
    class_finder = BPlusTree(5)
    for char in characters:
        class_finder.insert(char["class"], char)
    return class_finder


def search_by_class(class_finder, in_class):
    return class_finder.search(in_class)


if __name__ == "__main__":
    class_finder = create_characters_bptree()
    result = search_by_class(class_finder, "Nigromante")
    print(result)
