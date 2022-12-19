#
# Regular cron jobs for the ascend-npu package
#
0 4	* * *	root	[ -x /usr/bin/ascend-npu_maintenance ] && /usr/bin/ascend-npu_maintenance
