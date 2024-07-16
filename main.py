import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoring Tool")

        root.configure(bg='#2b2b2b')
        root.option_add('*TCombobox*Listbox*background', '#2b2b2b')
        root.option_add('*TCombobox*Listbox*foreground', 'white')
        root.option_add('*TCombobox*Listbox*selectBackground', '#4b4b4b')
        root.option_add('*TCombobox*Listbox*selectForeground', 'white')

        style = ttk.Style()
        style.configure('TLabel', foreground='white', background='#2b2b2b')
        style.configure('TButton', foreground='white', background='#444444', font=('Segoe UI', 10))
        style.map('TButton', background=[('active', '#666666')])
        style.configure('TRadiobutton', background='#2b2b2b', foreground='white')
        style.map('TRadiobutton', background=[('active', '#444444')])

        self.monitor_registry = tk.IntVar()
        self.monitor_files = tk.IntVar()
        self.monitor_processes = tk.IntVar()
        self.monitor_network = tk.IntVar()

        ttk.Checkbutton(root, text="Monitor Registry", variable=self.monitor_registry, style='TRadiobutton').grid(row=0, sticky=tk.W)
        ttk.Checkbutton(root, text="Monitor Files", variable=self.monitor_files, style='TRadiobutton').grid(row=1, sticky=tk.W)
        ttk.Checkbutton(root, text="Monitor Processes", variable=self.monitor_processes, style='TRadiobutton').grid(row=2, sticky=tk.W)
        ttk.Checkbutton(root, text="Monitor Network", variable=self.monitor_network, style='TRadiobutton').grid(row=3, sticky=tk.W)

        self.start_button = ttk.Button(root, text="Start Monitoring", command=self.start_monitoring, style='TButton')
        self.start_button.grid(row=4, pady=10)
        
        self.stop_button = ttk.Button(root, text="Stop Monitoring", state=tk.DISABLED, command=self.stop_monitoring, style='TButton')
        self.stop_button.grid(row=4, column=1, pady=10)
        
        self.open_logs_button = ttk.Button(root, text="Open Log Files", command=self.open_logs, style='TButton')
        self.open_logs_button.grid(row=5, pady=10)
        
        self.subprocesses = []

    def start_monitoring(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        subprograms_dir = os.path.join(base_dir, 'subprograms')

        if self.monitor_registry.get() == 1:
            proc = subprocess.Popen(['python', os.path.join(subprograms_dir, 'registry_logging.py')])
            self.subprocesses.append(proc)

        if self.monitor_files.get() == 1:
            proc = subprocess.Popen(['python', os.path.join(subprograms_dir, 'files_logging.py')])
            self.subprocesses.append(proc)

        if self.monitor_processes.get() == 1:
            proc = subprocess.Popen(['python', os.path.join(subprograms_dir, 'process_logging.py')])
            self.subprocesses.append(proc)

        if self.monitor_network.get() == 1:
            proc = subprocess.Popen(['python', os.path.join(subprograms_dir, 'network_logging.py')])
            self.subprocesses.append(proc)

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_monitoring(self):
        for proc in self.subprocesses:
            proc.terminate()

        time.sleep(1)

        self.subprocesses = []

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def open_logs(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        logs_dir = os.path.join(base_dir, 'logs')

        if os.path.exists(logs_dir):
            subprocess.Popen(['explorer', logs_dir]) 
        else:
            messagebox.showinfo("Logs Directory Not Found", "The logs directory does not exist.")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
