import subprocess
from typing import Any, Dict, List, Tuple
import psutil
from pypresence import Presence
import json
import os


class VMWare:
    def __init__(self, vmrun_path, vmware_file) -> None:
        if os.path.exists("./config/vms.json"):
            with open("./config/vms.json", "r") as f:
                vms = json.load(f)
        else:
            vms = {}
            with open("./config/vms.json", "w") as f:
                json.dump(vms, f, indent=4)

        self.vms = vms
        self.vmware_file = vmware_file
        self.vmrun_path = vmrun_path

    def is_vmware_running(self) -> bool:
        # Function to check if a process name is related to VMware VMs
        if self.vmware_file == "FILE_HERE":
            return -1

        def is_vmware_process(process):
            return self.vmware_file in process.name().lower()

        # Get a list of all running processes
        all_processes = psutil.process_iter(attrs=["pid", "name"])

        # Filter and return True if VMware VM processes are found
        vmware_processes = [p for p in all_processes if is_vmware_process(p)]
        return True if len(vmware_processes) > 0 else False

    def get_running_vms(self) -> List[str]:
        # Checks if vmware is still running
        is_vmware_running = self.is_vmware_running()

        if is_vmware_running == -1:
            print("VMware file wasnt set in config file!")
            exit(0)

        if is_vmware_running is False:
            exit(0)

        try:
            process_output = subprocess.check_output(
                f'"{self.vmrun_path}" list', shell=True
            )
            # splits the output into a list of lines and then removes the path from each line, so that only the VM name is left
            # (e.g. "C:\Users\user\Documents\Virtual Machines\KaliCTF\KaliCTF.vmx" -> "KaliCTF.vmx")
            # skip the first line because it's just the header and remove \r from the end of each line
            return [
                line.split("\\")[-1].rstrip("\r")
                for line in process_output.decode().split("\n")[1:]
                if line != ""
            ]
        except subprocess.CalledProcessError:
            raise Exception("Got CalledProcessError while trying to get running VMs!")
        except Exception as e:
            raise Exception(f"Error while trying to get running VMs: {e}")

    def process_running_vms(self) -> Tuple:
        running_vms = self.get_running_vms()

        if len(running_vms) == 0:
            return 2, None, None, None

        newest_vm = running_vms[len(running_vms) - 1]

        if newest_vm not in self.vms:
            image = self.vms.get("default", "")

            self.vms[newest_vm] = {
                "hostname": "",
                "os": newest_vm.split(".")[0],
                "image_key": image,
            }

            with open("./config/vms.json", "w") as f:
                json.dump(self.vms, f, indent=4)

            hostname = None
            os = newest_vm.split(".")[0]
            image_key = self.vms["default"]
        else:
            hostname = self.vms[newest_vm]["hostname"]
            os = self.vms[newest_vm]["os"]

            image_key = (
                self.vms[newest_vm]["image_key"]
                if self.vms[newest_vm].get("image_key", "") != ""
                else self.vms["default"]
            )

        return 1, hostname, os, image_key

    def rpc_update(
        self,
        rpc: Presence,
        status: int,
        images: Dict[Any, Any],
        vm_hostname: str,
        vm_os: str,
        start_time: int,
        image_key: Any,
    ) -> None:
        # Status 1 -> some vm is running
        # Status 2 -> no vm is running

        if status == 1:
            if vm_hostname == None:
                detail = "Virtualizing..."
            else:
                detail = "Hostname: " + vm_hostname
            rpc.update(
                state="OS: " + vm_os,
                details=detail,
                large_image=image_key,
                large_text="Virtualizing...",
                start=start_time,
            )
        elif status == 2:
            rpc.update(
                state="No VMs running",
                details="I am not virtualizing yet!",
                large_image=images["no_vm"],
                large_text="VMware Workstation Pro",
                start=start_time,
            )
        else:
            raise Exception(f"Invalid status: {status}")
