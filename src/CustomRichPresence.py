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
if platform.system() == "Darwin":
    from AppleMusicHandler import AppleMusicHandler
    from Foundation import NSRunLoop


installed_version = "1.0.1"
app_resource_manager = AppResourceManager()
old_client_id = ""
client_id = ""
apple_music_client_id = "827124648206270514"
details = ""
state = ""
song_duration = float(0)
buttons_information = ["", "", "", ""]
image_name = ""
connected = False
is_dark = True
rpc = Presence("")
use_apple_music = False
run_thread = False

settings_path = ""

# Paths which we need for Windows to access the files
if platform.system() != "Darwin":
    if platform.system() == "Windows":
        settings_path = os.path.join(os.environ.get("APPDATA"), "CustomRichPresence")
    else:
        settings_path = os.path.join(Path.home(), ".customrichpresence")

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(__file__)


# -- Apple Music -- #

# Enable/Disable Entrys and Buttons if apple music gets toggled
def toggle_apple_music():
    global use_apple_music

    if is_dark:
        primary_color = "#212121"
        secondary_color = "#FFFFFF"
    else:
        primary_color = "#FFFFFF"
        secondary_color = "#000000"

    tertiary_color = "#7f7f7f"

    if use_apple_music:
        # Apple Music was disabled
        use_apple_music = False
        for slave in root.pack_slaves():
            if type(slave) is Entry:
                slave.config(state=NORMAL, highlightbackground=secondary_color)
            elif type(slave) is TkinterCustomButton:
                slave.configure_color(None, secondary_color, None, primary_color)

        title_button.configure_command(command=edit_title)
        manage_images_button.configure_command(command=manage_images)
        update_button.configure_command(command=update_rp)
    else:
        # Apple Music was enabled
        use_apple_music = True
        for slave in root.pack_slaves():
            if type(slave) is Entry:
                slave.config(state=DISABLED, highlightbackground=secondary_color)
            elif type(slave) is TkinterCustomButton:
                slave.configure_command(command=None)
                slave.configure_color(None, tertiary_color, None, primary_color)


# If song was detected, update presence
def on_song_detected(_details, _state, _song_duration):
    global details, state, song_duration

    details = _details
    state = _state
    song_duration = _song_duration
    update_rp()


# Start apple music query in a loop
def apple_music_loop():
    AppleMusicHandler(command=on_song_detected)
    while True:
        loop = NSRunLoop.currentRunLoop()
        loop.run()
        if not run_thread:
            break


# Apple music gets toggled
def sync_with_apple_music():
    global apple_music_var, run_thread, details, state, client_id, old_client_id, connected, rpc

    # Skip if it's not macOS
    if platform.system() != "Darwin":
        display_message(app_resource_manager.get_string("apple_music_only_macos"))
        apple_music_var.set(value=0)
        return

    # Update information and toggle apple music
    if apple_music_var.get():
        run_thread = True
        apple_music_loop_thread = Thread(target=apple_music_loop)
        apple_music_loop_thread.start()
        old_client_id = client_id
        client_id = apple_music_client_id
    else:
        run_thread = False
        if connected:
            try:
                rpc.close()
            except AssertionError:
                pass
            connected = False
        client_id = clientId_sv.get()
        old_client_id = apple_music_client_id
        details = details_sv.get()
        state = state_sv.get()
    toggle_apple_music()

# -- End apple music -- #


# Open page to manage the title
def edit_title():
    webbrowser.open_new_tab(f"https://discord.com/developers/applications/{client_id}/information")


# Update clientID
def clientId_entry_changed(e):
    global client_id
    client_id = e.get()


# Update details
def details_entry_changed(e):
    global details
    details = e.get()


# Update state
def state_entry_changed(e):
    global state
    state = e.get()


# Update Buttons
def button_entry_changed(e, entry_id):
    buttons_information[entry_id] = str(e.get())


# Update image
def image_entry_changed(e):
    global image_name
    image_name = e.get()


# Open page to manage images
def manage_images():
    webbrowser.open_new_tab(f"https://discord.com/developers/applications/{client_id}/rich-presence/assets")


# Show an Error
def display_message(msg):
    messagebox.showerror(app_resource_manager.get_string("error"), str(msg))


