import numpy as np
import matplotlib.pyplot as plt
import sys

# -----------------------------
# Usage: python3 plot_snapshot.py <datafile>
# -----------------------------
if len(sys.argv) < 2:
    print("Usage: python3 plot_snapshot.py <datafile>")
    sys.exit(1)

filename = sys.argv[1]
Fs = 10000.0  # Hz

# Load the file (space separated columns)
data = np.loadtxt(filename)

# Mean-removed signals (DCCT1, DCCT2)
col2 = data[:, 1] - np.mean(data[:, 1])
col3 = data[:, 2] - np.mean(data[:, 2])

# Stats (after mean removal)
rms2 = np.sqrt(np.mean(col2**2))   # RMS noise
rms3 = np.sqrt(np.mean(col3**2))
sigma2 = np.std(col2)
sigma3 = np.std(col3)

print(f"File: {filename}")
print(f"DCCT1: mean={np.mean(col2):.6f}  RMS={rms2:.6f}  sigma={sigma2:.6f}")
print(f"DCCT2: mean={np.mean(col3):.6f}  RMS={rms3:.6f}  sigma={sigma3:.6f}")

# Time axis (seconds)
N = len(col2)
t = np.arange(N) / Fs

# -----------------------------
# FFT (single-sided amplitude spectrum)
# -----------------------------
def amp_spectrum_db(x, Fs):
    """
    Returns (freq_Hz, mag_db) for single-sided amplitude spectrum.
    Uses rFFT, scales amplitude so a full-scale sine has correct amplitude.
    """
    N = len(x)
    X = np.fft.rfft(x)
    freq = np.fft.rfftfreq(N, d=1.0 / Fs)

    mag = np.abs(X) / N
    if N > 1:
        mag[1:-1] *= 2.0  # single-sided correction (exclude DC and Nyquist)

    mag_db = 20.0 * np.log10(np.maximum(mag, 1e-20))  # avoid log(0)
    return freq, mag_db

f2, db2 = amp_spectrum_db(col2, Fs)
f3, db3 = amp_spectrum_db(col3, Fs)

# -----------------------------
# Histogram bins aligned to integer codes (if data are integer-ish)
# For non-integer noise, this still works fine; adjust step if desired.
# -----------------------------
bins2 = np.arange(np.min(col2) - 0.5, np.max(col2) + 1.5, 1.0)
bins3 = np.arange(np.min(col3) - 0.5, np.max(col3) + 1.5, 1.0)

# -----------------------------
# Plot: 3 rows x 2 cols
# Row 1: time domain
# Row 2: histogram
# Row 3: FFT (dB)
# -----------------------------
fig, ax = plt.subplots(3, 2, figsize=(13, 9), constrained_layout=True)

# Time domain
ax[0, 0].plot(t, col2)
ax[0, 0].set_title(f"zPSC DCCT1 Time Domain (mean removed)  RMS={rms2:.3f}")
ax[0, 0].set_xlabel("Time (s)")
ax[0, 0].set_ylabel("ADC bits (mean removed)")
ax[0, 0].grid(True)

ax[0, 1].plot(t, col3)
ax[0, 1].set_title(f"zPSC DCCT2 Time Domain (mean removed)  RMS={rms3:.3f}")
ax[0, 1].set_xlabel("Time (s)")
ax[0, 1].set_ylabel("ADC bits (mean removed)")
ax[0, 1].grid(True)

# Histogram
ax[1, 0].hist(col2, bins=bins2)
ax[1, 0].set_title("DCCT1 Histogram (mean removed)")
ax[1, 0].set_xlabel("ADC bits (mean removed)")
ax[1, 0].set_ylabel("Counts")
ax[1, 0].grid(True)

ax[1, 1].hist(col3, bins=bins3)
ax[1, 1].set_title("DCCT2 Histogram (mean removed)")
ax[1, 1].set_xlabel("ADC bits (mean removed)")
ax[1, 1].set_ylabel("Counts")
ax[1, 1].grid(True)

# FFT in dB
ax[2, 0].plot(f2, db2)
ax[2, 0].set_title("DCCT1 FFT (Amplitude Spectrum, dBFS-like)")
ax[2, 0].set_xlabel("Frequency (Hz)")
ax[2, 0].set_ylabel("Magnitude (dB)")
ax[2, 0].set_xlim(0, Fs / 2)
ax[2, 0].set_ylim(-80,0)
ax[2, 0].grid(True)

ax[2, 1].plot(f3, db3)
ax[2, 1].set_title("DCCT2 FFT (Amplitude Spectrum, dBFS-like)")
ax[2, 1].set_xlabel("Frequency (Hz)")
ax[2, 1].set_ylabel("Magnitude (dB)")
ax[2, 1].set_xlim(0, Fs / 2)
ax[2, 1].set_ylim(-80,0)
ax[2, 1].grid(True)

plt.suptitle(f"Snapshot Analysis: {filename}", y=1.02)
plt.show()
