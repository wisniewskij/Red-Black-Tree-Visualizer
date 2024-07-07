from pygame import Vector2

from utility.gui import drawAALine


class RbtEdge:
    def __init__(self, node1, node2, visualizer, length_multiplier=1.0):
        self.node1, self.node2 = (node1, node2) if node1.value < node2.value else (node2, node1)
        self.length_multiplier = length_multiplier
        self.visualizer = visualizer

    def __str__(self):
        return f'({self.node1}, {self.node2}, {self.length_multiplier})'

    def __repr__(self):
        return f'({self.node1}, {self.node2}, {self.length_multiplier})'

    def update_length_multiplier(self, length_multiplier):
        self.length_multiplier = length_multiplier

    def draw(self, thickness=3.0):
        if self.length_multiplier < 0.001:
            return

        position1, position2 = Vector2(self.node1.position), Vector2(self.node2.position)
        if self.length_multiplier < 1.0:
            position_diff = position1.distance_to(position2)
            position1.move_towards_ip(position2, int(position_diff * (1.0 - self.length_multiplier) / 2))
            position2.move_towards_ip(position1, int(position_diff * (1.0 - self.length_multiplier) / 2))

        drawAALine(self.visualizer, position1, position2, thickness)
