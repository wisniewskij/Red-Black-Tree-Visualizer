from queue import Queue

from pygame import Vector2

from controllers.PathGenerator import PathGenerator


class EdgeLengthUpdateController:
    def __init__(self):
        self.update_queues = dict()

    def change_len(self, edge, target_len_mult, steps=100):
        start_len_mult = edge.length_multiplier

        item_tuple = self.update_queues.get(edge, None)
        if item_tuple is None:
            q = Queue()
        else:
            q, last = item_tuple
            start_len_mult = last

        self.update_queues[edge] = (q, target_len_mult)

        if abs(target_len_mult - start_len_mult) < 0.01:
            return

        position_list = PathGenerator.bezier_interp_position_list((start_len_mult, 0),
                                                                  (target_len_mult, 0), point_number=steps)

        for pos in position_list:
            q.put(pos[0])

    def update(self):
        to_be_deleted = []
        for edge, (q, last) in self.update_queues.items():
            if q.empty():
                to_be_deleted.append(edge)
            else:
                edge.update_length_multiplier(q.get())

        for edge in to_be_deleted:
            del self.update_queues[edge]
