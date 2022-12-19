#
# Regular cron jobs for the ascend-tfplugin package
#
0 4	* * *	root	[ -x /usr/bin/ascend-tfplugin_maintenance ] && /usr/bin/ascend-tfplugin_maintenance
