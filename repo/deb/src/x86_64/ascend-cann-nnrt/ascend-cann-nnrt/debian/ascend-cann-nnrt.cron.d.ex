#
# Regular cron jobs for the ascend-cann-nnrt package
#
0 4	* * *	root	[ -x /usr/bin/ascend-cann-nnrt_maintenance ] && /usr/bin/ascend-cann-nnrt_maintenance
