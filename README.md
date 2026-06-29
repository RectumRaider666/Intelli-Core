# Intellicore

Collection of random scripts and programs I've wrote.

## Abot

My attempt at a Kalshi Trading bot that uses my self-developed strategy to make new trades and monitor existing ones.

- [X] Async playwright fetcher on a no-gap overlapping handoff.
- [X] Real-Time Rolling Window Ring Buffer of recent prices.
- [X] Tensor mathematics of technical indicators.
- [X] State based decision engine.

## AndFind

My attempt at circumventing Pyautogui's NO-DISPLAY error that happens on android devices, by forcing opencv to check against a screenshot rather than the display itself.

Intended for use in Termux environments with adb wireless debugging on a loop to itself using '$adb tcpip 5555 && adb connect HOST:5555' for device automations using pre-saved images.
## btcswiper
## Daemon

I made this to practice making daemons, learning the signal lib, and system arch
The daemon in this project handels pausing, resuming, restarting, and killing a counter loop in the background. Once a process is running you can use a seperate terminal to control already running processes.

This has no real use. Just cool to see.

## Maze

My blind attempt at single-run maze generation with Python. Now accepts dynamic map sizes.
