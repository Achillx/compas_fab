*******************************************************************************
Planning scene and collision objects
*******************************************************************************

.. note::

    The following examples use `ROS <http://www.ros.org/>`_ as a backend client.

    Before running them, please make sure you have the
    :ref:`ROS backend <ros_backend>` correctly configured.

To plan motion paths that avoid collisions with other objects than the robot
itself, the backend's planning scene has to be updated.

This is the representation of the planning scene in RViz with the UR5.

.. figure:: files/03_collision_objects_attached_without.jpg
    :figclass: figure
    :class: figure-img img-fluid

Collision meshes
================

The following script adds a floor to the planning scene.

.. literalinclude :: files/03_add_collision_mesh.py
   :language: python

The backend's updated planning scene after executing the above script.

.. figure:: files/03_collision_objects.jpg
    :figclass: figure
    :class: figure-img img-fluid

To remove the floor, use the identifier assigned when adding it:

.. literalinclude :: files/03_remove_collision_mesh.py
   :language: python

The following script adds several boxes (bricks) to the planning scene. Here,
we use ``append`` instead of ``add`` to have multiple collision objects
clustered under the same identifier. Like that, we don't need to keep track of
all identifiers if we later want to remove them.

.. literalinclude :: files/03_append_collision_meshes.py
   :language: python

The backend's updated planning scene after executing the above script. Note the
red robot link indicating the collision.

.. figure:: files/03_collision_objects_append.jpg
    :figclass: figure
    :class: figure-img img-fluid



Attach a collision mesh to a robot's end-effector
=================================================

The following script attaches a collision mesh to the robot's end-effector.
Collision objects can be attached to any of the robot's links.

.. literalinclude :: files/03_attach_mesh_to_ee.py
   :language: python

The backend's updated planning scene after executing the above script.

.. figure:: files/03_collision_objects_attached.jpg
    :figclass: figure
    :class: figure-img img-fluid



Plan motion with an attached collision mesh
===========================================

Coming soon...
