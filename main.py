from vmware import VMWare
from pypresence import Presence
from time import time, sleep
import json, os

if os.path.exists("./config/") == False:
    os.mkdir("./config/")

if __name__ == "__main__":
    try:
        print("Trying to load config...")
        if os.path.exists("./config/settings.json"):
            with open("./config/settings.json", "r") as file:
                config = json.load(file)
        else:  # If config file not found, create it
            print("Config file not found!")
            print("Creating config file...")
            config = {
                "application_id": "ID_HERE",
                "vmrun_path": "PATH_HERE",
                "vmware_file": "FILE_HERE",
            }
            with open("./config/settings.json", "w") as file:
                json.dump(config, file, indent=4)
            print("Config file created!")
            print("Please fill in the config file and restart the program!")
            exit()

        print("Loading images...")
        if os.path.exists("./config/vms.json"):
            with open("./config/vms.json", "r") as file:
                images = json.load(file)
        else:
            images = {}
            with open("./config/vms.json", "w") as file:
                json.dump(images, file, indent=4)

        if config["application_id"] == "ID_HERE":
            print("Please fill in the config file and restart the program!")
            exit()

        rpc = Presence(config["application_id"])
        print("Trying to connect to Discord...")
        try:
            rpc.connect()
        except Exception as e:
            print("Error while connecting to Discord!")
            print(e)
            exit()

        print("Connected to Discord!")
        start_time = time()

        if config["vmrun_path"] == "PATH_HERE":
            print("Please fill in the config file and restart the program!")
            exit()
        vm_instance = VMWare(config["vmrun_path"], config["vmware_file"])

        while True:
            status, vm_hostname, vm_os, image_key = vm_instance.process_running_vms()
            vm_instance.rpc_update(
                rpc, status, images, vm_hostname, vm_os, start_time, image_key
            )
            sleep(5)
    except KeyboardInterrupt:
        rpc.close()
        print("\nDisconnected from Discord!")
        print("Exiting...")
        exit()
    except Exception as e:
        print("\nError!")
        print(e)
        exit()
