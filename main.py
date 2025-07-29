import time, schedule
import os, sys, subprocess
import random, json 
from term_logger import Logger


logger = Logger()

class Device:
    def __init__(self) -> None:
        pass 

    def battery(self) -> dict:
        result = self.shell("termux-battery-status")
        return json.loads(result.stdout)

    def wifi(self) -> dict:
        result = self.shell("termux-wifi-scaninfo")
        return json.loads(result.stdout)


    def append_wifi(self, data: dict) -> None:
        try:
            with open("wifi_data.json", "r") as fp:
                json_data = json.load(fp)
        except:
            json_data = []

        json_data += data

        with open("wifi_data.json", "w") as fp:
            json.dump(json_data, fp, sort_keys=True, indent=4)

    def vibrate(self) -> None:
        self.shell("termux-vibrate")

    def notification(self, title, content) -> None:
        res = self.shell("termux-notification", "--title", f"'{title}'", "--content", f"'{content}'")

    def shell(self, *args) -> subprocess.CompletedProcess:
        result = subprocess.run(" ".join(args), shell=True, capture_output=True,text=True)
        return result

device = Device()
battery = device.battery()

logger.info("Welcome to Harbinger")
logger.info(f"Battery percentage: {battery['percentage']}")

current_wifi = 0
def monitor_wifi():
    global current_wifi
    wifi_list = device.wifi() 
    if (len(wifi_list) > current_wifi):
        current_wifi = len(wifi_list)
        device.notification(
            title="Discovered new network!",
            content=wifi_list[-1]["ssid"]
        )
        device.vibrate()
        logger.success("Discovered a new wifi network")
        logger.info(f"ssid: {wifi_list[-1]["ssid"]}")
        device.append_wifi(wifi_list)
        
        for wifi in wifi_list:
            print("Network found!")
            logger.info(f"Network: {wifi['ssid']}")
            logger.info(f"Connection: {wifi['capabilities']}")
            logger.info(f"Timestamp: {wifi['timestamp']}")
            print("-"*20, sep="")



battery_count = device.battery()["percentage"]
last_10_count = battery_count

charging = False 

def monitor_battery():
    global battery_count, last_10_count, charging
    output = device.battery()

    if output["percentage"] < battery_count:
        battery_count = output["percentage"]
        logger.info(f"New battery: {output['percentage']}%")

    if (last_10_count - battery_count) >= 10:
        last_10_count = battery_count
        logger.warning("10 percent lost!")

    if output["percentage"] < 15 and output["status"] != "charging".upper():
        logger.error(f"Low battery, please charge! - {output['percentage']}%")
        device.vibrate()
        device.notification("Low battery", f"Only {output['percentage']} percent left!")
        time.sleep(60 * 5)


    if output['status'] != "CHARGING" and charging:
        logger.warning(f"Device unplugged! : {output['percentage']}%")

    if output["status"] == "CHARGING":
        if not charging:
            logger.success(f"Device charging : {output['percentage']}%")
            charging = True
    else:
        charging = False

    




schedule.every(1).seconds.do(monitor_battery)
schedule.every(1).seconds.do(monitor_wifi)
while True:
    schedule.run_pending()
