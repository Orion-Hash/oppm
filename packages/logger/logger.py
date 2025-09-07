# Creates custom Loggers
from datetime import datetime
from tkinter import filedialog, Tk
import inspect
import os

root = Tk()
root.withdraw()  # Hide the root window

class Logger:

    
    LEVELS = {
            "DEBUG": 10,
            "INFO": 20,
            "SUCCESS": 25,
            "WARN": 30,
            "ERROR": 40
        }
    
    def __init__(self, name):
        self.name = name
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
        }
        self.LogTypes = {
            "WARN": self.colors["yellow"],
            "ERROR": self.colors["red"],
            "SUCCESS": self.colors["green"],
            "INFO": self.colors["blue"],
            "DEBUG": self.colors["purple"],
        }
        self.logs = []
        self.current_level = self.LEVELS["DEBUG"]  # default: log everything




    def Display(self, Type, message):
        # --- color setup ---
        color = self.LogTypes.get(Type, "")
        reset_color = "\033[0m"

        # --- timestamp setup ---
        timestamp = datetime.now().strftime("%H:%M:%S")

        # --- context retrieval ---
        frame = inspect.currentframe()
        caller = None
        if frame is not None:
            caller = frame.f_back.f_back
        if caller is None:
            caller = frame.f_back

        if caller is not None:
            filename = os.path.basename(caller.f_code.co_filename)
            func_name = caller.f_code.co_name
            line_no = caller.f_lineno
        else:
            filename = "<unknown>"
            func_name = "<unknown>"
            line_no = 0
        # -------------------------

        # --- log formatting and output ---
        if self.LEVELS[Type] < self.current_level:
            return  # don’t log it

        log_entry = f"[{timestamp}][{Type}] [{self.name}] {message} ({filename}:{func_name}:{line_no})"
        self.logs.append(log_entry)
        print(f"{color}{log_entry}{reset_color}")

        # avoid holding frame references
        del frame
        del caller


    # Create helper methods for each log type
    def Warn(self, message):
        self.Display("WARN", message)
    def Error(self, message):
        self.Display("ERROR", message)
    def Success(self, message):
        self.Display("SUCCESS", message)
    def Info(self, message):
        self.Display("INFO", message)
    def Debug(self, message):
        self.Display("DEBUG", message)

    def SaveLogs(self, file_path=None):
        if not file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(f"Logs for {self.name}\n")
                f.write("="*40 + "\n")
                for log in self.logs:
                    f.write(log + "\n")
            self.Info(f"Logs saved to {file_path}")
        else:
            self.Warn("Log saving cancelled.")

    def SetLevel(self, level):
        if level not in self.LEVELS:
            self.Warn(f"Invalid log level: {level}")
        else:
            if level in Logger.LEVELS:
                self.current_level = self.LEVELS[level]
                self.Info(f"Log level set to {level}")

