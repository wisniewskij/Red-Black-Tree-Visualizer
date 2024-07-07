from queue import Queue

from controllers.PathGenerator import PathGenerator
from utility.enums import Operation, Color


class AnimationController:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.curr_animated_elements = []
        self.anim_queue = Queue()
        self.node_update_set = set()
        self.curr_animated_color_nodes = []


    def add_animated_element(self, animated_element):
        self.anim_queue.put(animated_element)

    def idle(self):
        return self.anim_queue.empty() and len(self.curr_animated_elements) == 0

    def update(self):
        if len(self.curr_animated_elements) == 0 and not self.anim_queue.empty():
            queue_front = self.anim_queue.get()
            if queue_front[0] == Operation.BUNDLE:
                for operation in queue_front[1]:
                    self.curr_animated_elements.append((operation[0], operation[1], operation[2], 0))
            else:
                self.curr_animated_elements.append((queue_front[0], queue_front[1], queue_front[2], 0))

        for i in range(len(self.curr_animated_elements)):
            length_proportion = self.curr_animated_elements[i][3] / self.curr_animated_elements[i][2]
            if self.curr_animated_elements[i][0] == Operation.INSERT and self.curr_animated_elements[i][3] == 0:
                node, node_pos = self.curr_animated_elements[i][1]
                self.visualizer.node_position_update_controller.move_node(node, node_pos, self.curr_animated_elements[i][2])
            elif self.curr_animated_elements[i][0] == Operation.HIGHLIGHT:
                node = self.curr_animated_elements[i][1]
                node.outline_color = Color.HIGHLIGHT_YELLOW.value
                if length_proportion <= 0.2:
                    node.radius_mult = (1 + 0.1 * (length_proportion / 0.2) ** 2)
                elif length_proportion <= 0.8:
                    node.radius_mult = (1 + 0.1)
                else:
                    node.radius_mult = (1 + 0.1 * ((1 - length_proportion) / 0.2) ** 2)
            elif self.curr_animated_elements[i][0] == Operation.MOVE and self.curr_animated_elements[i][3] == 0:
                node, node_pos = self.curr_animated_elements[i][1]
                self.visualizer.node_position_update_controller.move_node(node, node_pos, self.curr_animated_elements[i][2])
            elif self.curr_animated_elements[i][0] == Operation.CHANGE_COLOR:
                if self.curr_animated_elements[i][3] == 0:
                    self.curr_animated_color_nodes = [node for node in self.node_update_set]
                    self.node_update_set.clear()
                for node in self.curr_animated_color_nodes:
                    node.additional_circle_radius_mult = ((2 ** ((1 - length_proportion) * 5)) - 1) / 31
            elif self.curr_animated_elements[i][0] == Operation.CHANGE_LEN and self.curr_animated_elements[i][3] == 0:
                edge, edge_mult = self.curr_animated_elements[i][1]
                self.visualizer.edge_length_update_controller.change_len(edge, edge_mult, self.curr_animated_elements[i][2])


        to_be_deleted = []
        if len(self.curr_animated_elements) != 0:
            for i in range(len(self.curr_animated_elements)):
                self.curr_animated_elements[i] = (
                    self.curr_animated_elements[i][0],
                    self.curr_animated_elements[i][1],
                    self.curr_animated_elements[i][2],
                    self.curr_animated_elements[i][3] + 1
                )
                if self.curr_animated_elements[i][2] == self.curr_animated_elements[i][3]:
                    to_be_deleted.append(i)

                    if self.curr_animated_elements[i][0] == Operation.HIGHLIGHT:
                        self.curr_animated_elements[i][1].radius_mult = 1.0
                    elif self.curr_animated_elements[i][0] == Operation.CHANGE_COLOR:
                        self.curr_animated_color_nodes = []


        self.curr_animated_elements = [
            elem for i, elem in enumerate(self.curr_animated_elements) if i not in to_be_deleted
            ]
