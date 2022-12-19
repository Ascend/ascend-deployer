#
# Regular cron jobs for the ascend-cann-nnae package
#
0 4	* * *	root	[ -x /usr/bin/ascend-cann-nnae_maintenance ] && /usr/bin/ascend-cann-nnae_maintenance
