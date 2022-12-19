#
# Regular cron jobs for the ascend-tensorflow package
#
0 4	* * *	root	[ -x /usr/bin/ascend-tensorflow_maintenance ] && /usr/bin/ascend-tensorflow_maintenance
