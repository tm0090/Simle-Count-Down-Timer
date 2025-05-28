import tkinter as tk
from datetime import datetime, timedelta
import os
import json
import sys
import base64
from ctypes import windll, byref, sizeof, c_int

# Create minimal transparent icon (1x1 pixel)
TRANSPARENT_ICON = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.configure(bg='black')
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Set transparent icon
        try:
            self.root.iconphoto(True, tk.PhotoImage(data=TRANSPARENT_ICON))
        except:
            pass
        
        # Apply Windows dark title bar if available
        self.apply_dark_title_bar()
        
        # Load saved time or use default
        self.target_time = self.load_time() or datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Create UI
        self.create_widgets()
        self.update_timer()
    
    def apply_dark_title_bar(self):
        """Apply Windows dark mode title bar if running on Windows"""
        if sys.platform == 'win32':
            try:
                self.root.update()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                DWMWA_ATTRIBUTE = c_int(DWMWA_USE_IMMERSIVE_DARK_MODE)
                value = c_int(True)
                hwnd = windll.user32.GetParent(self.root.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_ATTRIBUTE,
                    byref(value),
                    sizeof(value)
                )
            except Exception as e:
                print("Could not set dark title bar:", e)
    
    def create_widgets(self):
        # Header with target time
        am_pm = "AM" if self.target_time.hour < 12 else "PM"
        target_hour = self.target_time.hour if self.target_time.hour <= 12 else self.target_time.hour - 12
        if target_hour == 0: 
            target_hour = 12
        self.header = tk.Label(
            self.root, 
            text=f"Time remaining until {target_hour}:{self.target_time.minute:02d} {am_pm}",
            font=('Arial', 14),
            fg='white',
            bg='black'
        )
        self.header.pack(pady=15)
        
        # Countdown display
        self.timer_label = tk.Label(
            self.root,
            text="00:00:00",
            font=('Courier New', 48, 'bold'),
            fg='white',
            bg='black'
        )
        self.timer_label.pack(pady=10)
        
        # Set time button
        self.set_btn = tk.Button(
            self.root,
            text="Set New Target Time",
            command=self.set_time_dialog,
            bg='black',
            fg='white',
            relief='flat',
            activebackground='#333333',
            activeforeground='white',
            bd=1,
            highlightthickness=1,
            highlightbackground="#333",
            highlightcolor="#333"
        )
        self.set_btn.pack(pady=5)
    
    def update_timer(self):
        now = datetime.now()
        next_target = self.target_time
        
        # If target time already passed today, move to next day
        if now.time() > next_target.time():
            next_target = now + timedelta(days=1)
            next_target = next_target.replace(
                hour=self.target_time.hour,
                minute=self.target_time.minute,
                second=0,
                microsecond=0
            )
        else:
            next_target = now.replace(
                hour=self.target_time.hour,
                minute=self.target_time.minute,
                second=0,
                microsecond=0
            )
        
        time_left = next_target - now
        
        # Convert to H:M:S format
        total_seconds = time_left.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.timer_label.config(text=time_str)
        self.root.after(1000, self.update_timer)
    
    def set_time_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Target Time")
        dialog.configure(bg='black')
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Set transparent icon
        try:
            dialog.iconphoto(True, tk.PhotoImage(data=TRANSPARENT_ICON))
        except:
            pass
        
        # Apply dark title bar to dialog
        if sys.platform == 'win32':
            try:
                dialog.update()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                DWMWA_ATTRIBUTE = c_int(DWMWA_USE_IMMERSIVE_DARK_MODE)
                value = c_int(True)
                hwnd = windll.user32.GetParent(dialog.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_ATTRIBUTE,
                    byref(value),
                    sizeof(value)
                )
            except:
                pass
        
        tk.Label(dialog, 
                text="Enter time (HH:MM):", 
                bg='black', 
                fg='white').pack(pady=10)
        
        self.time_entry = tk.Entry(dialog, font=('Arial', 14), justify='center')
        self.time_entry.pack(pady=5)
        self.time_entry.insert(0, f"{self.target_time.hour:02d}:{self.target_time.minute:02d}")
        
        tk.Button(dialog, 
                 text="Save", 
                 command=lambda: self.save_time(dialog), 
                 bg='black', 
                 fg='white').pack(pady=10)
    
    def save_time(self, dialog):
        try:
            time_str = self.time_entry.get()
            hour, minute = map(int, time_str.split(':'))
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
                
            # Create a new target time based on current date
            now = datetime.now()
            self.target_time = now.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )
            
            # Update header
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0: display_hour = 12
            self.header.config(text=f"Time remaining until {display_hour}:{minute:02d} {am_pm}")
            
            # Save to file
            self.save_time_to_file()
            dialog.destroy()
            
        except:
            # Reset to current time on error
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, f"{self.target_time.hour:02d}:{self.target_time.minute:02d}")
    
    def save_time_to_file(self):
        data = {
            'hour': self.target_time.hour,
            'minute': self.target_time.minute
        }
        with open('countdown_settings.json', 'w') as f:
            json.dump(data, f)
    
    def load_time(self):
        try:
            if os.path.exists('countdown_settings.json'):
                with open('countdown_settings.json', 'r') as f:
                    data = json.load(f)
                now = datetime.now()
                return now.replace(
                    hour=data['hour'],
                    minute=data['minute'],
                    second=0,
                    microsecond=0
                )
        except:
            pass
        return None

if __name__ == "__main__":
    root = tk.Tk()
    # Center the window
    root.eval('tk::PlaceWindow . center')
    app = CountdownTimer(root)
    root.mainloop()