# Update presence
def update_rp():
    global details, state, image_name, connected, old_client_id, client_id, rpc

    # Check if clientID is valid
    if not client_id.isnumeric():
        display_message(app_resource_manager.get_string("invalid_client_id"))
        return

    # Connect with discord
    try:
        if not connected:
            # Not connected
            rpc = Presence(client_id)
            rpc.connect()
            connected = True
        elif client_id is not old_client_id:
            # Connected, but clientID was changed
            rpc.close()
            rpc = Presence(client_id)
            rpc.connect()
        old_client_id = client_id
    except:
        display_message(app_resource_manager.get_string("could_not_connect_to_discord"))
        return

    if not use_apple_music:
        # Check if the buttons information were correctly entered
        buttons_list = []
        if buttons_information[0] and buttons_information[0] != app_resource_manager.get_string("text_1"):
            if buttons_information[1] and validators.url(buttons_information[1]):
                if buttons_information[2] and buttons_information[2] != app_resource_manager.get_string("text_2"):
                    if buttons_information[3] and validators.url(buttons_information[3]):
                        buttons_list = [{"label": buttons_information[0], "url": buttons_information[1]}, {"label": buttons_information[2], "url": buttons_information[3]}]
                    else:
                        display_message(app_resource_manager.get_string("invalid_second_link"))
                        return
                else:
                    buttons_list = [{"label": buttons_information[0], "url": buttons_information[1]}]
            else:
                display_message(app_resource_manager.get_string("invalid_first_link"))
                return

        # Check if some data was not entered
        if not details or len(details) < 2:
            details = "  "
        if not state or len(state) < 2:
            state = "  "
        if not image_name:
            image_name = "  "

        # Update presence (with or without buttons)
        try:
            if buttons_information[0] and len(buttons_list) > 0:
                rpc.update(details=details, state=state, large_image=image_name, start=int(time.time()), buttons=buttons_list)
            else:
                rpc.update(details=details, state=state, large_image=image_name, start=int(time.time()))
        except:
            display_message(app_resource_manager.get_string("could_not_update"))

    else:
        # Update presence (apple music)
        try:
            rpc.update(details=details, state=state, large_image="icon", end=(time.time() + song_duration) if not details.startswith(app_resource_manager.get_string("paused")) else None)
        except:
            display_message(app_resource_manager.get_string("could_not_update"))


# Open my github page
def my_label_clicked():
    webbrowser.open_new_tab("https://github.com/WorldOfBasti")


# Change theme
def toggle_theme_button_clicked():
    global is_dark, use_apple_music

    if is_dark:
        # Light Theme
        is_dark = False
        primary_color = "#FFFFFF"
        secondary_color = "#000000"
        tertiary_color = "#3f3f3f"
        if platform.system() == "Windows":
            img_url = os.path.join(base_dir, "files\\theme_dark.png")
        elif platform.system() == "Linux":
            img_url = os.path.join(base_dir, "files/theme_dark.png")
        else:
            img_url = "files/theme_dark.png"
    else:
        # Dark Theme
        is_dark = True
        primary_color = "#212121"
        secondary_color = "#FFFFFF"
        tertiary_color = "#989898"
        if platform.system() == "Windows":
            img_url = os.path.join(base_dir, "files\\theme_light.png")
        elif platform.system() == "Linux":
            img_url = os.path.join(base_dir, "files/theme_light.png")
        else:
            img_url = "files/theme_light.png"

    quaternary_color = "#7f7f7f"

    root.config(bg=primary_color)
    apple_music_checkbox.config(bg=primary_color, fg=secondary_color)
    my_label.config(bg=primary_color, fg=secondary_color)

    # Adjust color of objects
    for slave in root.pack_slaves():
        if type(slave) is Label:
            slave.config(bg=primary_color, fg=secondary_color)
        elif type(slave) is Entry:
            slave.config(bg=primary_color, fg=secondary_color, highlightbackground=secondary_color, insertbackground=secondary_color, disabledbackground=secondary_color, highlightcolor=tertiary_color if platform.system() == "Linux" else None)
        elif type(slave) is TkinterCustomButton:
            slave.configure_color(bg_color=primary_color, fg_color=quaternary_color if use_apple_music else secondary_color, text_color=primary_color, hover_color=tertiary_color)

    apple_music_checkbox.config(activebackground=primary_color, activeforeground=secondary_color)
    with Image.open(img_url) as image:
        img = ImageTk.PhotoImage(image.resize((50, 50)))
    toggle_theme_button.config(image=img, bg=primary_color)
    toggle_theme_button.image = img


