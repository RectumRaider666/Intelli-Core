#!/usr/bin/env python3
import subprocess, os, time, re, argparse
from datetime import datetime

def cenv():
    deps=["curl", "termux-api", "android-tools", "python3", "python3-pip"]

def tap_rec(directory="/sdcard/Download", filename=None, hold_threshold=0.5, time_limit=None):
    os.makedirs(directory, exist_ok=True)
    stamp = filename or datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(directory, f"tap_log_{stamp}.txt")
    video_file = os.path.join(directory, f"vid_log_{stamp}.mp4")

    print(f"Recording to:\n  Log: {log_file}\n  Video: {video_file}\nPress Ctrl+C to stop.")

    pattern_x = re.compile(r'ABS_MT_POSITION_X\s+(\w+)')
    pattern_y = re.compile(r'ABS_MT_POSITION_Y\s+(\w+)')

    record_cmd = ["adb", "shell", "screenrecord", video_file]
    if time_limit:
        record_cmd.insert(3, f"--time-limit={int(time_limit)}")

    screen_proc = subprocess.Popen(record_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(log_file, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(["adb", "shell", "getevent", "-lt"], stdout=subprocess.PIPE, text=True)
        x = y = None
        gesture_points = []
        touch_start_time = None
        try:
            for line in proc.stdout:
                if 'ABS_MT_POSITION_X' in line:
                    match = pattern_x.search(line)
                    if match:
                        x = int(match.group(1), 16)
                elif 'ABS_MT_POSITION_Y' in line:
                    match = pattern_y.search(line)
                    if match:
                        y = int(match.group(1), 16)
                elif 'BTN_TOUCH' in line and 'DOWN' in line:
                    touch_start_time = time.time()
                    gesture_points = [(x, y)] if x is not None and y is not None else []
                elif 'EV_SYN' in line and touch_start_time is not None and x and y:
                    gesture_points.append((x, y))
                elif 'BTN_TOUCH' in line and 'UP' in line:
                    duration = time.time() - touch_start_time if touch_start_time else 0
                    gesture_type = "Tap"
                    if gesture_points:
                        x0, y0 = gesture_points[0]
                        x1, y1 = gesture_points[-1]
                        dist = ((x1 - x0)**2 + (y1 - y0)**2) ** 0.5
                    else:
                        dist = 0
                    if duration >= hold_threshold and dist <= 10:
                        gesture_type = "Hold"
                    elif dist > 10:
                        gesture_type = "Swipe"
                    timestamp_now = datetime.now().isoformat()
                    log_line = f"[{timestamp_now}] {gesture_type} ({duration:.2f}s): {gesture_points}\n"
                    print(log_line.strip())
                    f.write(log_line)
                    f.flush()
                    x = y = None
                    gesture_points.clear()
                    touch_start_time = None
        except KeyboardInterrupt:
            print("\nStopping recording...")
        finally:
            proc.terminate()
            if screen_proc.poll() is None:
                screen_proc.terminate()
            print(f"\nLogs saved to: {log_file}\nVideo saved to: {video_file}")

def main():
    parser = argparse.ArgumentParser(description="Record touch gestures and screen video via ADB.")
    parser.add_argument("-d", "--directory", default="/sdcard/Download", help="Directory to save files")
    parser.add_argument("-f", "--filename", default=None, help="Base filename (default: datetime stamp)")
    parser.add_argument("-t", "--time", type=int, default=None, help="Screen recording time limit in seconds (default: unlimited)")
    args = parser.parse_args()
    tap_rec(directory=args.directory, filename=args.filename, time_limit=args.time)

if __name__ == "__main__":
    main()