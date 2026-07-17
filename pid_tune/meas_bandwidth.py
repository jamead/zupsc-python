import cothread
import epics
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

datapts = 100000




def get_waveform(PVs,numpts):
  

  data = []
  for i in range(len(PVs)):
     data.append(PVs[i].get())

  waveform = np.asarray(data, dtype=np.float32)
  waveform = waveform[:,0:numpts] 

  return waveform 


def wait_snapshot(trig_pv,wfmrdy_pv):

  # Trigger the snapshot
  trig_pv.put(1)
  print("Triggering Snapshot...")
  time.sleep(1)
  print("Waiting for Snapshot Data... ")

  
    
  while True:
    val = wfmrdy_pv.get(1)
    #print("Busy=%d" % val)
    time.sleep(1)
    if val == 0:
      break;

  print("Transfer Complete")    
    



def plot_snapshot(snapshot_data, freq, ax=None):
    dac   = snapshot_data[:, 0]
    dcct1 = snapshot_data[:, 1]

    if ax is None:
        fig, ax = plt.subplots(2, 1, sharex=True, figsize=(12, 6))

    label = f"freq={freq}"

    ax[0].plot(dac, label=label)
    ax[0].set_ylabel("DAC")
    ax[0].grid(True)

    ax[1].plot(dcct1, label=label)
    ax[1].set_ylabel("DCCT")
    ax[1].grid(True)

    return ax



def main():
    parser = argparse.ArgumentParser(description="Read Snapshot data from a PSC and save to file.")
    parser.add_argument("psc_prefix", type=str, help="PSC prefix string (e.g., lab{1})")
    parser.add_argument("outfile", type=str, help="Output filename (e.g., psc_snapshot.txt)")
    args = parser.parse_args()

    psc_prefix = args.psc_prefix
    out_filename = args.outfile

    snapshot_pv = [
        epics.PV(psc_prefix+'Chan1:USR:DAC-Wfm'),
        epics.PV(psc_prefix+'Chan1:USR:DCCT1-Wfm'),
        epics.PV(psc_prefix+'Chan1:USR:DCCT2-Wfm'),]
  
    #get PV names
    dds_enb_pv = epics.PV(psc_prefix+'Chan1:DAC-DDS-Enb-SP')
    dds_freq_pv = epics.PV(psc_prefix+'Chan1:DAC-DDS-Freq-SP')
    trig_pv = epics.PV(psc_prefix+'Chan1:SS:Trig:Usr')
    dac_setpt_pv = epics.PV(psc_prefix+'Chan1:DAC_SetPt-SP')
    pid_rst_int_pv = epics.PV(psc_prefix+'Chan1:DPIDResetI-SP')
    kp_pv = epics.PV(psc_prefix+'Chan1:Kp-SP')
    ki_pv = epics.PV(psc_prefix+'Chan1:Ki-SP')
    wfmrdy_pv = epics.PV(psc_prefix+'Chan1:UsrTrigActive-I')
    
    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
    
    ki = 0.01
    kp = 0.5
    
    #initialize dpid (open loop, enable Reset)
    pid_rst_int_pv.put(1)
    kp_pv.put(kp)
    ki_pv.put(ki)
    dac_setpt_pv.put(0)
    
    for freq in np.arange(100, 1000, 100):
      print("Setting DDS Freq to %d" % freq)
      dds_freq_pv.put(freq)
      time.sleep(1);
      wait_snapshot(trig_pv,wfmrdy_pv)
      time.sleep(1);



      # Read waveform
      snapshot_data = get_waveform(snapshot_pv, 100000)
  
      # Fix orientation
      snapshot_data = snapshot_data.T
      snapshot_data = snapshot_data[0:1000, :]
      plot_snapshot(snapshot_data,freq,ax=ax)


    ax[0].legend()
    ax[1].legend()
    ax[1].set_xlabel("Sample")

    plt.tight_layout()
    plt.show()

    dac_setpt_pv.put(0)

    # Save to file
    np.savetxt(out_filename, snapshot_data.T, fmt="%f", delimiter=" ")
    print(f"Saved Snapshot data to {out_filename}")


if __name__ == "__main__":
    main()