# Check for newer versions of the program
def update():
    try:
        request = str(requests.get("https://raw.githubusercontent.com/WorldOfBasti/CustomRichPresence/master/latest_version.txt"))
        if not version.parse(installed_version) >= version.parse(request):
            should_download = messagebox.askyesno(app_resource_manager.get_string("update_available"), app_resource_manager.get_string("would_you_like_to_update"))
            if should_download:
                webbrowser.open_new_tab("https://github.com/WorldOfBasti/CustomRichPresence/releases")
    except:
        pass


# Save settings and close the program
def on_close():
    global data, run_thread

    try:
        run_thread = False
        data = [str(clientId_sv.get()), is_dark]
        if platform.system() != "Darwin":
            Path(settings_path).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(settings_path, "settings.dat"), "wb") as f:
                pickle.dump(data, f)
        else:
            with open("files/settings.dat", "wb") as f:
                pickle.dump(data, f)
    except:
        pass
    finally:
        root.destroy()


# Tkinter window
root = Tk()
root.title("CustomRichPresence")
root.geometry("475x675")
root.resizable(0, 0)
if platform.system() == "Windows":
    root.iconbitmap(os.path.join(base_dir, "files\\icon_windows.ico"))
elif platform.system() == "Linux":
    root.wm_iconphoto(True, PhotoImage(file=os.path.join(base_dir, "files/icon_linux.png")))
root.bind("<Return>", lambda event: update_rp() if not use_apple_music else None)
if platform.system() == "Darwin":
    menu = Menu(root)
    root.config(menu=menu)


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


# Apple music
apple_music_var = IntVar()
apple_music_checkbox = Checkbutton(root, text=app_resource_manager.get_string("sync_with_apple_music"), highlightthickness=0, variable=apple_music_var, onvalue=True, offvalue=False, command=sync_with_apple_music)
apple_music_checkbox.pack(pady=(0, 15))

# ClientId
clientId_label = Label(root, text=app_resource_manager.get_string("client_id"), width=label_width, anchor=W)
clientId_label.pack()
clientId_sv = StringVar()
clientId_sv.trace("w", lambda name, index, mode, sv=clientId_sv: clientId_entry_changed(sv))
clientId_entry = Entry(root, textvariable=clientId_sv, highlightthickness=3, bd=0, width=entry_width)
clientId_entry.pack(pady=(0, 10))

# Title
title_label = Label(root, text=app_resource_manager.get_string("title"), width=label_width, anchor=W)
title_label.pack()
title_button = TkinterCustomButton(text=app_resource_manager.get_string("edit_title"), command=edit_title, height=35, width=button_width, corner_radius=0 if platform.system() == "Windows" else 10)
title_button.pack(pady=(0, 10))

# Details
details_label = Label(root, text=app_resource_manager.get_string("details"), width=label_width, anchor=W)
details_label.pack()
details_sv = StringVar()
details_sv.trace("w", lambda name, index, mode, sv=details_sv: details_entry_changed(sv))
details_entry = Entry(root, textvariable=details_sv, highlightthickness=3, bd=0, width=entry_width)
details_entry.pack(pady=(0, 10))

# State
state_label = Label(root, text=app_resource_manager.get_string("state"), width=label_width, anchor=W)
state_label.pack()
state_sv = StringVar()
state_sv.trace("w", lambda name, index, mode, sv=state_sv: state_entry_changed(sv))
state_entry = Entry(root, textvariable=state_sv, highlightthickness=3, bd=0, width=entry_width)
state_entry.pack(pady=(0, 10))

