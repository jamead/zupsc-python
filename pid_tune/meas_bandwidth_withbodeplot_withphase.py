import cothread
import epics
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

DATAPTS = 100000
SAMPLE_RATE_HZ = 100000.0


def get_waveform(pvs, numpts):
    data = []

    for pv in pvs:
        waveform = pv.get()

        if waveform is None:
            raise RuntimeError(f"Failed to read waveform PV: {pv.pvname}")

        data.append(waveform)

    waveform = np.asarray(data, dtype=np.float64)

    if waveform.shape[1] < numpts:
        raise RuntimeError(
            f"Expected {numpts} waveform points, "
            f"but received only {waveform.shape[1]}"
        )

    return waveform[:, :numpts]


def wait_snapshot(trig_pv, wfmrdy_pv):
    trig_pv.put(1)
    print("Triggering Snapshot...")
    time.sleep(1)

    print("Waiting for Snapshot Data...")

    while True:
        val = wfmrdy_pv.get()

        if val is None:
            raise RuntimeError(
                f"Failed to read snapshot status PV: {wfmrdy_pv.pvname}"
            )

        if val == 0:
            break

        time.sleep(0.25)

    print("Transfer Complete")


def fit_sine(waveform, frequency_hz, sample_rate_hz):
    """
    Fit the waveform to:

        y(t) = B*sin(2*pi*f*t) + C*cos(2*pi*f*t) + offset

    Returns:
        amplitude
        phase in radians
        DC offset
    """
    waveform = np.asarray(waveform, dtype=np.float64)

    t = np.arange(len(waveform), dtype=np.float64) / sample_rate_hz
    omega_t = 2.0 * np.pi * frequency_hz * t

    fit_matrix = np.column_stack(
        (
            np.sin(omega_t),
            np.cos(omega_t),
            np.ones_like(omega_t),
        )
    )

    coefficients, _, _, _ = np.linalg.lstsq(
        fit_matrix,
        waveform,
        rcond=None
    )

    sin_coefficient = coefficients[0]
    cos_coefficient = coefficients[1]
    offset = coefficients[2]

    amplitude = np.hypot(
        sin_coefficient,
        cos_coefficient
    )

    phase_rad = np.arctan2(
        cos_coefficient,
        sin_coefficient
    )

    return amplitude, phase_rad, offset


def plot_snapshot(snapshot_data, freq, ax):
    dac = snapshot_data[:, 0]
    dcct1 = snapshot_data[:, 1]
    dcct2 = snapshot_data[:, 2]

    label = f"{freq:g} Hz"

    ax[0].plot(dac, label=label)
    ax[0].set_ylabel("DAC")
    ax[0].grid(True)

    ax[1].plot(dcct1, label=label)
    ax[1].set_ylabel("DCCT1")
    ax[1].grid(True)

    ax[2].plot(dcct2, label=label)
    ax[2].set_ylabel("DCCT2")
    ax[2].grid(True)


