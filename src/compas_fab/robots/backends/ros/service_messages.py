from compas.robots.model.geometry import SCALE_FACTOR

from compas_fab.robots.backends.ros import ROSmsg
from compas_fab.robots.backends.ros import Header
from compas_fab.robots.backends.ros import Pose
from compas_fab.robots.backends.ros import JointState
from compas_fab.robots.backends.ros import MultiDOFJointState
from compas_fab.robots.backends.ros import Constraints
from compas_fab.robots.backends.ros import RobotState
from compas_fab.robots.backends.ros.messages import PoseStamped
from compas_fab.robots.backends.ros.messages import MoveItErrorCodes
from compas_fab.robots.backends.ros.messages import RobotTrajectory
from compas_fab.robots.backends.ros.messages import PositionIKRequest

__all__ = ['GetCartesianPathRequest', 'GetCartesianPathResponse',
           'GetPositionIKRequest', 'GetPositionIKResponse']


class GetPositionIKRequest(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/srv/GetPositionIK.html

    Examples
    --------
    >>> import roslibpy
    >>> base_link = 'base_link'  # robot.get_base_link_name()
    >>> planning_group = 'manipulator'  # robot.main_planning_group
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
    >>> reqmsg = GetPositionIKRequest(ik_request)
    >>> srv = roslibpy.Service(ros_client, '/compute_ik', 'GetPositionIK')
    >>> request = roslibpy.ServiceRequest(reqmsg.msg)
    >>> srv.call(request, GetPositionIKResponse.from_msg, GetPositionIKResponse.from_msg)
    """
    def __init__(self, ik_request=PositionIKRequest()):
        self.ik_request = ik_request


class GetPositionIKResponse(ROSmsg):
    """http://docs.ros.org/kinetic/api/moveit_msgs/html/srv/GetPositionIK.html
    """

    def __init__(self, solution=RobotState(), error_code=MoveItErrorCodes()):
        self.solution = solution  # moveit_msgs/RobotState
        self.error_code = error_code  # moveit_msgs/MoveItErrorCodes

    @classmethod
    def from_msg(cls, msg):
        solution = RobotState.from_msg(msg['solution'])
        error_code = MoveItErrorCodes.from_msg(msg['error_code'])
        return cls(solution, error_code)


class GetCartesianPathRequest(ROSmsg):
    """http://docs.ros.org/melodic/api/moveit_msgs/html/srv/GetCartesianPath.html

    Examples
    --------
    >>> import roslibpy
    >>> base_link = 'base_link' # robot.get_base_link_name()
    >>> ee_link = 'ee_link' # robot.get_end_effector_link_name()
    >>> main_planning_group = 'manipulator' # robot.main_planning_group
    >>> joint_names = ['j0', 'j1', 'j2', 'j3', 'j4', 'j5']
    >>> position = [0, 0, 0, 0, 0, 0] # robot.get_configurable_joint_names()
    >>> header = Header(frame_id=base_link)
    >>> joint_state = JointState(header=header, name=joint_names, position=position) # or: robot.get_joint_state()
    >>> multi_dof_joint_state = MultiDOFJointState(header=header, joint_names=joint_names)
    >>> start_state = RobotState(joint_state=joint_state, multi_dof_joint_state=multi_dof_joint_state)
    >>> start_pose = Pose([106.8, -181.8, 593.0], [1., 0., 0.], [-0., 0., 1.])
    >>> end_pose = Pose([104.1, -294.6, 184.3], [1., 0., 0.], [0., 1., 0.])
    >>> waypoints = [start_pose, end_pose]
    >>> reqmsg = GetCartesianPathRequest(header=header,
                                         start_state=start_state,
                                         group_name=main_planning_group,
                                         link_name=ee_link,
                                         waypoints=waypoints,
                                         max_step=10,
                                         avoid_collisions=True)
    >>> srv = roslibpy.Service(ros_client, '/compute_cartesian_path', 'GetCartesianPath')
    >>> request = roslibpy.ServiceRequest(reqmsg.msg)
    >>> srv.call(request, GetCartesianPathResponse.from_msg, GetCartesianPathResponse.from_msg)
    """

    def __init__(self, header=Header(), start_state=RobotState(), group_name='',
                 link_name='', waypoints=[], max_step=10., jump_threshold=0.,
                 avoid_collisions=True, constraints=Constraints()):
        self.header = header
        self.start_state = start_state  # moveit_msgs/RobotState
        self.group_name = group_name
        self.link_name = link_name  # ee_link
        self.waypoints = waypoints  # geometry_msgs/Pose[]
        self.max_step = float(max_step)
        self.jump_threshold = jump_threshold
        self.avoid_collisions = avoid_collisions
        self.path_constraints = constraints  # moveit_msgs/Constraints

    @property
    def msg(self):
        msg = super(GetCartesianPathRequest, self).msg
        msg['max_step'] = msg['max_step'] / SCALE_FACTOR
        return msg


class GetCartesianPathResponse(ROSmsg):
    """http://docs.ros.org/melodic/api/moveit_msgs/html/srv/GetCartesianPath.html
    """

    def __init__(self, start_state=RobotState(), solution=RobotTrajectory(),
                 fraction=0., error_code=MoveItErrorCodes()):
        self.start_state = start_state  # moveit_msgs/RobotState
        self.solution = solution  # moveit_msgs/RobotTrajectory
        self.fraction = fraction
        self.error_code = error_code  # moveit_msgs/MoveItErrorCodes

    @classmethod
    def from_msg(cls, msg):
        start_state = RobotState.from_msg(msg['start_state'])
        solution = RobotTrajectory.from_msg(msg['solution'])
        error_code = MoveItErrorCodes.from_msg(msg['error_code'])
        return cls(start_state, solution, msg['fraction'], error_code)


if __name__ == '__main__':

    # GetPositionIKRequest
    print("GetPositionIKRequest")
    base_link = 'base_link'  # robot.get_base_link_name()
    planning_group = 'manipulator'  # robot.main_planning_group
    pose = Pose([420, -25, 459], [1, 0, 0], [0, 1, 0])
    joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                   'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']  # robot.get_configurable_joint_names()
    joint_positions = [3.39, -1.47, -2.05, 0.38, -4.96, -6.28]
    header = Header(frame_id='base_link')
    pose_stamped = PoseStamped(header, pose)
    joint_state = JointState(
        name=joint_names,
        position=joint_positions,
        header=header)
    multi_dof_joint_state = MultiDOFJointState(
        header=header, joint_names=joint_names)
    start_state = RobotState(joint_state, multi_dof_joint_state)
    ik_request = PositionIKRequest(group_name=planning_group,
                                   robot_state=start_state,
                                   pose_stamped=pose_stamped,
                                   avoid_collisions=True)
    reqmsg = GetPositionIKRequest(ik_request)
    print(reqmsg)

    # GetCartesianPathRequest
    print("GetCartesianPathRequest")
    base_link = 'base_link'  # robot.get_base_link_name()
    ee_link = 'ee_link'  # robot.get_end_effector_link_name()
    main_planning_group = 'manipulator'  # robot.main_planning_group
    joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                   'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']  # robot.get_configurable_joint_names()
    position = [0, 0, 0, 0, 0, 0]
    header = Header(frame_id=base_link)
    joint_state = JointState(header=header, name=joint_names, position=position)  # or: robot.get_configuration()
    multi_dof_joint_state = MultiDOFJointState(header=header, joint_names=joint_names)
    start_state = RobotState(joint_state=joint_state, multi_dof_joint_state=multi_dof_joint_state)
    start_pose = Pose([106.8, -181.8, 593.0], [1., 0., 0.], [-0., 0., 1.])
    end_pose = Pose([104.1, -294.6, 184.3], [1., 0., 0.], [0., 1., 0.])
    waypoints = [start_pose, end_pose]
    reqmsg = GetCartesianPathRequest(header=header,
                                     start_state=start_state,
                                     group_name=main_planning_group,
                                     link_name=ee_link,
                                     waypoints=waypoints,
                                     max_step=10,
                                     avoid_collisions=True)
    print(reqmsg)
