# recorder.py

import pyaudio
import wave
import cv2
import numpy as np
import pyautogui
from multiprocessing import Process
import threading
import os
import shutil
import ctypes
import subprocess
from time import sleep


# Video and audio parameters
SCREEN_SIZE = pyautogui.size()
FPS = 20.0
OUTPUT_AUDIO = "audio.wav"
VIDEO_FORMATS = {"avi": "XVID", "mp4": "mp4v", "mkv": "X264"}

def start_audio_recording(recording_flag):
    """Starts audio recording."""
    stop_audio_event = threading.Event()

    # Thread for audio recording
    audio_thread = threading.Thread(target=record_audio, args=(stop_audio_event, OUTPUT_AUDIO))
    audio_thread.start()

    # Return only processes related to audio recording
    return [stop_audio_event, audio_thread]

def list_active_microphones():
    """Retrieves a list of available and functional microphones."""
    p = pyaudio.PyAudio()
    active_devices = []

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            try:
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                input_device_index=i)
                stream.close()
                active_devices.append((i, device_info['name']))
            except Exception:
                pass  # Skip non-functional devices

    p.terminate()
    return active_devices

def load_openh264_dll():
    """Loads the openh264 DLL only once before initializing VideoWriter."""
    cv2_dir = os.path.dirname(cv2.__file__)
    dll_filename = "openh264-1.8.0-win64.dll"
    dll_path = os.path.join(cv2_dir, dll_filename)

    if os.path.exists(dll_path):
        try:
            ctypes.WinDLL(dll_path)
            print(f"DLL successfully loaded from path: {dll_path}")
        except Exception as e:
            print(f"Error loading DLL: {e}")
    else:
        print(f"DLL not found at the expected location: {dll_path}")



def record_screen(recording_flag, video_format):
    """Records the screen and saves the video in the selected format."""
    load_openh264_dll()  # Load DLL before initializing VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*VIDEO_FORMATS[video_format])
    output_video = f"recording.{video_format}"
    out = cv2.VideoWriter(output_video, fourcc, FPS, SCREEN_SIZE)

    if not out.isOpened():
        print(f"Error initializing VideoWriter for file {output_video}")
        return

    try:
        print(f"Screen recording started: {output_video}")
        while recording_flag.value:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
    except Exception as e:
        print(f"Error during screen recording: {e}")
    finally:
        out.release()
        print(f"Screen recording ended: {output_video}")

def record_audio(stop_event, filename="audio.wav"):
    """Records audio from the first available microphone and saves it to a file."""
    active_microphones = list_active_microphones()
    if not active_microphones:
        print("No available microphones found.")
        return

    selected_index = active_microphones[0][0]
    print(f"Using microphone: {active_microphones[0][1]}")

    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        input_device_index=selected_index,
                        frames_per_buffer=1024)

        frames = []
        print("Audio recording started...")
        while not stop_event.is_set():
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)

        # Save audio to WAV file
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

        print(f"Audio saved to file: {filename}")
    except Exception as e:
        print(f"Error during audio recording: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()







def start_recording(recording_flag, video_format):
    """Starts audio recording first, followed by video recording."""
    recording_flag.value = 1
    stop_audio_event = threading.Event()

    # Thread for audio
    audio_thread = threading.Thread(target=record_audio, args=(stop_audio_event, OUTPUT_AUDIO))
    audio_thread.start()

    # Wait for audio recording to initialize (e.g., 0.5 seconds)
    sleep(0.5)

    # Process for screen recording
    screen_process = Process(target=record_screen, args=(recording_flag, video_format))
    screen_process.start()

    # Return processes and threads: [screen_process, stop_audio_event, audio_thread]
    return [screen_process, stop_audio_event, audio_thread]

def stop_recording(recording_flag, processes):
    """Stops video and audio recording."""
    recording_flag.value = 0

    # Stop the screen recording process
    processes[0].join()  # Video process

    # Trigger the event to stop the audio thread
    processes[1].set()  # Stop audio thread

    # Wait for the audio thread to finish
    processes[2].join()


def combine_video_audio(video_file, audio_file, output_file):
    """Combines video and audio into a single file using FFmpeg."""
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")

    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' does not exist.")
        return
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print(f"Audio file '{audio_file}' does not exist or is empty. Saving video only.")
        shutil.move(video_file, output_file)
        return

    try:
        command = [
            ffmpeg_path,
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"Combined file saved as: {output_file}")
    except Exception as e:
        print(f"Error during combining: {e}")

def save_video(save_path, video_format, combine=False):
    """Saves video and audio separately or combined. Returns True if the operation was successful."""
    temp_video = f"recording.{video_format}"
    temp_audio = OUTPUT_AUDIO

    if not os.path.exists(temp_video):
        print(f"Temporary video file '{temp_video}' does not exist. Recording may have failed.")
        return False

    try:
        if combine:
            combine_video_audio(temp_video, temp_audio, save_path)
        else:
            video_output = save_path.replace(f".{video_format}", f"_video.{video_format}")
            audio_output = save_path.replace(f".{video_format}", "_audio.wav")
            shutil.move(temp_video, video_output)
            if os.path.exists(temp_audio) and os.path.getsize(temp_audio) > 0:
                shutil.move(temp_audio, audio_output)

        # Delete temporary files
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        print("Saving was successful.")
        return True
    except Exception as e:
        print(f"Error during saving files: {e}")
        return False


