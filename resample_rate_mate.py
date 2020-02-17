
import numpy as np
import scipy.io.wavfile as wf
from scipy.signal import resample
import warnings


try:
    # shush any potential- skipping weird meta data warning
    warnings.simplefilter('ignore', category=wf.WavFileWarning)
    sample_rate_old, data = wf.read('/path_to/whateva.wav')

    sample_rate_new = 48000                   # New sample rate
    resample_factor = 1.08843537414966      # 48000 / 44100 = 1.08843537414966

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

except ValueError:

    axis_0 = data.shape
    print('mono')

    # Chop sound file into a list of mono blox of signal.resamplable size.

    blox = int(len(data) // window_size)
    remainder = (len(data) % window_size) > 0

    for i in range(blox):
        data_list.append(data[i * window_size:(i * window_size) + window_size])
    if remainder is True:
        data_list.append(data[blox * window_size:])

    data_resampled = np.empty(shape=[0, ])

# Resample each blox individualy.
for i in data_list:
    new_sample_amount = int(len(i) * resample_factor)

    slice_resampled = resample(i, new_sample_amount)
    data_resampled = np.concatenate((data_resampled, slice_resampled))

data_resampled = np.int16(data_resampled)

wf.write('resampled_whateva.wav', sample_rate_new, data_resampled)
