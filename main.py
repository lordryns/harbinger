from enum import StrEnum
import time, schedule
import os, sys, subprocess
import random, json 
from term_logger import Logger
import threading
import requests
from yt_dlp import YoutubeDL
import questionary
from art import tprint


logger = Logger()

SETTINGS = {
    "wifi": True, 
    "header": True
}

class Device:
    def __init__(self) -> None:
        pass 

    def battery(self) -> dict:
        result = self.shell("termux-battery-status")
        return json.loads(result.stdout)

    def wifi(self) -> dict:
        result = self.shell("termux-wifi-scaninfo")
        return json.loads(result.stdout)


    def device_info(self) -> dict:
        result = self.shell("termux-telephony-deviceinfo")
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

    def terminal_size(self):
        res = self.shell("stty", "size")
        return tuple(int(i) for i in res.stdout.split(" "))

    def shell(self, *args) -> subprocess.CompletedProcess:
        result = subprocess.run(" ".join(args), shell=True, capture_output=True,text=True)
        return result


def reboot_program():
    os.execv(sys.executable, [sys.executable] + sys.argv)


def restart_program():
    current_date = time.strftime("%d, %B %Y (%A) ")
    subprocess.run("clear")
    if SETTINGS['header']:
        tprint("Harbinger")


    logger.info("Welcome to Harbinger")
    logger.info(f"Date: {current_date}")
    logger.info(f"Battery percentage: {battery['percentage']}")

    print("")
    logger.info("Use [h] for help")

    if device.terminal_size() < (33, 59):
        logger.warning("Terminal size is too small so header may not format properly, zoom out.")



device = Device()
battery = device.battery()


restart_program()


def download_yt_video(link: str):
    options = {
        'format': 'bv+ba/best',
        'merge_output_format': 'mp4',
        'outtmpl': '~/storage/downloads/%(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            },
            {
                'key': 'FFmpegMetadata'
            }
        ],
        'postprocessor_args': [
            '-c:v', 'libx264',  
            '-preset', 'fast',  
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart'  
        ]
    }

    with YoutubeDL(options) as ydl:
        ydl.download([link, ])
    os.system('am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///storage/emulated/0/Download')


def download_yt_video_prompt():
    link = questionary.text("Video link:").ask() 

    logger.info("Starting process...")
    download_yt_video(link=link)
    logger.success("Video process finished.")

def check_network_speed():
    try:
        t0 = time.perf_counter()
        requests.get("https://www.google.com/", timeout=7)
        t1 = time.perf_counter()

        logger.success(f"Responded in: {t1 - t0}s ")

    except:
        logger.error("You aren't connected to the internet!")


downloads_list = []
def watch_downloads():
    global downloads_list
    downloads_path = os.path.join(os.path.expanduser("~"), "storage", "downloads")
    list_dir = os.listdir(downloads_path)
    if downloads_list:
        if list_dir != downloads_list:
            additions = list(set(downloads_list) ^ set(list_dir))
            logger.info("Noticed a new addition to downloads!")
            for addition in additions:
                device.notification("Harbinger", f"New download - {addition}")


    downloads_list = list_dir

current_wifi = 0
def monitor_wifi():
    global current_wifi
    wifi_list = device.wifi()
    if wifi_list and (len(wifi_list) > current_wifi):
        current_wifi = len(wifi_list)
        device.notification(
            title="Discovered new network!",
            content=wifi_list[-1]["ssid"]
        )
        device.vibrate()
        logger.success("Discovered a new wifi network")
        logger.info(f"ssid: {wifi_list[-1]['ssid']}")
        device.append_wifi(wifi_list)

        for wifi in wifi_list:
            print("Network found!")
            logger.info(f"Network: {wifi['ssid']}")
            logger.info(f"Connection: {wifi['capabilities']}")
            logger.info(f"Timestamp: {wifi['timestamp']}")
            print("-"*20)


battery_count = device.battery()["percentage"]
last_10_count = battery_count
low_battery_count = 0
charging = False 

def monitor_battery():
    global battery_count, last_10_count, charging, low_battery_count
    output = device.battery()
    if output["percentage"] < battery_count:
        battery_count = output["percentage"]
        logger.info(f"New battery: {output['percentage']}%")

    if (last_10_count - battery_count) >= 10:
        last_10_count = battery_count
        logger.warning("10 percent lost!")

    if output["percentage"] <= 15 and output["status"] != "charging".upper():
        low_battery_count += 1
    

    if low_battery_count > (60 * 5):
        logger.error(f"Low battery, please charge! - {output['percentage']}%")
        device.vibrate()
        device.notification("Low battery", f"Only {output['percentage']} percent left!")
        low_battery_count = 0 


    if output['status'] != "CHARGING" and charging:
        logger.warning(f"Device unplugged! : {output['percentage']}%")

    if output["status"] == "CHARGING":
        if not charging:
            logger.success(f"Device charging : {output['percentage']}%")
            charging = True
    else:
        charging = False


    
def display_net_details():
    res = device.device_info()
    for r in res:
        logger._log(f"{r}: {res[r]}", "network", False)


def send_get_request():
    prompts = ["Status code", "Html", "Json"]
    url = questionary.text("url:").ask()
    res_type = questionary.select("Response:", prompts).ask() 

    try:
        t0 = time.perf_counter()
        query = requests.get(url)
        t1 = time.perf_counter()

        if res_type == prompts[0]:
            logger.info(str(query.status_code))
        elif res_type == prompts[1]:
            print(query.text)

        elif res_type == prompts[2]:
            print(query.json())
        logger.info(f"responded in: {t1 - t0}")

    except Exception as e:
        logger.error(str(e))


def create_ascii_text():
    text = questionary.text("Enter text:").ask() 
    tprint(text)

schedule.every(1).seconds.do(monitor_battery)
schedule.every(1).seconds.do(monitor_wifi)
schedule.every(1).seconds.do(watch_downloads)

def command_func():
    HELP = """
h, help          => Display this message 
q, exit, quit    => Exit program 
cls, clear       => Clear shell
get, fetch       => Send get request
net              => Displays network details
netspeed         => Check network speed 
yt               => Download Youtube video
restart          => Restart application (memory persists)
reboot           => Reboot application (factory reset)
ascii            => Writes ascii to stdout
head             => Hide/Show the ascii header 
togwifi          => Hide/Show the wifi alerts

settings         => Display current working settings
    """
    while True:
        command = input().lower().strip()
        if command in ["h", "help"]:
            logger._log("Harbinger v 0.1", "help", show_time=False)
            print(HELP)
        elif command in ["q", "exit", "quit"]:
            logger.info("Process completed.")
            sys.exit(0)

        elif command in ["clear", "cls"]:
            subprocess.run("clear")
            if SETTINGS['header']:
                tprint("Harbinger")

        elif command == "netspeed":
            check_network_speed()

        elif command == "yt":
            download_yt_video_prompt()

        elif command == "head":
            SETTINGS['header'] = not SETTINGS['header']
            logger.info(str(SETTINGS['header']))

        elif command == "restart":
            logger.info("Restarting application...")
            restart_program()

        elif command == "net":
            display_net_details()


        elif command in ["get", "fetch"]:
            send_get_request()

        elif command == "ascii":
            create_ascii_text()

        elif command == "settings":
            for key in SETTINGS:
                setting = SETTINGS[key]
                logger._log(f"{key}: {setting}", "setting", False)


        elif command == "reboot":
            logger.info("Rebooting application...")
            reboot_program()





def run_resender():
    while True:
        schedule.run_pending()
    
threading.Thread(target=run_resender, daemon=True).start()
command_func()
