#
# Regular cron jobs for the ascend-cann-toolkit package
#
0 4	* * *	root	[ -x /usr/bin/ascend-cann-toolkit_maintenance ] && /usr/bin/ascend-cann-toolkit_maintenance
