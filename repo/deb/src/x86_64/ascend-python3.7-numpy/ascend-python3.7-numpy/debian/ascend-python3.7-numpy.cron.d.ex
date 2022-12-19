#
# Regular cron jobs for the ascend-python3.7-numpy package
#
0 4	* * *	root	[ -x /usr/bin/ascend-python3.7-numpy_maintenance ] && /usr/bin/ascend-python3.7-numpy_maintenance
