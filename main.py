import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial
from tkinter import Button


class JoystickApp:
    def __init__(self, master):
        self.x_min = 0
        self.x_max = 180
        self.y_min = 20
        self.y_max = 190
        self.z_min = 20
        self.z_max = 330
        self.x_step = 5
        self.y_step = 5
        self.z_step = 5

        self.master = master
        self.master.title("CodaBot E-Arm")
        self.master.geometry("440x300")
        self.master.resizable(False, False)

        # Get available COM ports
        self.com_ports = self.get_available_com_ports()
        self.bitrates = [9600, 115200]  # Example bitrates, modify as needed

        # Create the COM port selection dropdown box
        self.com_port_var = tk.StringVar()
        self.com_port_var.set(self.com_ports[0])  # Set default selection
        self.com_port_dropdown = ttk.Combobox(
            self.master, textvariable=self.com_port_var, values=self.com_ports, width=8
        )
        self.com_port_dropdown.grid(row=0, column=0, padx=10, pady=10, columnspan=1)
        self.com_port_dropdown.bind("<<ComboboxSelected>>", self.on_com_port_selected)

        # Create the bitrate selection dropdown box
        self.baudrate_var = tk.IntVar()
        self.baudrate_var.set(self.bitrates[0])  # Set default selection
        self.baudrate_dropdown = ttk.Combobox(
            self.master, textvariable=self.baudrate_var, values=self.bitrates, width=10
        )
        self.baudrate_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Create the Connect button
        self.connect_btn = tk.Button(self.master, text="Connect", command=self.connect)
        self.connect_btn.grid(row=0, column=2, padx=10, pady=10)

        # Create the indicator canvas
        self.indicator_canvas = tk.Canvas(self.master, width=30, height=30, highlightthickness=0)
        self.indicator_canvas.grid(row=0, column=3, padx=10, pady=10)
        self.indicator_oval = self.indicator_canvas.create_oval(2, 2, 28, 28, fill="red")

        # Create the axis value labels
        self.x_label = tk.Label(self.master, text="X: 90")
        self.x_label.grid(row=1, column=0, padx=10, pady=5)
        self.y_label = tk.Label(self.master, text="Y: 120")
        self.y_label.grid(row=1, column=1, padx=10, pady=5)
        self.z_label = tk.Label(self.master, text="Z: 150")
        self.z_label.grid(row=1, column=2, padx=10, pady=5)

        # Initialize the serial connection
        self.serial = None

        # Create the X, Y, Z buttons
        self.x_left_btn = Button(self.master, text="<", height=2, width=7, command=lambda: self.move_axis("X", -1))
        self.x_left_btn.grid(row=3, column=0, padx=10, pady=10)
        self.x_right_btn = Button(self.master, text=">", height=2, width=7, command=lambda: self.move_axis("X", 1))
        self.x_right_btn.grid(row=3, column=2, padx=10, pady=10)
        self.y_up_btn = Button(self.master, text="^", height=2, width=7, command=lambda: self.move_axis("Y", 1))
        self.y_up_btn.grid(row=2, column=1, padx=10, pady=10)
        self.y_down_btn = Button(self.master, text="v", height=2, width=7, command=lambda: self.move_axis("Y", -1))
        self.y_down_btn.grid(row=4, column=1, padx=10, pady=10)
        self.z_up_btn = Button(self.master, text="Z Up", height=2, width=7, command=lambda: self.move_axis("Z", 1))
        self.z_up_btn.grid(row=2, column=3, padx=10, pady=10)
        self.z_down_btn = Button(self.master, text="Z Down", height=2, width=7, command=lambda: self.move_axis("Z", -1))
        self.z_down_btn.grid(row=4, column=3, padx=10, pady=10)

        # Create the Air Pump toggle button
        self.air_pump_toggle_btn = Button(self.master, text="Vacuum OFF", width=10, command=self.air_pump_toggle)
        self.air_pump_toggle_btn.grid(row=5, column=0, padx=10, pady=10)

        # Create the Suction toggle button
        self.suction_toggle_btn = Button(self.master, text="Suction OFF", width=10, command=self.suction_toggle)
        self.suction_toggle_btn.grid(row=5, column=1, padx=10, pady=10)

    # Get available COM ports
    def get_available_com_ports(self):
        com_ports = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            com_ports.append(port.device)
        return com_ports

    # COM port selection event handler
    def on_com_port_selected(self, event):
        selected_port = self.com_port_var.get()
        print(f"Selected COM port: {selected_port}")

    # Connect button event handler
    def connect(self):
        if self.serial is None or not self.serial.is_open:
            selected_port = self.com_port_var.get()
            try:
                self.serial = serial.Serial(selected_port, baudrate=9600, timeout=0.1)
                self.connect_btn.config(text="Disconnect")
                self.indicator_canvas.itemconfig(self.indicator_oval, fill="green")

                # Enable joystick buttons and suction button
                for widget in self.master.winfo_children():
                    if isinstance(widget, tk.Button) and widget != self.connect_btn:
                        widget.config(state=tk.NORMAL)
                self.suction_toggle_btn.config(state=tk.NORMAL)

                # Send default values
                self.send_default_values()

            except serial.SerialException as e:
                print(f"Error connecting to COM port: {str(e)}")
        else:
            self.send_default_values()
            self.serial.close()
            self.connect_btn.config(text="Connect")
            self.indicator_canvas.itemconfig(self.indicator_oval, fill="red")

            # Disable joystick buttons and suction button
            for widget in self.master.winfo_children():
                if isinstance(widget, tk.Button) and widget != self.connect_btn:
                    widget.config(state=tk.DISABLED)
            self.suction_toggle_btn.config(state=tk.DISABLED)

    def send_default_values(self):
        default_x = 90
        default_y = 120
        default_z = 150
        pump_status = 0
        suction_status = 0

        # Update axis value labels with default values
        self.x_label.config(text=f"X: {default_x}")
        self.y_label.config(text=f"Y: {default_y}")
        self.z_label.config(text=f"Z: {default_z}")

        # Create the data string with default values
        data_string = f"{default_x},{default_y},{default_z},{pump_status},{suction_status}\n"

        # Send the encoded data over serial
        self.serial.write(data_string.encode())
        print(data_string.encode())

    # Move the specifiedaxis in the given direction
    def move_axis(self, axis, direction):
        if self.serial is not None and self.serial.is_open:
            if axis == "X":
                button_value = int(self.x_label["text"].split(": ")[1])
                button_value += direction * self.x_step
                button_value = max(self.x_min, min(button_value, self.x_max))
                self.x_label.config(text=f"X: {button_value}")

            elif axis == "Y":
                button_value = int(self.y_label["text"].split(": ")[1])
                button_value += direction * self.y_step
                button_value = max(self.y_min, min(button_value, self.y_max))
                self.y_label.config(text=f"Y: {button_value}")

            elif axis == "Z":
                button_value = int(self.z_label["text"].split(": ")[1])
                button_value += direction * self.z_step
                button_value = max(self.z_min, min(button_value, self.z_max))
                self.z_label.config(text=f"Z: {button_value}")

            self.send_data()

    # Toggle the Air Pump
    def air_pump_toggle(self):
        if self.serial is not None and self.serial.is_open:
            if self.air_pump_toggle_btn["text"] == "Vacuum OFF":
                self.air_pump_toggle_btn["text"] = "Vacuum ON"
            else:
                self.air_pump_toggle_btn["text"] = "Vacuum OFF"
            self.send_data()

    # Toggle the Suction
    def suction_toggle(self):
        if self.serial is not None and self.serial.is_open:
            if self.suction_toggle_btn["text"] == "Suction OFF":
                self.suction_toggle_btn["text"] = "Suction ON"
            else:
                self.suction_toggle_btn["text"] = "Suction OFF"
            self.send_data()

    # Send button data to serial port
    def send_data(self):
        if self.serial is not None and self.serial.is_open:
            x_value = int(self.x_label["text"].split(": ")[1])
            y_value = int(self.y_label["text"].split(": ")[1])
            z_value = int(self.z_label["text"].split(": ")[1])

            pump_status = 1 if self.air_pump_toggle_btn["text"] == "Vacuum ON" else 0
            suction_status = 1 if self.suction_toggle_btn["text"] == "Suction ON" else 0

            data_string = f"{x_value},{y_value},{z_value},{pump_status},{suction_status}\n"
            self.serial.write(data_string.encode())
            print(data_string.encode())

# Create the main window
root = tk.Tk()

# Create the joystick application
joystick_app = JoystickApp(root)

# Run the application
root.mainloop()
