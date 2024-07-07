from collections import deque

from pygame import Vector2

from rbt.RbtNode import RbtNode
from utility.enums import Operation, RbtColor, Color


class RedBlackVisualizedTree:
    def __init__(self, visualizer, comparator_func=lambda x, y: x > y):
        self.base_position = (visualizer.screen.get_width() // 2, 100)
        self.nil = RbtNode(
            0, None, RbtColor.BLACK.value, 0, 0,
            position=self.base_position,
            dest_position=(visualizer.screen.get_width() // 2, 100), radius=50,
            visualizer=visualizer
        )  # Base position and radius
        self.nil.parent = self.nil.left = self.nil.right = self.root = self.nil
        self.comparator_func = comparator_func

        self.visualizer = visualizer
        self.nodes_being_deleted = set()

    def __len__(self):
        return 0 if self.root is self.nil else self.root.subtree_size

    def __contains__(self, value):
        return self.search(value) is not self.nil

    def __iter__(self):
        self.current = self.minimum(self.root)
        return self

    def __next__(self):
        if self.current is self.nil:
            raise StopIteration
        else:
            next_node = self.current
            self.current = self.successor(self.current)
            return next_node

    def __str__(self):
        nodes = [str(node) for node in self]
        return f'[{", ".join(nodes)}]'

    def __repr__(self):
        nodes = [repr(node) for node in self]
        return f'[{", ".join(nodes)}]'

    def __getitem__(self, index):
        return self.find_by_rank(self.root, index + 1).value

    def minimum(self, node):
        if node is self.nil:
            return self.nil
        while node.left is not self.nil:
            node = node.left
        return node

    def maximum(self, node):
        if node is self.nil:
            return self.nil
        while node.right is not self.nil:
            node = node.right
        return node

    def successor(self, node):
        if node is self.nil:
            return self.nil
        if node.right is not self.nil:
            return self.minimum(node.right)
        parent_node = node.parent
        while parent_node is not self.nil and node == parent_node.right:
            node = parent_node
            parent_node = parent_node.parent
        return parent_node

    def predecessor(self, node):
        if node is self.nil:
            return self.nil
        if node.left is not self.nil:
            return self.maximum(node.left)
        parent_node = node.parent
        while parent_node is not self.nil and node == parent_node.left:
            node = parent_node
            parent_node = parent_node.parent
        return parent_node

    def _left_rotate(self, node):
        rot_node = node.right
        node.right = rot_node.left
        if rot_node.left is not self.nil:
            rot_node.left.parent = node
        rot_node.parent = node.parent
        if node.parent is self.nil:
            self.root = rot_node
        elif node is node.parent.left:
            node.parent.left = rot_node
        else:
            node.parent.right = rot_node
        rot_node.left = node
        node.parent = rot_node
        rot_node.subtree_size = node.subtree_size
        node.subtree_size = node.left.subtree_size + node.right.subtree_size + node.quantity
        self.bfs_reposition(rot_node)
        self.visualizer.animation_controller.add_animated_element((Operation.CHANGE_COLOR, None, 20))

    def _right_rotate(self, rot_node):
        node = rot_node.left
        rot_node.left = node.right
        if node.right is not self.nil:
            node.right.parent = rot_node
        node.parent = rot_node.parent
        if rot_node.parent is self.nil:
            self.root = node
        elif rot_node is rot_node.parent.right:
            rot_node.parent.right = node
        else:
            rot_node.parent.left = node
        node.right = rot_node
        rot_node.parent = node
        node.subtree_size = rot_node.subtree_size
        rot_node.subtree_size = rot_node.left.subtree_size + rot_node.right.subtree_size + rot_node.quantity
        self.bfs_reposition(node)
        self.visualizer.animation_controller.add_animated_element((Operation.CHANGE_COLOR, None, 20))

    def get_nodes_bfs(self):
        nodes = []
        if len(self):
            queue = deque([self.root])
            while queue:
                node = queue.popleft()
                nodes.append(node)
                if node.left is not self.nil:
                    queue.append(node.left)
                if node.right is not self.nil:
                    queue.append(node.right)
        return nodes

    def get_edges_set(self):
        edges = set()
        for node in self:
            if node.parent is not self.nil:
                edges.add((node, node.parent) if node.value < node.parent.value else (node.parent, node))
        return edges

    def get_values(self):
        return [node.value for node in self]

    def get_quantities(self):
        return [node.quantity for node in self]

    def get_values_with_quantity(self):
        return [node.quantity for node in self for _ in range(node.quantity)]

    def get_nodes(self):
        return [node for node in self]

    def reset_child_offset(self):
        for node in self.get_nodes():
            node.child_side_offset_mult = self.nil.child_side_offset_mult

    def collision_check(self):
        self.reset_child_offset()
        self.mock_bfs_reposition(self.root)
        for node1 in reversed(self.get_nodes()):
            for node2 in self.get_nodes():
                if (node1 is not node2 and (
                        Vector2(node1.dest_position).distance_to(Vector2(node2.dest_position)) <= 3 * node1.radius or
                        node1.value < node2.value and node1.position[0] > node2.position[0]
                )):
                    self.double_radius_offset(node1, node2)
                    self.bfs_reposition()
                    print("COLLISION!")

        moves = []
        for node in self.get_nodes():
            if node.position != node.dest_position:
                moves.append((Operation.MOVE, (node, node.dest_position), 50))

        moves.extend(
            self.visualizer.edge_manager.edge_diffs_with_animations(self.get_edges_set(), 50)
        )
        self.visualizer.animation_controller.add_animated_element((Operation.BUNDLE, moves))


    def mock_bfs_reposition(self, node=None):
        self.nil.position = self.base_position
        self.nil.dest_position = self.base_position

        if len(self):
            if node is None:
                node = self.root

            queue = deque([node])
            while queue:
                node = queue.popleft()
                node.dest_position = (
                    node.parent.dest_position[0] + node.radius * node.parent.child_side_offset_mult * (
                        -1 if node.parent.left is node else 1) * (0 if node.parent is self.nil else 1),
                    node.parent.dest_position[1] + node.radius * 3 * (0 if node.parent is self.nil else 1)
                )
                if node.left is not self.nil:
                    queue.append(node.left)
                if node.right is not self.nil:
                    queue.append(node.right)


    def bfs_reposition(self, node=None):
        self.nil.position = self.base_position
        self.nil.dest_position = self.base_position

        moves = []
        if len(self):
            if node is None:
                node = self.root

            queue = deque([node])
            while queue:
                node = queue.popleft()
                node.dest_position = (
                    node.parent.dest_position[0] + node.radius * node.parent.child_side_offset_mult * (
                        -1 if node.parent.left is node else 1) * (0 if node.parent is self.nil else 1),
                    node.parent.dest_position[1] + node.radius * 3 * (0 if node.parent is self.nil else 1)
                )
                moves.append((Operation.MOVE, (node, node.dest_position), 50))
                if node.left is not self.nil:
                    queue.append(node.left)
                if node.right is not self.nil:
                    queue.append(node.right)


        moves.extend(
            self.visualizer.edge_manager.edge_diffs_with_animations(self.get_edges_set(), 50)
        )
        self.visualizer.animation_controller.add_animated_element((Operation.BUNDLE, moves))

    def double_radius_offset(self, node1, node2):
        while node1 is not self.nil and node2 is not self.nil and node1 is not node2:
            node1 = node1.parent
            node2 = node2.parent

        if node1 is node2 and node1 is not self.nil:
            node1.child_side_offset_mult *= 2

    def depth(self, node):
        depth = 0
        while node is not self.nil:
            node = node.parent
            depth += 1
        return depth

    def begin(self):
        return self.minimum(self.root)

    def end(self):
        return self.maximum(self.root)

    def clear(self):
        old = self.nil
        for node in self:
            if old is not self.nil:
                old.parent = self.nil
                old.right = self.nil
                old.left = self.nil
            old = node

        self.root = self.nil

    def count(self, val):
        node = self.search(val)
        return node.quantity if node is not self.nil else 0

    def search(self, key):
        node = self.root
        while node is not self.nil and (self.comparator_func(node.value, key) or self.comparator_func(key, node.value)):
            if self.comparator_func(node.value, key):
                node = node.left
            else:
                node = node.right

        return node

    def insert(self, key):
        node = self.root
        parent_node = self.nil
        while node is not self.nil:

            self.visualizer.animation_controller.add_animated_element((Operation.HIGHLIGHT, node, 30))
            node.subtree_size += 1
            parent_node = node
            if not self.comparator_func(node.value, key) and not self.comparator_func(key, node.value):
                node.quantity += 1
                return
            elif self.comparator_func(node.value, key):
                node = node.left
            else:
                node = node.right

        pos = parent_node.position
        if len(self) == 0:
            pos = (self.base_position[0], -100)

        new_node = RbtNode(
            key, self.nil, RbtColor.RED.value, visualizer=self.visualizer,
            position=pos, dest_position=parent_node.dest_position, radius=parent_node.radius
        )  # change position and radius

        new_node.parent = parent_node
        if parent_node is self.nil:
            self.root = new_node
        elif self.comparator_func(parent_node.value, new_node.value):
            parent_node.left = new_node
        else:
            parent_node.right = new_node

        if len(self) > 1:
            new_node.dest_position = (
                parent_node.dest_position[0] + new_node.radius * parent_node.child_side_offset_mult * (
                    -1 if parent_node.left is new_node else 1
                ), parent_node.dest_position[1] + new_node.radius * 3
            )

            anim_bundle = [(
                Operation.INSERT, (new_node, new_node.dest_position), 50
            )] + self.visualizer.edge_manager.edge_diffs_with_animations(self.get_edges_set())
        else:
            anim_bundle = [(
                Operation.MOVE, (new_node, new_node.dest_position), 50
            )]

        self.visualizer.animation_controller.add_animated_element((
            Operation.BUNDLE, anim_bundle
        ))

        self._insert_fixup(new_node)

        self.collision_check()

    def _insert_fixup(self, z):
        while not z.parent.color:
            # animations = [(Operation.HIGHLIGHT, z, 30)]
            if z.parent is z.parent.parent.left:
                y = z.parent.parent.right
                if not y.color:
                    z.parent.set_color(RbtColor.BLACK.value)
                    y.set_color(RbtColor.BLACK.value)
                    z.parent.parent.set_color(RbtColor.RED.value)
                    z = z.parent.parent
                else:
                    if z is z.parent.right:
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.set_color(RbtColor.BLACK.value)
                    z.parent.parent.set_color(RbtColor.RED.value)
                    self._right_rotate(z.parent.parent)
            elif z.parent is z.parent.parent.right:
                y = z.parent.parent.left
                if not y.color:
                    z.parent.set_color(RbtColor.BLACK.value)
                    y.set_color(RbtColor.BLACK.value)
                    z.parent.parent.set_color(RbtColor.RED.value)
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.set_color(RbtColor.BLACK.value)
                    z.parent.parent.set_color(RbtColor.RED.value)
                    self._left_rotate(z.parent.parent)

        self.root.set_color(RbtColor.BLACK.value)
        self.visualizer.animation_controller.add_animated_element((Operation.CHANGE_COLOR, None, 20))

    def insert_iterable(self, key_list):
        for x in key_list:
            self.insert(x)

    def _transplant(self, x, y):
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.parent = x.parent
        y.subtree_size = (0 if y.left is self.nil else y.left.subtree_size) + (
            0 if y.right is self.nil else y.right.subtree_size) + y.quantity

        y.dest_position = x.dest_position
        return Operation.MOVE, (y, y.dest_position), 50


    def delete(self, node):
        if node.quantity > 1:
            node.quantity -= 1
            self._subtree_size_decrease(node)
            return
        self.delete_all(node)

    def delete_all(self, node):

        node_is_root = node is self.root

        self.nodes_being_deleted.add(node)
        node.being_deleted = True
        anim_bundle = []

        self._subtree_size_decrease(node.parent, node.quantity)
        y = node
        y_og_color = y.color
        if node.left is self.nil:
            z = node.right
            anim_bundle.append(self._transplant(node, node.right))
        elif node.right is self.nil:
            z = node.left
            anim_bundle.append(self._transplant(node, node.left))
        else:
            y = self.minimum(node.right)
            y_og_color = y.color
            z = y.right

            if y.parent is node:
                z.parent = y
            else:
                anim_bundle.append(self._transplant(y, y.right))
                y.right = node.right
                y.right.parent = y
            anim_bundle.append(self._transplant(node, y))
            y.left = node.left
            y.left.parent = y
            y.set_color(node.color)
            y.subtree_size = (0 if y.left is self.nil else y.left.subtree_size) + (
                0 if y.right is self.nil else y.right.subtree_size) + y.quantity

        if node_is_root:
            node.dest_position = (self.base_position[0], -100)
        else:
            node.dest_position = node.parent.dest_position

        anim_bundle.extend([(
            Operation.MOVE, (node, node.dest_position), 50
        )] + self.visualizer.edge_manager.edge_diffs_with_animations(self.get_edges_set()))

        anim_bundle.append((Operation.CHANGE_COLOR, None, 20))

        self.visualizer.animation_controller.add_animated_element((
            Operation.BUNDLE, anim_bundle
        ))

        if y_og_color:
            self._delete_fixup(z)

        self.collision_check()


    def _delete_fixup(self, node):
        while node is not self.root and node.color:
            if node is node.parent.left:
                sibling = node.parent.right
                if not sibling.color:
                    sibling.set_color(RbtColor.BLACK.value)
                    sibling.parent.set_color(RbtColor.RED.value)
                    self._left_rotate(node.parent)
                    sibling = node.parent.right
                if sibling is self.nil or (sibling.left.color and sibling.right.color):
                    if sibling is not self.nil:
                        sibling.set_color(RbtColor.RED.value)
                    node = node.parent
                else:
                    if not sibling.left.color:
                        sibling.left.set_color(RbtColor.BLACK.value)
                        sibling.set_color(RbtColor.RED.value)
                        self._right_rotate(sibling)
                        sibling = node.parent.right
                    sibling.set_color(node.parent.color)
                    node.parent.set_color(RbtColor.BLACK.value)
                    sibling.right.set_color(RbtColor.BLACK.value)

                    self._left_rotate(node.parent)
                    node = self.root
            else:
                sibling = node.parent.left
                if not sibling.color:
                    sibling.set_color(RbtColor.BLACK.value)
                    sibling.parent.set_color(RbtColor.RED.value)
                    self._right_rotate(node.parent)
                    sibling = node.parent.left
                if sibling is self.nil or (sibling.right.color and sibling.left.color):
                    if sibling is not self.nil:
                        sibling.set_color(RbtColor.RED.value)
                    node = node.parent
                else:
                    if not sibling.right.color:
                        sibling.right.set_color(RbtColor.BLACK.value)
                        sibling.set_color(RbtColor.RED.value)
                        self._left_rotate(sibling)
                        sibling = node.parent.left
                    sibling.set_color(node.parent.color)
                    node.parent.set_color(RbtColor.BLACK.value)
                    sibling.left.set_color(RbtColor.BLACK.value)

                    self._right_rotate(node.parent)
                    node = self.root
        node.set_color(RbtColor.BLACK.value)
        self.visualizer.animation_controller.add_animated_element((
            Operation.CHANGE_COLOR, None, 20
        ))

    def _subtree_size_decrease(self, node, val=1):
        while node is not self.nil:
            node.subtree_size -= val
            node = node.parent

    def delete_by_value(self, value):
        node = self.search(value)
        if node is self.nil:
            raise ValueError('Value not in the structure')
        else:
            self.delete(node)

    def delete_all_by_value(self, value):
        node = self.search(value)
        if node is self.nil:
            raise ValueError('Value not in the structure')
        else:
            self.delete_all(node)

    def lower_bound(self, key):
        node = self.root
        candidate = self.nil
        while node is not self.nil:
            if self.comparator_func(key, node.value):
                node = node.right
            else:
                if candidate is self.nil or self.comparator_func(candidate.value, node.value):
                    candidate = node
                node = node.left

        return candidate

    def upper_bound(self, key):
        node = self.root
        candidate = self.nil
        while node is not self.nil:
            if self.comparator_func(node.value, key):
                if candidate is self.nil or self.comparator_func(candidate.value, node.value):
                    candidate = node
                node = node.left
            else:
                node = node.right

        return candidate

    def find_by_rank(self, node, i):
        if not (1 <= i <= len(self)):
            raise IndexError("Invalid index")
        r = node.left.subtree_size + 1
        if r <= i < r + node.quantity:
            return node
        return self.find_by_rank(node.left, i) if i < r else self.find_by_rank(node.right, i - r - node.quantity + 1)

    def get_rank(self, node):
        if node is self.nil:
            raise ValueError("Node not found in the container")
        r = node.left.subtree_size + 1
        while node is not self.root:
            if node is node.parent.right:
                r += node.parent.left.subtree_size + node.parent.quantity
            node = node.parent
        return r

    def get_rank_range(self, node):  # right-side exclusive
        r = self.get_rank(node)
        return r, r + node.quantity

    def get_rank_by_value(self, val):
        node = self.search(val)
        if node is self.nil:
            raise ValueError("Node not found in the container")
        return self.get_rank(node)

    def get_rank_range_by_value(self, val):  # right-side exclusive
        node = self.search(val)
        if node is self.nil:
            raise ValueError("Node not found in the container")
        return self.get_rank_range(node)

    def _set_value(self, key, value, new_quantity=1):  # potentially dangerous
        if key in self:
            node = self.search(key)
            node.value = value
            prev_quantity = node.quantity
            node.quantity = new_quantity
            self._subtree_size_decrease(node, prev_quantity - node.quantity)

    def update(self):
        to_be_removed = set()
        for node in self.nodes_being_deleted:
            if node.dest_position == node.position:
                to_be_removed.add(node)

        self.nodes_being_deleted.difference_update(to_be_removed)
