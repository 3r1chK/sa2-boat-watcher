# course_generator.py
from typing import List
from src.Course import Point, Vector, Course
from src.Utils import Utils


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
