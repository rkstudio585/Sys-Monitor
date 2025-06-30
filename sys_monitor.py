
import curses
import psutil
import time
import os
import sys
import subprocess
import json
from datetime import datetime

def get_termux_battery_status():
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        percent = data.get('percentage')
        status = data.get('status')
        plugged = data.get('plugged') == 'PLUGGED_AC' or data.get('plugged') == 'PLUGGED_USB'
        return {'percent': percent, 'status': status, 'power_plugged': plugged}
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None

def get_color(percent):
    if percent < 50:
        return 1  # Green
    elif 50 <= percent < 75:
        return 2  # Yellow
    else:
        return 3  # Red

def get_bar(percent, width):
    filled_width = int(percent / 100 * width)
    bar = "█" * filled_width
    bar += " " * (width - filled_width)
    return bar

def get_processes(sort_by='cpu'):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if sort_by == 'cpu':
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    else:
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)

    return processes[:5]

def main_curses(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(0)
    stdscr.nodelay(1)

    sort_by = 'cpu'

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('\t'):
            sort_by = 'ram' if sort_by == 'cpu' else 'cpu'
        elif key == ord('r'):
            pass  # Refresh is continuous

        h, w = stdscr.getmaxyx()
        stdscr.clear()

        # CPU
        cpu_percents = [] # Initialize to an empty list
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_percents = psutil.cpu_percent(interval=None, percpu=True)
            stdscr.addstr(0, 1, f"CPU [{get_bar(cpu_percent, 10)}] {cpu_percent}%", curses.color_pair(get_color(cpu_percent)))
            for i, p in enumerate(cpu_percents):
                stdscr.addstr(1 + i, 1, f"  Core {i} [{get_bar(p, 10)}] {p}%", curses.color_pair(get_color(p)))
        except PermissionError:
            stdscr.addstr(0, 1, "CPU [Permission Denied]")

        # RAM
        mem = psutil.virtual_memory()
        stdscr.addstr(len(cpu_percents) + 2, 1, f"RAM [{get_bar(mem.percent, 10)}] {mem.percent}%", curses.color_pair(get_color(mem.percent)))

        # Storage
        try:
            storage_root = psutil.disk_usage('/')
            stdscr.addstr(len(cpu_percents) + 4, 1, "Storage:")
            stdscr.addstr(len(cpu_percents) + 5, 1, f"  /     [{get_bar(storage_root.percent, 10)}] {storage_root.percent}%", curses.color_pair(get_color(storage_root.percent)))
            if storage_root.percent > 90:
                stdscr.addstr(len(cpu_percents) + 5, 30, "Storage Warning!", curses.A_BOLD | curses.color_pair(3))
        except PermissionError:
            stdscr.addstr(len(cpu_percents) + 4, 1, "Storage: Permission Denied for /")
        try:
            storage_sd = psutil.disk_usage('/storage/emulated/0')
            stdscr.addstr(len(cpu_percents) + 6, 1, f"  /sdcard [{get_bar(storage_sd.percent, 10)}] {storage_sd.percent}%", curses.color_pair(get_color(storage_sd.percent)))
            if storage_sd.percent > 90:
                stdscr.addstr(len(cpu_percents) + 6, 30, "Storage Warning!", curses.A_BOLD | curses.color_pair(3))
        except PermissionError:
            stdscr.addstr(len(cpu_percents) + 6, 1, "Storage: Permission Denied for /sdcard")


        # Battery
        battery_info = get_termux_battery_status()
        if battery_info:
            bat_percent = battery_info['percent']
            charge_char = "▲" if battery_info['power_plugged'] else "▼"
            health_char = "♥" # Simplified
            if bat_percent < 15:
                stdscr.addstr(len(cpu_percents) + 8, 1, f"BAT [{get_bar(bat_percent, 10)}] {bat_percent}% {charge_char} {health_char}", curses.A_BOLD | curses.color_pair(3))
                stdscr.addstr(len(cpu_percents) + 8, 30, "Low Battery!", curses.A_BOLD | curses.color_pair(3))
            else:
                stdscr.addstr(len(cpu_percents) + 8, 1, f"BAT [{get_bar(bat_percent, 10)}] {bat_percent}% {charge_char} {health_char}", curses.color_pair(get_color(bat_percent)))
        else:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    charge_char = "▲" if battery.power_plugged else "▼"
                    health_char = "♥" # Simplified
                    bat_percent = battery.percent
                    if bat_percent < 15:
                        stdscr.addstr(len(cpu_percents) + 8, 1, f"BAT [{get_bar(bat_percent, 10)}] {bat_percent}% {charge_char} {health_char}", curses.A_BOLD | curses.color_pair(3))
                        stdscr.addstr(len(cpu_percents) + 8, 30, "Low Battery!", curses.A_BOLD | curses.color_pair(3))
                    else:
                        stdscr.addstr(len(cpu_percents) + 8, 1, f"BAT [{get_bar(bat_percent, 10)}] {bat_percent}% {charge_char} {health_char}", curses.color_pair(get_color(bat_percent)))

            except (AttributeError, FileNotFoundError, PermissionError):
                 stdscr.addstr(len(cpu_percents) + 8, 1, "BAT [No battery sensor found or Permission Denied]")


        # Processes
        stdscr.addstr(len(cpu_percents) + 10, 1, f"Processes (sort: {sort_by.upper()})")
        try:
            processes = get_processes(sort_by)
            for i, p in enumerate(processes):
                stdscr.addstr(len(cpu_percents) + 11 + i, 1, f"  {p['name']:<15} {p['cpu_percent'] if sort_by == 'cpu' else p['memory_percent']:.1f}%")
        except PermissionError:
            stdscr.addstr(len(cpu_percents) + 11, 1, "  Process information: Permission Denied")


        stdscr.refresh()
        time.sleep(1)

def main_text():
    while True:
        print("--- System Monitor (Text Mode) ---")
        # CPU
        try:
            print(f"CPU Usage: {psutil.cpu_percent()}%")
        except PermissionError:
            print("CPU Usage: Permission Denied")
        # RAM
        mem = psutil.virtual_memory()
        print(f"RAM Usage: {mem.percent}%")
        # Storage
        try:
            storage_root = psutil.disk_usage('/')
            print(f"Root Storage: {storage_root.percent}%")
        except PermissionError:
            print("Root Storage: Permission Denied")
        try:
            storage_sd = psutil.disk_usage('/storage/emulated/0')
            print(f"SD Card Storage: {storage_sd.percent}%")
        except PermissionError:
            print("SD Card Storage: Permission Denied")
        # Battery
        battery_info = get_termux_battery_status()
        if battery_info:
            print(f"Battery: {battery_info['percent']}% (Termux)")
        else:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    print(f"Battery: {battery.percent}% (psutil)")
            except (AttributeError, FileNotFoundError, PermissionError):
                print("Battery: Not found or Permission Denied")

        print("")
        print("--- Top 5 Processes (CPU) ---")
        try:
            processes = get_processes('cpu')
            for p in processes:
                print(f"  {p['name']:<15} {p['cpu_percent']:.1f}%")
        except PermissionError:
            print("  Process information: Permission Denied")

        time.sleep(2)
        


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--text':
        main_text()
    else:
        try:
            curses.wrapper(main_curses)
        except curses.error:
            print("curses error. Falling back to text mode.")
            main_text()

