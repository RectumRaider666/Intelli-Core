#!/usr/bin/env python3

from pathlib import Path
import subprocess
import threading
import signal
import socket
import time
import sys
import os

PROC_COUNT = 1
VALIDS = []

ROOT = Path(__file__).parent
PIDS_FILE = str(ROOT / "pids.txt")
SOCK_DIR = str(f"/tmp/counter")
SOCK_FILE = str(f"/tmp/counter/{PROC_COUNT}.sock")

## <!-- [PID] ----->
def add_pid(pid:int) -> str:
	"""Adds a pid value to pids.txt"""
	with open(PIDS_FILE, "a") as f:
		 f.write(f"{pid}\n")
    return str(f"Added Counter ID:{pid} to pids.txt")

def del_pid(pid:int) -> str:
	"""Deletes an active pid from pids.txt"""
    active = []
    with open(PIDS_FILE, "r") as f:
        for line in f:
            fx_pid = int(line.strip())
            active.append(fx_pid)
        if pid in active:
            os.kill(pid, signal.SIGTERM)
            active.remove(pid)
            with open(PIDS_FILE, "w") as fx:
                for pid in active:
                    fx.write(f"{pid}\n")
            return str(f"Process {pid} was terminated")
        elif pid not in active:
            return str(f"PID: {pid} was not found")
	
def clear_pid() -> str:
    """Deletes all pids from pids.txt"""
    count = 0
    with open(PIDS_FILE, "r") as f:
        for line in f:
            fx_pid = int(line.strip())
            os.kill(fx_pid, signal.SIGTERM)
            print(f"Terminated PID: {fx_pid}")
            count += 1
    open(PIDS_FILE, "w").close()
    return str(f"Terminated {count} processes")

## <!-- [IPC Socket] ----->
def search_ipc() -> list:
    """Returns the names of any IPC Socket files it finds"""
    socks = []
    try:
        for sock in SOCKET_DIR.glob("counter*.sock"):
            socks.append(sock)
        if socks:
            return (socks)
    except FileNotFoundError:
        return ("No sock files were found")

def clear_ipc() -> str:
    """Clears all ipc socket files"""
    for sock in SOCKET_DIR.glob("counter*.sock")
        suff = sock.stem.removeprefix("counter")
        if suff.isdigit():
            try:
                sock.unlink()
                print(f"Socket {sock} was successfully unlinked")
            except:
                print(f"Error deleting sock file {sock}")
    return str("Finished clearing ipc sock files")

def del_ipc(ipc:int) -> str:
    """Deletes a specific ipc sock file"""
    try:
        os.remove(str("/tmp/counter/counter{ipc}.sock"))
        return str(f"Sock file {ipc} was deleted")
    except FileNotFoundError:
        return str(f"Sock file {ipc} doesnt exist")

## <!-- [Daemon Object] ----->
def Counter:
	"""Initializes a process in the background"""
	def __init__(self):
		self.count = 0
		self.pid = None
		self.running = False
		self.paused = False
		self.lock = threading.lock()
		
	def loop(self):
		"""Starts Counting Loop"""
		while True:
			if not self.running:
				break
			if not self.paused:
				self.count += 1
			elif self.paused:
				pass
	
	def begin(self) -> str:
		"""Start the counter"""
		with self.lock:
			if self.running:
				return str(f"Counter ID:{self.pid}, Already Running")
			self.running = True
			self.paused = False
		threading.Thread(target=self.loop, daemon=True).start()
		return str(f"Counter ID:{self.pid}, Successfully Started")
		
	def pause(self) -> str:
		"""Pauses a process in the background"""
		with self.lock:
			self.paused = True
		return str(f"Counter ID:{self.pid}, Paused")
		
	def resume(self) -> str:
		"""Resumes a paused processes counter"""
		with self.lock:
			self.paused = False
		return str(f"Counter ID:{self.pid}, Resumed Processing")
		
	def reset(self) -> int:
		"""Returns count to 0"""
		with self.lock:
			self.count = 0
		return str(f"Counter ID:{self.pid}, Reset to 0")
		
	def show(self) -> str:
		"""Returns the current count to console"""
		with self.lock:
			return str(f"Count ID:{self.pid}, Current-Count:{self.count}")

## <!-- [Daemon] ----->
def inti() -> list:
	"""Initializes the Daemon and Dependencies & Returns Active PID list"""
	os.makedirs(PIDS_FILE, exists_ok = True)
	with open(PID_FILE, "r") as f:
		for line in f:
			try:
				pid = int(line.strip())
				VALIDS.append(pid)
				PROC_COUNT += 1
			except:
				pass
	return VALIDS

def run_daemon():
	"""Initializes a Daemon server"""
	VALIDS = inti()
	Daemon = Counter()
	server = socket.socket(Socket.AF_UNIX, socket.SOCK_STREAM)
	server.bind(SOCK_FILE)
	server.listen(5)
	while True:
		conn, _ = server.accept()
		cmd = conn.recv(1024).decode().strip().lower()
		
		if cmd == "count start"
		    response = Daemon.start()
		    
		elif cmd == "count pause":
			response = Daemon.pause()
			
		elif cmd == "count resume":
			response = Daemon.resume()
			
		elif cmd == "count reset":
			response = Daemon.reset()
			
		elif cmd == "count show":
			response = Daemon.show()
		
		else:
			response = str("Unkown Command")
	    
	    conn.send(response.encode())
	    conn.close()
	    
def start_daemon():
	"""Begins a full background process and assigns PID"""
	process = subprocess.Popen(
	    [
	        sys.executable,
	        __file__,
	        "--daemon"
	    ],
	    start_new_session = True,
	    stdout = subprocess.DEVNULL,
	    stderr = subprocess.DEVNULL
	)
	pid = int(process.pid)
	Counter.pid = int(pid)

## <!-- [Client] ----->
def send(cmd, ipc:str):
	"""Send a specific socket IPC a command"""
	if not os.path.exists(SOCK_FILE):
		print (f"Daemon Not Running")
		return
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(SOCK_FILE)
	s.send(cmd.encode())
	print (s.recv(1024).decode())
	s.close()

## <!-- [Entry] ----->
def main():
    """The main program loop"""
    # Check to see if there is anything in pids.txt
    # Check to see if there is any tmp socket files
    ## If there is a process already running, return their current states otherwise start a new one

if __name__ == "__main__":
	"""The main entry point"""
	main()	