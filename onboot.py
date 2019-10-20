import subprocess
import os

def excu_optimization(nicname):
    os.system("ethtool -G " + nicname + " rx 4096 tx 4096")
    os.system("ethtool -A " + nicname + " rx off tx off")
    os.system("setpci -v -d 8086:10fb e6.b=2e")
    os.system("setpci -v -d 8086:154d e6.b=2e")
    Out_CPUs = subprocess.Popen(["cat /sys/class/net/" + nicname + "/device/local_cpulist"],stdout=subprocess.PIPE, shell=True)
    cpus, cpu_error = Out_CPUs.communicate()
    cpunumber = cpus.strip().count(',')
    os.system("ethtool -L " + nicname + " combined " + str(cpunumber))

    if (not os.path.exists("/etc/set_irq_affinity.sh")):
        os.system("curl -o /etc/set_irq_affinity.sh https://raw.githubusercontent.com/DMIT-Inc/Operation-Scripts/master/set_irq_affinity.sh")

    os.system("bash /etc/set_irq_affinity.sh local " + nicname)

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
                excu_optimization(nic)


if __name__ == "__main__":
    maindef()