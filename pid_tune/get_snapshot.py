import cothread
import epics
import numpy as np
import time
import argparse

datapts = 100000




def get_waveform(PVs,numpts):
  

  data = []
  for i in range(len(PVs)):
     data.append(PVs[i].get())

  waveform = np.asarray(data, dtype=np.float32)
  waveform = waveform[:,0:numpts] 

  return waveform 




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
        epics.PV(psc_prefix+'Chan1:USR:DCCT2-Wfm'),
]
  

    trig_pv = epics.PV(psc_prefix+'Chan1:SS:Trig:Usr')

    # Trigger the snapshot
    trig_pv.put(1)
    print("Triggering Snapshot...")
    time.sleep(1)
    print("Waiting for Snapshot Data... ")

    wfmrdy_pv = epics.PV(psc_prefix+'Chan1:UsrTrigActive-I')
    
    while True:
        val = wfmrdy_pv.get(1)
        print("Busy=%d" % val)
        time.sleep(1)
        if val == 0:
            break;

    print("Transfer Complete")    
    
    
    time.sleep(1)

    # Read waveform
    snapshot_data = get_waveform(snapshot_pv, 100000)
    print(type(snapshot_data))
    rows, cols = snapshot_data.shape
    print(f"Number of rows: {rows}")
    print(f"Number of columns: {cols}")

    # Save to file
    np.savetxt(out_filename, snapshot_data.T, fmt="%f", delimiter=" ")
    print(f"Saved Snapshot data to {out_filename}")


if __name__ == "__main__":
    main()
