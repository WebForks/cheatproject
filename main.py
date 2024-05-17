# pyinstaller --onefile --noconsole main.py
# ctrl + h to open the dialog box
# esc to close the dialog box

import tkinter as tk
from tkinter import simpledialog
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw
import keyboard
from openai import OpenAI

API_KEY = ' WRITE YOUR API KEY HERE'
database_schema = """ WRITE YOUR ALWAYS GOING TO INSERT INFORMATION HERE """

print(database_schema)


def create_image(width, height, color1, color2):
    # Create a new image with given width and height
    image = Image.new('RGB', (width, height), color1)
    # Initialize the drawing context
    dc = ImageDraw.Draw(image)
    # Draw a rectangle with the specified color2
    dc.rectangle(
        [width // 2, 0, width, height],
        fill=color2)
    return image


def ask_gpt(question):
    messages = [{"role": "user", "content": database_schema + question}]
    client = OpenAI(
        api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    print(messages)
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def on_hotkey_pressed(icon):
    def run():
        root = tk.Tk()
        root.overrideredirect(True)
        root.geometry("300x24+700+790")
        root.lift()
        root.wm_attributes("-topmost", True)
        root.after_idle(root.wm_attributes, "-topmost", False)
        entry = tk.Entry(root, bd=0, bg="white", width=50)
        entry.pack()
        entry.focus_force()

        def submit_and_close(event):
            question = entry.get()
            if question:
                answer = ask_gpt(question)
                root.destroy()  # Close the question window
                # Call to display the answer in a new window
                display_answer(answer)

        def close_on_esc(event):
            root.destroy()

        entry.bind("<Return>", submit_and_close)
        root.bind("<Escape>", close_on_esc)
        root.mainloop()

    def display_answer(answer):
        answer_root = tk.Tk()
        answer_root.overrideredirect(True)
        answer_root.lift()
        answer_root.wm_attributes("-topmost", True)

        # Create a frame to contain the text widget and the scrollbar
        frame = tk.Frame(answer_root)
        frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(frame, bd=0, bg="white", wrap="word")
        text_widget.insert("1.0", answer)

        # Create a Scrollbar and set it to the right side of the frame
        scrollbar = tk.Scrollbar(
            frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Configure the text widget to use the scrollbar
        text_widget.config(yscrollcommand=scrollbar.set)
        # Make the text widget read-only
        text_widget.config(state="disabled")

        # Estimate the window size required to display the answer
        lines = answer.count('\n') + 1
        char_in_longest_line = max(len(line)
                                   for line in answer.split('\n'))
        width = min(max(char_in_longest_line, 20), 100) * \
            7  # Estimate width based on characters
        # Estimate height based on lines
        height = min(max(lines, 1), 40) * 20

        answer_root.geometry(f"{width}x{height}+0+0")

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind any key press to close the window
        text_widget.bind("<Key>", lambda e: answer_root.destroy())

        text_widget.focus_force()  # Focus to capture key press
        answer_root.mainloop()

    threading.Thread(target=run).start()


def setup_tray_icon():
    # Icon image creation
    icon_image = create_image(64, 64, 'black', 'red')

    # Define a function to show the dialog when the menu item is clicked
    def show_dialog(icon, item):
        on_hotkey_pressed(icon)

    # Define the menu for the system tray icon
    menu = (item('Ask GPT', show_dialog), item(
        'Quit', lambda icon, item: icon.stop()))

    # Create the system tray icon
    icon = pystray.Icon("test_icon", icon_image, "Test Icon", menu)

    # Run the icon
    icon.run()


if __name__ == "__main__":
    # Set up hotkey to show input dialog
    keyboard.add_hotkey('ctrl+h', lambda: on_hotkey_pressed(None))

    # Set up and run system tray icon in a separate thread to prevent blocking
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.start()

    # Wait for escape key to stop the script
    keyboard.wait('esc')
