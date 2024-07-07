from rbt.RbtEdge import RbtEdge
from utility.enums import Operation


class EdgeManager:
    def __init__(self, visualizer):
        self.edges = dict()
        self.edges_set = set()
        self.edges_being_removed_set = set()
        self.visualizer = visualizer

    def draw(self):
        for edge in self.edges.values():
            edge.draw()

    def add_edge(self, edge):
        node, node2 = edge
        edge = (node, node2) if node.value < node2.value else (node2, node)
        if edge in self.edges_set:
            return False

        self.edges_set.add(edge)

        if edge in self.edges_being_removed_set:
            self.edges_being_removed_set.remove(edge)
        else:
            edge_obj = RbtEdge(*edge, visualizer=self.visualizer)
            self.edges[edge] = edge_obj
        return True

    def remove_edge(self, edge):
        if edge not in self.edges_set:
            return False
        self.edges_set.remove(edge)
        self.edges_being_removed_set.add(edge)

    def get_edge(self, edge):
        node, node2 = edge
        edge = (node, node2) if node.value < node2.value else (node2, node)
        if edge in self.edges_set or edge in self.edges_being_removed_set:
            return self.edges[edge]

        raise KeyError(f'Edge not found in Manager')


    def update(self):
        to_be_removed = set()
        for edge in self.edges_being_removed_set:
            if self.edges[edge].length_multiplier <= 0.0:
                del self.edges[edge]
                to_be_removed.add(edge)
        self.edges_being_removed_set.difference_update(to_be_removed)

    def edge_diffs(self, new_edges_set):
        edges_to_add = new_edges_set - self.edges_set
        edges_to_remove = self.edges_set - new_edges_set

        for edge in edges_to_add:
            self.add_edge(edge)

        for edge in edges_to_remove:
            self.remove_edge(edge)

        return edges_to_add, edges_to_remove

    def edge_diffs_with_animations(self, new_edges_set, add_frames=0, remove_frames=50):
        edges_to_add, edges_to_remove = self.edge_diffs(new_edges_set)
        bundle = []

        if add_frames > 0:
            for edge in edges_to_add:
                self.edges[edge].length_multiplier = 0.0
                bundle.append((Operation.CHANGE_LEN, (self.edges[edge], 1.0), add_frames))

        if remove_frames > 0:
            for edge in edges_to_remove:
                bundle.append((Operation.CHANGE_LEN, (self.edges[edge], 0.0), remove_frames))

        return bundle


        #
        # self.edges_set.update(edges_to_add)
        #
        # for edge in edges_to_add:
        #     self.edges[edge] = RbtEdge(*edge, self.visualizer, 1.0)
        #     # self.visualizer.animation_controller.add_animated_element((Operation.CHANGE_LEN, (self.edges[edge], 1.0), 50))
        #
        # anims = []
        # for edge in edges_to_remove:
        #     print('prrrt', edge)
        #     anims.append((Operation.CHANGE_LEN, (self.edges[edge], 0.0), 50))
        #     # del self.edges[edge]
        # if anims:
        #     self.visualizer.animation_controller.add_animated_element((Operation.BUNDLE, anims))
        #
        # self.edges_being_removed_set.update(edges_to_remove)
        # self.edges_set.difference_update(edges_to_remove)

