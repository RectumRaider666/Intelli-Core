# Intellicore

My collection of random scripts and programs I've wrote.
Some shiny new CrapWare awaits you XD

## Abot

My attempt at a Kalshi Trading bot that uses my self-developed strategy to make new trades and monitor existing ones.

- [X] Async playwright fetcher on a no-gap overlapping handoff.
- [X] Real-Time Rolling Window Ring Buffer of recent prices.
- [X] Tensor mathematics of technical indicators.
- [X] State based decision engine.

## AndFind

My attempt at circumventing Pyautogui's NO-DISPLAY error that happens on android devices, by forcing opencv to check against a screenshot rather than the display itself.

Intended for use in Termux environments with adb wireless debugging on a loop to itself using '$adb tcpip 5555 && adb connect HOST:5555' for device automations using pre-saved images.

## Autux

My attempt at turning Termux into a powerful Device Automation environment that can be easily scripted to build out full & robust automations with an extremely straight-forward cli on a tuned parser makes Android Automation a breeze.

Some Achievments made by Autux:

- [X] Commands runnable via terminal in any directory, full cli control, and in-depth bash scripting addaptioning.
- [X] Simplistic command schema: Running autux tap(X, Y) taps at the coords, autux hold (X,Y,D) for holding a specific coord for a set time
- [X] autux swipe(X1, Y1, X2, Y2, D)
- [X] autux rec or cap(Optional_filename) to start screen recording or taking a screen shot
- [X] autux taprec for a Macro-Scripting by Intiating a Screenrecording, then listening to device signals to interpret where & when you tapped, how hard, how long, and where did you release at, and outputs all logs into a txtfile that can be converted to a macro to perform all the same actions, in the exact manner and timing you pressed them. 
- [X] Many, Many more features & slight compatibility changes to the Termux environment.

## BtcSwiper

My attempt at learning how to create BTC wallets, check balance via block-chain API, create new transactions, & how to publish a transction safley.

## CodeServer

I decided to learn how to host my own managed CodeServer with Shared Collaboration, Sandboxing, Peronsal User Directories, authentication. as my introductory to networks, websites back-end, api endpoints, html/css/js, etc. While redudant anymore with things like Code-Spaces and github.dev personal servers, the project is great for managing small team or in local LAN setting for sharing projects across home devices.     

## Daemon

I made this to practice making daemons, learning the signal lib, and system arch
The daemon in this project handels pausing, resuming, restarting, and killing a counter loop in the background. Once a process is running you can use a seperate terminal to control already running processes.

This has no real use. Just cool to see.

## InTable

A self built brute-force 'jail-break' for the Arcade 1UP Infinity Gaming Tables through a series of device exploits, android-debugging loopbacks, a Termux environment housing Termux-Boot & Termux-Boot, and logic to 'automatically' patch updates by forcing the user into a set of controlled steps that will re-establish the Jail-Break.  

## FstClkr

How fast can a single optimized thread click the mouse over a target X,Y? This project aims to find out by utelizing Rust and its low-level control, in very a tight loop. Plan to figure out a way to count the clicks via serperate running processes.

## Maze

My blind attempt at single-run maze generation with Python. Now accepts dynamic map sizes.

## OrnaBot

**GAME BREAKING CHEATS**
This was actually my first program/script I ever wrote. While the original was wrote in Generic Notepad on a HP Stream 11, 2GB of DDR3L RAM, Intel Celeron N2840, & 32GB eMMC flash memory.
Even on this barbaric heap of a 'computer' and my VERY inefficent coding, I was still capable of landing myself in the Global Leaderboads in just 1 week of full-auto botting. It achieved this by using ADB + SCRCPY + PyAutoGUI.

2-3yrs later and my coding skills have grown immensively, I can control the device without SCRCPY or PyAutoGUI. I also now own an ASUS PRO WRX80SE SAGE 2 + AMD Threadripper Pro 5945wx CPU + 256GB DDR4 ECCRDIMM Ram + 2TB (2x1TB) Samsung 980 Pro NvME.SSD. I can also practically completely drop Python from the project and replace it with much cleaner Rust execution/logic & a healthy dose of Bash 'Glue'. This also gives me the ability of running directly on the device through Termux instead of a connected PC managing the bot by only clicking the SCRCPY window.

So I've come back to visit this program to see just how much better my coding has gotten, but to also laugh histarically as this beast of a PC chews through the game.

## Scripts

These are just random scripts that I used once or twice then never needed to implement anywhere. Not powerful on their own but usefull to keep around. 

## TornBot

**GAME BREAKING CHEATS**
Just a simple project I came up with, aimed at automations involving both local machine and remote api requests, handeling system timing, and managing state-based actions / reactions. 