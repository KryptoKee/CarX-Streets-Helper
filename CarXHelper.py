import tkinter as tk
from tkinter import ttk, messagebox
import pymem
import threading
import time
from ttkthemes import ThemedTk

class GameResource:
    def __init__(self, name, offsets, format_func):
        self.name = name
        self.offsets = offsets
        self.format_func = format_func

def calculate_xp_for_level(level):
    if level == 1:
        return 0  # Minimum XP for level 1
    elif level == 2:
        return 700  # Changed from 701 to 700
    elif 3 <= level <= 24:
        return 1500 + (level - 3) * 1000
    elif level == 25:
        return 25300  # Changed from 25301 to 25300
    elif 26 <= level <= 31:
        return 27300 + (level - 26) * 2000
    elif level == 32:
        return 39300  # Changed from 39301 to 39300
    elif level == 33:
        return 41300  # Changed from 41301 to 41300
    elif 34 <= level <= 49:
        return 44300 + (level - 34) * 3000
    elif level == 50:
        return 92300  # Changed from 92301 to 92300
    else:
        return 0  # Invalid level

def calculate_max_xp_for_level(level):
    if level == 1:
        return 700
    elif level == 2:
        return 1500
    elif 3 <= level <= 24:
        return 2500 + (level - 3) * 1000
    elif level == 25:
        return 27300
    elif 26 <= level <= 31:
        return 29300 + (level - 26) * 2000
    elif level == 32:
        return 41300
    elif level == 33:
        return 44300
    elif 34 <= level <= 49:
        return 47300 + (level - 34) * 3000
    elif level == 50:
        return 92300
    else:
        return 0  # Invalid level

