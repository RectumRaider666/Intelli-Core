#!/usr/bin/env python3

import sys
import subprocess
from datetime import datetime
import time
import os
import argparse

_dir = os.path.dirname(os.path.abspath(__file__))

def check_display():
    """Check if display is available"""
    try:
        import os
        if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            return True
        return False
    except:
        return False

def init_mouse_control():
    """Initialize mouse control with fallback options"""
    global mouse_controller, Button, display_available, use_xdotool
    display_available = check_display()
    use_xdotool = False
    try:
        from pynput.mouse import Button, Controller
        mouse_controller = Controller()
        if display_available:
            try:
                pos = mouse_controller.position
                print(f"pynput mouse control available at: {pos}")
                return True
            except Exception as e:
                print(f"pynput failed despite display: {e}")
                display_available = False
    except ImportError:
        print("pynput not available")
    if not display_available:
        try:
            result = subprocess.run(['which', 'xdotool'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Using xdotool as fallback")
                use_xdotool = True
                display_available = True
                return True
        except:
            pass
    if not display_available:
        print("No mouse control available - will run in simulation mode")
    return display_available

def get_mouse_position():
    """Get current mouse position"""
    try:
        if display_available and not use_xdotool:
            return mouse_controller.position
        elif use_xdotool:
            result = subprocess.run(['xdotool', 'getmouselocation'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                parts = output.split()
                x = int(parts[0].split(':')[1])
                y = int(parts[1].split(':')[1])
                return (x, y)
        import random
        x, y = random.randint(0, 1920), random.randint(0, 1080)
        print(f"SIMULATION: Mock mouse position: ({x}, {y})")
        return (x, y)
    except Exception as e:
        print(f"Error getting mouse position: {e}")
        return (0, 0)

def click_at_position(x, y):
    """Click at specified position"""
    try:
        if display_available and not use_xdotool:
            mouse_controller.position = (x, y)
            mouse_controller.click(Button.left, 1)
            return True
        elif use_xdotool:
            subprocess.run(['xdotool', 'mousemove', str(x), str(y)], check=True)
            subprocess.run(['xdotool', 'click', '1'], check=True)
            return True
        else:
            print(f"SIMULATION: Would click at ({x}, {y})")
            return False
    except Exception as e:
        print(f"Error clicking at ({x}, {y}): {e}")
        print(f"SIMULATION: Would click at ({x}, {y})")
        return False

def get_mouse_positions():
    """Capture mouse positions when Enter is pressed"""
    history = {}
    print("Mouse Position Tracker")
    print("Press Enter to capture current mouse position")
    print("Press Ctrl+C to exit and show history")
    if not display_available:
        print("WARNING: Running in simulation mode")
    try:
        while True:
            input()
            x, y = get_mouse_position()
            timestamp = datetime.now()
            history[timestamp] = (x, y)
            print(f"Position captured: {x}, {y}")
    except KeyboardInterrupt:
        print("\nExiting...")
        if history:
            print("\nCaptured positions:")
            for timestamp, position in history.items():
                print(f"{timestamp.strftime('%H:%M:%S')}: {position}")
        return history

def save_positions_to_file(history, filename="mouse_positions.txt"):
    """Save captured positions to a file"""
    if not history:
        return
    with open(filename, "w") as f:
        f.write("Mouse Position History\n")
        f.write("=" * 30 + "\n")
        for timestamp, position in history.items():
            f.write(f"{timestamp}: {position}\n")
    print(f"Positions saved to {filename}")

def click_macro(filename, delay=1.0):
    """Execute a click macro from a position history file"""
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
        positions = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Mouse Position History") or line.startswith("="):
                continue
            if ": (" in line and line.endswith(")"):
                try:
                    timestamp_part, coords_part = line.split(": (", 1)
                    coords_part = coords_part.rstrip(")")
                    x, y = coords_part.split(", ")
                    positions.append((int(x), int(y)))
                    print(f"Parsed position: ({x}, {y})")
                except (ValueError, IndexError) as e:
                    print(f"Skipping invalid line: {line} - {e}")
                    continue
        if not positions:
            print("No valid positions found in file")
            return
        print(f"Found {len(positions)} positions to click")
        if not display_available:
            print("WARNING: Running in simulation mode")
        print("Starting macro in 3 seconds...")
        time.sleep(3)
        successful_clicks = 0
        for i, (x, y) in enumerate(positions, 1):
            print(f"Position {i}/{len(positions)}: ({x}, {y})")
            success = click_at_position(x, y)
            if success:
                successful_clicks += 1
            time.sleep(delay)
        if display_available:
            print(f"Macro completed! {successful_clicks}/{len(positions)} clicks successful.")
        else:
            print("Simulation completed!")
    except FileNotFoundError:
        print(f"Macro file {filename} not found.")
    except Exception as e:
        print(f"Error executing macro: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mouse position tracker and macro executor")
    parser.add_argument("--version", action="version", version="2.0.0")
    parser.add_argument("--save", action="store_true", help="Save positions to file")
    parser.add_argument("--macro", type=str, help="Execute macro from position history file")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between clicks in seconds")
    parser.add_argument("--force", action="store_true", help="Force execution in simulation mode")
    args = parser.parse_args()
    has_display = init_mouse_control()
    if not has_display and not args.force:
        print("No display/mouse control detected.")
        print("Use --force to run in simulation mode.")
        print("Install xdotool for Linux CLI mouse control.")
        exit(1)
    if args.macro:
        click_macro(args.macro, args.delay)
    else:
        positions = get_mouse_positions()
        if args.save and positions:
            save_positions_to_file(positions)

