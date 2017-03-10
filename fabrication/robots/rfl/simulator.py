from __future__ import print_function

import math
import logging
from timeit import default_timer as timer
from compas.datastructures.mesh import Mesh
from compas_fabrication.fabrication.robots.rfl.vrep_remote_api import vrep

DEFAULT_OP_MODE = vrep.simx_opmode_blocking
CHILD_SCRIPT_TYPE = vrep.sim_scripttype_childscript
LOG = logging.getLogger('compas_fabrication.simulator')


class SimulationError(Exception):
    """Wraps an exception that occurred inside the simulation engine."""

    def __init__(self, message, error_code):
        super(SimulationError, self).__init__('Error code: ' +
                                              str(error_code) +
                                              '; ' + message)
        self.error_code = error_code


class Simulator(object):
    """Interface to run simulations on the RFL using VREP as
    the engine for inverse kinematics.

    :class:`.Simulator` is a context manager type, so it's best used in combination
    with the ``with`` statement to ensure resource deallocation.

    Examples:

        >>> with Simulator() as simulator:
        ...     print ('Connected: ' + str(simulator.is_connected()))
        ...
        Connected: True

    """
    def __init__(self, host='127.0.0.1', port=19997, debug=False):
        self.client_id = None
        self.host = host
        self.port = port
        self.default_timeout_in_ms = -50000000
        self.thread_cycle_in_ms = 5
        self.debug = debug
        self._lua_script_name = 'RFL'

    def __enter__(self):
        # Stop existing simulation, if any
        vrep.simxFinish(-1)

        if self.debug:
            LOG.debug('Connecting to V-REP...')

        # Connect to V-REP, set a very large timeout for blocking commands
        self.client_id = vrep.simxStart(self.host, self.port, True, True,
                                        self.default_timeout_in_ms,
                                        self.thread_cycle_in_ms)

        # Start simulation
        vrep.simxStartSimulation(self.client_id, DEFAULT_OP_MODE)

        return self

    def __exit__(self, *args):
        # Stop simulation
        vrep.simxStopSimulation(self.client_id, DEFAULT_OP_MODE)

        # Close the connection to V-REP
        vrep.simxFinish(self.client_id)
        self.client_id = None

        if self.debug:
            LOG.debug('Disconnected from V-REP')

    def is_connected(self):
        """Indicates whether the simulator has an active connection.

        Returns:
            bool: Indicating if the simulator is connected.
        """
        return self.client_id is not None and self.client_id != -1

    def get_object_handle(self, object_name):
        """Gets the object handle (identifier) for a given object name.

        Args:
            object_name (:obj:`string`): Name of the object.

        Returns:
            int: Object handle.
        """
        _res, handle = vrep.simxGetObjectHandle(self.client_id,
                                                object_name,
                                                DEFAULT_OP_MODE)
        return handle

    def set_metric(self, metric_values):
        """Assigns a metric defining relations between axis values.

        It takes a list of 9 :obj:`float` values (3 for gantry + 6 for joints)
        ranging from 0 to 1, where 1 indicates the axis is blocked and cannot
        move during inverse kinematic solving.

        Args:
            metric_values (:obj:`list` of :obj:`float`): 9 :obj:`float`
                values from 0 to 1.

        Returns:
            None
        """
        return vrep.simxCallScriptFunction(self.client_id,
                                           self._lua_script_name,
                                           CHILD_SCRIPT_TYPE, 'setTheMetric',
                                           [], metric_values, [],
                                           bytearray(), DEFAULT_OP_MODE)

    def set_robot_config(self, robot, gantry_values, joint_values):
        """Moves the robot the the specified configuration.

        Args:
            robot (:class:`.Robot`): Robot instance to move.
            gantry_values (:obj:`list` of :obj:`float`): Gantry position
                in x, y, z in meters.
            joint_values (:obj:`list` of :obj:`float`): 6 joint values
                expressed in degrees.

        Examples:

            >>> from compas_fabrication.fabrication.robots.rfl import Robot
            >>> with Simulator() as simulator:
            ...     simulator.set_robot_config(Robot('A'),
            ...                                [7.6, -4.5, -4.5],
            ...                                [90, 0, 0, 0, 0, -90])
            ...

        """
        values = list(gantry_values)
        values.extend([math.radians(angle) for angle in joint_values])

        self.set_metric([0.0] * 9)
        self.run_child_script('moveRobotFK',
                              [], values, ['robot' + robot.name])

    def find_path_plan(self, robot, metric_values, goal_pose, collision_meshes=None,
                       algorithm='rrtconnect', trials=1, resolution=0.02):
        """Finds a path plan to move the selected robot from its current position
        to the `goal_pose`.

        Args:
            robot (:class:`.Robot`): Robot instance to move.
            metric_values (:obj:`list` of :obj:`float`): 9 :obj:`float`
                values (3 for gantry + 6 for joints) ranging from 0 to 1,
                where 1 indicates the axis is blocked and cannot
                move during inverse kinematic solving.
            goal_pose (:obj:`list` of :obj:`float`): Target or goal pose
                specified as a list of 12 :obj:`float` values.
            collision_meshes (:obj:`list` of :class:`compas.datastructures.mesh.Mesh`): Collision meshes
                to be taken into account when calculating the motion plan.
                Defaults to ``None``.
            algorithm (:obj:`list` of :obj:`float`): 6 joint values
                expressed in degrees. Defaults to ``rrtconnect``.
            trials (:obj:`int`): Number of search trials to run. Defaults to ``1``.
            resolution (:obj:`float`): Validity checking resolution. This value
                is specified as a fraction of the space's extent.
                Defaults to ``0.02``.
        """
        mesh_handles = []

        try:
            start = timer() if self.debug else None
            if collision_meshes:
                mesh_handles = self.add_meshes(collision_meshes)
            if self.debug:
                LOG.debug('Execution time: add_meshes=%f.2', timer() - start)

            start = timer() if self.debug else None
            self.set_metric(metric_values)
            if self.debug:
                LOG.debug('Execution time: set_metric=%f.2', timer() - start)

            start = timer() if self.debug else None
            res, _, states, _, _ = self.run_child_script('searchRobotStates',
                                                         [robot.index],
                                                         goal_pose, [])
            if self.debug:
                LOG.debug('Execution time: search_robot_states=%f.2', timer() - start)

            if res != 0:
                raise SimulationError('Failed to search robot states', res)

            start = timer() if self.debug else None
            res, _, path, _, _ = self.run_child_script('searchRobotPath',
                                                       [robot.index,
                                                        trials,
                                                        (int)(resolution * 1000)],
                                                       states, [algorithm])
            if self.debug:
                LOG.debug('Execution time: search_robot_path=%f.2', timer() - start)

            if res != 0:
                raise SimulationError('Failed to search robot path', res)

            # TODO: Document return type on docstring.
            # TODO: Path should not be a plain list
            # we should instead return a list of list or a
            # more specialized data structure.
            return path

        finally:
            try:
                start = timer() if self.debug else None
                self.remove_meshes(mesh_handles)
                if self.debug:
                    LOG.debug('Execution time: remove_meshes=%f.2', timer() - start)
            except:
                pass

    def add_meshes(self, meshes):
        """Adds meshes to the RFL scene.

        Args:
            meshes (:obj:`list` of :class:`compas.datastructures.mesh.Mesh`): Add
                the specified meshes to the current simulation scene.

        Returns
            list: List of object handles (identifiers) assigned to the meshes.
        """

        mesh_handles = []

        for mesh in meshes:
            # TODO: Remove the next two lines and uncomment the third
            # if `to_vertices_and_faces` is merged into compAS.
            vertices = mesh.xyz
            faces = [mesh.face_vertices(fkey, ordered=True) for fkey in mesh.face]
            # vertices, faces = mesh.to_vertices_and_faces()

            vrep_packing = ([item for sublist in vertices for item in sublist] +
                            [item for sublist in faces for item in sublist])
            params = [[len(vertices) * 3, len(faces) * 4], vrep_packing]

            handles = self.run_child_script('buildMesh',
                                            params[0],
                                            params[1],
                                            [])[1]
            mesh_handles.extend(handles)

        return mesh_handles

    def remove_meshes(self, mesh_handles):
        """Removes meshes from the RFL scene.

        This is functionally identical to ``remove_objects``, but it's here for
        symmetry reasons.

        Args:
            mesh_handles (:obj:`list` of :obj:`int`): Object handles to remove.
        """
        self.remove_objects(mesh_handles)

    def remove_objects(self, object_handles):
        """Removes objects from the RFL scene.

        Args:
            object_handles (:obj:`list` of :obj:`int`): Object handles to remove.
        """
        for handle in object_handles:
            vrep.simxRemoveObject(self.client_id, handle, DEFAULT_OP_MODE)

    def run_child_script(self, function_name, in_ints, in_floats, in_strings):
        return vrep.simxCallScriptFunction(self.client_id,
                                           self._lua_script_name,
                                           CHILD_SCRIPT_TYPE, function_name,
                                           in_ints, in_floats, in_strings,
                                           bytearray(), DEFAULT_OP_MODE)