class CarXStreetModifier:
    def __init__(self, master):
        self.master = master
        master.title("CarX Street Modifier")
        master.geometry("500x475")
        master.resizable(False, False)
        master.configure(bg='#1e1e1e')

        self.process_name = "CarX Street"
        self.base_address = 0x07927218
        self.resources = [
            GameResource("XP", [0xB8, 0x58, 0x60, 0x20, 0x18, 0x60, 0x38], lambda x: f"{x:,.0f}"),
            GameResource("Cash", [0xB8, 0x58, 0x70, 0x60, 0x18, 0x30, 0x38], lambda x: f"${x:,.0f}"),
            GameResource("Gold", [0xB8, 0x58, 0x70, 0x60, 0x18, 0x48, 0x38], lambda x: f"{x:,.0f}")
        ]

        self.pm = None
        self.module = None
        self.connected = False
        self.lock = threading.Lock()
        self.running = True

        self.setup_styles()
        self.create_widgets()
        self.update_thread = threading.Thread(target=self.update_values_thread, daemon=True)
        self.update_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def setup_styles(self):
        self.style = ttk.Style(self.master)
        self.style.theme_use('equilux')
        self.style.configure('TFrame', background='#1e1e1e')
        self.style.configure('TButton', font=('Segoe UI', 10), background='#0078d4', foreground='white')
        self.style.map('TButton', background=[('active', '#005a9e')])
        self.style.configure('TEntry', font=('Segoe UI', 10), fieldbackground='#2d2d2d', foreground='white')
        self.style.configure('TLabel', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background='#1e1e1e', foreground='#0078d4', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Current.TLabel', background='#1e1e1e', foreground='#00ca00', font=('Segoe UI', 12, 'bold'))
        self.style.configure('TScale', background='#1e1e1e', troughcolor='#2d2d2d', slidercolor='#0078d4')
        self.style.configure('Group.TFrame', background='#252525')  # Slightly lighter background for grouping

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="CarX Street Modifier", style='Header.TLabel').pack(pady=(0, 20))

        # Connection status and controls
        status_frame = ttk.Frame(main_frame, style='Group.TFrame', padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Button(status_frame, text="Connect", command=self.connect_to_game, width=12).pack(side=tk.LEFT)
        ttk.Button(status_frame, text="Refresh", command=self.refresh_values, width=12).pack(side=tk.LEFT, padx=10)
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Segoe UI', 12), foreground='#ff0000')
        self.status_label.pack(side=tk.RIGHT)

        # Resources
        resources_frame = ttk.Frame(main_frame, style='Group.TFrame', padding=10)
        resources_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.resource_frames = {}
        for i, resource in enumerate(self.resources):
            frame = ttk.Frame(resources_frame, style='TFrame')
            frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(frame, text=f"{resource.name}:", style='TLabel', width=10).pack(side=tk.LEFT)
            
            new_value_var = tk.StringVar()
            ttk.Entry(frame, textvariable=new_value_var, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Set", command=lambda r=resource, v=new_value_var: self.set_value(r, v), width=8).pack(side=tk.LEFT, padx=(0, 10))

            current_value_var = tk.StringVar(value="N/A")
            ttk.Label(frame, textvariable=current_value_var, style='Current.TLabel', width=15).pack(side=tk.RIGHT)

            self.resource_frames[resource.name] = {"current_var": current_value_var, "new_var": new_value_var}

        # Level control
        level_frame = ttk.Frame(main_frame, style='Group.TFrame', padding=10)
        level_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(level_frame, text="Level:", style='TLabel').pack(side=tk.LEFT)
        self.level_var = tk.IntVar(value=1)
        self.level_slider = ttk.Scale(level_frame, from_=1, to=50, orient=tk.HORIZONTAL, variable=self.level_var, command=self.update_xp_from_level)
        self.level_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        self.level_label = ttk.Label(level_frame, text="1", style='TLabel')
        self.level_label.pack(side=tk.RIGHT)

        # XP Range and Set Button
        xp_frame = ttk.Frame(main_frame, style='Group.TFrame', padding=10)
        xp_frame.pack(fill=tk.X)
        self.xp_range_label = ttk.Label(xp_frame, text="XP Range: 0 - 700", style='TLabel')
        self.xp_range_label.pack(side=tk.LEFT)
        ttk.Button(xp_frame, text="Set XP from Slider", command=self.set_xp_from_slider, width=20).pack(side=tk.RIGHT)

    def update_xp_from_level(self, *args):
        level = self.level_var.get()
        min_xp = calculate_xp_for_level(level)
        max_xp = calculate_max_xp_for_level(level)
        self.level_label.config(text=str(level))
        self.xp_range_label.config(text=f"Level's XP Range: {min_xp:,} - {max_xp:,}")

    def set_xp_from_slider(self):
        level = self.level_var.get()
        xp = calculate_xp_for_level(level)
        self.set_value(self.resources[0], tk.StringVar(value=str(xp)))

    def connect_to_game(self):
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.module = pymem.process.module_from_name(self.pm.process_handle, "GameAssembly.dll")
            if not self.module:
                raise Exception("GameAssembly.dll not found")
            self.connected = True
            self.status_var.set("Connected")
            self.status_label.configure(foreground='green')
            self.refresh_values()
        except Exception as e:
            self.disconnect()
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}\nPlease ensure the game is running.")

    def disconnect(self):
        self.connected = False
        self.status_var.set("Disconnected")
        self.status_label.configure(foreground='red')
        if self.pm:
            self.pm.close_process()
            self.pm = None
        self.module = None

    def read_memory(self, offsets):
        if not self.connected:
            return None
        try:
            with self.lock:
                address = self.module.lpBaseOfDll + self.base_address
                for offset in offsets:
                    address = self.pm.read_longlong(address) + offset
                return self.pm.read_float(address)
        except Exception as e:
            self.disconnect()
            print(f"Error reading memory: {e}")
            return None

    def write_memory(self, address, value):
        if not self.connected:
            return False
        try:
            with self.lock:
                for i in range(8):
                    self.pm.write_float(address + i * 4, value)
            return True
        except Exception as e:
            self.disconnect()
            print(f"Error writing memory: {e}")
            return False

    def refresh_values(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the game first.")
            return
        for resource in self.resources:
            value = self.read_memory(resource.offsets)
            if value is not None:
                formatted_value = resource.format_func(value)
                self.resource_frames[resource.name]["current_var"].set(formatted_value)
            else:
                self.resource_frames[resource.name]["current_var"].set("N/A")

    def set_value(self, resource, value_var):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the game first.")
            return
        try:
            new_value = float(value_var.get().replace('$', '').replace(',', ''))
            if new_value < 0:
                raise ValueError("Value must be non-negative")
            address = self.module.lpBaseOfDll + self.base_address
            for offset in resource.offsets:
                address = self.pm.read_longlong(address) + offset
            if self.write_memory(address, new_value):
                self.refresh_values()
                messagebox.showinfo("Success", f"{resource.name} value updated successfully.")
            else:
                messagebox.showerror("Error", f"Failed to set {resource.name} value")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def update_values_thread(self):
        while self.running:
            if self.connected:
                self.refresh_values()
            time.sleep(5)

    def on_closing(self):
        self.running = False
        self.disconnect()
        self.master.destroy()

def main():
    root = ThemedTk(theme="arc")
    app = CarXStreetModifier(root)
    root.mainloop()

if __name__ == "__main__":
    main()