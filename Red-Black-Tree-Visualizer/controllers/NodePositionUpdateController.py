from queue import Queue

from pygame import Vector2

from controllers.PathGenerator import PathGenerator


class NodePositionUpdateController:
    def __init__(self):
        self.update_queues = dict()

    def move_node(self, node, end_pos=None, steps=100):
        if end_pos is None:
            end_pos = node.dest_position
        start_pos = node.position

        item_tuple = self.update_queues.get(node, None)
        if item_tuple is None:
            q = Queue()
        else:
            q, last = item_tuple
            start_pos = last

        self.update_queues[node] = (q, end_pos)

        if Vector2(start_pos).distance_squared_to(Vector2(end_pos)) < 4:
            return

        position_list = PathGenerator.bezier_interp_position_list(start_pos, end_pos, point_number=steps)

        for pos in position_list:
            q.put(pos)

    def update(self):
        to_be_deleted = []
        for node, (q, last) in self.update_queues.items():
            if q.empty():
                to_be_deleted.append(node)
            else:
                node.update_position(q.get())

        for node in to_be_deleted:
            del self.update_queues[node]
