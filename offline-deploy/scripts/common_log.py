from ansible.plugins.callback.default import CallbackModule as default
from ansible import constants as C


class CallbackModule(default):
    """
    This callback module tells you how long your plays ran for.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'common_log'

    def __init__(self):
        super(CallbackModule, self).__init__()

    def v2_runner_on_failed(self, result, ignore_errors=False):
        print("fatal: [%s]: FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result)))
        super(CallbackModule, self).v2_runner_on_failed(result, ignore_errors)