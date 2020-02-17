
# resample-rate-mate-python
### Resample or change speed of a .wav file

**Well, it works!**

Now all I got to do is make it user friendly. I think I will do
it tomorrow.

Divide the sample_rate_new rate by the sample_rate_old to get resampling
factor. OR. Make the sample_rate_new = sample_rate_old, then you can change
the play-back speed by some factor **f** by making the resample_factor = **f**.

```
pip3 install scipy
pip3 install numpy
```
...And to run it:

```
python3 resample_rate_mate.py
```