def main():
    parser = argparse.ArgumentParser(
        description="Measure the frequency response of a PSC power supply."
    )

    parser.add_argument(
        "psc_prefix",
        type=str,
        help="PSC prefix string, for example lab{1}"
    )

    parser.add_argument(
        "outfile",
        type=str,
        help="Output filename, for example psc_frequency_response.txt"
    )

    args = parser.parse_args()

    psc_prefix = args.psc_prefix
    out_filename = args.outfile

    snapshot_pv = [
        epics.PV(psc_prefix + "Chan1:USR:DAC-Wfm"),
        epics.PV(psc_prefix + "Chan1:USR:DCCT1-Wfm"),
        epics.PV(psc_prefix + "Chan1:USR:DCCT2-Wfm"),
    ]

    dds_enb_pv = epics.PV(
        psc_prefix + "Chan1:DAC-DDS-Enb-SP"
    )

    dds_freq_pv = epics.PV(
        psc_prefix + "Chan1:DAC-DDS-Freq-SP"
    )

    trig_pv = epics.PV(
        psc_prefix + "Chan1:SS:Trig:Usr"
    )

    dac_setpt_pv = epics.PV(
        psc_prefix + "Chan1:DAC_SetPt-SP"
    )

    pid_rst_int_pv = epics.PV(
        psc_prefix + "Chan1:DPIDResetI-SP"
    )

    kp_pv = epics.PV(
        psc_prefix + "Chan1:Kp-SP"
    )

    ki_pv = epics.PV(
        psc_prefix + "Chan1:Ki-SP"
    )

    wfmrdy_pv = epics.PV(
        psc_prefix + "Chan1:UsrTrigActive-I"
    )

    ki = 0.01
    kp = 0.5

    # Initialize DPID/open-loop test configuration
    pid_rst_int_pv.put(1)
    kp_pv.put(kp)
    ki_pv.put(ki)
    dac_setpt_pv.put(0)
    dds_enb_pv.put(1)

    frequencies_to_test = np.concatenate(
        (
            np.arange(1.0, 20.0, 1.0),
            np.arange(20.0, 50.0, 2.0),
            np.arange(50.0, 100.0, 5.0),
            np.arange(100.0, 500.0, 10.0),
        )
    )

    frequencies = []

    dac_amplitudes = []
    dcct1_amplitudes = []
    dcct2_amplitudes = []

    gain_values = []
    gain_db_values = []
    phase_values_rad = []

    fig_waveforms, waveform_ax = plt.subplots(
        3,
        1,
        sharex=True,
        figsize=(12, 8)
    )

    try:
        for freq in frequencies_to_test:
            print(f"\nSetting DDS frequency to {freq:g} Hz")

            dds_freq_pv.put(freq)

            # Allow more settling time at low frequencies.
            settling_time = max(1.0, 3.0 / freq)
            print(f"Waiting {settling_time:.2f} seconds to settle...")
            time.sleep(settling_time)

            wait_snapshot(
                trig_pv,
                wfmrdy_pv
            )

            snapshot_data = get_waveform(
                snapshot_pv,
                DATAPTS
            ).T

            dac = snapshot_data[:, 0]
            dcct1 = snapshot_data[:, 1]
            dcct2 = snapshot_data[:, 2]

            dac_amplitude, dac_phase, dac_offset = fit_sine(
                dac,
                freq,
                SAMPLE_RATE_HZ
            )

            dcct1_amplitude, dcct1_phase, dcct1_offset = fit_sine(
                dcct1,
                freq,
                SAMPLE_RATE_HZ
            )

            dcct2_amplitude, dcct2_phase, dcct2_offset = fit_sine(
                dcct2,
                freq,
                SAMPLE_RATE_HZ
            )

            if dac_amplitude <= 0:
                gain = np.nan
                gain_db = np.nan
                phase_difference_rad = np.nan

                print("Warning: DAC fitted amplitude is zero.")
            else:
                # Power-supply transfer function:
                # output DCCT2 divided by input DAC
                gain = dcct2_amplitude / dac_amplitude

                if gain > 0:
                    gain_db = 20.0 * np.log10(gain)
                else:
                    gain_db = np.nan

                # Output phase relative to the DAC input
                phase_difference_rad = dcct2_phase - dac_phase

                # Initially wrap to -pi through +pi
                phase_difference_rad = np.angle(
                    np.exp(1j * phase_difference_rad)
                )

            frequencies.append(freq)

            dac_amplitudes.append(dac_amplitude)
            dcct1_amplitudes.append(dcct1_amplitude)
            dcct2_amplitudes.append(dcct2_amplitude)

            gain_values.append(gain)
            gain_db_values.append(gain_db)
            phase_values_rad.append(phase_difference_rad)

            print(f"DAC amplitude:    {dac_amplitude:.8f}")
            print(f"DCCT1 amplitude:  {dcct1_amplitude:.8f}")
            print(f"DCCT2 amplitude:  {dcct2_amplitude:.8f}")
            print(f"DCCT2/DAC gain:   {gain:.8f}")
            print(f"Gain:             {gain_db:.3f} dB")
            print(
                f"Phase:            "
                f"{np.degrees(phase_difference_rad):.3f} degrees"
            )

            plot_snapshot(
                snapshot_data,
                freq,
                waveform_ax
            )

    finally:
        dac_setpt_pv.put(0)
        dds_enb_pv.put(0)

    frequencies_array = np.asarray(
        frequencies,
        dtype=np.float64
    )

    gain_array = np.asarray(
        gain_values,
        dtype=np.float64
    )

    gain_db_array = np.asarray(
        gain_db_values,
        dtype=np.float64
    )

    phase_array_rad = np.asarray(
        phase_values_rad,
        dtype=np.float64
    )

    # Remove artificial +/-180-degree phase jumps
    phase_array_deg = np.degrees(
        np.unwrap(phase_array_rad)
    )

    valid_gain = (
        np.isfinite(frequencies_array)
        & np.isfinite(gain_array)
        & (frequencies_array > 0)
    )

    valid_bode = (
        np.isfinite(frequencies_array)
        & np.isfinite(gain_db_array)
        & np.isfinite(phase_array_deg)
        & (frequencies_array > 0)
    )

    # Finish waveform plots
    waveform_ax[0].set_title("PSC Snapshot Waveforms")
    waveform_ax[2].set_xlabel("Sample")

    # There are many frequencies, so a legend may become very crowded.
    waveform_ax[0].legend(fontsize=6, ncol=4)
    waveform_ax[1].legend(fontsize=6, ncol=4)
    waveform_ax[2].legend(fontsize=6, ncol=4)

    fig_waveforms.tight_layout()

    # Linear gain plot
    fig_gain, gain_ax = plt.subplots(
        figsize=(10, 6)
    )

    gain_ax.plot(
        frequencies_array[valid_gain],
        gain_array[valid_gain],
        marker="o"
    )

    gain_ax.set_title(
        "Power Supply Frequency Response"
    )

    gain_ax.set_xlabel(
        "DDS Frequency (Hz)"
    )

    gain_ax.set_ylabel(
        "Gain: DCCT2 Amplitude / DAC Amplitude"
    )

    gain_ax.grid(True)
    fig_gain.tight_layout()

    # Bode magnitude and phase
    fig_bode, bode_ax = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(10, 8)
    )

    bode_ax[0].semilogx(
        frequencies_array[valid_bode],
        gain_db_array[valid_bode],
        marker="o"
    )

    bode_ax[0].set_title(
        "Power Supply Bode Plot"
    )

    bode_ax[0].set_ylabel(
        "Magnitude (dB)"
    )

    bode_ax[0].grid(
        True,
        which="both"
    )

    bode_ax[1].semilogx(
        frequencies_array[valid_bode],
        phase_array_deg[valid_bode],
        marker="o"
    )

    bode_ax[1].set_xlabel(
        "Frequency (Hz)"
    )

    bode_ax[1].set_ylabel(
        "Phase (degrees)"
    )

    bode_ax[1].grid(
        True,
        which="both"
    )

    fig_bode.tight_layout()

    response_data = np.column_stack(
        (
            frequencies_array,
            np.asarray(dac_amplitudes),
            np.asarray(dcct1_amplitudes),
            np.asarray(dcct2_amplitudes),
            gain_array,
            gain_db_array,
            phase_array_deg,
        )
    )

    header = (
        "Frequency_Hz "
        "DAC_Amplitude "
        "DCCT1_Amplitude "
        "DCCT2_Amplitude "
        "DCCT2_div_DAC "
        "Gain_dB "
        "Phase_Deg"
    )

    np.savetxt(
        out_filename,
        response_data,
        fmt="%.8f",
        delimiter=" ",
        header=header
    )

    print(
        f"\nSaved frequency-response data to "
        f"{out_filename}"
    )

    plt.show()


if __name__ == "__main__":
    main()
