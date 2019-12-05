import subprocess
import os
import re

def maindef():
    Out_CPUsTotal = subprocess.Popen(["cat /proc/cpuinfo| grep \"processor\"| wc -l"],stdout=subprocess.PIPE, shell=True)
    totalcpu, cpu_error = Out_CPUsTotal.communicate()
    cpus = ""
    tcpu = int(totalcpu)
    if (tcpu > 2):
        for c in range(1, tcpu / 2):
            cpus = cpus + "01"
    cpus = cpus + "00"
    pattern = re.compile('.{8}')
    f_cpus = ','.join(pattern.findall(format(int(cpus,2),'x')))

    ifslist = traversalDir_FirstDir("/sys/class/net/")
    for ifname in ifslist:
        if ("fw" in ifname):
            queueslist = traversalDir_FirstDir("/sys/class/net/" + ifname + "/queues/")
            for queue in queueslist:
                if ("rx" in queue):
                    os.system("echo \"" + f_cpus + "\" > /sys/class/net/" + ifname + "/queues/" + queue + "/rps_cpus")
                    os.system("echo 2048 > /sys/class/net/" + ifname + "/queues/" + queue + "/rps_flow_cnt")
                if ("tx" in queue):
                    os.system("echo \"" + f_cpus + "\" > /sys/class/net/" + ifname + "/queues/" + queue + "/xps_cpus")

def traversalDir_FirstDir(path):
    list = []
    if (os.path.exists(path)):
        files = os.listdir(path)
        for file in files:
            m = os.path.join(path,file)
            if (os.path.isdir(m)):
                h = os.path.split(m)
                list.append(h[1])
    return list

if __name__ == "__main__":
    maindef()