class PathGenerator:
    @staticmethod
    def bezier_interpolation(p0, p1, p2, p3, t):
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        return x, y

    @staticmethod
    def bezier_interp_position_list(start_point, end_point, point_number=100, int_point1=None,
                                    int_point2=None, density_function=lambda x: 3 * x ** 2 - 2 * x ** 3):

        if int_point1 is None and int_point2 is not None:
            int_point1 = int_point2
        elif int_point2 is None and int_point1 is not None:
            int_point2 = int_point1
        elif int_point1 is None and int_point2 is None:
            int_point1 = start_point
            int_point2 = end_point

        positions = []

        for i in range(point_number):
            t = i / (point_number - 1)
            mapped_t = density_function(t)
            positions.append(PathGenerator.bezier_interpolation(
                start_point, int_point1, int_point2, end_point, mapped_t
            ))

        return positions

