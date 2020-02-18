
import numpy as np
import scipy.io.wavfile as wf
from scipy.signal import resample
import warnings
import tkinter as tk
import sounddevice as sd
import time


def go():
    try:
        # shush any potential- skipping weird meta data warning
        warnings.simplefilter('ignore', category=wf.WavFileWarning)
        sample_rate_old, data = wf.read(input_file_entry.get())

        data_list = []
        window_size = 88200

        # Chop sound file into a list of stereo blox of signal.resamplable size.

        blox = int(len(data[:, 0]) // window_size)
        remainder = (len(data[:, 0]) % window_size) > 0

        for i in range(blox):
            data_list.append(data[i * window_size:(i * window_size) + window_size, :])
        if remainder is True:
            data_list.append(data[blox * window_size:, :])  # Tack on remaining samples
        data_resampled = np.empty(shape=[0, 2])

    except FileNotFoundError:
        print("bollox")
        input_file_entry.delete(0, last='end')
        show_message('FileNotFoundError', 'File name wrong or does not exist')
        return
    except IndexError:

        axis_0 = data.shape  # see if triggers error
        print('mono')

        # Chop sound file into a list of mono blox of signal.resamplable size.

        blox = int(len(data) // window_size)
        remainder = (len(data) % window_size) > 0

        for i in range(blox):
            data_list.append(data[i * window_size:(i * window_size) + window_size])
        if remainder is True:
            data_list.append(data[blox * window_size:])

        data_resampled = np.empty(shape=[0, ])

    try:
        sample_rate_new = int(sample_rate_var.get())           # New sample rate
        resample_factor = sample_rate_new / sample_rate_old     # 48000 / 44100 = 1.08843537414966
        speed_factor = float(speed_factor_entry.get())
        if speed_factor != 0.0:
            if speed_factor < 0.1 or speed_factor > 10.0:
                speed_factor_entry.delete(0, last='end')
                show_message('Speed Factor Value Out Of Bounds',
                             'Speed Change Factor must be betwen 0.1 to 10')
                speed_factor_entry.insert(0, 0.0)
                return
            resample_factor = resample_factor / speed_factor
            print('speed factor ran {}'.format(speed_factor))
    except ValueError:
        speed_factor_entry.delete(0, last='end')
        show_message('ValueError', 'Speed Change Factor must be a number')
        speed_factor_entry.insert(0, 0.0)
        return
    else:
        # Resample each blox individualy.
        for i in data_list:
            new_sample_amount = int(len(i) * resample_factor)

            slice_resampled = resample(i, new_sample_amount)
            data_resampled = np.concatenate((data_resampled, slice_resampled))

        data_resampled = np.int16(data_resampled)

        # wf.write(output_file_entry.get(), sample_rate_new, data_resampled)

        sd.play(data_resampled, sample_rate_new)
        time.sleep(len(data_resampled) / sample_rate_new)
        sd.stop()
        print(output_file_entry.get())  # ../resample-it-baby/nano_sample.wav
        print(sample_rate_new)
        # ../resample-it-baby/fm_wave.wav


def message_win_func(mtitle, blah):
    def closer():
        message_win.destroy()

    global message_win
    message_win = tk.Toplevel(master)
    message_win.title(mtitle)
    label = tk.Label(message_win, text=blah, font='Times 20')
    button = tk.Button(message_win, text='OK', width=6, bg="#728C00", fg="white", command=closer)

    label.pack(padx=30, pady=10)
    button.pack(pady=20)
    message_win.lift()


def show_message(mtitle, blah):
    if message_win is None:
        message_win_func(mtitle, blah)
        return
    try:
        message_win.lift()
    except tk.TclError:
        message_win_func(mtitle, blah)


message_win = None

master = tk.Tk()
master.geometry('600x300')

sample_rate_var = tk.StringVar()

input_file_label = tk.Label(master, text='Input Path To File')
output_file_label = tk.Label(master, text='Name The Ouput File')
input_file_entry = tk.Entry(master)
input_file_entry.focus_set()
output_file_entry = tk.Entry(master)
sample_rate_label = tk.Label(master, text='Select Sample Rate')
speed_factor_label = tk.Label(master, text='Speed Change Factor')
radio_0 = tk.Radiobutton(master, text='44100 Hz', variable=sample_rate_var, value=44100)
radio_1 = tk.Radiobutton(master, text='48000 Hz', variable=sample_rate_var, value=48000)
radio_1.select()

speed_factor_entry = tk.Entry(master)
speed_factor_entry.insert(0, 0.0)
go_button = tk.Button(master, text='GO', bg='green', height=3, width=7, command=go)

input_file_label.grid(column=0, row=0, padx=20)
output_file_label.grid(column=0, row=1, padx=20)
input_file_entry.grid(column=1, row=0)
output_file_entry.grid(column=1, row=1)
sample_rate_label.grid(column=0, row=2, padx=20, pady=10)
radio_0.grid(column=1, row=2)
radio_1.grid(column=1, row=3)
speed_factor_label.grid(column=0, row=4, padx=20, pady=15)
speed_factor_entry.grid(column=1, row=4)
go_button.grid(column=3, row=0, padx=20, pady=10, rowspan=2)

master.mainloop()
