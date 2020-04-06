import math
from compas.geometry import Point
from compas.geometry import Frame
from compas.geometry import Transformation
from compas_fab.robots import Configuration
from compas_fab.backends.ik_analytical import fit_within_bounds
from compas_fab.backends.ik_analytical import inverse_kinematics_spherical_wrist


class InverseKinematicsSolver(object):
    """Create a custom InverseKinematicsSolver for a robot.
    """

    def __init__(self, robot, group, function, base_frame=None, tool_frame=None):

        self.robot = robot
        self.group = group
        self.joints = robot.get_configurable_joints(group=group)
        self.joint_names = robot.get_configurable_joint_names(group=group)
        self.function = function

        self.base_transformation = Transformation.from_frame(base_frame).inverse() if base_frame else None
        self.tool_transformation = Transformation.from_frame(tool_frame).inverse() if tool_frame else None

    def update_base_transformation(self, base_frame):
        self.base_transformation = Transformation.from_frame(base_frame).inverse()

    def convert_frame_wcf_to_frame_tool0_rcf(self, frame_wcf, base_transformation=None, tool_transformation=None):
        T = Transformation.from_frame(frame_wcf)
        if base_transformation:
            T = base_transformation * T
        if tool_transformation:
            T = T * tool_transformation
        return Frame.from_transformation(T)
        # return Frame.from_transformation(self.base_transformation * Transformation.from_frame(frame_wcf) * self.tool_transformation)

    def try_to_fit_configurations_between_bounds(self, configurations):
        """
        """
        j1, j2, j3, j4, j5, j6 = self.joints
        for i, c in enumerate(configurations):
            a1, a2, a3, a4, a5, a6 = c.values
            try:
                a1 = fit_within_bounds(a1, j1.limit.lower, j1.limit.upper)
                a2 = fit_within_bounds(a2, j2.limit.lower, j2.limit.upper)
                a3 = fit_within_bounds(a3, j3.limit.lower, j3.limit.upper)
                a4 = fit_within_bounds(a4, j4.limit.lower, j4.limit.upper)
                a5 = fit_within_bounds(a5, j5.limit.lower, j5.limit.upper)
                a6 = fit_within_bounds(a6, j6.limit.lower, j6.limit.upper)
                configurations[i].values = [a1, a2, a3, a4, a5, a6]
            except AssertionError:
                configurations[i] = None
        return configurations

    def add_joint_names_to_configurations(self, configurations):
        """
        """
        for i, c in enumerate(configurations):
            configurations[i].joint_names = self.joint_names[:]

    def inverse_kinematics_function(self):
        """
        """

        def inverse_kinematics(frame_WCF, start_configuration=None, group=None,
                               avoid_collisions=True, constraints=None,
                               attempts=8, attached_collision_meshes=None,
                               return_full_configuration=False,
                               cull_not_working=False,
                               return_closest_to_start=False):

            if start_configuration:
                base_frame = self.robot.get_base_frame(self.group, full_configuration=start_configuration)
                self.update_base_transformation(base_frame)
                # in_collision = self.robot.client.configuration_in_collision(start_configuration)
                # if in_collision:
                #    raise ValueError("Start configuration already in collision")

            # frame_tool0_RCF = self.convert_frame_wcf_to_frame_tool0_rcf(frame_WCF)
            frame_tool0_RCF = Frame.from_transformation(self.base_transformation * Transformation.from_frame(frame_WCF) * self.tool_transformation)

            # call the ik function
            configurations = self.function(frame_tool0_RCF)

            # The ik solution for 6 axes industrial robots returns by default 8
            # configurations, which are sorted. That means, the if you call ik
            # on 2 frames that are close to each other, and compare the 8
            # configurations of the first one with the 8 of the second one at
            # their respective indices, then these configurations are 'close' to
            # each other. That is why for certain use cases, e.g. custom cartesian
            # path planning it makes sense to keep the sorting and set the ones
            # that are out of joint limits or in collison to `None`.

            # add joint names to configurations
            self.add_joint_names_to_configurations(configurations)
            # fit configurations within joint bounds (sets those to `None` that are not working)
            self.try_to_fit_configurations_between_bounds(configurations)
            # check collisions for all configurations (sets those to `None` that are not working)
            if self.robot.client:
                self.robot.client.check_configurations_for_collision(configurations)

            if cull_not_working:
                configurations = [c for c in configurations if c is not None]

            if return_closest_to_start:
                # sort by diff
                return configurations[0]

            return configurations
        return inverse_kinematics


def joint_angles_to_configurations(A1, A2, A3, A4, A5, A6):
    return [Configuration.from_revolute_values([a1, a2, a3, a4, a5, a6]) for a1, a2, a3, a4, a5, a6 in zip(A1, A2, A3, A4, A5, A6)]


def ik_staubli_txl60(frame_rcf):

    p1 = Point(0.000, 0.000, 0.375)
    p2 = Point(0.000, 0.020, 0.775)
    p3 = Point(0.450, 0.020, 0.775)
    p4 = Point(0.520, 0.020, 0.775)

    A1, A2, A3, A4, A5, A6 = inverse_kinematics_spherical_wrist(p1, p2, p3, p4, frame_rcf)

    for i in range(8):
        A1[i] = -1 * A1[i]
        A2[i] = A2[i] + math.pi / 2
        A4[i] = A4[i] * -1
        A6[i] = A6[i] * -1 + math.pi / 2

    return joint_angles_to_configurations(A1, A2, A3, A4, A5, A6)


def ik_abb_irb4600_40_255(frame_rcf):

    p1 = Point(0.175, 0.000, 0.495)
    p2 = Point(0.175, 0.000, 1.590)
    p3 = Point(1.446, 0.000, 1.765)
    p4 = Point(1.581, 0.000, 1.765)

    A1, A2, A3, A4, A5, A6 = inverse_kinematics_spherical_wrist(p1, p2, p3, p4, frame_rcf)

    for i in range(8):
        A1[i] = -1 * A1[i]
        A2[i] = A2[i] + math.pi / 2
        A3[i] = A3[i] - math.pi / 2
        A4[i] = -1 * A4[i]
        A6[i] = -1 * A6[i] + math.pi/2

    return joint_angles_to_configurations(A1, A2, A3, A4, A5, A6)


if __name__ == "__main__":

    frame_rcf = Frame((0.600, 0.700, 1.000), (-1., 0., 0.), (0., 1., 0.))
    configurations = ik_abb_irb4600_40_255(frame_rcf)

    print("")
    frame_rcf = Frame((0.200, 0.200, 0.200), (-1., 0., 0.), (0., 1., 0.))
    configurations = ik_staubli_txl60(frame_rcf)
