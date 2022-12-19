#
# Regular cron jobs for the ascend-mindspore package
#
0 4	* * *	root	[ -x /usr/bin/ascend-mindspore_maintenance ] && /usr/bin/ascend-mindspore_maintenance
