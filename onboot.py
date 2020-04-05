import subprocess
import os
import re

def excu_optimization(nicname):
    os.system("ethtool -G " + nicname + " rx 4096 tx 4096")
    os.system("ethtool -A " + nicname + " rx off tx off")
    os.system("ethtool -K " + nicname + " ntuple off")
    os.system("ethtool -C " + nicname + " adaptive-rx off")
    # Enable RSS Hash For UDP package
    os.system("ethtool -N " + nicname + " rx-flow-hash udp4 sdfn")
    os.system("setpci -v -d 8086:10fb e6.b=2e")
    os.system("setpci -v -d 8086:154d e6.b=2e")

    #System default setting is good for most situation. Using multiple queue on same IRQ is ok. 
'''
    Out_CPUs = subprocess.Popen(["cat /sys/class/net/" + nicname + "/device/local_cpulist"],stdout=subprocess.PIPE, shell=True)
    cpus, cpu_error = Out_CPUs.communicate()
    cpunumber = 0
    if ("-" in cpus):
        temp_cpu = re.split(r",", cpus)
        for i_u in temp_cpu:
            t_u = re.split(r"-", i_u)
            if (len(t_u) != 2):
                break
            cpunumber += int(t_u[1]) - int(t_u[0]) + 1
    else:
        cpunumber = cpus.strip().count(',')
    os.system("ethtool -L " + nicname + " combined " + str(cpunumber))
'''

    # Set IRQ Affinity for every queue.
    if (not os.path.exists("/etc/set_irq_affinity.sh")):
        os.system("curl -o /etc/set_irq_affinity.sh https://raw.githubusercontent.com/DMIT-Inc/Operation-Scripts/master/set_irq_affinity.sh")

    os.system("bash /etc/set_irq_affinity.sh local " + nicname)

    Out_CPUsLits = subprocess.Popen(["cat /sys/class/net/" + nicname + "/device/local_cpus"],stdout=subprocess.PIPE, shell=True)
    cpulists, cpu_error = Out_CPUsLits.communicate()

    queueslist = traversalDir_FirstDir("/sys/class/net/" + nicname + "/queues/")
    for queue in queueslist:
        if ("rx" in queue):
            # RSS enable, disable RPS
            #os.system("echo \"" + cpulists + "\" > /sys/class/net/" + nicname + "/queues/" + queue + "/rps_cpus")
            os.system("echo 2048 > /sys/class/net/" + nicname + "/queues/" + queue + "/rps_flow_cnt")
        if ("tx" in queue):
            # RSS enable, disable XPS
            #os.system("echo \"" + cpulists + "\" > /sys/class/net/" + nicname + "/queues/" + queue + "/xps_cpus")

def maindef():
    Output_NICList = subprocess.Popen(["find /sys/class/net ! -type d | xargs --max-args=1 realpath | awk -F\/ '/pci/{print $NF}'", ],stdout=subprocess.PIPE, shell=True)
    nic_List, nic_error = Output_NICList.communicate()
    for nic in nic_List.split(os.linesep):
        nicName = nic.strip()
        if (not nicName):
            continue
        Out_ETHTOOL = subprocess.Popen(["ethtool -i " + nicName],stdout=subprocess.PIPE, shell=True)
        eth, eth_error = Out_ETHTOOL.communicate()
        for d_nic in eth.split(os.linesep):
            if ("ixgbe" in d_nic):
                excu_optimization(nicName)


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