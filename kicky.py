import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
import os
import glob
import shutil
import numpy as np
import scipy.io.wavfile as wav
import subprocess
from scipy.fft import fft

reference_frequency = 440.0 * pow(2, -4.75)
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Audio Functions

def trim_audio(data, rate, duration_ms=64):
    num_samples = int(rate * duration_ms / 1000)
    return data[num_samples:]

def fade_audio(data, rate, fade_in_ms=32):
    fade_in_samples = int(rate * fade_in_ms / 1000)
    fade_in_window = np.linspace(0, 1, fade_in_samples)
    data[:fade_in_samples] *= fade_in_window
    return data

def get_highest_fft_peak(data, rate):
    fft_result = fft(data)
    freqs = np.fft.fftfreq(len(data), 1/rate)
    peak_freq = freqs[np.argmax(np.abs(fft_result))]
    return abs(peak_freq)

def frequency_to_note(frequency, reference_note, note_names):

    if frequency == 0:  # Avoid log(0) error
        return "Unknown"
    
    h = 12 * np.log2(frequency / reference_note)
    n = int(round(h)) % 12
    return note_names[n]

def process_directory(input_directory, output_directory):
    for file_path in glob.glob(os.path.join(input_directory, '*.wav')):
        rate, data = wav.read(file_path)
        
        if len(data.shape) == 2:
            data = data.mean(axis=1)
        
        trimmed_data = trim_audio(data, rate)
        faded_data = fade_audio(trimmed_data, rate)
        peak_freq = get_highest_fft_peak(faded_data, rate)
        note = frequency_to_note(peak_freq, reference_frequency, note_names)
        new_file_name = os.path.basename(file_path).replace('.wav', f' ({note}).wav')
        new_file_path = os.path.join(output_directory, new_file_name)
        shutil.copyfile(file_path, new_file_path)
        terminal_output.insert(tk.END, f"Processed {new_file_name}\n")





# GUI Functions

def select_directory():
    dir_path = filedialog.askdirectory()
    if dir_path:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, dir_path)
    else:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, "No directory selected")

def select_output_directory():
    output_dir_path = filedialog.askdirectory()
    if output_dir_path:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, output_dir_path)
    else:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, "No directory selected")

def process():
    input_path = dir_entry.get()
    output_dir = output_dir_entry.get()

    if not input_path or not output_dir or "No directory selected" in [input_path, output_dir]:
        messagebox.showwarning("Warning", "Please select an input file/directory and an output directory.")
        return

    terminal_output.insert(tk.END, "Processing...\n")
    try:
        process_directory(input_path, output_dir)
        terminal_output.insert(tk.END, "Finished\n")
        subprocess.run(['open', output_dir])
    except Exception as e:
        terminal_output.insert(tk.END, f"Error: {e}\n")



# GUI setup
root = tk.Tk()
root.title("Kicky Program")

# Left section for inputs and buttons
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Input Directory selection
dir_frame = tk.Frame(left_frame)
dir_frame.pack(fill=tk.X)
tk.Button(dir_frame, text="Select Source Folder", command=select_directory).pack(side=tk.LEFT)
dir_entry = tk.Entry(dir_frame, width=40)
dir_entry.insert(0, "No directory selected")
dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

# Output directory selection
output_dir_frame = tk.Frame(left_frame)
output_dir_frame.pack(fill=tk.X)
tk.Button(output_dir_frame, text="Select Destination Folder", command=select_output_directory).pack(side=tk.LEFT)
output_dir_entry = tk.Entry(output_dir_frame, width=40)
output_dir_entry.insert(0, "No directory selected")
output_dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

# Process and reset buttons
tk.Button(left_frame, text="Process", command=process).pack(fill=tk.X)

# Right section for terminal output
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
terminal_output = scrolledtext.ScrolledText(right_frame, width=40, height=10)
terminal_output.pack(expand=True, fill=tk.BOTH)

terminal_output.insert(tk.END, f"Thank you for using Kicky!\n")
terminal_output.insert(tk.END, f"This app reads a folder containing .WAV kick samples, and copies & renames the samples to another folder with the key in the filename.\n")
terminal_output.insert(tk.END, f"Select a source folder containing single kick samples, then select a destination folder to output the renamed samples to. Then hit the Process button.\n")

root.mainloop()