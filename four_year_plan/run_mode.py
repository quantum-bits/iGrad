import os

class RunMode(object):
    """Convenience class for run-time mode configuration."""

    def __init__(self, mode=None):
        self._project_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                           os.path.pardir))

        valid_modes = ('dev', 'stage', 'prod')
        if mode is None:
            for m in valid_modes:
                if m in self._project_path:
                    self.mode = m
                    break
            if self.mode not in valid_modes:
                raise RuntimeError("Can't determine mode from '{0}'".format(self._project_path))
        else:
            if mode not in valid_modes:
                raise RuntimeError("Mode not in '{0}'".format(valid_modes))
            self.mode = mode

    @property
    def project_path(self):
        "Return top-level project path."
        return self._project_path

    def path_to(self, partial_path):
        "Join partial_path to top-level path and return result."
        return os.path.join(self._project_path, partial_path)

    @property
    def dev(self):
        "Running in development mode?"
        return self.mode == 'dev'

    @property
    def stage(self):
        "Running in staging mode?"
        return self.mode == 'stage'

    @property
    def prod(self):
        "Running in production mode?"
        return self.mode == 'prod'