# Buttons
buttons_label = Label(root, text=app_resource_manager.get_string("buttons"), width=label_width, anchor=W)
buttons_label.pack()
button1text_sv = StringVar()
button1text_sv.trace("w", lambda name, index, mode, sv=button1text_sv: button_entry_changed(sv, 0))
button1text_entry = Entry(root, textvariable=button1text_sv, highlightthickness=3, bd=0, width=entry_width)
button1text_entry.insert(0, app_resource_manager.get_string("text_1"))
button1text_entry.bind("<FocusIn>", lambda event: button1text_entry.delete(0, "end") if button1text_sv.get() == app_resource_manager.get_string("text_1") else None)
button1text_entry.pack(pady=2.5)
button1link_sv = StringVar()
button1link_sv.trace("w", lambda name, index, mode, sv=button1link_sv: button_entry_changed(sv, 1))
button1link_entry = Entry(root, textvariable=button1link_sv, highlightthickness=3, bd=0, width=entry_width)
button1link_entry.insert(0, app_resource_manager.get_string("link_1"))
button1link_entry.bind("<FocusIn>", lambda event: button1link_entry.delete(0, "end") if button1link_sv.get() == app_resource_manager.get_string("link_1") else None)
button1link_entry.pack(pady=2.5)
button2text_sv = StringVar()
button2text_sv.trace("w", lambda name, index, mode, sv=button2text_sv: button_entry_changed(sv, 2))
button2text_entry = Entry(root, textvariable=button2text_sv, highlightthickness=3, bd=0, width=entry_width)
button2text_entry.insert(0, app_resource_manager.get_string("text_2"))
button2text_entry.bind("<FocusIn>", lambda event: button2text_entry.delete(0, "end") if button2text_sv.get() == app_resource_manager.get_string("text_2") else None)
button2text_entry.pack(pady=2.5)
button2link_sv = StringVar()
button2link_sv.trace("w", lambda name, index, mode, sv=button2link_sv: button_entry_changed(sv, 3))
button2link_entry = Entry(root, textvariable=button2link_sv, highlightthickness=3, bd=0, width=entry_width)
button2link_entry.insert(0, app_resource_manager.get_string("link_2"))
button2link_entry.bind("<FocusIn>", lambda event: button2link_entry.delete(0, "end") if button2link_sv.get() == app_resource_manager.get_string("link_2") else None)
button2link_entry.pack(pady=(2.5, 10))

# Image
image_label = Label(root, text=app_resource_manager.get_string("image"), width=label_width, anchor=W)
image_label.pack()
manage_images_button = TkinterCustomButton(text=app_resource_manager.get_string("manage_images"), command=manage_images, height=35, width=button_width, corner_radius=0 if platform.system() == "Windows" else 10)
manage_images_button.pack(pady=(0, 7.5))
image_sv = StringVar()
image_sv.trace("w", lambda name, index, mode, sv=image_sv: image_entry_changed(sv))
image_entry = Entry(root, textvariable=image_sv, highlightthickness=3, bd=0, width=entry_width)
image_entry.insert(0, app_resource_manager.get_string("image_name"))
image_entry.bind("<FocusIn>", lambda event: image_entry.delete(0, "end") if image_entry.get() == app_resource_manager.get_string("image_name") else None)
image_entry.pack(pady=(0, 20))

# Update presence
update_button = TkinterCustomButton(text=app_resource_manager.get_string("update_rich_presence"), command=update_rp, height=35, width=250, corner_radius=0 if platform.system() == "Windows" else 10)
update_button.pack(pady=(0, 10))

# DarkMode Switch
toggle_theme_button = Label(root, height=50, width=50)
toggle_theme_button.bind("<Button-1>", lambda event: toggle_theme_button_clicked())
toggle_theme_button.place(relx=0.5, rely=0.91, anchor=CENTER)

# "By WorldOfBasti" label
my_label = Label(root, text="by WorldOfBasti")
my_label.bind("<Button-1>", lambda event: my_label_clicked())
my_label.place(relx=0.5, rely=0.975, anchor=CENTER)

# Load settings
try:
    if platform.system() != "Darwin":
        with open(os.path.join(settings_path, "settings.dat"), "rb") as f:
            data = pickle.load(f)
    else:
        with open("files/settings.dat", "rb") as f:
            data = pickle.load(f)
    clientId_entry.insert(0, data[0])
    is_dark = not data[1]
except FileNotFoundError or TypeError:
    pass

# Load Light/Dark mode for the first time
toggle_theme_button_clicked()

# Set close method
root.protocol("WM_DELETE_WINDOW", on_close)

# Check for newer versions
update_thread = Thread(target=update)
update_thread.start()

# Make sure that the window stays open
root.mainloop()
