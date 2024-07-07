import pygame

from utility.gui import drawTextWithOutline
from utility.enums import RbtColor, Color


class RbtNode:
    def __init__(self, value, nil, color=RbtColor.BLACK.value, quantity=1, subtree_size=1, visualizer=None,
                 position=(0, 0), dest_position=(0, 0), radius=0):
        self.value = value
        self.quantity = quantity
        self.parent = nil
        self.right = nil
        self.left = nil
        self.color = color
        self.subtree_size = subtree_size  # including the node itself
        self.nil = nil

        self.visualizer = visualizer
        self.position = position
        self.dest_position = dest_position
        self.radius = radius
        self.radius_mult = 1.0
        self.child_side_offset_mult = 2

        self.additional_circle_radius_mult = 0.0
        self.additional_circle_color = Color.BLACK.value

        self.recently_added = True
        self.being_deleted = False



    def __str__(self):
        return f'({self.value}, {self.quantity})'

    def __repr__(self):
        return f'({self.value}, {self.quantity}, {"Black" if self.color else "Red"}, {self.subtree_size}, {self.position}, {self.radius})'

    def update_position(self, position):
        self.position = position

    def clear_additional_circle(self):
        self.additional_circle_radius_mult = 0

    def is_left_child(self):
        return self is self.parent.left

    def is_right_child(self):
        return self is self.parent.right

    def set_additional_circle(self, radius, color=Color.BLACK.value):
        self.additional_circle_radius_mult = radius
        self.additional_circle_color = color

    def set_color(self, color):
        if self.color == color:
            return
        else:
            if self.additional_circle_radius_mult < 1.0:
                self.set_additional_circle(
                    1.0, Color.BLACK.value if self.color == RbtColor.BLACK.value else Color.RED.value
                )
            self.color = color
            if self not in self.visualizer.animation_controller.node_update_set:
                self.visualizer.animation_controller.node_update_set.add(self)

    def get_transformed_position(self):
        zoom = self.visualizer.zoom
        x_transformed = int((self.position[0] + self.visualizer.x_offset) * zoom)
        y_transformed = int((self.position[1] + self.visualizer.y_offset) * zoom)
        return x_transformed, y_transformed

    def draw(self):
        zoom = self.visualizer.zoom
        x_transformed, y_transformed = self.get_transformed_position()

        # Outline
        for i in range(1):
            pygame.draw.circle(
                self.visualizer.screen, Color.OUTLINE_BLACK.value, (x_transformed, y_transformed),
                int(self.radius * self.radius_mult * zoom),
            )


        # Filling
        pygame.draw.circle(
            self.visualizer.screen,
            Color.BLACK.value if self.color == RbtColor.BLACK.value else Color.RED.value,
            (x_transformed, y_transformed),
            int(self.radius * self.radius_mult * zoom),
            0
        )

        # Additional circle
        if self.additional_circle_radius_mult > 0:
            pygame.draw.circle(
                self.visualizer.screen,
                self.additional_circle_color,
                (x_transformed, y_transformed),
                int(self.radius * self.additional_circle_radius_mult * self.radius_mult * zoom),
                0
            )


        # Value
        drawTextWithOutline(self.visualizer, str(self.value), 'Helvetica', int(self.radius * 1.5 * zoom),
                            Color.WHITE.value, x_transformed, y_transformed, 1.8 * self.radius * zoom)


