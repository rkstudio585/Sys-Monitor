# Termux System Monitor

This is a Python-based system monitor designed for Termux, providing real-time insights into your device's performance.

## Features

- **Real-time Terminal UI:** Utilizes `curses` for an interactive and live-updating dashboard.
- **Comprehensive Metrics:** Displays CPU usage (overall and per-core), RAM usage, battery status, and storage information for root and SD card partitions.
- **Top Processes:** Shows the top 5 resource-intensive processes, sortable by CPU or RAM usage.
- **Visual Elements:** Features color-coded progress bars using Unicode block characters for easy readability.
- **Dynamic Resizing:** Automatically adjusts to terminal dimensions.
- **User Controls:**
    - `q`: Quit the application.
    - `Tab`: Toggle process sorting between CPU and RAM usage.
    - `r`: Manual refresh (though updates are continuous).
- **Termux Compatibility:** Handles Android-specific paths and uses `termux-battery-status` for accurate battery information.
- **Fallback Mode:** Automatically switches to a simple text-based output if `curses` is not available or encounters issues.
- **Alerts:** Provides warnings for low battery (<15%) and high storage usage (>90%).

## Installation

1. **Install Termux:** If you don't have Termux, download it from F-Droid or Google Play Store.

2. **Install Python and necessary packages:**
   ```bash
   pkg install python
   pip install psutil
   pkg install termux-api
   ```

3. **Clone the repository:**
   ```bash
   git clone https://github.com/rkstudio585/Sys-Monitor.git
   cd Sys-Monitor
   ```

## Usage

To run the system monitor:

```bash
python sys_monitor.py
```

To run in text-only mode (if `curses` causes issues or for basic output):

```bash
python sys_monitor.py --text
```

## Troubleshooting

- **Permission Denied Errors:** If you encounter `PermissionError` for `/proc/stat` or `/sys/class/power_supply`, this is due to Android's security restrictions. The script includes error handling to gracefully manage these, displaying "Permission Denied" for the affected metrics.
- **`curses` issues:** If the `curses` UI fails to initialize, the script will automatically fall back to text mode. Ensure your Termux environment is up-to-date.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements.
