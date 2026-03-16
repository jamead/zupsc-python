import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal




def read_filedata(fname):
    data = np.loadtxt(fname,dtype=float)
    print(data.ndim)
    print(data.shape)
    print(type(data.ndim))
    return data


def calc_ppm(sigma,fs):
    ppm = sigma / 10 * 1e6
    return ppm

    
    


def plot_all(title, time, brdtemp, dcct1, dcct2, dac):

    FULL_SCALE = 10.0  # amps

    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(12, 6), constrained_layout=True)
    fig.suptitle(' Digital PID zPSC Long Term Drift', fontsize=14)

    # ---- DCCT1 ----
    sigma_dcct1 = np.std(dcct1) * 1e6  # uA
    ppm_dcct1 = sigma_dcct1 / FULL_SCALE

    ax[0].plot(time, dcct1)
    ax[0].set_ylabel('DCCT 1 (A)')
    ax[0].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_dcct1:3.5f} $\mu$A',
               transform=ax[0].transAxes, fontsize=10, va='top')
    ax[0].text(0.05, 0.87,
               f'PPM = {ppm_dcct1:.3f}',
               transform=ax[0].transAxes, fontsize=10, va='top')
    ax[0].grid(True)

    # ---- DCCT2 ----
    sigma_dcct2 = np.std(dcct2) * 1e6  # uA
    ppm_dcct2 = sigma_dcct2 / FULL_SCALE

    ax[1].plot(time, dcct2)
    ax[1].set_ylabel('DCCT 2 (A)')
    ax[1].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_dcct2:3.5f} $\mu$A',
               transform=ax[1].transAxes, fontsize=10, va='top')
    ax[1].text(0.05, 0.87,
               f'PPM = {ppm_dcct2:.3f}',
               transform=ax[1].transAxes, fontsize=10, va='top')
    ax[1].grid(True)

    # ---- Regulator ----
    sigma_dac = np.std(dac) * 1e6  # uA
    ppm_dac = sigma_dac / FULL_SCALE

    ax[2].plot(time, dac)
    ax[2].set_ylabel('DAC (A)')
    ax[2].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_dac:3.5f} $\mu$A',
               transform=ax[2].transAxes, fontsize=10, va='top')
    ax[2].text(0.05, 0.87,
               f'PPM = {ppm_dac:.3f}',
               transform=ax[2].transAxes, fontsize=10, va='top')
    ax[2].grid(True)

    # ---- Board Temp ----
    sigma_brdtemp = np.std(brdtemp)

    ax[3].plot(time, brdtemp)
    ax[3].set_ylabel('Board Temp (F)')
    ax[3].set_xlabel('Hours')
    ax[3].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_brdtemp:3.5f}',
               transform=ax[3].transAxes, fontsize=10, va='top')
    ax[3].grid(True)

    return fig, ax   
    
    

  






def main():

   plt.rcParams['axes.formatter.useoffset'] = False
   
   if len(sys.argv) != 2:
       print ("No input file specified...")
       return 1
   else:
       fname = sys.argv[1];
       data_raw=read_filedata(fname)
     
   data = data_raw[:,:]
   timesec = np.arange(0,len(data[:,0]),1)
   time = timesec * (1/3600)
 

   print ("Number of Samples Collected: %d" % data.shape[0])
   ts = data[:,0]  
   brdtemp = data[:,1]
   dcct1 = data[:,2]
   dcct2 = data[:,3]
   dac = data[:,4]
   reg = data[:,5]
   err = data[:,6]
 


   plot_all("Mag",time,brdtemp,dcct2,dcct1,dac)


  
   plt.show()




if __name__ == "__main__":
    main()



