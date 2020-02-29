
import numpy as np
import scipy.io.wavfile as wf
from scipy.signal import resample
import warnings
import tkinter as tk
import time


def go():
    try:
        go_button.config(text='Wait', state='disabled')
        go_button.update()
        if message_win is not None:
            message_win.destroy()
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
        input_file_entry.delete(0, last='end')
        show_message('FileNotFoundError', 'File name wrong or does not exist')
        go_button.update()
        go_button.config(text='GO', state='normal')
        return
    except IndexError:
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
            if speed_factor < 0.1 or speed_factor > 12.0:
                speed_factor_entry.delete(0, last='end')
                show_message('Speed Factor Value Out Of Bounds',
                             'Speed Change Factor must be betwen 0.1 to 12.0')
                speed_factor_entry.insert(0, 0.0)
                return
            resample_factor = resample_factor / speed_factor

    except ValueError:
        speed_factor_entry.delete(0, last='end')
        show_message('ValueError', 'Speed Change Factor must be a number')
        speed_factor_entry.insert(0, 0.0)
        go_button.update()
        go_button.config(text='GO', state='normal')
        return
    else:
        # Resample each blox individualy.
        for i in data_list:
            new_sample_amount = int(len(i) * resample_factor)

            slice_resampled = resample(i, new_sample_amount)
            data_resampled = np.concatenate((data_resampled, slice_resampled))

        data_resampled = np.int16(data_resampled)

        stamp = output_file_entry.get()
        if len(stamp) == 0:
            stamp = "RRM-{}.wav".format(str(time.ctime()[-16:].replace(" ", "-").replace(":", "-")))
        else:
            stamp = "{}.wav".format(stamp)
        wf.write(stamp, sample_rate_new, data_resampled)

        show_message("Done- {}Hz wav".format(sample_rate_new), "File Saved as {}".format(stamp))

        go_button.update()
        go_button.config(text='GO', state='normal')


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
master.geometry('700x310')
master.title("Resample Rate Mate")
master.configure(padx=40, pady=20)

sample_rate_var = tk.StringVar()

input_file_label = tk.Label(master, text='Input /Path/To-File')
output_file_label = tk.Label(master, text='Name The Ouput File')
dot_wav_label = tk.Label(master, text='.wav', bg='white', relief=tk.SUNKEN)
input_file_entry = tk.Entry(master, width=24)
input_file_entry.focus_set()
output_file_entry = tk.Entry(master)
sample_rate_label = tk.Label(master, text='Select Sample Rate')
speed_factor_label = tk.Label(master, text='Speed Change Factor')
radio_0 = tk.Radiobutton(master, text='44100 Hz', variable=sample_rate_var,
                         value=44100, font='Times 15', relief=tk.RAISED, padx=10)
radio_1 = tk.Radiobutton(master, text='48000 Hz', variable=sample_rate_var,
                         value=48000, font='Times 15', relief=tk.RAISED, padx=10)
radio_1.select()

speed_factor_entry = tk.Entry(master, font=("Helvetica", 13))
speed_factor_entry.insert(0, 0.0)
go_button = tk.Button(master, text='GO', bg='#0ba4a4',
                      activebackground='#17fbfb', height=3, width=7, command=go)
master.bind('<Down>', lambda event=None: output_file_entry.focus_set())
master.bind('<Up>', lambda event=None: input_file_entry.focus_set())


input_file_label.grid(column=0, row=0, padx=30, sticky='se')
output_file_label.grid(column=0, row=1, pady=20, padx=20, sticky='e')
dot_wav_label.grid(column=2, row=1, sticky='w')
input_file_entry.grid(column=1, row=0, columnspan=2)
output_file_entry.grid(column=1, row=1)
sample_rate_label.grid(column=0, row=2, pady=10)
radio_0.grid(column=1, row=2)
radio_1.grid(column=1, row=3)
speed_factor_label.grid(column=0, row=4, pady=30, sticky='s')
speed_factor_entry.grid(column=1, row=4)
go_button.grid(column=3, row=0, padx=20, rowspan=2, sticky='n')

master.mainloop()
