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

    
    


def plot_all(title, time, brdtemp, dcct1, dcct2, reg):

    FULL_SCALE = 10.0  # amps

    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(12, 6), constrained_layout=True)
    fig.suptitle('Analog PID zPSC Long Term Drift', fontsize=14)

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
    sigma_reg = np.std(reg) * 1e6  # uA
    ppm_reg = sigma_reg / FULL_SCALE

    ax[2].plot(time, reg)
    ax[2].set_ylabel('Regulator (A)')
    ax[2].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_reg:3.5f} $\mu$A',
               transform=ax[2].transAxes, fontsize=10, va='top')
    ax[2].text(0.05, 0.87,
               f'PPM = {ppm_reg:.3f}',
               transform=ax[2].transAxes, fontsize=10, va='top')
    ax[2].grid(True)

    # ---- Board Temp ----
    sigma_brdtemp = np.std(brdtemp)

    ax[3].plot(time, brdtemp)
    ax[3].set_ylabel('Board Temp (C)')
    ax[3].set_xlabel('Hours')
    ax[3].text(0.05, 0.95,
               rf'$\sigma$ = {sigma_brdtemp:3.5f}',
               transform=ax[3].transAxes, fontsize=10, va='top')
    ax[3].grid(True)

    return fig, ax   
    
    

def plot_all_old1(title, time, brdtemp, dcct1, dcct2, reg):
    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(12, 6), constrained_layout=True)
    fig.suptitle('PSC Long Term Drift', fontsize=14)

    sigma_dcct1 = np.std(dcct1) * 1e6  # uA
    ax[0].plot(time, dcct1)
    ax[0].set_ylabel('DCCT 1 (A)')
    ax[0].text(0.05, 0.95, rf'$\sigma$ = {sigma_dcct1:3.5f} $\mu$A',
               transform=ax[0].transAxes, fontsize=10, va='top')
    ax[0].grid(True)

    sigma_dcct2 = np.std(dcct2) * 1e6  # uA
    ax[1].plot(time, dcct2)
    ax[1].set_ylabel('DCCT 2 (A)')
    ax[1].text(0.05, 0.95, rf'$\sigma$ = {sigma_dcct2:3.5f} $\mu$A',
               transform=ax[1].transAxes, fontsize=10, va='top')
    ax[1].grid(True)

    sigma_reg = np.std(reg) * 1e6  # uA
    ax[2].plot(time, reg)
    ax[2].set_ylabel('Regulator (A)')
    ax[2].text(0.05, 0.95, rf'$\sigma$ = {sigma_reg:3.5f} $\mu$A',
               transform=ax[2].transAxes, fontsize=10, va='top')
    ax[2].grid(True)

    sigma_brdtemp = np.std(brdtemp)
    ax[3].plot(time, brdtemp)
    ax[3].set_ylabel('Board Temp (C)')
    ax[3].set_xlabel('Hours')
    ax[3].text(0.05, 0.95, rf'$\sigma$ = {sigma_brdtemp:3.5f}',
               transform=ax[3].transAxes, fontsize=10, va='top')
    ax[3].grid(True)

    return fig, ax    
    
    

def plot_all_old(title,time,brdtemp,dcct1,dcct2,reg):
   fig,axes = plt.subplots(nrows=4,ncols=1)
   fig.suptitle('Analog PID zPSC Long Term Drift', fontsize=14)
   fig.tight_layout()

   sigma_dcct1 = np.std(dcct1) * 1e6  # uA
   ppm_dcct1 = calc_ppm(sigma_dcct1,10)
   ax1=plt.subplot(411)
   plt.plot(time,dcct1,'b')
   plt.ylabel('DCCT 1 (A)')
   plt.xlabel('Hours')
   ax1.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_dcct1, transform=ax1.transAxes,fontsize=10,verticalalignment='top') 
   ax1.text(0.05, 0.85, 'PPM = %3.1f' % ppm_dcct1, transform=ax1.transAxes,fontsize=10,verticalalignment='top')     
   plt.grid()
   
   sigma_dcct2 = np.std(dcct2) * 1e6  # uA 
   ppm_dcct2 = calc_ppm(sigma_dcct2,10)   
   ax2=plt.subplot(412, sharex=ax1)
   plt.plot(time,dcct2,'b')
   plt.ylabel('DCCT 2 (A)')
   plt.xlabel('Hours')  
   ax2.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_dcct2, transform=ax2.transAxes,fontsize=10,verticalalignment='top')   
   ax2.text(0.05, 0.85, 'PPM = %3.1f' % ppm_dcct2, transform=ax2.transAxes,fontsize=10,verticalalignment='top')         
   plt.grid()
   
   sigma_reg = np.std(reg) * 1e6
   ax8=plt.subplot(413, sharex=ax1)
   plt.plot(time,reg,'b')
   plt.ylabel('Regulator (A)')
   plt.xlabel('Hours')  
   ax8.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_reg, transform=ax8.transAxes,fontsize=10,verticalalignment='top')     
   plt.grid() 
 
   sigma_brdtemp = np.std(brdtemp)
   ax3=plt.subplot(414, sharex=ax1)
   plt.plot(time,brdtemp,'b')
   plt.ylabel('Board Temp (C)')
   plt.xlabel('Hours')  
   ax3.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_brdtemp, transform=ax3.transAxes,fontsize=10,verticalalignment='top')     
   plt.grid() 
 
 
   
  


def plot_xy(time,x,y):
   print("Xsigma = %2.5f     Ysigma = %2.5f" % (np.std(x),np.std(y)))
   fig,axes = plt.subplots(nrows=2,ncols=1)
   fig.tight_layout()
   ax1=plt.subplot(211)
   plt.plot(time,x,'b')
   plt.ylabel('XPos (um)')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(x)),fontsize=10)
   plt.grid()
   ax2=plt.subplot(212, sharex=ax1)
   plt.plot(time,y,'b')
   plt.ylabel('YPos (um)')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(y)),fontsize=10)
   plt.xlabel('Time (hours)')
   plt.grid()




def plot_xy_wtemps(x,y,tempa,tempb,i):
   print("Xsigma = %2.5f     Ysigma = %2.5f" % (np.std(x),np.std(y)))
   fig,axes = plt.subplots(nrows=4,ncols=1)
   fig.tight_layout()
   ax1=plt.subplot(411)
   plt.plot(x,'b')
   plt.ylabel('XPos (um)')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(x)),fontsize=10)
   plt.grid()
   ax2=plt.subplot(412, sharex=ax1)
   plt.plot(y,'b')
   plt.ylabel('YPos (um)')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(y)),fontsize=10)
   plt.grid()
   ax3=plt.subplot(413, sharex=ax1)
   plt.plot(tempa,'b')
   plt.plot(tempb,'g') 
   plt.ylabel('RF ChA Temp')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(tempa)),fontsize=10)
   plt.grid()
   ax4=plt.subplot(414, sharex=ax1)
   plt.plot(i,'b')
   plt.ylabel('Beam Current (mA)')
   plt.title(r'$\sigma$' + ' = %2.5f' % (np.std(i)),fontsize=10)
   plt.grid()





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
 


   plot_all("Mag",time,brdtemp,dcct1,dcct2,reg)


  
   plt.show()




if __name__ == "__main__":
    main()



