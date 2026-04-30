# Imports
from customtkinter import *
from tkinter import messagebox
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
# Get All Required Paths
def get_base_path():
    """Unified base directory for app data."""

    if getattr(sys, 'frozen', False):
        compiled = True
        # Compiled App → Use User Directory
        if sys.platform == "darwin":
            return os.path.join(
                os.path.expanduser("~"),
                "Library", "Application Support",
                "PyWareFishingV3"
            ), compiled
        elif sys.platform == "win32":
            return os.path.join(
                os.path.expanduser("~"),
                "AppData", "Roaming",
                "PyWareFishingV3"
            ), compiled
        else:
            return os.path.join(os.path.expanduser("~"), "PyWareFishingV3"), compiled
    compiled = False
    # Dev Mode → Project Directory
    return os.path.dirname(os.path.abspath(__file__)), compiled

BASE_PATH, IS_COMPILED = get_base_path()

CONFIG_DIR = os.path.join(BASE_PATH, "configs")
IMAGES_PATH = os.path.join(BASE_PATH, "images")
DEBUG_DIR = BASE_PATH

CONFIG_PATH = os.path.join(BASE_PATH, "last_config.json")
APP_VERSION = "3.01"

set_appearance_mode("dark")

def ensure_last_config_exists():
    """Ensure last_config.json exists at BASE_PATH, create default if missing."""
    config_file = os.path.join(BASE_PATH, "last_config.json")
    
    # Check If It Exists As A File (Not A Directory)
    if os.path.exists(config_file):
        if os.path.isdir(config_file):
            # It'S A Directory - Remove It And Recreate As File
            print(f"Removing directory at {config_file} to create file...")
            try:
                os.rmdir(config_file)  # Use Shutil.Rmtree() If Directory Has Contents
                print(f"Removed directory: {config_file}")
            except Exception as e:
                print(f"Could not remove directory: {e}")
                # Try To Rename It As Backup
                backup_path = config_file + "_backup_folder"
                os.rename(config_file, backup_path)
                print(f"Renamed directory to: {backup_path}")
        else:
            # It Exists As A File, No Action Needed
            return config_file
    
    # Create Default Config Structure
    default_config = {
        "version": APP_VERSION,
        "last_profile": "default",
        "last_macro_name": None,
        "settings": {},
        "tos_accepted": False
    }
    
    try:
        # Ensure The Parent Directory Exists
        os.makedirs(BASE_PATH, exist_ok=True)
        
        # Write The File
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file at: {config_file}")
    except Exception as e:
        print(f"Error creating config file: {e}")
        pass
    
    return config_file

ensure_last_config_exists()
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(IMAGES_PATH, exist_ok=True)

