from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

import compas.robots.model
from compas.geometry import Frame
from compas.geometry.xforms import Transformation

from .configuration import Configuration
from .semantics import RobotSemantics
from .urdf_importer import UrdfImporter

LOGGER = logging.getLogger('compas_fab.robots.robot')

__all__ = [
    'Robot',
]


class Robot(object):
    """Represents a **robot** instance.

    This class binds together several building blocks, such as the robot's descriptive model,
    its semantic information and an instance of a backend client
    into a cohesive programmable interface. This representation builds upon the model
    described in the class :class:`compas.robots.Robot` of the **COMPAS** framework.

    Attributes
    ----------
    robot_model : :class:`compas.robots.Robot`
        The robot model, usually created out of an URDF structure.
    semantics : :class:`RobotSemantics`, optional
        The semantic model of the robot.
    client : optional
        The backend client to use for communication, e.g. :class:`RosClient`
    name : :obj:`str`
        The name of the robot
    """

    def __init__(self, robot_model, semantics=None, client=None):
        self.model = robot_model
        self.semantics = semantics
        self.client = client  # setter and getter

        # TODO: if client is ros client: tell urdf importer...
        # should be corrected by self.model
        self.RCF = Frame.worldXY()

    @classmethod
    def basic(cls, name, **kwargs):
        """Convenience method to create the most basic instance of a robot, based only on a name.

        Parameters
        ----------
        name : str
            Name of the robot

        Returns
        -------
        :class:`Robot`
            Newly created instance of a robot.
        """
        model = compas.robots.model.Robot(name, joints=[], links=[], materials=[], **kwargs)
        return cls(model)

    @classmethod
    def from_urdf_model(cls, urdf_model, client=None):
        urdf_importer = UrdfImporter.from_urdf_model(urdf_model)
        return cls(urdf_model, None, client)

    @classmethod
    def from_urdf_and_srdf_models(cls, urdf_model, srdf_model, client=None):
        urdf_importer = UrdfImporter.from_urdf_model(urdf_model)
        return cls(urdf_model, srdf_model, client)

    @classmethod
    def from_resource_path(cls, directory, client=None):
        """Creates a robot from a directory with the necessary resource files.

        The directory must contain a .urdf, a .srdf file and a directory with
        the robot's geometry as indicated in the urdf file.
        """
        urdf_importer = UrdfImporter.from_robot_resource_path(directory)
        urdf_file = urdf_importer.urdf_filename
        srdf_file = urdf_importer.srdf_filename
        urdf_model = compas.robots.model.Robot.from_urdf_file(urdf_file)
        srdf_model = RobotSemantics.from_srdf_file(srdf_file, urdf_model)
        return cls(urdf_model, srdf_model, client)

    @property
    def name(self):
        """Name of the robot, as defined by its model

        Returns
        -------
        str
            Name of the robot.
        """

        return self.model.name

    @property
    def group_names(self):
        self.ensure_semantics()
        return self.semantics.group_names

    @property
    def main_group_name(self):
        self.ensure_semantics()
        return self.semantics.main_group_name

    def get_end_effector_link_name(self, group=None):
        if not self.semantics:
            return self.model.get_end_effector_link_name()
        else:
            return self.semantics.get_end_effector_link_name(group)

    def get_end_effector_link(self, group=None):
        name = self.get_end_effector_link_name(group)
        return self.model.get_link_by_name(name)

    def get_end_effector_frame(self, group=None):
        link = self.get_end_effector_link(group)
        return link.parent_joint.origin.copy()

    def get_base_link_name(self, group=None):
        if not self.semantics:
            return self.model.get_base_link_name()
        else:
            return self.semantics.get_base_link_name(group)

    def get_base_link(self, group=None):
        name = self.get_base_link_name(group)
        return self.model.get_link_by_name(name)

    def get_base_frame(self, group=None):
        link = self.get_base_link(group)
        for joint in link.joints:
            if joint.type == "fixed":
                return joint.origin.copy()
        else:
            return Frame.worldXY()

    def get_configurable_joints(self, group=None):
        if self.semantics:
            return self.semantics.get_configurable_joints(group)
        else:
            return self.model.get_configurable_joints()

    def get_configurable_joint_names(self, group=None):
        if self.semantics:
            return self.semantics.get_configurable_joint_names(group)
        else:
            # passive joints are only defined in the semantic model,
            # so we just get the ones that are configurable
            return self.model.get_configurable_joint_names()

    @property
    def transformation_RCF_WCF(self):
        # transformation matrix from world coordinate system to robot coordinate system
        return Transformation.from_frame_to_frame(Frame.worldXY(), self.RCF)

    @property
    def transformation_WCF_RCF(self):
         # transformation matrix from robot coordinate system to world coordinate system
        return Transformation.from_frame_to_frame(self.RCF, Frame.worldXY())

    def set_RCF(self, robot_coordinate_frame):
        self.RCF = robot_coordinate_frame

    def get_configuration(self, group=None):
        """Returns the current joint configuration.
        """
        positions = []
        types = []

        for joint in self.get_configurable_joints(group):
            positions.append(joint.position)
            types.append(joint.type)

        return Configuration(positions, types)

    def update(self, configuration, group=None, collision=False):
        """
        """
        names = self.get_configurable_joint_names(group)
        self.model.update(names, configuration.values, collision)

    def ensure_client(self):
        if not self.client:
            raise Exception('This method is only callable once a client is assigned')

    def ensure_semantics(self):
        if not self.semantics:
            raise Exception('This method is only callable once a semantic model is assigned')

    def inverse_kinematics(self, frame):
        self.ensure_client()
        raise NotImplementedError
        configuration = self.client.inverse_kinematics(frame)
        return configuration

    def forward_kinematics(self, configuration):
        self.ensure_client()
        raise NotImplementedError

    def compute_cartesian_path(self, frames):
        self.ensure_client()
        raise NotImplementedError

    def send_frame(self):
        # (check service name with ros)
        self.ensure_client()
        raise NotImplementedError

    def send_configuration(self):
        # (check service name with ros)
        self.ensure_client()
        raise NotImplementedError

    def send_trajectory(self):
        # (check service name with ros)
        self.ensure_client()
        raise NotImplementedError

    @property
    def frames(self):
        return self.model.get_frames(self.transformation_RCF_WCF)

    @property
    def axes(self):
        return self.model.get_axes(self.transformation_RCF_WCF)

    def draw_visual(self):
        return self.model.draw_visual(self.transformation_RCF_WCF)

    def draw_collision(self):
        return self.model.draw_collision(self.transformation_RCF_WCF)

    def draw(self):
        return self.model.draw()

    def scale(self, factor):
        """Scale the robot.
        """
        self.model.scale(factor)

    @property
    def scale_factor(self):
        return self.model.scale_factor


if __name__ == "__main__":
    pass
