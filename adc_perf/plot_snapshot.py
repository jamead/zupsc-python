import numpy as np
import matplotlib.pyplot as plt
import sys


# Check that a filename was provided
if len(sys.argv) < 2:
    print("Usage: python3 plot_snapshot.py <datafile>")
    sys.exit(1)

filename = sys.argv[1]

# Load the file
data = np.loadtxt(filename)

# Split columns
col1 = (data[:,0] - np.mean(data[:,0])) 
col2 = (data[:,1] - np.mean(data[:,1])) 
col3 = (data[:,2] - np.mean(data[:,2])) 

# Sample index for time axis (replace with real time if you know Fs)
n = np.arange(len(col2))


# ---- RMS calculations ----
rms2 = np.std(col2) 
rms3 = np.std(col3)
print(f"DCCT1 mean: {np.mean(col2):.3f}  RMS noise: {rms2:.3f} ")
print(f"DCCT2 mean: {np.mean(col3):.3f}  RMS noise: {rms3:.3f} ")


# ---- Plot: time domain + histograms ----
fig, ax = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)

# Time domain DCCT1
ax[0, 0].plot(col2[0:10000])
ax[0, 0].set_title(f"zPSC DCCT1  RMS={rms2:.3f}")
ax[0, 0].set_xlabel("Sample #")
ax[0, 0].set_ylabel("ADC bits")
ax[0, 0].grid(True)

# Time domain DCCT2
ax[0, 1].plot(col3[0:10000])
ax[0, 1].set_title(f"zPSC DCCT2   RMS={rms3:.3f}")
ax[0, 1].set_xlabel("Sample #")
ax[0, 1].set_ylabel("ADC bits")
ax[0, 1].grid(True)

# Histogram DCCT1 (integer-aligned bins)
bins2 = np.arange(np.min(col2) - 0.5, np.max(col2) + 1.5, 1)
ax[1, 0].hist(col2, bins=bins2)
ax[1, 0].set_title("zPSC DCCT1 Histogram")
ax[1, 0].set_xlabel("ADC bits (mean removed)")
ax[1, 0].set_ylabel("Counts")
ax[1, 0].grid(True)

# Histogram DCCT2 (integer-aligned bins)
bins3 = np.arange(np.min(col3) - 0.5, np.max(col3) + 1.5, 1)
ax[1, 1].hist(col3, bins=bins3)
ax[1, 1].set_title("zPSC DCCT2 Histogram")
ax[1, 1].set_xlabel("ADC bits (mean removed)")
ax[1, 1].set_ylabel("Counts")
ax[1, 1].grid(True)


plt.show()







# Plot histograms
#plt.figure(figsize=(10,6))



#bins = np.arange(np.min(col2), np.max(col2)+2)
#plt.subplot(2,1,1)
#plt.hist(col2, bins=bins)
#plt.title(f"zPSC DCCT1 ADC (input grounded) RMS={rms2:.3f}")
#plt.xlabel("ADC bits")
#plt.grid()

#bins = np.arange(np.min(col3), np.max(col3)+2)
#plt.subplot(2,1,2)
#plt.hist(col3, bins=bins)
#plt.title(f"zPSC DCCT2 ADC (input grounded) RMS={rms3:.3f}")
##plt.xlabel("ADC bits")
#plt.grid()

#plt.tight_layout()
#plt.show()
