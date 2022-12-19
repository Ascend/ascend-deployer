#
# Regular cron jobs for the ascend-torch package
#
0 4	* * *	root	[ -x /usr/bin/ascend-torch_maintenance ] && /usr/bin/ascend-torch_maintenance
