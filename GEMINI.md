Create a Python system monitor for Termux with the following requirements:

1. **Metrics Display**  
   - Use `psutil` to collect:  
     - CPU usage (per core and overall)  
     - RAM usage (used/cached/buffers)  
     - Storage (root and sdcard partitions)  
     - Battery (percentage, status, health)  
     - Top 5 processes by CPU/RAM  

2. **Terminal UI**  
   - Implement using `curses` for live updating  
   - Layout:  
     ```
     +-----------------------+
     | CPU [██████   60%]    |
     | RAM [████▊    45%]    |
     | BAT [█████▎   78%]    |
     +-----------------------+
     | Storage:              |
     | /     [██████ 85%]    |
     | /sdcard [███    30%]  |
     +-----------------------+
     | Processes:            |
     | chrome      32% CPU   |
     | python      15% CPU   |
     | ...                   |
     +-----------------------+  
     ```  

3. **Visual Elements**  
   - Progress bars using Unicode block characters (▏▎▍▌▋▊▉█)  
   - Color coding:  
     - Green: <50% usage  
     - Yellow: 50-75%  
     - Red: >75%  
   - Auto-resize with terminal dimensions  

4. **Features**  
   - Refresh interval: 1 second  
   - Sort processes by CPU/RAM (tab toggle)  
   - Disk space warnings (>90% used)  
   - Battery alerts (<15% level)  

5. **Termux Compatibility**  
   - Handle Android-specific paths (`/storage/emulated/0`)  
   - Fallback to text mode if `curses` fails  
   - Minimal dependencies (only `psutil` + stdlib)  

6. **Controls**  
   - `q`: Quit  
   - `Tab`: Toggle process sort (CPU/RAM)  
   - `r`: Refresh immediately  

7. **GitHub & Cli**
    - Always make a new branch and push on GitHub.
    ```
    git init
    git add .
    git commit -m "<commit-name>"
    git branch -M main
    git remote add origin https://github.com/rkstudio585/Sys-Monitor.git
    git push -u origin main
    ```

Include error handling for missing sensors (e.g., battery on emulators).
