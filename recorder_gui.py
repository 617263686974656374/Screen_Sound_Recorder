# recorder_gui.py
import tkinter as tk
from tkinter import messagebox, filedialog
from recorder import start_recording, stop_recording, save_video, VIDEO_FORMATS, start_audio_recording, record_screen
from multiprocessing import Value, Process
import threading
import time

class RecorderGUI:
    def __init__(self, root):
        """Initialization of the GUI application."""
        self.root = root
        self.root.title("Screen and Sound Recorder")
        self.root.geometry("400x650")
        self.root.resizable(False, False)

        # Initialization of variables
        self.recording_flag = Value('i', 0)
        self.start_time = None
        self.processes = []

        self.video_format = tk.StringVar(value="")  # Default format is empty

        # GUI components
        self.setup_gui()

    def setup_gui(self):
        """Setting up GUI components."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for countdown
        self.canvas = tk.Canvas(self.main_frame, width=400, height=250, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Video format selection
        format_label = tk.Label(self.main_frame, text="Select video format:", font=("Arial", 12))
        format_label.pack(pady=5)

        # Frame for radiobuttons
        format_frame = tk.Frame(self.main_frame)
        format_frame.pack(pady=5)

        # Creating radiobuttons for video formats
        for fmt in VIDEO_FORMATS.keys():
            rb = tk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                variable=self.video_format,
                value=fmt,
                font=("Arial", 10)
            )
            rb.pack(anchor=tk.W)  # Align radiobuttons to the left

        # Frame for buttons and time
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Recording time
        self.time_label = tk.Label(self.button_frame, text="Recording time: 00:00", font=("Arial", 12))
        self.time_label.pack(pady=5)

        # Buttons
        self.start_button = tk.Button(
            self.button_frame, text="Start Recording",
            command=self.start_recording_with_countdown,
            width=20, bg="green", fg="white"
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop Recording",
            command=self.stop_recording_and_save,
            width=20, bg="red", fg="white"
        )
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def show_countdown(self, countdown=3):
        """Displays the countdown on the canvas."""
        for i in range(countdown, 0, -1):
            self.canvas.delete("all")
            self.canvas.create_text(
                200, 125,
                text=str(i),
                font=("Arial", 48),
                fill="red",
            )
            self.canvas.update()
            time.sleep(1)
        self.canvas.delete("all")

    def stop_recording_and_save(self):
        """Stops recording and allows saving the video."""
        if not self.start_time:
            messagebox.showwarning("Warning", "Recording has not started yet!")
            return

        # Stop processes
        stop_recording(self.recording_flag, self.processes)
        elapsed_time = time.time() - self.start_time
        messagebox.showinfo("Info", f"Recording lasted {elapsed_time:.2f} seconds.")
        self.start_time = None
        self.time_label.config(text="Recording time: 00:00")
        self.canvas.delete("all")

        # Save the video
        save_path = filedialog.asksaveasfilename(
            title="Save recorded video",
            defaultextension=f".{self.video_format.get()}",
            filetypes=[(f"{self.video_format.get().upper()} file", f"*.{self.video_format.get()}"),
                       ("All files", "*.*")]
        )

        if save_path:
            if save_video(save_path, self.video_format.get()):
                messagebox.showinfo("Info", f"Video was successfully saved as:\n{save_path}")
            else:
                messagebox.showerror("Error", "The video could not be saved.")
        else:
            messagebox.showinfo("Info", "The video was not saved. Temporary file remains preserved.")

    def start_recording_with_countdown(self):
        """Starts audio recording immediately and video after the countdown."""
        if self.recording_flag.value:  # Checks if recording is already in progress
            messagebox.showwarning("Warning", "Recording is already in progress!")
            return

        if self.video_format.get() not in VIDEO_FORMATS:
            messagebox.showerror("Error", "Select a valid video format before starting the recording!")
            return

        # Start audio recording immediately
        self.recording_flag.value = 1
        audio_processes = start_audio_recording(self.recording_flag)

        # Start thread for countdown and screen recording
        threading.Thread(target=self._start_video_recording_with_countdown, args=(audio_processes,)).start()

    def _start_video_recording_with_countdown(self, audio_processes):
        """Thread for countdown and starting video recording."""
        self.show_countdown()
        self.start_time = time.time()

        # Start screen recording
        screen_process = Process(target=record_screen, args=(self.recording_flag, self.video_format.get()))
        screen_process.start()

        # Combine processes for audio and video
        self.processes = [screen_process] + audio_processes

        self.update_recording_time()
        self.canvas.create_text(
            200, 100,
            text="Recording in progress...",
            font=("Arial", 24),
            fill="green",
        )
        audio_status = "with sound"
        self.canvas.create_text(
            200, 150,
            text=f"Recording {audio_status}",
            font=("Arial", 16),
            fill="blue",
        )

    def _start_recording_thread(self):
        """Thread for countdown and starting recording."""
        self.show_countdown()
        self.start_time = time.time()
        self.processes = start_recording(self.recording_flag, self.video_format.get())  # Passing the format
        self.update_recording_time()
        self.canvas.create_text(
            200, 100,
            text="Recording in progress...",
            font=("Arial", 24),
            fill="green",
        )
        audio_status = "with sound"
        self.canvas.create_text(
            200, 150,
            text=f"Recording {audio_status}",
            font=("Arial", 16),
            fill="blue",
        )

    def update_recording_time(self):
        """Updates the recording time."""
        if self.start_time and self.recording_flag.value:
            elapsed_time = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            self.time_label.config(text=f"Recording time: {minutes:02}:{seconds:02}")
            self.time_label.after(1000, self.update_recording_time)


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    root = tk.Tk()
    app = RecorderGUI(root)
    root.mainloop()


# pyinstaller --onefile --noconsole --add-data ".venv\Lib\site-packages\cv2\openh264-1.8.0-win64.dll;cv2" --add-data "ffmpeg;ffmpeg" --icon=my_icon.ico recorder_gui.py




