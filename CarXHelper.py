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

class CarXStreetModifier:
    def __init__(self, master):
        self.master = master
        master.title("CarX Streets Helper")
        master.geometry("450x300")
        master.configure(bg='#2c3e50')

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
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TLabel', background='#2c3e50', foreground='white', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background='#2c3e50', foreground='#3498db', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Current.TLabel', background='#2c3e50', foreground='#2ecc71', font=('Segoe UI', 12, 'bold'))

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="CarX Streets Helper", style='Header.TLabel').pack(pady=(0, 20))

        self.resource_frames = {}
        for resource in self.resources:
            frame = ttk.Frame(main_frame, style='TFrame')
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=f"{resource.name}:", style='TLabel', width=10).pack(side=tk.LEFT)
            
            new_value_var = tk.StringVar()
            ttk.Entry(frame, textvariable=new_value_var, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Set", command=lambda r=resource, v=new_value_var: self.set_value(r, v), width=8).pack(side=tk.LEFT)

            current_value_var = tk.StringVar(value="N/A")
            ttk.Label(frame, textvariable=current_value_var, style='Current.TLabel', width=15).pack(side=tk.RIGHT)

            self.resource_frames[resource.name] = {"current_var": current_value_var, "new_var": new_value_var}

        control_frame = ttk.Frame(main_frame, style='TFrame')
        control_frame.pack(fill=tk.X, pady=20)

        ttk.Button(control_frame, text="Connect", command=self.connect_to_game, width=10).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_values, width=10).pack(side=tk.LEFT, padx=10)

        self.status_var = tk.StringVar(value="●")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var, font=('Segoe UI', 16), foreground='#e74c3c')
        self.status_label.pack(side=tk.RIGHT)

    def connect_to_game(self):
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.module = pymem.process.module_from_name(self.pm.process_handle, "GameAssembly.dll")
            if not self.module:
                raise Exception("GameAssembly.dll not found")
            self.connected = True
            self.status_var.set("●")
            self.status_label.configure(foreground='#2ecc71')
            self.refresh_values()
        except Exception as e:
            self.disconnect()
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def disconnect(self):
        self.connected = False
        self.status_var.set("●")
        self.status_label.configure(foreground='#e74c3c')
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
            messagebox.showwarning("Warning", "Not connected to the game. Please connect first.")
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
                messagebox.showinfo("Success", 
                    f"{resource.name} value updated successfully.\n\n"
                    "IMPORTANT:\n"
                    "- If CASH shows as 0 or 1, restart the game.\n"
                    "- Spending Gold or Cash will update the value in-game.\n"
                    "- Gaining any XP will apply changes in-game.")
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
    root = ThemedTk(theme="equilux")
    app = CarXStreetModifier(root)
    root.mainloop()

if __name__ == "__main__":
    main()