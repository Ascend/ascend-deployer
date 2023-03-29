import os.path
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts import common_log
from ansible.plugins.callback.default import CallbackModule as default
from ansible import constants as C

COMPAT_OPTIONS = (('display_skipped_hosts', C.DISPLAY_SKIPPED_HOSTS),
                  ('display_ok_hosts', True),
                  ('show_custom_stats', C.SHOW_CUSTOM_STATS),
                  ('display_failed_stderr', False),)

log_write = common_log.Get_logger_ansible("ansible")
log_stdout = common_log.Get_logger_deploy("deployer")


class CallbackModule(default):
    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'ansible_log'

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        self._last_task_name = None
        self._task_type_cache = {}
        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        # for backwards compat with plugins subclassing default, fallback to constants
        for option, constant in COMPAT_OPTIONS:
            try:
                value = self.get_option(option)
            except (AttributeError, KeyError):
                value = constant
            setattr(self, option, value)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            log_stdout.info("ignore error:%s", str(result._task))
        else:
            log_stdout.error(str(result._task) + " failed")
        result._result['_ansible_verbose_always'] = True
        log_write.error("failed: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_on_ok(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info("ok: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_on_skipped(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info("skipping: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_on_unreachable(self, result):
        log_stdout.error(str(result._task) + " failed")
        result._result['_ansible_verbose_always'] = True
        log_write.error("unreachable: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_playbook_on_no_hosts_matched(self):
        log_write.info("skipping: no hosts matched")

    def v2_playbook_on_no_hosts_remaining(self):
        log_write.info("NO MORE HOSTS LEFT")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._task_start(task, prefix='TASK')

    def _task_start(self, task, prefix=None):
        # Cache output prefix for task if provided
        # This is needed to properly display 'RUNNING HANDLER' and similar
        # when hiding skipped/ok task results
        if prefix is not None:
            self._task_type_cache[task._uuid] = prefix

        # Preserve task name, as all vars may not be available for templating
        # when we need it later
        if self._play.strategy == 'free':
            # Explicitly set to None for strategy 'free' to account for any cached
            # task title from a previous non-free play
            self._last_task_name = None
        else:
            self._last_task_name = task.get_name().strip()

            # Display the task banner immediately if we're not doing any filtering based on task result
            if self.display_skipped_hosts and self.display_ok_hosts:
                self._print_task_banner(task)

    def _print_task_banner(self, task):
        # args can be specified as no_log in several places: in the task or in
        # the argument spec.  We can check whether the task is no_log but the
        # argument spec can't be because that is only run on the target
        # machine and we haven't run it thereyet at this time.
        #
        # So we give people a config option to affect display of the args so
        # that they can secure this if they feel that their stdout is insecure
        # (shoulder surfing, logging stdout straight to a file, etc).
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args

        prefix = self._task_type_cache.get(task._uuid, 'TASK')

        # Use cached task name
        task_name = self._last_task_name
        if task_name is None:
            task_name = task.get_name().strip()

        log_write.info(u"%s [%s%s]" % (prefix, task_name, args))
        if self._display.verbosity >= 2:
            path = task.get_path()
            if path:
                log_write.info(u"task path: %s" % path)

        self._last_task_banner = task._uuid

    def v2_playbook_on_cleanup_task_start(self, task):
        self._task_start(task, prefix='CLEANUP TASK')

    def v2_playbook_on_handler_task_start(self, task):
        self._task_start(task, prefix='RUNNING HANDLER')

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name

        self._play = play

        log_write.info(msg)

    def v2_on_file_diff(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info("diff - RETRYING: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_item_on_ok(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info("ok: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_item_on_failed(self, result):
        log_stdout.warning("some items in " + str(result._task) + " failed")
        result._result['_ansible_verbose_always'] = True
        log_write.error("failed: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_runner_item_on_skipped(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info(
            "skipping - RETRYING: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_playbook_on_include(self, included_file):
        msg = 'included: %s for %s' % (included_file._filename, ", ".join([h.name for h in included_file._hosts]))
        if 'item' in included_file._args:
            msg += " => (item=%s)" % (self._get_item_label(included_file._args),)
        log_write.info(msg)

    def v2_playbook_on_stats(self, stats):
        pass

    def v2_playbook_on_start(self, playbook):
        pass

    def v2_runner_retry(self, result):
        result._result['_ansible_verbose_always'] = True
        log_write.info("FAILED - RETRYING: [%s -> %s]" % (result._host.get_name(), self._dump_results(result._result)))

    def v2_playbook_on_notify(self, handler, host):
        if self._display.verbosity > 1:
            log_write.info("NOTIFIED HANDLER %s for %s" % (handler.get_name(), host))

    def v2_runner_on_start(self, host, task):
        """Event used when host begins execution of a task

        .. versionadded:: 2.8
        """
        pass
