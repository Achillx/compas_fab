from __future__ import print_function
import math


class Configuration(object):
    """Represents a configuration of an RFL robot based on its
    coordinates (position of the gantry system) and joint angle values.

    Args:
        coordinates (:obj:`list` of :obj:`float`): Gantry position
            in x, y, z in meters.
        joint_values (:obj:`list` of :obj:`float`): 6 joint values
            expressed in degrees.
    """
    def __init__(self, coordinates, joint_values):
        if len(coordinates) != 3:
            raise ValueError('Expected 3 floats: x, y, z but got %d' % len(coordinates))
        if len(joint_values) != 6:
            raise ValueError('Expected 6 floats expressed in degrees, but got %d' % len(joint_values))

        self.coordinates = coordinates
        self.joint_values = joint_values

    def __str__(self):
        return "xyz: %s, joints: %s" % (self.coordinates, self.joint_values)

    @classmethod
    def from_list(cls, list_of_floats):
        angles = map(math.degrees, list_of_floats[3:])
        return cls(list_of_floats[0:3], angles)


# TODO: This should inherit from compas_fabrication.fabrication.robots.Robot
# once that is in place.
class Robot(object):
    """Represents an instance of the ABB robots of the Robotic Fabrication Lab.

    Communication to the robot is delegated to the `client` instance
    passed when initializing the robot.


    Args:
        id (:obj:`int`): Robot identifier.
        client (:obj:`object`): A client to execute the commands
            such as :class:`.Simulator`.
        index (:obj:`int`): Robot index (for internal use).
    """
    SUPPORTED_ROBOTS = (11, 12, 21, 22)
    ROBOT_SETTINGS = {
        11: {'name': 'A', 'base_coordinates': [7, -2, -4]},
        12: {'name': 'B', 'base_coordinates': [7, -10, -4]},
        21: {'name': 'C', 'base_coordinates': [30, -2, -4]},
        22: {'name': 'D', 'base_coordinates': [30, -10, -4]},
    }
    BASE_JOINT_VALUES = [0.] * 6

    def __init__(self, id, client=None):
        if id not in self.SUPPORTED_ROBOTS:
            raise ValueError('Robot ID is not valid, must be one of: ' + str(self.SUPPORTED_ROBOTS))
        self.id = id
        self.client = client
        self.name = self.ROBOT_SETTINGS[id]['name']
        self.index = self.SUPPORTED_ROBOTS.index(id)

    def set_config(self, config):
        """Moves the robot the the specified configuration.

        Args:
            config (:class:`.Configuration`): Instance of robot's
                configuration.

        Examples:

            >>> from compas_fabrication.fabrication.robots.rfl import Simulator
            >>> with Simulator() as simulator:
            ...     robot = Robot(11, simulator)
            ...     robot.set_config(Configuration(
            ...                      [7.6, -4.5, -4.5],
            ...                      [90, 0, 0, 0, 0, -90]))
            ...

        """
        self.client.set_robot_config(self, config)

    def get_config(self):
        """Gets the current configuration of the robot.

        Returns:
            config: Instance of (:class:`.Configuration`).
        """
        return self.client.get_robot_config(self)

    def reset_config(self):
        """Resets a robot's configuration to a safe initial position."""
        self.set_config(Configuration(coordinates=self.ROBOT_SETTINGS[self.id]['base_coordinates'],
                                      joint_values=self.BASE_JOINT_VALUES))
