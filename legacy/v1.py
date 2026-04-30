# Check the second and third tab for example CustomTkinter syntaxes. Sample macro functions are in the 24 reference.py (ICF V2.4 reference)

# Imports
from customtkinter import *
import os
import subprocess
# Keyboard and Mouse
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
# Key Listeners
import threading
from pynput.keyboard import Listener as KeyListener, Key
macro_running = False
macro_thread = None
# Key Inputs
import threading
# Time
import time
import json
# Web browsing
import webbrowser
# Initialize controllers
keyboard_controller = KeyboardController()
mouse_controller = MouseController()

# Set appearance
set_default_color_theme("blue") # This makes the buttons having a blue color (you can't set this to a custom color)
# set_appearance_mode("dark") # This makes the theme always dark
# These lines until the App class fixes the "crashing when compiled" problem on macOS
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))
if sys.platform == "darwin":
    user_config_dir = os.path.join(os.path.expanduser("~"), 
                                   "Library", "Application Support", 
                                   "Example", "configs")
else:
    user_config_dir = os.path.join(os.path.expanduser("~"),
                                   "AppData","Roaming",
                                   "Example","configs")

os.makedirs(user_config_dir, exist_ok=True)
BASE_PATH = get_base_path()

if sys.platform == "darwin" and getattr(sys, "frozen", False):
    # Only use Application Support when bundled
    USER_CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Library", 
                                   "Application Support", "Example", 
                                   "configs")
elif sys.platform == "win32" and getattr(sys, "frozen", False):
    # Only use AppData/Roaming when bundled
    USER_CONFIG_DIR = os.path.join(os.path.expanduser("~"), "AppData",
                                   "Roaming", "Example",
                                   "configs")
else:
    # During development, use local project folder
    USER_CONFIG_DIR = os.path.join(BASE_PATH, "configs")

os.makedirs(USER_CONFIG_DIR, exist_ok=True)
if sys.platform == "darwin":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
else:
    pass
