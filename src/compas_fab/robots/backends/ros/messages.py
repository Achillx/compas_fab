from compas.geometry import Frame
from compas.robots.model.geometry import SCALE_FACTOR

from compas.geometry.transformations import basis_vectors_from_matrix
from compas.geometry.transformations import matrix_from_quaternion

__all__ = ['AttachedCollisionObject', 'CollisionObject', 'Constraints',
           'Header', 'JointState', 'JointTrajectory', 'JointTrajectoryPoint',
           'Mesh', 'MoveItErrorCodes', 'MultiDOFJointState',
           'MultiDOFJointTrajectory', 'MultiDOFJointTrajectoryPoint',
           'ObjectType', 'Plane', 'Pose', 'PoseStamped', 'PositionIKRequest',
           'ROSmsg', 'RobotState', 'RobotTrajectory', 'SolidPrimitive', 'Time']


class ROSmsg(object):
    """The base class for ros messages.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def msg(self):
        msg = {}
        for key, value in self.__dict__.items():
            if hasattr(value, 'msg'):
                msg[key] = value.msg
            elif isinstance(value, list):
                if len(value):
                    if hasattr(value[0], 'msg'):
                        msg[key] = [v.msg for v in value]
                    else:
                        msg[key] = value
                else:
                    msg[key] = value
            else:
                msg[key] = value
        return msg

    @classmethod
    def from_msg(cls, msg):
        return cls(**msg)

    def __str__(self):
        return str(self.msg)

# ------------------------------------------------------------------------------
# std_msgs
# ------------------------------------------------------------------------------


class Time(ROSmsg):
    def __init__(self, secs=0., nsecs=0.):
        self.secs = secs
        self.nsecs = nsecs


class Header(ROSmsg):
    """http://docs.ros.org/melodic/api/std_msgs/html/msg/Header.html
    """

    def __init__(self, seq=0, stamp=Time(), frame_id='/world'):
        self.seq = seq
        self.stamp = stamp
        self.frame_id = frame_id

# ------------------------------------------------------------------------------
# geometry_msgs
# ------------------------------------------------------------------------------


class Pose(Frame):
    """Represents a robot pose.

    In principal the ``Pose`` is a wrapper object around the frame to derive
    rosbridge messages therefrom.

    Examples:
        >>> f = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> p1 = Pose.from_frame(f)
        >>> msg = p1.msg
        >>> p2 = Pose.from_msg(msg)
        >>> print(p1 == p2)
    """

    @classmethod
    def from_frame(cls, frame):
        return cls(frame.point, frame.xaxis, frame.yaxis)

    @property
    def frame(self):
        return Frame(self.point, self.xaxis, self.yaxis)

    @classmethod
    def from_msg(cls, msg):
        point = [msg['position']['x'] * SCALE_FACTOR,
                 msg['position']['y'] * SCALE_FACTOR,
                 msg['position']['z'] * SCALE_FACTOR]
        quaternion = [msg['orientation']['w'], msg['orientation']['x'],
                      msg['orientation']['y'], msg['orientation']['z']]
        R = matrix_from_quaternion(quaternion)
        xaxis, yaxis = basis_vectors_from_matrix(R)
        return cls(point, xaxis, yaxis)

    @property
    def msg(self):
        """Returns the pose as dictionary to use with rosbridge.

        http://docs.ros.org/kinetic/api/geometry_msgs/html/msg/Pose.html
        """
        pose = {}
        pose['position'] = {'x': self.point[0]/SCALE_FACTOR,
                            'y': self.point[1]/SCALE_FACTOR,
                            'z': self.point[2]/SCALE_FACTOR}
        qw, qx, qy, qz = self.quaternion
        pose['orientation'] = {'x': qx, 'y': qy, 'z': qz, 'w': qw}
        return pose


class PoseStamped(ROSmsg):
    """http://docs.ros.org/melodic/api/geometry_msgs/html/msg/PoseStamped.html
    """

    def __init__(self, header=Header(), pose=Pose.worldXY()):
        self.header = header
        self.pose = pose


class Transform(ROSmsg):
    """http://docs.ros.org/kinetic/api/geometry_msgs/html/msg/Transform.html
    """
    pass

# ------------------------------------------------------------------------------
# sensor_msgs
# ------------------------------------------------------------------------------


class JointState(ROSmsg):
    """http://docs.ros.org/kinetic/api/sensor_msgs/html/msg/JointState.html
    """

    def __init__(self, header=Header(), name=[], position=[], velocity=[],
                 effort=[]):
        self.header = header
        self.name = name
        self.position = position
        self.velocity = velocity
        self.effort = effort

    @classmethod
    def from_name_and_position(cls, name, position):
        return cls(Header(), name, position, [], [])

    @classmethod
    def from_msg(cls, msg):
        header = Header.from_msg(msg['header'])
        name = msg['name']
        position = msg['position']
        velocity = msg['velocity']
        effort = msg['effort']
        return cls(header, name, position, velocity, effort)


class MultiDOFJointState(ROSmsg):
    """http://docs.ros.org/kinetic/api/sensor_msgs/html/msg/MultiDOFJointState.html
    """

    def __init__(self, header=Header(), joint_names=[], transforms=[], twist=[],
                 wrench=[]):
        self.header = header
        self.joint_names = joint_names
        self.transforms = transforms
        self.twist = twist
        self.wrench = wrench

# ------------------------------------------------------------------------------
# trajectory_msgs
# ------------------------------------------------------------------------------


class JointTrajectoryPoint(ROSmsg):
    """http://docs.ros.org/kinetic/api/trajectory_msgs/html/msg/JointTrajectoryPoint.html
    """

    def __init__(self, positions=[], velocities=[], accelerations=[], effort=[], time_from_start=Time()):
        self.positions = positions
        self.velocities = velocities
        self.accelerations = accelerations
        self.effort = effort
        self.time_from_start = time_from_start

    @classmethod
    def from_msg(cls, msg):
        time_from_start = Time.from_msg(msg['time_from_start'])
        return cls(msg['positions'], msg['velocities'], msg['accelerations'], msg['effort'], time_from_start)


class JointTrajectory(ROSmsg):
    """http://docs.ros.org/kinetic/api/trajectory_msgs/html/msg/JointTrajectory.html
    """

    def __init__(self, header=Header(), joint_names=[], points=[]):
        self.header = header
        self.joint_names = joint_names  # string[]
        self.points = points  # JointTrajectoryPoint[]

    @classmethod
    def from_msg(cls, msg):
        header = Header.from_msg(msg['header'])
        joint_names = msg['joint_names']
        points = [JointTrajectoryPoint.from_msg(
            item) for item in msg['points']]
        return cls(header, joint_names, points)


class MultiDOFJointTrajectoryPoint(ROSmsg):
    """http://docs.ros.org/kinetic/api/trajectory_msgs/html/msg/MultiDOFJointTrajectoryPoint.html
    """

    def __init__(self, transforms=[], velocities=[], accelerations=[], time_from_start=Time()):
        self.transforms = transforms  # geometry_msgs/Transform[]
        self.velocities = velocities  # geometry_msgs/Twist[]
        self.accelerations = accelerations  # geometry_msgs/Twist[]
        self.time_from_start = time_from_start  # duration


class MultiDOFJointTrajectory(ROSmsg):
    """http://docs.ros.org/kinetic/api/trajectory_msgs/html/msg/MultiDOFJointTrajectory.html
    """

    def __init__(self, header=Header(), joint_names=[], points=[]):
        self.header = header
        self.joint_names = joint_names  # string[]
        self.points = points  # trajectory_msgs/MultiDOFJointTrajectoryPoint[]

    @classmethod
    def from_msg(cls, msg):
        header = Header.from_msg(msg['header'])
        joint_names = msg['joint_names']
        points = [MultiDOFJointTrajectoryPoint.from_msg(
            item) for item in msg['points']]
        return cls(header, joint_names, points)


# ------------------------------------------------------------------------------
# object_recognition_msgs
# ------------------------------------------------------------------------------


class ObjectType(ROSmsg):
    """http://docs.ros.org/kinetic/api/object_recognition_msgs/html/msg/ObjectType.html
    """

    def __init__(self, key="key", db="db"):
        self.key = key
        self.db = db

# ------------------------------------------------------------------------------
# shape_msgs
# ------------------------------------------------------------------------------


class SolidPrimitive(ROSmsg):
    """http://docs.ros.org/kinetic/api/shape_msgs/html/msg/SolidPrimitive.html
    """
    BOX = 1
    SPHERE = 2
    CYLINDER = 3
    CONE = 4
    BOX_X = 0
    BOX_Y = 1
    BOX_Z = 2
    SPHERE_RADIUS = 0
    CYLINDER_HEIGHT = 0
    CYLINDER_RADIUS = 1
    CONE_HEIGHT = 0
    CONE_RADIUS = 1

    def __init__(self, type=1, dimensions=[1, 1, 1]):
        self.type = type
        self.dimensions = dimensions


class Mesh(ROSmsg):
    """http://docs.ros.org/kinetic/api/shape_msgs/html/msg/Mesh.html
    """

    def __init__(self, triangles=[], vertices=[]):
        self.triangles = triangles
        self.vertices = vertices


class Plane(ROSmsg):
    """http://docs.ros.org/kinetic/api/shape_msgs/html/msg/Plane.html
    """

    def __init__(self, coef):
        self.coef = coef

# ------------------------------------------------------------------------------
# moveit_msgs
# ------------------------------------------------------------------------------


class CollisionObject(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/CollisionObject.html
    """
    ADD = 0
    REMOVE = 1
    APPEND = 2
    MOVE = 3

    def __init__(self, header=Header(), id="collision_obj", type=ObjectType(),
                 primitives=[], primitive_poses=[], meshes=[], mesh_poses=[],
                 planes=[], plane_poses=[], operation=0):
        self.header = header
        self.id = id
        self.type = type
        self.primitives = primitives
        self.primitive_poses = primitive_poses
        self.meshes = meshes
        self.mesh_poses = mesh_poses
        self.planes = planes
        self.plane_poses = plane_poses
        self.operation = operation  # ADD or REMOVE or APPEND or MOVE


