from typing import Optional, List, Tuple, Any


class Node:
    def __init__(self, order: int) -> None:
        self.order = order
        self.keys: List[str] = []
        self.parent: Optional["Node"] = None


class LeafNode(Node):
    def __init__(self, order) -> None:
        super().__init__(order)
        self.values: List[List[dict]] = []
        self.next: Optional["LeafNode"] = None

    def insert(self, key: str, value: dict):
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < key:
            idx += 1

        if idx < len(self.keys) and self.keys[idx] == key:
            self.values[idx].append(value)
        else:
            self.keys.insert(idx, key)
            self.values.insert(idx, [value])

            # check if split is needed
            if self.order - 1 < len(self.keys):
                return self.split()
        return None

    def split(self):
        mid = len(self.keys) // 2

        node_from_split = LeafNode(self.order)
        node_from_split.keys = self.keys[mid:]
        node_from_split.values = self.values[mid:]

        self.keys = self.keys[:mid]
        self.values = self.values[:mid]

        node_from_split.next = self.next
        self.next = node_from_split
        node_from_split.parent = self.parent

        promoted_key = node_from_split.keys[0]

        return promoted_key, node_from_split


class InternalNode(Node):
    def __init__(self, order) -> None:
        super().__init__(order)
        self.children: List[Node] = []

    def split(self):
        mid = len(self.keys) // 2

        promoted_key = self.keys[mid]

        node_from_split = InternalNode(self.order)
        node_from_split.keys = self.keys[mid + 1 :]
        node_from_split.children = self.children[mid + 1 :]

        self.keys = self.keys[:mid]
        self.children = self.children[: mid + 1]
        node_from_split.parent = self.parent

        for child in node_from_split.children:
            child.parent = node_from_split

        return promoted_key, node_from_split

    def insert(self, key, child):
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < key:
            idx += 1

        self.keys.insert(idx, key)
        self.children.insert(idx + 1, child)
        child.parent = self

        if self.order - 1 < len(self.keys):
            return self.split()

        return None


class BPlusTree:
    def __init__(self, order: int) -> None:
        self.order = order
        self.root: Node = LeafNode(order)

    def _normalize(self, key: Any) -> str:
        # convert to string and lower for case-insensitive comparisons
        if key is None:
            return ""
        return str(key).strip().lower()

    def _find_leaf(self, key: str) -> LeafNode:
        current_node = self.root

        while isinstance(current_node, InternalNode):
            idx = 0
            while idx < len(current_node.keys) and current_node.keys[idx] < key:
                idx += 1
            current_node = current_node.children[idx]
        return current_node  # type: ignore

    def _create_new_root(self, promoted_key, left_node, right_node):
        new_root = InternalNode(self.order)
        new_root.keys = [promoted_key]
        new_root.children = [left_node, right_node]

        left_node.parent = new_root
        right_node.parent = new_root
        self.root = new_root

        return

    def _insert_into_parent(self, key, left_node, right_node):
        parent: Optional[InternalNode] = left_node.parent  # type: ignore

        if parent is None:
            self._create_new_root(key, left_node, right_node)
            return

        result = parent.insert(key, right_node)

        if result is None:
            return

        promoted_key, split_node = result
        self._insert_into_parent(promoted_key, parent, split_node)

    def insert(self, key: Any, value: dict):
        normalized_key = self._normalize(key)
        # find the corresponding leaf node
        leaf: LeafNode = self._find_leaf(normalized_key)

        result = leaf.insert(normalized_key, value)
        if result is None:
            return
        # handle split node
        promoted_key, node_from_split = result

        self._insert_into_parent(promoted_key, leaf, node_from_split)
        return

    def search(self, key: Any):
        normalized_key = self._normalize(key)
        leaf: LeafNode = self._find_leaf(normalized_key)

        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < normalized_key:
            idx += 1

        if idx < len(leaf.keys) and leaf.keys[idx] == normalized_key:
            return leaf.values[idx]

        return None

    def search_prefix(self, prefix: Any) -> List[dict]:
        """
        Return list of values whose normalized key starts with prefix (case-insensitive).
        It traverses leaf nodes starting from the leaf where prefix would be placed.
        """
        results: List[dict] = []
        normalized_prefix = self._normalize(prefix)

        # start at leaf where prefix would be found/inserted
        leaf: LeafNode = self._find_leaf(normalized_prefix)

        # find first key in this leaf >= prefix and test startswith
        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < normalized_prefix:
            idx += 1

        # iterate through this leaf and subsequent leaves
        current = leaf
        while current:
            i = idx if current is leaf else 0
            while i < len(current.keys):
                k = current.keys[i]
                if k.startswith(normalized_prefix):
                    results.extend(current.values[i])
                elif k > normalized_prefix and not k.startswith(normalized_prefix):
                    pass
                i += 1
            if current.next:
                current = current.next
                idx = 0
            else:
                break

        return results
