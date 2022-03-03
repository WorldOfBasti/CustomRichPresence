import tkinter
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image as Image
from Resources.AppResourceManager import AppResourceManager
from TkinterCustomButton import TkinterCustomButton
from pypresence import Presence
from packaging import version
from threading import Thread
from pathlib import Path
import validators as validators
import requests
import webbrowser
import time
import pickle
import os
import sys
import platform
if platform.system() != "Linux":
    import pystray
if platform.system() == "Darwin":
    from AppleMusicManager import AppleMusicManager
    from Cocoa import NSApp


class Main(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)

        self.installed_version = "1.1.1"
        self.app_resource_manager = AppResourceManager()
        if platform.system() == "Darwin":
            self.apple_music_manager = AppleMusicManager(app_resource_manager=self.app_resource_manager, command=self.apple_music_song_updated)
        self.old_client_id = ""
        self.client_id = ""
        self.apple_music_client_id = "827124648206270514"
        self.details = ""
        self.state = ""
        self.song_duration = float(0)
        self.buttons_information = ["", "", "", ""]
        self.image_name = ""
        self.connected = False
        self.is_dark = True
        self.rpc = None
        self.use_apple_music = False
        self.tray = None

        # Paths which we need for Windows to access the files
        if platform.system() != "Darwin":
            if platform.system() == "Windows":
                self.settings_path = os.path.join(os.environ.get("APPDATA"), "CustomRichPresence")
            else:
                self.settings_path = os.path.join(Path.home(), ".customrichpresence")

        # Save relative path, so the files can be accessed
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(__file__)

        # Tkinter window
        self.title("CustomRichPresence")
        self.geometry(f"{475}x{700 if platform.system() == 'Windows' else 725}")
        self.resizable(False, False)
        if platform.system() == "Windows":
            self.iconbitmap(os.path.join(self.base_dir, "files\\icon_windows.ico"))
        elif platform.system() == "Linux":
            self.wm_iconphoto(True, PhotoImage(file=os.path.join(self.base_dir, "files/icon_linux.png")))
        self.bind("<Return>", lambda event: self.update_rp() if not self.use_apple_music else None)
        if platform.system() == "Darwin":
            menu = Menu(self)
            self.config(menu=menu)

        # Default values (platform specific)
        if platform.system() == "Windows":
            label_width = 27
            entry_width = 30
            button_width = 190
        elif platform.system() == "Linux":
            label_width = 23
            entry_width = 23
            button_width = 190
        else:
            label_width = 20
            entry_width = 20
            button_width = 190

        # Apple Music
        self.apple_music_var = IntVar()
        self.apple_music_checkbox = Checkbutton(self, text=self.app_resource_manager.get_string("sync_with_apple_music"), highlightthickness=0, variable=self.apple_music_var, onvalue=True, offvalue=False, command=self.sync_with_apple_music)
        self.apple_music_checkbox.pack(pady=(0, 15))

        # ClientId
        client_id_label = Label(self, text=self.app_resource_manager.get_string("client_id"), width=label_width, anchor=W)
        client_id_label.pack()
        self.clientId_sv = StringVar()
        self.clientId_sv.trace("w", lambda name, index, mode, sv=self.clientId_sv: self.clientId_entry_changed(sv))
        client_id_entry = Entry(self, textvariable=self.clientId_sv, highlightthickness=3, bd=0, width=entry_width)
        client_id_entry.pack(pady=(0, 10))

        # Title
        title_label = Label(self, text=self.app_resource_manager.get_string("title"), width=label_width, anchor=W)
        title_label.pack()
        self.title_button = TkinterCustomButton(master=self, text=self.app_resource_manager.get_string("edit_title"), command=self.edit_title, height=35, width=button_width, corner_radius=0 if platform.system() == "Windows" else 10)
        self.title_button.pack(pady=(0, 10))

        # Details
        details_label = Label(self, text=self.app_resource_manager.get_string("details"), width=label_width, anchor=W)
        details_label.pack()
        self.details_sv = StringVar()
        self.details_sv.trace("w", lambda name, index, mode, sv=self.details_sv: self.details_entry_changed(sv))
        details_entry = Entry(self, textvariable=self.details_sv, highlightthickness=3, bd=0, width=entry_width)
        details_entry.pack(pady=(0, 10))

        # State
        state_label = Label(self, text=self.app_resource_manager.get_string("state"), width=label_width, anchor=W)
        state_label.pack()
        self.state_sv = StringVar()
        self.state_sv.trace("w", lambda name, index, mode, sv=self.state_sv: self.state_entry_changed(sv))
        state_entry = Entry(self, textvariable=self.state_sv, highlightthickness=3, bd=0, width=entry_width)
        state_entry.pack(pady=(0, 10))

        # Buttons
        buttons_label = Label(self, text=self.app_resource_manager.get_string("buttons"), width=label_width, anchor=W)
        buttons_label.pack()
        button1text_sv = StringVar()
        button1text_sv.trace("w", lambda name, index, mode, sv=button1text_sv: self.button_entry_changed(sv, 0))
        button1text_entry = Entry(self, textvariable=button1text_sv, highlightthickness=3, bd=0, width=entry_width)
        button1text_entry.insert(0, self.app_resource_manager.get_string("text_1"))
        button1text_entry.bind("<FocusIn>", lambda event: button1text_entry.delete(0, "end") if button1text_sv.get() == self.app_resource_manager.get_string("text_1") else None)
        button1text_entry.pack(pady=2.5)
        button1link_sv = StringVar()
        button1link_sv.trace("w", lambda name, index, mode, sv=button1link_sv: self.button_entry_changed(sv, 1))
        button1link_entry = Entry(self, textvariable=button1link_sv, highlightthickness=3, bd=0, width=entry_width)
        button1link_entry.insert(0, self.app_resource_manager.get_string("link_1"))
        button1link_entry.bind("<FocusIn>", lambda event: button1link_entry.delete(0, "end") if button1link_sv.get() == self.app_resource_manager.get_string("link_1") else None)
        button1link_entry.pack(pady=2.5)
        button2text_sv = StringVar()
        button2text_sv.trace("w", lambda name, index, mode, sv=button2text_sv: self.button_entry_changed(sv, 2))
        button2text_entry = Entry(self, textvariable=button2text_sv, highlightthickness=3, bd=0, width=entry_width)
        button2text_entry.insert(0, self.app_resource_manager.get_string("text_2"))
        button2text_entry.bind("<FocusIn>", lambda event: button2text_entry.delete(0, "end") if button2text_sv.get() == self.app_resource_manager.get_string("text_2") else None)
        button2text_entry.pack(pady=2.5)
        button2link_sv = StringVar()
        button2link_sv.trace("w", lambda name, index, mode, sv=button2link_sv: self.button_entry_changed(sv, 3))
        button2link_entry = Entry(self, textvariable=button2link_sv, highlightthickness=3, bd=0, width=entry_width)
        button2link_entry.insert(0, self.app_resource_manager.get_string("link_2"))
        button2link_entry.bind("<FocusIn>", lambda event: button2link_entry.delete(0, "end") if button2link_sv.get() == self.app_resource_manager.get_string("link_2") else None)
        button2link_entry.pack(pady=(2.5, 10))

        # Image
        image_label = Label(self, text=self.app_resource_manager.get_string("image"), width=label_width, anchor=W)
        image_label.pack()
        self.manage_images_button = TkinterCustomButton(master=self, text=self.app_resource_manager.get_string("manage_images"), command=self.manage_images, height=35, width=button_width, corner_radius=0 if platform.system() == "Windows" else 10)
        self.manage_images_button.pack(pady=(0, 7.5))
        image_sv = StringVar()
        image_sv.trace("w", lambda name, index, mode, sv=image_sv: self.image_entry_changed(sv))
        image_entry = Entry(self, textvariable=image_sv, highlightthickness=3, bd=0, width=entry_width)
        image_entry.insert(0, self.app_resource_manager.get_string("image_name"))
        image_entry.bind("<FocusIn>", lambda event: image_entry.delete(0, "end") if image_entry.get() == self.app_resource_manager.get_string("image_name") else None)
        image_entry.pack(pady=(0, 20))

        # Update presence
        self.update_button = TkinterCustomButton(master=self, text=self.app_resource_manager.get_string("update_rich_presence"), command=self.update_rp, height=35, width=250, corner_radius=0 if platform.system() == "Windows" else 10)
        self.update_button.pack(pady=(0, 10))

        # Enable minimized mode
        self.enable_tray_button = TkinterCustomButton(master=self, text=self.app_resource_manager.get_string("enable_minimized_mode"), command=self.enable_minimized_mode, height=35, width=250, corner_radius=0 if platform.system() == "Windows" else 10)
        self.enable_tray_button.pack(pady=(0, 15))

        # DarkMode Switch
        self.toggle_theme_button = Label(self, height=50, width=50)
        self.toggle_theme_button.bind("<Button-1>", lambda event: self.toggle_theme_button_clicked())
        self.toggle_theme_button.place(relx=0.5, rely=0.91, anchor=CENTER)

        # My label
        self.my_label = Label(self, text="by WorldOfBasti")
        self.my_label.bind("<Button-1>", lambda event: self.my_label_clicked())
        self.my_label.place(relx=0.5, rely=0.975, anchor=CENTER)

        # Load settings
        try:
            if platform.system() == "Darwin":
                with open(os.path.join(self.base_dir, "files/settings.dat"), "rb") as f:
                    data = pickle.load(f)
            else:
                with open(os.path.join(self.settings_path, "settings.dat"), "rb") as f:
                    data = pickle.load(f)

            client_id_entry.insert(0, data[0])
            self.is_dark = not data[1]
        except FileNotFoundError or TypeError:
            pass

        # Load Light/Dark mode for the first time
        self.toggle_theme_button_clicked()

        # Set close method
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Check for newer versions
        update_thread = Thread(target=self.update)
        update_thread.start()

        # Make sure that the window stays open
        self.mainloop()

    # Apple Music checkbox gets toggled
    def sync_with_apple_music(self):
        # Skip if it's not macOS
        if platform.system() != "Darwin":
            self.display_message(self.app_resource_manager.get_string("apple_music_only_macos"))
            self.apple_music_var.set(value=0)
            return

        if self.is_dark:
            primary_color = "#212121"
            secondary_color = "#FFFFFF"
        else:
            primary_color = "#FFFFFF"
            secondary_color = "#000000"

        tertiary_color = "#7f7f7f"

        if self.apple_music_var.get():
            # Change ClientID
            self.old_client_id = self.client_id
            self.client_id = self.apple_music_client_id

            # Start Apple Music synchronization
            self.use_apple_music = True
            self.apple_music_manager.start_syncing()

            # Disable controls
            for slave in self.pack_slaves():
                if type(slave) is Entry:
                    slave.config(state=DISABLED, highlightbackground=secondary_color)
                elif type(slave) is TkinterCustomButton and slave is not self.enable_tray_button:
                    slave.configure_command(command=None)
                    slave.configure_color(None, tertiary_color, None, primary_color)
        else:
            # Stop Apple Music synchronization
            self.apple_music_manager.stop_syncing()
            self.use_apple_music = False
            if self.connected:
                try:
                    self.rpc.close()
                except AssertionError:
                    pass
                self.connected = False

            # Load old ClientID
            self.client_id = self.clientId_sv.get()
            self.old_client_id = self.apple_music_client_id
            self.details = self.details_sv.get()
            self.state = self.state_sv.get()

            # Enable controls
            for slave in self.pack_slaves():
                if type(slave) is Entry:
                    slave.config(state=NORMAL, highlightbackground=secondary_color)
                elif type(slave) is TkinterCustomButton and slave is not self.enable_tray_button:
                    slave.configure_color(None, secondary_color, None, primary_color)

                    self.title_button.configure_command(command=self.edit_title)
                    self.manage_images_button.configure_command(command=self.manage_images)
                    self.update_button.configure_command(command=self.update_rp)

    # Apple Music song updated
    def apple_music_song_updated(self, details, state, song_duration):
        self.details = details
        self.state = state
        self.song_duration = song_duration
        self.update_rp()

    # Minimized mode was enabled
    def enable_minimized_mode(self):
        # Not available for Linux
        if platform.system() == "Linux":
            self.display_message(self.app_resource_manager.get_string("minimized_not_linux"))
            return

        # Hide window and dock icon
        if platform.system() == "Darwin":
            NSApp.setActivationPolicy_(1)
        self.withdraw()

        # Show and run tray icon
        if platform.system() == "Darwin":
            tray_icon = Image.open(os.path.join(self.base_dir, "files/tray_icon.png"))
        else:
            tray_icon = Image.open(os.path.join(self.base_dir, "files\\tray_icon.png"))
        tray_menu = pystray.Menu(pystray.MenuItem(self.app_resource_manager.get_string("open_program"), self.disable_minimized_mode, default=True), pystray.MenuItem(self.app_resource_manager.get_string("stop_program"), self.on_close))
        self.tray = pystray.Icon("CustomRichPresence", tray_icon, "CustomRichPresence", tray_menu)
        self.tray.run()

    # Minimized mode was disabled
    def disable_minimized_mode(self):
        # Not available for Linux
        if platform.system() == "Linux":
            return

        # Hide tray icon
        if self.tray:
            self.tray.stop()

        # Show window and dock icon
        if platform.system() == "Darwin":
            NSApp.setActivationPolicy_(0)
        self.deiconify()

    # Open page to manage the title
    def edit_title(self):
        webbrowser.open_new_tab(f"https://discord.com/developers/applications/{self.client_id}/information")

        # Stop current presence, so the title gets updated
        if self.connected:
            self.rpc.close()
            self.rpc = Presence(self.client_id)
            self.connected = False

    # Update clientID
    def clientId_entry_changed(self, e):
        self.client_id = e.get()

    # Update details
    def details_entry_changed(self, e):
        self.details = e.get()

    # Update state
    def state_entry_changed(self, e):
        self.state = e.get()

    # Update Buttons
    def button_entry_changed(self, e, entry_id):
        self.buttons_information[entry_id] = str(e.get())

    # Update image
    def image_entry_changed(self, e):
        self.image_name = e.get()

    # Open page to manage images
    def manage_images(self):
        webbrowser.open_new_tab(f"https://discord.com/developers/applications/{self.client_id}/rich-presence/assets")

    # Show an Error
    def display_message(self, msg):
        messagebox.showerror(self.app_resource_manager.get_string("error"), str(msg))

    # Update presence
    def update_rp(self):
        # Check if clientID is valid
        if not self.client_id.isnumeric():
            self.display_message(self.app_resource_manager.get_string("invalid_client_id"))
            return

        # Connect with discord
        try:
            if not self.connected:
                # Not connected
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                self.connected = True
            elif self.client_id is not self.old_client_id:
                # Connected, but clientID was changed
                self.rpc.close()
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
            self.old_client_id = self.client_id
        except:
            self.display_message(self.app_resource_manager.get_string("could_not_connect_to_discord"))
            return

        # Update presence (apple music)
        if self.use_apple_music:
            try:
                self.rpc.update(details=self.details, state=self.state, large_image="icon", end=(time.time() + self.song_duration) if not self.details.startswith(self.app_resource_manager.get_string("paused")) else None)
            except:
                self.display_message(self.app_resource_manager.get_string("could_not_update"))
        # Update presence with entered information
        else:
            # Check if the buttons information were correctly entered
            buttons_list = []
            if self.buttons_information[0] and self.buttons_information[0] != self.app_resource_manager.get_string("text_1"):
                if self.buttons_information[1] and validators.url(self.buttons_information[1]):
                    if self.buttons_information[2] and self.buttons_information[2] != self.app_resource_manager.get_string("text_2"):
                        if self.buttons_information[3] and validators.url(self.buttons_information[3]):
                            buttons_list = [{"label": self.buttons_information[0], "url": self.buttons_information[1]}, {"label": self.buttons_information[2], "url": self.buttons_information[3]}]
                        else:
                            self.display_message(self.app_resource_manager.get_string("invalid_second_link"))
                            return
                    else:
                        buttons_list = [{"label": self.buttons_information[0], "url": self.buttons_information[1]}]
                else:
                    self.display_message(self.app_resource_manager.get_string("invalid_first_link"))
                    return

            # Check if some data was not entered
            if not self.details or len(self.details) < 2:
                self.details = "  "
            if not self.state or len(self.state) < 2:
                self.state = "  "
            if not self.image_name:
                self.image_name = "  "

            # Update presence (with or without buttons)
            try:
                if self.buttons_information[0] and len(buttons_list) > 0:
                    self.rpc.update(details=self.details, state=self.state, large_image=self.image_name, start=int(time.time()), buttons=buttons_list)
                else:
                    self.rpc.update(details=self.details, state=self.state, large_image=self.image_name, start=int(time.time()))
            except:
                self.display_message(self.app_resource_manager.get_string("could_not_update"))
                if self.rpc:
                    self.rpc.close()
                    self.rpc = None
                    self.connected = False

    # Open my GitHub page
    @staticmethod
    def my_label_clicked():
        webbrowser.open_new_tab("https://github.com/WorldOfBasti")

    # Change theme
    def toggle_theme_button_clicked(self):
        if self.is_dark:
            # Light Theme
            self.is_dark = False
            primary_color = "#FFFFFF"
            secondary_color = "#000000"
            tertiary_color = "#3f3f3f"
            if platform.system() == "Windows":
                img_url = os.path.join(self.base_dir, "files\\theme_dark.png")
            else:
                img_url = os.path.join(self.base_dir, "files/theme_dark.png")
        else:
            # Dark Theme
            self.is_dark = True
            primary_color = "#212121"
            secondary_color = "#FFFFFF"
            tertiary_color = "#989898"
            if platform.system() == "Windows":
                img_url = os.path.join(self.base_dir, "files\\theme_light.png")
            else:
                img_url = os.path.join(self.base_dir, "files/theme_light.png")

        quaternary_color = "#7f7f7f"

        self.config(bg=primary_color)
        self.apple_music_checkbox.config(bg=primary_color, fg=secondary_color)
        self.my_label.config(bg=primary_color, fg=secondary_color)

        # Adjust color of objects
        for slave in self.pack_slaves():
            if type(slave) is Label:
                slave.config(bg=primary_color, fg=secondary_color)
            elif type(slave) is Entry:
                slave.config(bg=primary_color, fg=secondary_color, highlightbackground=secondary_color, insertbackground=secondary_color, disabledbackground=secondary_color, highlightcolor=tertiary_color if platform.system() == "Linux" else None)
            elif type(slave) is TkinterCustomButton:
                slave.configure_color(bg_color=primary_color, fg_color=quaternary_color if self.use_apple_music else secondary_color, text_color=primary_color, hover_color=tertiary_color)

        self.apple_music_checkbox.config(activebackground=primary_color, activeforeground=secondary_color)
        with Image.open(img_url) as image:
            img = ImageTk.PhotoImage(image.resize((50, 50)))
            self.toggle_theme_button.config(image=img, bg=primary_color)
            self.toggle_theme_button.image = img

    # Check for newer versions of the program
    def update(self):
        try:
            request = requests.get("https://raw.githubusercontent.com/WorldOfBasti/CustomRichPresence/master/latest_version.txt").text
            if version.parse(self.installed_version) < version.parse(request):
                should_download = messagebox.askyesno(self.app_resource_manager.get_string("update_available"), self.app_resource_manager.get_string("would_you_like_to_update"))
                if should_download:
                    webbrowser.open_new_tab("https://github.com/WorldOfBasti/CustomRichPresence/releases")
        except:
            pass

    # Save settings, stop syncing and close the program
    def on_close(self):
        try:
            data = [str(self.clientId_sv.get()), self.is_dark]
            if platform.system() == "Darwin":
                if self.use_apple_music:
                    self.apple_music_manager.stop_syncing()
                with open(os.path.join(self.base_dir, "files/settings.dat"), "wb") as f:
                    pickle.dump(data, f)
            else:
                Path(self.settings_path).mkdir(parents=True, exist_ok=True)
                with open(os.path.join(self.settings_path, "settings.dat"), "wb") as f:
                    pickle.dump(data, f)
        except:
            pass
        finally:
            os._exit(0)


if __name__ == "__main__":
    main = Main()
