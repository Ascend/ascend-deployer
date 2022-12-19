#
# Regular cron jobs for the ascend-cann-toolbox package
#
0 4	* * *	root	[ -x /usr/bin/ascend-cann-toolbox_maintenance ] && /usr/bin/ascend-cann-toolbox_maintenance
