import subprocess
import os
import re
from collections import defaultdict


def maindef():

    vmbr_list = defaultdict(list)
    nic_cpus = {}
    not_config_list = []

    Out_vmbr_sum =  subprocess.Popen(["brctl show"],stdout=subprocess.PIPE, shell=True)
    vmbr_sum, vmbr_error = Out_vmbr_sum.communicate()
    vmbr_sum_list = vmbr_sum.split(os.linesep)
    del vmbr_sum_list[0]
    nowbrint = ""
    for vmbrl in vmbr_sum_list:
        line = re.split(r"\t+", vmbrl)
        if ("vmbr" in line[0]):
            nowbrint = line[3].split('.')[0]
            vmbr_list[nowbrint].append(line[0])
            if ("." in line[3]):
                vmbr_list[nowbrint].append(line[3])
        elif ("fwbr" in line[0]):
            not_config_list.append(line[0])
            not_config_list.append(line[3])
        else :
            if (len(line) < 2 or nowbrint == ""):
                continue
            if ("fwbr" in nowbrint):
                not_config_list.append(line[1])
            if (("tap" in line[1]) or ("fwln" in line[1]) or ("fwpr" in line[1])):
                vmbr_list[nowbrint].append(line[1])

    for nic_not in not_config_list:
        vmid = re.split(r"fwbr", nic_not)
        if ((vmid is None) or len(vmid) < 1):
            continue
        vmid = re.split(r"i0", vmid[0])
        if ((vmid is None) or len(vmid) < 1):
            continue
        for nicname in vmbr_list:
            for ifname in vmbr_list[nicname]:
                if (vmid[0] in ifname):
                    vmbr_list[nicname].append(nic_not)
                    break

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
                Out_CPUsLits = subprocess.Popen(["cat /sys/class/net/" + nicName + "/device/local_cpus"],stdout=subprocess.PIPE, shell=True)
                cpulists, cpu_error = Out_CPUsLits.communicate()
                nic_cpus[nicName] = str.strip(cpulists)
                    
    for nicname in vmbr_list:
        for ifname in vmbr_list[nicname]:
            queueslist = traversalDir_FirstDir("/sys/class/net/" + ifname + "/queues/")
            for queue in queueslist:
                if ("rx" in queue):
                    os.system ("echo \"" + nic_cpus[nicname] + "\" > /sys/class/net/" + ifname + "/queues/" + queue + "/rps_cpus")
                    os.system ("echo 2048 > /sys/class/net/" + ifname + "/queues/" + queue + "/rps_flow_cnt")
                if ("tx" in queue):
                    os.system ("echo \"" + nic_cpus[nicname] + "\" > /sys/class/net/" + ifname + "/queues/" + queue + "/xps_cpus")


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