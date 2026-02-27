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
    ave_ppm = sigma / fs
    return ave_ppm

    

def plot_all(title,time,brdtemp,dcct1,dcct2,reg):
   fig,axes = plt.subplots(nrows=4,ncols=1)
   fig.suptitle('PSC Long Term Drift', fontsize=14)
   fig.tight_layout()

   sigma_dcct1 = np.std(dcct1) * 1e6  # uA
   ppm_dcct1 = calc_ppm(sigma_dcct1,10)
   ax1=plt.subplot(411)
   plt.plot(time,dcct1,'b')
   plt.ylabel('DCCT 1 (A)')
   plt.xlabel('Hours')
   ax1.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_dcct1, transform=ax1.transAxes,fontsize=10,verticalalignment='top') 
   #ax1.text(0.05, 0.85, 'PPM = %3.1f' % ppm_dcct1, transform=ax1.transAxes,fontsize=10,verticalalignment='top')     
   plt.grid()
   
   sigma_dcct2 = np.std(dcct2) * 1e6  # uA 
   ppm_dcct2 = calc_ppm(sigma_dcct2,10)   
   ax2=plt.subplot(412, sharex=ax1)
   plt.plot(time,dcct2,'b')
   plt.ylabel('DCCT 2 (A)')
   plt.xlabel('Hours')  
   ax2.text(0.05, 0.95, r'$\sigma$ = %3.5f $\mu$A' % sigma_dcct2, transform=ax2.transAxes,fontsize=10,verticalalignment='top')   
   #ax2.text(0.05, 0.85, 'PPM = %3.1f' % ppm_dcct2, transform=ax2.transAxes,fontsize=10,verticalalignment='top')         
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