# Terms Of Service Dialogue
class TermsOfServiceDialog(CTkToplevel):
    def __init__(self, parent=None):
        super().__init__()
        
        # Screen Size (Cache Once – Thread Safe)
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Window
        self.geometry("750x600")
        self.title("PyWare Fishing V3.1 - Terms of Use")
        self.minsize(650, 500)
        
        # Center Window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

        # Status Bar
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header Stays Fixed
        self.grid_rowconfigure(1, weight=1)  # Content Expands
        self.grid_rowconfigure(2, weight=0)  # Nav Bar Fixed
        
        # Top Bar Frame (Status + Buttons)
        top_bar = CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        # Logo Label
        logo_label = CTkLabel(
            top_bar, 
            text="TERMS OF SERVICE",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Main Content Container
        self.container = CTkFrame(self)
        self.container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Pages
        self.page_tos = CTkFrame(self.container)
        self.page_setup = CTkFrame(self.container)

        for page in (self.page_tos, self.page_setup):
            page.grid(row=0, column=0, sticky="nsew")

        # Agree Labels
        self.agree_var = BooleanVar(value=False)
        self.accepted = False

        # Build Pages
        self.build_tos_page(self.page_tos)
        self.build_setup_page(self.page_setup)

        # Navigation Bar
        nav_bar = CTkFrame(self)
        nav_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        nav_bar.grid_columnconfigure(0, weight=1)

        self.back_btn = CTkButton(nav_bar, text="Back", command=self.go_back)
        self.next_btn = CTkButton(nav_bar, text="Next", command=self.go_next)
        self.finish_btn = CTkButton(nav_bar, text="Finish", command=self.finish)

        self.back_btn.grid(row=0, column=0, padx=5, sticky="w")
        self.next_btn.grid(row=0, column=1, padx=5)
        self.finish_btn.grid(row=0, column=2, padx=5, sticky="e")

        # Initial State
        self.current_page = 0
        self.show_page(0)
    # Basic Settings Tab
    def build_tos_page(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        textbox = CTkTextbox(parent, wrap="word")
        textbox.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")

        textbox.insert("1.0", """
PyWare Fishing V3.1 - Terms of Use

By using this software, you agree to the following:


⚡ 1. USAGE & MODIFICATION

✅ YOU ARE ALLOWED TO:
Use these macros for personal purposes.
Study and reverse engineer the code for educational purposes.
Modify the code for your own personal use.
Share your modifications with proper attribution.
                            
❌ YOU ARE NOT ALLOWED TO:
Repackage or redistribute this software as your own.
Remove or modify credits to the author (Catman2608).
Sell or monetize this software or its derivatives.
Claim ownership of the original codebase.
                            
⚡ IF YOU SHARE MODIFICATIONS:
⚠️ You MUST credit Catman2608 as the original author.
⚠️ You MUST link to the original source (YouTube/Website).
⚠️ You MUST clearly indicate what changes you made.
                            
⚡ 2. INTENDED USE & GAME COMPLIANCE

This software suite is designed for use on multiple platforms.
You are responsible for ensuring your use complies with the platform's Terms of Service and specific game rules.
The developers and the website owner (Catman2608) are NOT responsible for any account actions (bans, suspensions) resulting from your use of this software.
Use at your own risk. (usage in Roblox games are allowed)

⚡ 3. LIABILITY DISCLAIMER

The owner and authors are NOT liable for any damages, data loss, or account issues.
There is no guarantee of functionality, compatibility, or performance.
Software is provided "as-is." Use is entirely at your own risk.
                            
⚡ 4. PRIVACY & DATA

Macros store configuration data (settings) locally on your device.
No personal data is collected or transmitted to external servers.
Your preferences are stored in a local .json file only.
                            
⚡ 5. CREDITS & ATTRIBUTION
                            
Original Author: Catman2608
YouTube: https://www.youtube.com/@HexaTitanGaming
Discord: https://discord.gg/aMZY8yrF8r
If you share, modify, or redistribute this software:
                            
📋 REQUIRED: Credit "Catman2608" as the original creator
📋 REQUIRED: Link to the original source
📋 REQUIRED: Indicate any changes you made
🚫 FORBIDDEN: Claim the entire work as your own
                            
⚡ 6. TERMS UPDATES

These terms may be updated at any time.
Continued use of the software from the PyWare Automate website constitutes acceptance of the updated terms.
                            
✅ 7. ACCEPTANCE

By accepting the terms, you acknowledge that you have read, understood, and agree to these Terms of Use.
If you do not agree, please remove the software from your device.

🚀 Thank you for using PyWare Fishing! 🚀
        """)
        textbox.configure(state="disabled")

        checkbox = CTkCheckBox(
            parent,
            text="I agree to the Terms of Service",
            variable=self.agree_var,
            command=self.update_next_button
        )
        checkbox.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
    # Second Tab
    def build_setup_page(self, parent):
        textbox = CTkTextbox(parent, wrap="word")
        textbox.pack(fill="both", expand=True, padx=12, pady=10)

        textbox.insert("1.0", """
Step 1: Download and extract the config pack and images pack from https://drive.google.com/drive/folders/1e9tZwDtAaiYKTVFeArjWTIuztLgLg88a?usp=drive_link
Step 2: Click Open Base Folder to open the base folder
Step 3: Paste the configs pack in the configs folder
Step 4: Paste the images pack in the images folder
Step 5: Change Bar Areas
        """)
        textbox.configure(state="disabled")
    def show_page(self, index):
        self.current_page = index

        if index == 0:
            self.page_tos.tkraise()
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(state="normal" if self.agree_var.get() else "disabled")
            self.finish_btn.configure(state="disabled")
        elif index == 1:
            self.page_setup.tkraise()
            self.back_btn.configure(state="normal")
            self.next_btn.configure(state="disabled")
            self.finish_btn.configure(state="normal")

    def go_back(self):
        if self.current_page == 1:
            self.show_page(0)

    def update_next_button(self):
        if self.current_page == 0:
            self.next_btn.configure(state="normal" if self.agree_var.get() else "disabled")

    def go_next(self):
        if self.current_page == 0 and self.agree_var.get():
            self.accepted = True
            self.show_page(1)

    def finish(self):
        self.accepted = True
        self.destroy()
    def on_close(self):
        if not self.accepted:
            self.accepted = False
        self.destroy()
# Main App
class App(CTk):
    def __init__(self):

        # Initialize Class
        super().__init__()

        # Initialize Save And Load (We Only Use
        # Entry, Checkboxes And Comboboxes)
        self.vars = {} # Save Entry Variables Here
        self.checkboxes = {}
        self.comboboxes = {} # Save Combobox Widgets Here For Dynamic Updates
        self.switches = {} # Save Ctkswitch Widgets Here For Load/Save

        # Store Screen Width And Height To Use Later
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()

        # Hotkey Variables
        self.hotkey_start = Key.f5
        self.hotkey_stop = Key.f7
        self.hotkey_change_areas = Key.f6 # Added For The Bar Area Selector
        self.hotkey_screenshot = Key.f8
        self.hotkey_labels = {}  # Store Label Widgets For Dynamic Updates

        # Macro State
        self.macro_running = False
        self.macro_thread = None

        # Discord Webhook And Totem Trigger Counters
        self.webhook_cycle_counter = 0   # Incremented Each Fishing Cycle
        self.webhook_start_time = None   # Set When Macro Starts (For Time Mode)
        self.totem_cycle_counter = 0
        self.totem_start_time = time.time()
        
        # Safe Defaults Before Key Listener Starts (Will Be Overwritten By Load_Misc_Settings)
        self.bar_areas = {"shake": None, "fish": None, "friend": None, "totem": None}
        self.current_rod_name = "Basic Rod"

        # Invalidate Scale Cache If The Window Moves To A Different Monitor
        if sys.platform == "darwin":
            self.bind("<Configure>", lambda e: self._invalidate_scale_cache())
        
        # Show Tos Dialogue
        state, first_launch, new_version = self.load_app_state()

        # 🔥 Show Tos If Needed
        if first_launch or not state.get("tos_accepted", False):
            dialog = TermsOfServiceDialog(self)
            self.wait_window(dialog)

            if not dialog.accepted:
                self.destroy()
                return

            # Mark Accepted
            state["tos_accepted"] = True

        # Update Version After Tos
        state["version"] = APP_VERSION

        self.save_app_state(state)

        # Start Hotkey Listener
        self.key_listener = KeyListener(on_press=self.on_key_press)
        self.key_listener.daemon = True
        self.key_listener.start()

        # Create Window
        self.configure(fg_color="#181836")   # <- Main Window Ultra Dark
        self.geometry("800x600")
        self.title("PyWare Fishing V3.1")

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
            text="PYWARE FISHING V3.1",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Status Label (Left Side)
        self.status_label = CTkLabel(top_bar, text="Macro status: Idle")
        self.status_label.grid(row=1, column=0, pady=5, sticky="w")

        # Buttons Frame (Right Side)
        button_frame = CTkFrame(top_bar, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        CTkButton(
            button_frame,
            text="Upcoming",
            width=120,
            corner_radius=8,
            command=self.open_link("https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/edit?tab=t.0")
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Website",
            width=120,
            corner_radius=8,
            command=self.open_link("https://sites.google.com/view/icf-automation-network/")
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Tutorial",
            width=120,
            corner_radius=8,
            command=self.open_link("https://docs.google.com/document/d/1EgzNRa5nxw90zxP4aij3DXl7cbarKNW_ozISom4McV0/")
        ).pack(side="left", padx=6)

        # Tabs
        self.tabs = CTkTabview(
            self,
            anchor="w",
            border_color = "#414167", fg_color = "#222244"
        )

        self.tabs._segmented_button.configure(
            fg_color="#414167",
            selected_color="#676780",
            selected_hover_color="#525267",
            unselected_color="#414167",
            unselected_hover_color="#565680",
            text_color="#FFFFFF"
        )

        self.tabs.grid(
            row=1, column=0, columnspan=6,
            padx=20, pady=10, sticky="nsew"
        )

        self.tabs.add("Tab 1")
        self.tabs.add("Tab 2")
        self.tabs.add("Tab 3")

        # Build tabs
        self.build_1_tab(self.tabs.tab("Tab 1"))
        self.build_2_tab(self.tabs.tab("Tab 2"))
        self.build_3_tab(self.tabs.tab("Tab 3"))

        # Load Last Config, Reapply Hotkeys And Set Reset Values
        self.load_last_config()
        self._apply_hotkeys_from_vars()
        self.default_settings_data = self._collect_settings_data()

        # Grid Behavior
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Top_Bar
        self.grid_rowconfigure(1, weight=1)  # Tabs Expand

        self.refresh_config_dropdown() # Auto Refresh Config
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    # Build Gui
    def build_1_tab(self, parent):
        # Configure scroll bar
        scroll = CTkScrollableFrame(parent, fg_color = "#222244")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Build main GUI
        basic_settings = CTkFrame(scroll, border_width=2, border_color = "#364167", fg_color = "#222244")
        basic_settings.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        CTkLabel(basic_settings, text="Basic Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        CTkLabel(basic_settings, text="Rod Type:").grid(row=1, column=0, padx=12, pady=10, sticky="w")

        self.config_var = StringVar(value="default")

        self.config_dropdown = CTkComboBox(
            basic_settings,
            variable=self.config_var,
            values=self.get_config_list(),
            command=self.on_config_selected
        )
        self.config_dropdown.grid(row=1, column=1, padx=12, pady=10, sticky="w")

        CTkButton(
            basic_settings, 
            text="🔄", 
            width=40,
            corner_radius=8,
            command=self.refresh_config_dropdown
        ).grid(row=0, column=2, padx=12, pady=10, sticky="w")

        CTkButton(basic_settings, text="Open Base Folder", corner_radius=8, 
                  command=self.open_base_folder,
                  width=140
                  ).grid(row=0, column=1, padx=12, pady=12, sticky="w")

        CTkButton(basic_settings, text="Add", width=40, corner_radius=8, command=self.add_rod).grid(row=1, column=2, padx=12, pady=12, sticky="w")
        CTkButton(basic_settings, text="Delete", width=40, corner_radius=8, command=self.delete_rod).grid(row=1, column=3, padx=12, pady=12, sticky="w")

        CTkButton(basic_settings, text="Reset Settings", width=140, corner_radius=8, command=self.reset_settings).grid(row=3, column=0, padx=12, pady=12, sticky="w")
        # Hotkey and Hotbar Settings
        hotkey_hotbar_settings = CTkFrame(scroll, border_width=2, border_color = "#364167", fg_color = "#222244")
        hotkey_hotbar_settings.grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(hotkey_hotbar_settings, text="Hotkey Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        CTkLabel(hotkey_hotbar_settings, text="Hotbar Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=2, padx=12, pady=8, sticky="w")
        # Key binds
        CTkLabel(hotkey_hotbar_settings, text="Start Key").grid(row=1, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Change Bar Areas Key").grid(row=2, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Stop Key").grid(row=3, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Screenshot Key").grid(row=4, column=0, padx=12, pady=6, sticky="w" )
        # Disable hotkeys
        enable_hotkeys_var = StringVar(value="off")
        self.vars["enable_hotkeys"] = enable_hotkeys_var
        sw = CTkSwitch(hotkey_hotbar_settings, text="Toggle", variable=enable_hotkeys_var, onvalue="on", offvalue="off")
        sw.grid(row=0, column=1, padx=12, pady=8, sticky="w")
        self.switches["enable_hotkeys"] = sw
        # Keys text changer
        start_key_var = StringVar(value="F5")
        self.vars["start_key"] = start_key_var
        start_key_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=start_key_var )
        start_key_entry.grid(row=1, column=1, padx=12, pady=10, sticky="w")
        change_bar_areas_key_var = StringVar(value="F6")
        self.vars["change_bar_areas_key"] = change_bar_areas_key_var
        change_bar_areas_key_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=change_bar_areas_key_var )
        change_bar_areas_key_entry.grid(row=2, column=1, padx=12, pady=10, sticky="w")
        stop_key_var = StringVar(value="F7")
        self.vars["stop_key"] = stop_key_var
        stop_key_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=stop_key_var )
        stop_key_entry.grid(row=3, column=1, padx=12, pady=10, sticky="w")
        screenshot_key_var = StringVar(value="F8")
        self.vars["screenshot_key"] = screenshot_key_var
        screenshot_key_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=screenshot_key_var)
        screenshot_key_entry.grid(row=4, column=1, padx=12, pady=10, sticky="w")
        # Hotkey for items
        CTkLabel(hotkey_hotbar_settings, text="Fishing Rod Slot:").grid(row=1, column=2, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Equipment Bag Slot").grid(row=2, column=2, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Sundial Totem Slot:").grid(row=3, column=2, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_hotbar_settings, text="Target Totem Slot:").grid(row=4, column=2, padx=12, pady=6, sticky="w" )
        # Hotkey entries
        rod_slot_var = StringVar(value="1")
        self.vars["rod_slot"] = rod_slot_var
        rod_slot_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=rod_slot_var)
        rod_slot_entry.grid(row=1, column=3, padx=12, pady=8, sticky="w")
        bag_slot_var = StringVar(value="2")
        self.vars["bag_slot"] = bag_slot_var
        bag_slot_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=bag_slot_var)
        bag_slot_entry.grid(row=2, column=3, padx=12, pady=8, sticky="w")
        sundial_slot_var = StringVar(value="6")
        self.vars["sundial_slot"] = sundial_slot_var
        sundial_slot_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=sundial_slot_var)
        sundial_slot_entry.grid(row=3, column=3, padx=12, pady=8, sticky="w")
        target_slot_var = StringVar(value="7")
        self.vars["target_slot"] = target_slot_var
        target_slot_entry = CTkEntry(hotkey_hotbar_settings, width=120, textvariable=target_slot_var)
        target_slot_entry.grid(row=4, column=3, padx=12, pady=8, sticky="w")
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
    def open_link(self, url):
        """Open a URL in the default web browser."""
        return lambda: webbrowser.open(url)
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    # Get Config List To Save
    def get_config_list(self):
        if not os.path.exists(CONFIG_DIR):
            return ["default"]
        folders = [name for name in os.listdir(CONFIG_DIR) if os.path.isdir(os.path.join(CONFIG_DIR, name))]
        return folders if folders else ["default"]
    def refresh_config_dropdown(self):
        configs = self.get_config_list()
        self.config_dropdown.configure(values=configs)
    def on_config_selected(self, new_name):
        "Save current config BEFORE switching"
        current_name = getattr(self, "_last_config", None)
        if current_name:
            self.save_settings(current_name)
        # Load New Config
        self.load_settings(new_name)
        # Track Current Config
        self._last_config = new_name
    def save_current_config(self):
        name = self.config_var.get()
        self.save_settings(name)
        self.refresh_config_dropdown()
        self.config_dropdown.set(name)
    # Get Items To Load Tos
    def load_app_state(self):
        # Default State
        state = {
            "version": None,
            "tos_accepted": False
        }

        # Use Config_Path (The Actual File) Instead Of Config_Dir
        if os.path.exists(CONFIG_PATH):  # Config_Path Is The File, Config_Dir Is The Folder
            try:
                with open(CONFIG_PATH, "r") as f:
                    state.update(json.load(f))
            except Exception as e:
                print(f"Error loading config: {e}")
                # Corrupted File = Treat As First Launch
                pass

        # 🔥 Detection Logic
        is_first_launch = state["version"] is None
        is_new_version = state["version"] != APP_VERSION

        return state, is_first_launch, is_new_version

    def save_app_state(self, state):
        # Ensure The Directory Exists Before Writing
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(state, f, indent=4)
            # Print(F"Successfully Saved Config To: {Config_Path}")
        except Exception as e:
            print(f"Error saving config: {e}")
            # Optionally Show Error To User
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")
    # Save And Load Settings
    def save_settings(self, name="default", prompt=True):
        """Save all settings to a JSON config file with optional comparison."""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)

        data = self._collect_settings_data()
        
        config_folder = os.path.join(CONFIG_DIR, name)
        os.makedirs(config_folder, exist_ok=True)
        path = os.path.join(config_folder, "config.json")
        
        # Check If Settings Have Changed
        settings_changed = False
        if os.path.exists(path) and prompt:
            try:
                with open(path, "r") as f:
                    old_data = json.load(f)
                if old_data != data:
                    settings_changed = True
            except:
                settings_changed = True
        
        # If Settings Changed And Prompt Is True, Ask User
        if settings_changed and prompt:
            result = messagebox.askyesno(
                "Settings Changed",
                f"The settings for '{name}' have changed.\nDo you want to save these changes?",
                icon=messagebox.QUESTION
            )
            if not result:
                self.set_status(f"Cancelled: Settings not saved")
                return
        
        # Save Misc Settings And Set Status
        self.save_misc_settings()
        self._apply_hotkeys_from_vars()
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.save_last_config(name)
            self.set_status(f"Config saved: {name}")
        except Exception as e:
            self.set_status(f"Error saving config: {e}")
    def _collect_settings_data(self):
        """Collect the full config payload in the same shape used by save/load."""
        data = {}

        # Save All Stringvar And Related Variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, "get") and var is not None:
                    try:
                        data[key] = var.get()
                    except Exception as e:
                        print(f"Skipping {key}: {e}")
        except Exception as e:
            print(f"Error saving vars: {e}")

        # Save Checkbox States
        try:
            for key, checkbox in self.checkboxes.items():
                data[f"checkbox_{key}"] = checkbox.get()
        except Exception as e:
            print(f"Error saving checkboxes: {e}")

        # Save Combobox States
        try:
            for key, combobox in self.comboboxes.items():
                data[f"combobox_{key}"] = combobox.get()
        except Exception as e:
            print(f"Error saving comboboxes: {e}")

        # Save Switch States
        try:
            for key, switch in self.switches.items():
                data[f"switch_{key}"] = self.vars[key].get()
        except Exception as e:
            print(f"Error saving switches: {e}")

        return data
    def load_settings(self, name="default"):
        """Load settings from a JSON config file."""
        path = os.path.join(CONFIG_DIR, name, "config.json")
        rod_folder = os.path.join(CONFIG_DIR, name.replace(".json", ""))
        if not os.path.exists(path):
            self.set_status(f"Config not found: {name}")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.set_status(f"Error loading config: {e}")
            return
        # Load Stringvar And Related Variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'set') and key in data:
                    var.set(data[key])
        except Exception as e:
            print(f"Error loading vars: {e}")
        # Load Checkbox States
        try:
            for key, checkbox in self.checkboxes.items():
                checkbox_key = f"checkbox_{key}"
                if checkbox_key in data:
                    value = data[checkbox_key]
                    if value == "on":
                        checkbox.select()
                    else:
                        checkbox.deselect()
        except Exception as e:
            print(f"Error loading checkboxes: {e}")
        # Load Combobox States
        try:
            for key, cb in self.comboboxes.items():
                combobox_key = f"combobox_{key}"
                if combobox_key in data:
                    cb.set(data[combobox_key])
        except Exception as e:
            print(f"Error loading comboboxes: {e}")
        # Load Switch States (Must Call Select/Deselect To Update Visuals)
        try:
            for key, switch in self.switches.items():
                switch_key = f"switch_{key}"
                if switch_key in data:
                    if data[switch_key] == "on":
                        switch.select()
                    else:
                        switch.deselect()
        except Exception as e:
            print(f"Error loading switches: {e}")
        # Save Misc Settings And Show Status
        self.load_misc_settings()
        self.set_status(f"Config loaded: {name}")
    
    def load_last_config(self):
        """Load the last used config."""
        last_config_path = os.path.join(BASE_PATH, "last_config.json")
        last_config = "default"
        if os.path.exists(last_config_path):
            try:
                with open(last_config_path, "r") as f:
                    data = json.load(f)
                    last_config = data.get("last_config", "default")
            except:
                last_config = "default"
        self.load_settings(last_config)
        # Update The Dropdown And Internal Tracker To Reflect The Loaded Config
        self.config_var.set(last_config)
        self.config_dropdown.set(last_config)
        self._last_config = last_config
    
    def save_last_config(self, name):
        """Save the last used config name (merge into last_config.json)."""
        last_config_path = os.path.join(BASE_PATH, "last_config.json")
        data = {}
        if os.path.exists(last_config_path):
            try:
                with open(last_config_path, "r") as f:
                    data = json.load(f)
            except:
                data = {}
        data["last_config"] = name
        try:
            with open(last_config_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving last config: {e}")
    def on_close(self):
        """This function will automatically run before the app is closed"""
        if self._last_config:
            self.save_settings(self._last_config)
        self.destroy()
    def load_misc_settings(self):
        """Load miscellaneous settings from last_config.json."""
        try:
            path = os.path.join(BASE_PATH, "last_config.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self.current_rod_name = data.get("last_rod", "Basic Rod")
                    self.bar_areas = data.get("bar_areas", {"shake": None, "fish": None, "friend": None, "totem": None})
                    # Important: Load Hotkeys If Present
                    start_key = data.get("start_key", "F5")
                    change_key = data.get("change_bar_areas_key", "F6")
                    screenshot_key = data.get("screenshot_key", "F8")
                    stop_key = data.get("stop_key", "F7")

                    self.vars["start_key"].set(start_key)
                    self.vars["change_bar_areas_key"].set(change_key)
                    self.vars["screenshot_key"].set(screenshot_key)
                    self.vars["stop_key"].set(stop_key)

                    # Convert To Pynput Keys
                    self.hotkey_start = self._string_to_key(start_key)
                    self.hotkey_change_areas = self._string_to_key(change_key)
                    self.hotkey_screenshot = self._string_to_key(screenshot_key)
                    self.hotkey_stop = self._string_to_key(stop_key)
            else:
                self.current_rod_name = "Basic Rod"
                self.bar_areas = {"fish": None, "shake": None, "friend": None, "totem": None}
        except:
            self.current_rod_name = "Basic Rod"
            self.bar_areas = {"fish": None, "shake": None, "friend": None, "totem": None}
    def save_misc_settings(self):
        """Save misc settings without overwriting last_config."""
        path = os.path.join(BASE_PATH, "last_config.json")
        # Load Existing Content
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except:
                data = {}
        # Build Clean Bar Areas
        clean_bar_areas = {}
        for key in ["shake", "fish", "friend", "totem"]:
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
        # Update Fields (Merge Only)
        data["last_rod"] = self.current_rod_name
        data["bar_areas"] = clean_bar_areas
        # Save Hotkeys
        data["start_key"] = self.vars["start_key"].get()
        data["change_bar_areas_key"] = self.vars["change_bar_areas_key"].get()
        data["screenshot_key"] = self.vars["screenshot_key"].get()
        data["stop_key"] = self.vars["stop_key"].get()
        # Write Merged Result
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    # Rod Utilities
    def add_rod(self):
        """Add a new rod configuration with user input."""
        # Create A Dialog Window To Ask For Rod Name
        dialog = CTkToplevel(self)
        dialog.title("Add New Rod")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        
        # Make It Modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Center On Parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Label
        label = CTkLabel(dialog, text="Enter Rod Name:")
        label.pack(pady=10)
        
        # Entry
        entry = CTkEntry(dialog, width=250)
        entry.pack(pady=5)
        entry.focus()
        
        result = {"name": None, "confirmed": False}
        
        def on_confirm():
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showwarning("Invalid Input", "Rod name cannot be empty!")
                return
            
            # Check If Name Already Exists
            if new_name in self.get_config_list():
                messagebox.showwarning("Duplicate Name", f"Rod '{new_name}' already exists!")
                return
            
            result["name"] = new_name
            result["confirmed"] = True
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        confirm_btn = CTkButton(button_frame, text="Confirm", command=on_confirm, width=100)
        confirm_btn.pack(side="left", padx=5)
        
        cancel_btn = CTkButton(button_frame, text="Cancel", command=on_cancel, width=100)
        cancel_btn.pack(side="left", padx=5)
        
        # Wait For Dialog
        self.wait_window(dialog)
        
        if result["confirmed"]:
            new_name = result["name"]
            # Create New Config Folder
            config_folder = os.path.join(CONFIG_DIR, new_name)
            os.makedirs(config_folder, exist_ok=True)
            
            # Create Config.Json With Default Settings
            config_data = {
                "stopping_distance": 2.0,
                "velocity_smoothing": 0.45,
                "movement_threshold": 3.0
            }
            
            with open(os.path.join(config_folder, "config.json"), "w") as f:
                json.dump(config_data, f, indent=4)
            
            # Update Dropdown And Select New Config
            self.config_dropdown.configure(values=self.get_config_list())
            self.config_var.set(new_name)
            self.on_config_selected(new_name)
            self.set_status(f"Rod '{new_name}' created and selected")

    def delete_rod(self):
        """Delete current rod configuration with confirmation."""
        current = self.config_var.get()

        if current == "default":
            messagebox.showwarning("Cannot Delete", "Cannot delete the default rod!")
            return
        
        # Show Confirmation Dialog
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{current}'?\nThis action cannot be undone.",
            icon=messagebox.WARNING
        )
        
        if result:
            config_folder = os.path.join(CONFIG_DIR, current)
            try:
                # Remove The Config Folder
                import shutil
                shutil.rmtree(config_folder)
                
                # Update Dropdown And Switch To Default
                new_list = self.get_config_list()
                self.config_dropdown.configure(values=new_list)
                self.config_var.set("default")
                self.on_config_selected("default")
                self.set_status(f"Rod '{current}' deleted. Switched to default.")
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete rod: {e}")

    def reset_settings(self):
        """Reset settings to default with confirmation."""
        current = self.config_var.get()
        
        result = messagebox.askyesno(
            "Confirm Reset",
            f"Are you sure you want to reset settings for '{current}' to default?\nThis will undo all customizations.",
            icon=messagebox.WARNING
        )
        
        if result:
            config_folder = os.path.join(CONFIG_DIR, current)
            config_path = os.path.join(config_folder, "config.json")
            
            os.makedirs(config_folder, exist_ok=True)
            
            default_settings = self.get_default_settings()
            
            try:
                with open(config_path, "w") as f:
                    json.dump(default_settings, f, indent=4)
                
                self.on_config_selected(current)
                self.set_status(f"Settings for '{current}' reset to default")
            except Exception as e:
                messagebox.showerror("Reset Error", f"Failed to reset settings: {e}")

    def get_default_settings(self):
        return dict(self.default_settings_data)

    # Key Press Functions
    def _apply_hotkeys_from_vars(self):
        """Apply hotkey StringVars to the live hotkey attributes used by on_key_press."""
        self.hotkey_start = self._string_to_key(self.vars["start_key"].get())
        self.hotkey_change_areas = self._string_to_key(self.vars["change_bar_areas_key"].get())
        self.hotkey_screenshot = self._string_to_key(self.vars["screenshot_key"].get())
        self.hotkey_stop = self._string_to_key(self.vars["stop_key"].get())
        # Show Status Lines
    def _string_to_key(self, key_string):
        key_string = key_string.strip().lower()
        # Try Special Keys
        if hasattr(Key, key_string):
            return getattr(Key, key_string)
        # Fallback To Character
        return key_string
    def _normalize_hotkey_value(self, hotkey):
        if isinstance(hotkey, Key):
            return str(hotkey).replace("Key.", "").lower()
        return str(hotkey).strip().lower()
    def normalize_key(self, key):
        try:
            return key.char.lower()  # Letter Keys
        except AttributeError:
            return str(key).replace("Key.", "").lower()
    def on_key_press(self, key):
        pressed_key = self.normalize_key(key)
        enable_hotkeys = (self.vars["enable_hotkeys"].get() or "on")
        # Save Settings (No Prompt - Auto Save Before Macro Starts)
        config_name = self.config_var.get()
        # Change Hotkeys First
        self.hotkey_start = self.vars["start_key"].get()
        self.hotkey_change_areas = self.vars["change_bar_areas_key"].get()
        self.hotkey_stop = self.vars["stop_key"].get()
        self.hotkey_screenshot = self.vars["screenshot_key"].get()
        if enable_hotkeys == "on":
            if pressed_key == self._normalize_hotkey_value(self.hotkey_start) and not self.macro_running:
                self.save_settings(config_name, prompt=True)
                if self.vars["auto_zoom"].get() == "on" and self.vars["casting_mode"].get() == "Perfect":
                    messagebox.showwarning("Error", "Auto Zoom In and Perfect Cast can't be enabled at once. \nDisable one of them to continue.")
                else:
                    self.macro_running = True
                    self.after(0, self.withdraw)
                    threading.Thread(target=self.start_macro, daemon=True).start() # This Will Start The Macro In A New Thread, Allowing The Gui To Remain Responsive
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_change_areas):
                self.open_area_selector()
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_screenshot):
                self._take_debug_screenshot()
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_stop):
                self.stop_macro()
        else:
            self.save_settings(config_name, prompt=False)
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    # Macro Helper Functions
    def open_base_folder(self):
        folder = BASE_PATH
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":  # Macos
            subprocess.run(["open", folder])
        else:  # Linux
            subprocess.run(["xdg-open", folder])
    def stop_macro(self):
        if not self.macro_running:
            return
        self.macro_running = False
        self._reset_pid_state()
        self.after(0, self.deiconify)  # Show Window Safely
        self.set_status("Macro Status: Stopped")
if __name__ == "__main__":
    app = App()
    app.mainloop()