class AttachedCollisionObject(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/AttachedCollisionObject.html
    """

    def __init__(self, link_name='ee_link', object=CollisionObject(),
                 touch_links=[], detach_posture=JointTrajectory(), weight=0):
        self.link_name = link_name
        self.object = object
        self.touch_links = touch_links
        self.detach_posture = detach_posture
        self.weight = weight


class Constraints(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/Constraints.html
    """

    def __init__(self, name='', joint_constraints=[], position_constraints=[],
                 orientation_constraints=[], visibility_constraints=[]):
        self.name = name
        self.joint_constraints = joint_constraints
        self.position_constraints = position_constraints
        self.orientation_constraints = orientation_constraints
        self.visibility_constraints = visibility_constraints


class RobotState(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/RobotState.html
    """

    def __init__(self, joint_state=JointState(),
                 multi_dof_joint_state=MultiDOFJointState(),
                 attached_collision_objects=[], is_diff=False):
        self.joint_state = joint_state
        self.multi_dof_joint_state = multi_dof_joint_state
        self.attached_collision_objects = attached_collision_objects
        self.is_diff = is_diff

    @classmethod
    def from_msg(cls, msg):
        joint_state = JointState.from_msg(msg['joint_state'])
        multi_dof_joint_state = MultiDOFJointState.from_msg(
            msg['multi_dof_joint_state'])
        attached_collision_objects = [AttachedCollisionObject.from_msg(
            item) for item in msg['attached_collision_objects']]
        return cls(joint_state, multi_dof_joint_state, attached_collision_objects, msg['is_diff'])


class PositionIKRequest(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/PositionIKRequest.html

    Examples
    --------
    >>> base_link = 'base_link'
    >>> planning_group = 'manipulator'
    >>> pose = Pose([420, -25, 459], [1, 0, 0], [0, 1, 0])
    >>> joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint',
                       'elbow_joint', 'wrist_1_joint', 'wrist_2_joint',
                       'wrist_3_joint']
    >>> joint_positions = [3.39, -1.47, -2.05, 0.38, -4.96, -6.28]
    >>> header = Header(frame_id='base_link')
    >>> pose_stamped = PoseStamped(header, pose)
    >>> joint_state = JointState(name=joint_names, position=joint_positions,
                                 header=header)
    >>> multi_dof_joint_state = MultiDOFJointState(header=header,
                                                   joint_names=joint_names)
    >>> start_state = RobotState(joint_state, multi_dof_joint_state)
    >>> ik_request = PositionIKRequest(group_name=planning_group,
                                       robot_state=start_state,
                                       pose_stamped=pose_stamped,
                                       avoid_collisions=True)
    """

    def __init__(self, group_name="robot", robot_state=RobotState(),
                 constraints=Constraints(), pose_stamped=PoseStamped(),
                 timeout=1.0, attempts=8, avoid_collisions=True):
        self.group_name = group_name
        self.robot_state = robot_state
        self.constraints = constraints
        self.avoid_collisions = avoid_collisions
        self.pose_stamped = pose_stamped
        self.timeout = timeout
        self.attempts = attempts


class RobotTrajectory(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/RobotTrajectory.html
    """

    def __init__(self, joint_trajectory=JointTrajectory(),
                 multi_dof_joint_trajectory=MultiDOFJointTrajectory()):
        self.joint_trajectory = joint_trajectory
        self.multi_dof_joint_trajectory = multi_dof_joint_trajectory

    @classmethod
    def from_msg(cls, msg):
        joint_trajectory = JointTrajectory.from_msg(msg['joint_trajectory'])
        multi_dof_joint_trajectory = MultiDOFJointTrajectory.from_msg(
            msg['multi_dof_joint_trajectory'])
        return cls(joint_trajectory, multi_dof_joint_trajectory)


class MoveItErrorCodes(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/msg/MoveItErrorCodes.html
    """
    # overall behavior
    SUCCESS = 1
    FAILURE = 99999

    PLANNING_FAILED = -1
    INVALID_MOTION_PLAN = -2
    MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE = -3
    CONTROL_FAILED = -4
    UNABLE_TO_AQUIRE_SENSOR_DATA = -5
    TIMED_OUT = -6
    PREEMPTED = -7

    # planning & kinematics request errors
    START_STATE_IN_COLLISION = -10
    START_STATE_VIOLATES_PATH_CONSTRAINTS = -11

    GOAL_IN_COLLISION = -12
    GOAL_VIOLATES_PATH_CONSTRAINTS = -13
    GOAL_CONSTRAINTS_VIOLATED = -14

    INVALID_GROUP_NAME = -15
    INVALID_GOAL_CONSTRAINTS = -16
    INVALID_ROBOT_STATE = -17
    INVALID_LINK_NAME = -18
    INVALID_OBJECT_NAME = -19

    # system errors
    FRAME_TRANSFORM_FAILURE = -21
    COLLISION_CHECKING_UNAVAILABLE = -22
    ROBOT_STATE_STALE = -23
    SENSOR_INFO_STALE = -24

    # kinematics errors
    NO_IK_SOLUTION = -31

    def __init__(self, val=-31):
        self.val = val

    def __eq__(self, other):
        return self.val == other


if __name__ == '__main__':

    header = Header(frame_id='base_link')
    pose = Pose([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
    pose_stamped = PoseStamped(header=header, pose=pose)
    print(pose_stamped, "\n")

    group_name = 'manipulator'
    ik_request = PositionIKRequest(
        group_name=group_name, pose_stamped=pose_stamped)
    print(ik_request, "\n")

    joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint',
                   'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
    joint_positions = [6.254248742364907, -0.06779616254839081,
                       4.497665741209763, -4.429869574230193, -4.741325546996638, 3.1415926363120015]

    joint_state = JointState(name=joint_names, position=joint_positions)
    print(joint_state, "\n")
    msg = joint_state.msg
    js = JointState.from_msg(msg)
    print(js, "\n")
