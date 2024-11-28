# Screen and Sound Recorder

## Overview
This project is a GUI-based screen and sound recorder implemented using Python. The application allows users to record their screen and audio simultaneously, save the recordings in various formats, and combine the video and audio into a single file using FFmpeg.

---

## Features

1. **Screen Recording**
   - Captures the screen and saves it as a video file in the chosen format.
   - Supported formats: `AVI`, `MP4`, `MKV`.

2. **Audio Recording**
   - Records audio from the first available microphone and saves it as a `.wav` file.

3. **Countdown Timer**
   - Displays a countdown before starting the video recording.

4. **GUI Features**
   - User-friendly interface built with `tkinter`.
   - Allows selection of video formats using radio buttons.

5. **Integration with FFmpeg**
   - Combines video and audio into a single file.
   - Handles cases where audio is missing by saving only the video.

6. **File Management**
   - Temporary files are cleaned up after saving the final recording.

---

## Requirements

### Python Packages
Install the following dependencies using `pip`:
- `pyaudio`
- `wave`
- `opencv-python`
- `numpy`
- `pyautogui`

### Additional Dependencies
- **FFmpeg**: Ensure that FFmpeg is installed and available at the specified path in the script.
- **OpenH264 DLL**: Ensure the `openh264-1.8.0-win64.dll` file is present in the `cv2` library directory.

---

## How to Run

1. Clone or download the repository.
2. Install the required dependencies listed above.
3. Execute the following command to run the GUI:
   ```bash
   python recorder_gui.py
   ```
4. Use the GUI to:
   - Select a video format.
   - Start recording with the "Start Recording" button.
   - Stop recording and save using the "Stop Recording" button.

---

## Building an Executable

To create a standalone `.exe` file:

1. Install `pyinstaller`:
   ```bash
   pip install pyinstaller
   ```

2. Run the following command to build the executable:
   ```bash
   pyinstaller --onefile --noconsole \
       --add-data ".venv\Lib\site-packages\cv2\openh264-1.8.0-win64.dll;cv2" \
       --add-data "ffmpeg;ffmpeg" \
       --icon=my_icon.ico \
       recorder_gui.py
   ```
3. The generated `.exe` file will be located in the `dist` directory.

---

## File Structure

- **`recorder_gui.py`**: Main GUI application.
- **`recorder.py`**: Core logic for audio and video recording.
- **FFmpeg Binary**: Located under `ffmpeg/bin/ffmpeg.exe`.

---

## Usage Instructions

1. **Start Recording**:
   - Select the desired video format.
   - Click "Start Recording" to begin audio recording immediately.
   - The video recording starts after a 3-second countdown.

2. **Stop Recording**:
   - Click "Stop Recording" to end both audio and video recording.
   - Save the recording to your desired location and format.

3. **Combine Video and Audio**:
   - The application uses FFmpeg to merge the recorded audio and video files into a single file.

4. **Error Handling**:
   - If audio recording fails, the application saves only the video.
   - Temporary files are cleaned up automatically.

---

## Known Issues

- Ensure that FFmpeg and OpenH264 DLL files are correctly configured.
- On some systems, microphone permissions may need to be granted explicitly.

---

## License
This project is licensed under the MIT License. Feel free to modify and distribute it as needed.

