try:
    import Grasshopper as gh
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


def update_component(ghenv, delay):
    """Schedule an update of the Grasshopper component.

    After the specified delay, the GH component will be automatically updated.

    Args:
        ghenv (:class:`GhPython.Component.PythonEnvironment`): just available from within the
            python Grasshopper component.

        delay (:obj:`int`): Time in milliseconds until the update is performed.
    """
    if delay <= 0:
        raise ValueError('Delay must be greater than zero')

    ghcomp = ghenv.Component
    ghdoc = ghcomp.OnPingDocument()

    def callback(ghdoc):
        ghcomp.ExpireSolution(False)

    ghdoc.ScheduleSolution(delay, gh.Kernel.GH_Document.GH_ScheduleDelegate(callback))
