# This points to a file, which should contains hostnames (one per line).
# E.g.,
#
# worker1
# worker2
# worker3
#
MACHINE_CFG=/data/legend/machine-all.cfg
time pssh -t 0 -P -h ${MACHINE_CFG} -x "-t -t" "cd /data/legend/ooni && python $@"
