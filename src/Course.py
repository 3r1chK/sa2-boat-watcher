# Course.py
from typing import List, Tuple
from pyproj import Geod
from src.Utils import Utils


# Initialize the geodetic converter for WGS84
g = Geod(ellps='WGS84')

# Define  a type for a point (latitude, longitude)
Point = Tuple[float, float]
# Define a type for a vector (direction in degrees, length in meters)
Vector = Tuple[float, float]


class Course:
    points: List[Point]
    vectors = List[Vector]

    def __init__(self, points: List[Point], vectors: List[Vector]):
        self.points = points
        self.vectors = vectors

    def rotate(self, degrees):
        resulting_vectors = []
        # Apply the new angle to each vector
        for i in range(len(self.vectors)):
            resulting_vectors.append([Utils.degree_sum(self.vectors[i][0], degrees), self.vectors[i][1]])
        self.vectors = resulting_vectors
        # Compute the new course
        new_course = Course.create_course(self.points[0], self.vectors)
        self.points = new_course.points
        self.vectors = new_course.vectors

    def move(self, direction, length):
        # Move the origin and then (re)compute the course
        lat, lon = self.points[0]
        lon, lat, _ = g.fwd(lon, lat, direction, length)
        new_course = Course.create_course((lat, lon), self.vectors)
        self.points = new_course.points
        self.vectors = new_course.vectors

    def get_port_buoys(self, point_index, port_direction, port_length):
        """
            Returns a couple of point coordinates representing the port and starboard buoy of a route port
        """
        lat, lon = self.points[point_index]
        # Compute buoy positions (direction at 90° respect the port)
        port_buoy_direction = Utils.degree_sum(port_direction, -90)
        starboard_buoy_direction = Utils.degree_sum(port_direction, 90)

        port_buoy_lon, port_buoy_lat, _ = g.fwd(lon, lat, port_buoy_direction, (port_length / 2))
        starboard_buoy_lon, starboard_buoy_lat, _ = g.fwd(lon, lat, starboard_buoy_direction, (port_length / 2))

        return [(port_buoy_lat, port_buoy_lon), (starboard_buoy_lat, starboard_buoy_lon)]

    def __str__(self,
                     start_line_orientation: float = 0, start_line_length: float = 100,
                     end_line_orientation: float = 180, end_line_length: float = 100
                 ):
        # Print the start line
        start_buoys = self.get_port_buoys(0, start_line_orientation, start_line_length)
        print("- Start line:")
        print(f"\tPort buoy:\t({start_buoys[0][0]:.5f}, {start_buoys[0][1]:.5f})")
        print(f"\tStarboard buoy:\t({start_buoys[1][0]:.5f}, {start_buoys[1][1]:.5f})")

        # Print each buoy in the middle
        for i, point in enumerate(self.points[1:-1], 1):
            print(f"- Buoy n.{i}:\t\t({point[0]:.5f}, {point[1]:.5f})")

        # Print the end line
        end_buoys = self.get_port_buoys(len(self.points) - 1, end_line_orientation, end_line_length)
        print("- End line:")
        print(f"\tPort buoy:\t({end_buoys[0][0]:.5f}, {end_buoys[0][1]:.5f})")
        print(f"\tStarboard buoy:\t({end_buoys[1][0]:.5f}, {end_buoys[1][1]:.5f})")

    @staticmethod
    def init_from_origin_and_legs(origin: Point, legs: List[Vector]):
        return Course.create_course(origin, legs)

    @staticmethod
    def create_course(origin: Point, vectors: List[Vector]):
        lat, lon = origin
        course: List[Point] = [(lat, lon)]

        # Loop through the list of vectors
        for direction, length in vectors:
            # Find the end point given a start point, bearing, and distance
            end_lon, end_lat, _ = g.fwd(lon, lat, direction, length)
            course.append((end_lat, end_lon))
            lat, lon = end_lat, end_lon  # Update current point

        return Course(course, vectors)


def course_creation_example():
    # Example usage:
    # Define origin lat and lon
    # origin: Point = (40.0, -100.9)
    # vectors: List[Vector] = [(0,10000), (90,5000), (180, 15000)] # Example: [(north, 10km), (est, 5km), (south, 15km)]
    origin: Point = (0.0, 0.0)
    vectors: List[Vector] = [  # Degrees, meters
        # Leg1 -> 104°, 3643.28 meters
        (104, 3643.2786885245895974),
        # Leg2 -> 256°, 3643.28 meters
        (256, 3643.2786885245895974),
        # Leg3 -> 104°, 3643.28 meters
        (104, 3643.2786885245895974),
        # Leg4 -> 256°, 3643.28 meters
        (256, 3643.2786885245895974),
        # Leg5 -> 104°, 3643.28 meters
        (104, 3643.2786885245895974),
        # Leg6 -> 256°, 4007.61 meters
        (256, 4007.6065573770488299)
    ]

    # Create the course
    course: Course = Course.create_course(origin, vectors)
    # Print the resulting course
    course.__str__(
        start_line_orientation=90, start_line_length=100,
        end_line_orientation=270, end_line_length=100
    )

    print("--- --- --- ---")

    # Rotate and move the course
    course.rotate(60)
    course.move(90, 1500)

    # Print the resulting course
    course.__str__(
        start_line_orientation=Utils.degree_sum(90, 60), start_line_length=100,
        end_line_orientation=Utils.degree_sum(270, 60), end_line_length=100
    )


if __name__ == "__main__":
    course_creation_example()
