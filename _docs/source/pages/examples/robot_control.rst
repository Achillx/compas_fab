.. _examples_robot:

********************************************************************************
The control of robotic manipulators
********************************************************************************

.. contents::

A variety of robot controllers exist for different types of tasks and robotic systems. Position controllers have been developed for free motion control and force controllers for constrained tasks. Industrial robots are typically position controlled and use joint-space-based controllers.

.. image:: robot_axis.jpg

Task space
==================
Robots are programmed and controlled to execute specific tasks defined in the task space, i.e., in the Cartesian coordinate system.

Joint space
==================
In the joint space, tasks are first mapped into the robot's joint space through inverse kinematic techniques. The robot is then controlled to track the trajectory in joint space. Redundant robots differ from non-redundant robots in that the former have more degrees of freedom than the task description needs, that is, the dimension of the joint space of redundant robots is larger than that of the task space.

Forward Kinetamics
==================
The Forward Kinematics function/algorithm takes the joint states as the input, and calculates the pose of the end effector in the task space as the output. This means the state of each joint in the articulated body of a robot needs to be defined.

Inverse Kinetamics
==================
Inverse Kinematics is the inverse function/algorithm of Forward Kinematics. The Forward Kinematics function/algorithm takes a target end effector pose in the task space as the input, and calculates the joint states required for the end effector to reach the target pose — the joint states are the output.