class App(CTk):
    def __init__(self):
        super().__init__()
        self.vars = {}     # Entry / Slider / Combobox vars
        self.vars = {}        # IntVar / StringVar / BooleanVar
        self.checkboxes = {}   # CTkCheckBox vars
        self.comboboxes = {}   # CTkComboBox vars
        
        # Screen size (cache once – thread safe)
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()

        # Window 
        self.geometry("800x600")
        self.title("Test (Change this)")

        # Macro state
        self.macro_running = False
        self.macro_thread = None

        # Hotkey variables
        self.hotkey_start = Key.f5
        self.hotkey_stop = Key.f7
        self.hotkey_labels = {}  # Store label widgets for dynamic updates

        # Start hotkey listener
        self.key_listener = KeyListener(on_press=self.on_key_press)
        self.key_listener.daemon = True
        self.key_listener.start()

        # Status Bar 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Top Bar Frame (Status + Buttons)
        top_bar = CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        # Logo Label
        logo_label = CTkLabel(
            top_bar, 
            text="TEST (ALL CAPS)",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Status label (left side)
        self.status_label = CTkLabel(top_bar, text="Macro status: Idle")
        self.status_label.grid(row=1, column=0, pady=5, sticky="w")

        # Buttons frame (right side)
        button_frame = CTkFrame(top_bar, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        CTkButton(
            button_frame,
            text="Website",
            corner_radius=32,
            command=self.open_link("https://sites.google.com/view/icf-automation-network/") # This opens the ICF website (change this)
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Upcoming Features",
            corner_radius=32,
            command=self.open_link("https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/edit?tab=t.0") # This opens the upcoming features docs (change this)
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Tutorial",
            corner_radius=32,
            command=self.open_link("https://docs.google.com/document/d/1qjhgcONxpZZbSAEYiSCXoUXGjQwd7Jghf4EysWC4Cps/edit?usp=drive_link") # This opens the ICF discord (change this)
        ).pack(side="left", padx=6)

        # Tabs 
        self.tabs = CTkTabview(
            self,
            anchor="w",
        )

        self.tabs.grid(
            row=2, column=0,
            padx=20, pady=10,
            sticky="nsew"
        )

        self.tabs.add("Tab 1")
        self.tabs.add("Tab 2")
        self.tabs.add("Tab 3")

        # Build tabs
        self.build_1_tab(self.tabs.tab("Tab 1"))
        self.build_2_tab(self.tabs.tab("Tab 2"))
        self.build_3_tab(self.tabs.tab("Tab 3"))

        # Grid behavior
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Logo
        self.grid_rowconfigure(1, weight=0)  # Status
        self.grid_rowconfigure(2, weight=1)  # Tabs take remaining space

        last = self.load_last_config_name()
        self.load_settings(last or "default.json")
        # Arrow variables
        self.initial_bar_size = None
        # Utility variables
        self.area_selector = None
        self.last_fish_x = None
    # BASIC SETTINGS TAB
    def build_1_tab(self, parent):
        scroll = CTkScrollableFrame(parent)
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        # VERY important
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        # Configs 
        configs = CTkFrame(scroll, border_width=2)
        configs.grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(configs, text="Config Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        CTkLabel(configs, text="Active Configuration:").grid( row=1, column=0, padx=12, pady=6, sticky="w" )
        config_list = self.load_configs()
        config_var = StringVar(value=config_list[0] if config_list else "default.json")
        self.vars["active_config"] = config_var
        config_cb = CTkComboBox( configs, values=config_list, 
                                variable=config_var, command=lambda v: self.load_settings(v) )
        config_cb.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.comboboxes["active_config"] = config_cb
        CTkButton(configs, text="Open Configs Folder", corner_radius=10, 
                  command=self.open_configs_folder
                  ).grid(row=2, column=0, padx=12, pady=12, sticky="w")
        CTkButton(configs, text="Save Misc Settings", 
                  corner_radius=10, command=self.save_misc_settings
        ).grid(row=2, column=1, padx=12, pady=12, sticky="w")
        # Hotkey Settings
        hotkey_settings = CTkFrame(scroll, border_width=2)
        hotkey_settings.grid(row=2, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(hotkey_settings, text="Hotkey Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        # Start key
        CTkLabel(hotkey_settings, text="Start Key").grid( row=1, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_settings, text="Stop Key").grid( row=2, column=0, padx=12, pady=6, sticky="w" )
        # Start, screenshot and stop key changer
        start_key_var = StringVar(value="F5")
        self.vars["start_key"] = start_key_var
        start_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=start_key_var )
        start_key_entry.grid(row=1, column=1, padx=12, pady=10, sticky="w")
        stop_key_var = StringVar(value="F7")
        self.vars["stop_key"] = stop_key_var
        stop_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=stop_key_var )
        stop_key_entry.grid(row=2, column=1, padx=12, pady=10, sticky="w")
    # Second tab
    def build_2_tab(self, parent):
        # 4 lines below initialize the scroll wheel and the grid section
        # scroll = CTkScrollableFrame(parent)
        # scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        # parent.grid_rowconfigure(0, weight=1)
        # parent.grid_columnconfigure(0, weight=1)

        # Initialize Frame
        # overlay_options = CTkFrame(scroll, border_width=2)
        # overlay_options.grid(row=4, column=0, padx=20, pady=20, sticky="nw")

        # Frame Header Label (important)
        # CTkLabel(overlay_options, text="Overlay Options", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        # Initialize Checkbox
        # fish_overlay_var = StringVar(value="off") # This line and the line below makes the checkbox save and load
        # self.vars["fish_overlay"] = fish_overlay_var
        # fish_overlay_cb = CTkCheckBox(overlay_options, text="Fish Overlay", variable=fish_overlay_var, onvalue="on", offvalue="off") # This line initializes checkboxes
        # fish_overlay_cb.grid(row=1, column=0, padx=12, pady=8, sticky="w") # This line initializes the position for the checkboxes (most important)

        # Normal Label and Entry
        # CTkLabel(sequence_options, text="Delay before casting").grid( row=3, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        # casting_delay2_var = StringVar(value="0.0") # This line is the default/placeholder value
        # self.vars["casting_delay2"] = casting_delay2_var # This line makes the entry save and load
        # casting_delay2_entry = CTkEntry(sequence_options, width=120, textvariable=casting_delay2_var) # This line initializes the entry
        # casting_delay2_entry.grid(row=3, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        pass # Comments doesn't count in functions
    # Third tab
    def build_3_tab(self, parent):
        # This tab contains a combobox
        # CTkLabel(casting_mode, text="Casting Mode:").grid(row=1, column=0, padx=12, pady=10, sticky="w" ) # You already know what this does in the second tab
        # casting_mode_var = StringVar(value="Normal") # This line is the default/placeholder value
        # self.vars["casting_mode"] = casting_mode_var # This line makes the entry save and load
        # casting_cb = CTkComboBox(casting_mode, values=["Perfect", "Normal"], 
        #                        variable=casting_mode_var, command=lambda v: self.set_status(f"Casting Mode: {v}")
        #                        ) # These 3 lines initializes the combobox
        # casting_cb.grid(row=1, column=1, padx=12, pady=10, sticky="w") # This line initializes the position for the comboboxes (most important)
        # self.comboboxes["casting_mode"] = casting_cb # This line makes the entry save and load
        pass
    # Save and load settings
    def load_configs(self):
        """Load list of available config files."""
        config_dir = USER_CONFIG_DIR
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        # Get config names from subdirectories
        config_names = [
            name for name in os.listdir(config_dir)
            if os.path.isdir(os.path.join(config_dir, name))
        ]

        if not config_names:
            # Create default config if none exists
            self.save_settings("default.json")
            config_names = ["default.json"]
        
        return sorted(config_names)
    
    def load_last_config_name(self):
        """Load the name of the last used config."""
        try:
            if os.path.exists("last_config.json"):
                with open("last_config.json", "r") as f:
                    data = json.load(f)
                    return data.get("last_config", "default.json")
        except:
            pass
        return "default.json"
    
    def save_last_config_name(self, name):
        """Save the name of the last used config."""
        try:
            with open("last_config.json", "w") as f:
                json.dump({"last_config": name}, f)
        except:
            pass
    
    def save_misc_settings(self):
        """Save miscellaneous settings to last_config.json."""
        try:
            clean_bar_areas = {}

            for key in ["shake", "fish"]:
                area = self.bar_areas.get(key)

                if isinstance(area, dict):
                    clean_bar_areas[key] = {
                        "x": int(area.get("x", 0)),
                        "y": int(area.get("y", 0)),
                        "width": int(area.get("width", 0)),
                        "height": int(area.get("height", 0))
                    }
                else:
                    clean_bar_areas[key] = None

            data = {
                # IMPORTANT: Save hotkeys
                "start_key": self.vars["start_key"].get(),
                "stop_key": self.vars["stop_key"].get()
            }
            with open("last_config.json", "w") as f:
                json.dump(data, f, indent=4)
            # IMPORTANT: Immediately update active hotkeys
            self.hotkey_start = self._string_to_key(self.vars["start_key"].get())
            self.hotkey_stop = self._string_to_key(self.vars["stop_key"].get())
        except Exception as e:
            import traceback
            traceback.print_exc()

    def save_settings(self, name):
        """Save all settings to a JSON config file."""
        config_dir = USER_CONFIG_DIR
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        data = {}
        
        # Save all StringVar and related variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'get'):
                    data[key] = var.get()
                else:
                    data[key] = var
        except Exception as e:
            print(f"Error saving vars: {e}")
        
        # Save checkbox states
        try:
            for key, checkbox in self.checkboxes.items():
                data[f"checkbox_{key}"] = checkbox.get()
        except Exception as e:
            print(f"Error saving checkboxes: {e}")
        
        # Save combobox states
        try:
            for key, combobox in self.comboboxes.items():
                data[f"combobox_{key}"] = combobox.get()
        except Exception as e:
            print(f"Error saving comboboxes: {e}")

        # Get rod folder based on config name
        rod_folder = os.path.join(config_dir, name.replace(".json", ""))
        os.makedirs(rod_folder, exist_ok=True)

        path = os.path.join(rod_folder, "config.json")
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.save_last_config_name(name)
            self.save_misc_settings()  # Also save misc settings
        except Exception as e:
            self.set_status(f"Error saving config: {e}")
    
    def load_settings(self, name):
        """Load settings from a JSON config file."""
        config_dir = USER_CONFIG_DIR
        rod_folder = os.path.join(config_dir, name.replace(".json", ""))
        path = os.path.join(rod_folder, "config.json")

        if not os.path.exists(path):
            self.set_status(f"Config not found: {name}")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.set_status(f"Error loading config: {e}")
            return
        
        # Load StringVar and related variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'set') and key in data:
                    var.set(data[key])
        except Exception as e:
            print(f"Error loading vars: {e}")
        
        # Load checkbox states
        try:
            for key, checkbox in self.checkboxes.items():
                checkbox_key = f"checkbox_{key}"
                if checkbox_key in data:
                    checkbox.set(data[checkbox_key])
        except Exception as e:
            print(f"Error loading checkboxes: {e}")
        
        # Load combobox states
        try:
            for key, cb in self.comboboxes.items():
                if key in data:
                    cb.set(data[key])
        except Exception as e:
            print(f"Error loading comboboxes: {e}")

        self.save_last_config_name(name)
    def load_misc_settings(self):
        """Load miscellaneous settings from last_config.json."""
        try:
            if os.path.exists("last_config.json"):
                with open("last_config.json", "r") as f:
                    data = json.load(f)
                    # IMPORTANT: Load hotkeys if present
                    start_key = data.get("start_key", "F5")
                    stop_key = data.get("stop_key", "F7")

                    self.vars["start_key"].set(start_key)
                    self.vars["stop_key"].set(stop_key)

                    # Convert to pynput keys
                    self.hotkey_start = self._string_to_key(start_key)
                    self.hotkey_stop = self._string_to_key(stop_key)
        except:
            pass # don't do anything here
    # Macro functions
    def open_configs_folder(self):
        folder = USER_CONFIG_DIR
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", folder])
        else:  # Linux
            subprocess.run(["xdg-open", folder])
    def open_link(self, url):
        """Open a URL in the default web browser."""
        return lambda: webbrowser.open(url)
    def _string_to_key(self, key_string):
        key_string = key_string.strip().lower()

        try:
            return Key[key_string]
        except KeyError:
            return key_string  # normal character keys
    def on_key_press(self, key):
        try:
            if key == self.hotkey_start and not self.macro_running:
                config_name = self.vars["active_config"].get()
                self.save_settings(config_name)

                self.macro_running = True
                self.after(0, self.withdraw)
                threading.Thread(target=self.start_playback, daemon=True).start()

            elif key == self.hotkey_stop:
                self.stop_playback()

        except Exception as e:
            print("Hotkey error:", e)
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    def start_playback(self):
        self.set_status("Macro Status: Started")
        self.macro_running = True
        while self.macro_running:
            # macro logic only
            time.sleep(0.01)
    def stop_playback(self):
        if not self.macro_running:
            return
        self.macro_running = False
        self.after(0, self.deiconify)  # show window safely
        self.set_status("Macro Status: Stopped")
if __name__ == "__main__":
    app = App()
    app.mainloop()