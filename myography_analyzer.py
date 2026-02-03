#!/usr/bin/env python3
"""
Wire Myography Analyzer v3.1
==============================

Analyzes intestinal smooth muscle contractility from LabChart text exports.

This tool detects contractions and calculates comprehensive metrics including
amplitude, frequency, kinetics, duty cycle, and tonic contraction properties.

Author: Geoanna Bautista, Immature Gut Biology Lab, UC Davis
Date: February 2026

Usage
-----
python3 myography_analyzer.py PROJECT_FOLDER [PEAK_HEIGHT]
python3 myography_analyzer.py INPUT_FOLDER OUTPUT_FOLDER [PEAK_HEIGHT]

Examples
--------
python3 myography_analyzer.py ../Projects/Piezo1_Adult
python3 myography_analyzer.py ../Projects/Piezo1_Adult 0.05
python3 myography_analyzer.py ./1_RawData ./3_Results 0.10

Parameters
----------
INPUT_FOLDER : str
    Path to folder containing LabChart .txt export files
OUTPUT_FOLDER : str
    Path where results (Excel, plots) will be saved
PEAK_HEIGHT : float, optional
    Minimum peak height in mN (default: 0.05)
    Recommended values:
    - 0.03 mN: Very sensitive (neonatal/weak contractions)
    - 0.05 mN: Recommended default (drug-treated tissue)
    - 0.08 mN: Standard (strong adult baseline contractions)
    - 0.10 mN: Less sensitive (noisy data)

Output
------
Excel file with two sheets:
1. Overall_Metrics: Summary statistics from first 150s of each recording
2. 10sec_Bins: Time-binned analysis (10s bins) from first 150s

Validation plots showing detected contractions for quality control.

Notes
-----
- Analysis uses the FIRST 150 seconds of each recording for standardization
  and to avoid contractile rundown artifacts.
- All parameters are FIXED across files for reproducible cross-condition
  comparisons. The same thresholds apply whether the file is baseline,
  drug-treated, WT, or KO.
- Files with mean amplitude below FLAG_AMPLITUDE_THRESHOLD are flagged
  for manual review but NOT excluded from analysis.

Version History
---------------
v3.1 - Added project-folder mode (single argument with auto-detect).
       Fixed critical kinetics bugs: relaxation time was inflated 5.3x,
       rise time inflated 32% due to array indexing errors.
       Added Time_to_Peak, Time_from_Peak, Rise_Fall_Ratio metrics.
       Changed PEAK_WIDTH from 0.6 sec to 0.3 sec to capture faster contractions.
v3.0 - Restored simple fixed-parameter detection for reproducibility.
       Fixed binned metrics peak index bug.
       Added amplitude flagging system.
       Improved validation plots with actual threshold display.
       User-configurable parameter block.
v2.9 - Added duty cycle, tonic detection, normalized metrics.
v2.8 - Added contraction kinetics (rise/relax times).
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import warnings
import shutil
from datetime import datetime

warnings.filterwarnings('ignore')

# =============================================================================
# USER-CONFIGURABLE PARAMETERS
# =============================================================================
# Adjust these for your tissue type. All values apply uniformly to every file.
#
# PEAK_HEIGHT: Minimum peak height above baseline (mN).
#   - This is the absolute floor. Anything below this is not counted.
#   - Lower = more sensitive (catches small contractions, risks noise).
#   - Higher = more selective (misses small contractions, rejects noise).
#   - Can also be set via command line argument (overrides this value).
#
# PEAK_PROMINENCE: Minimum local prominence of each peak (mN).
#   - How much a peak must stand out from its immediate surroundings.
#   - Helps reject peaks on slowly drifting baselines.
#   - Usually set equal to or slightly below PEAK_HEIGHT.
#
# PEAK_DISTANCE: Minimum distance between peaks in samples.
#   - At 250 Hz: 250 samples = 1.0 second.
#   - Prevents double-counting a single contraction.
#   - Intestinal contractions rarely occur faster than 1/sec.
#
# PEAK_WIDTH: Minimum width of a peak in samples.
#   - At 250 Hz: 150 samples = 0.6 seconds.
#   - THIS IS THE PRIMARY NOISE FILTER. Electrical noise spikes are
#     narrow (< 0.1 sec). Real contractions are wide (0.5-3.0 sec).
#   - Increase if you see noise being counted. Decrease for very fast
#     contractions (unlikely in intestinal smooth muscle).
#
# SAMPLING_RATE: Your LabChart acquisition rate in Hz.
#   - Standard is 250 Hz. Change ONLY if your setup differs.
#   - If you change this, PEAK_DISTANCE and PEAK_WIDTH (which are in
#     samples) will automatically scale correctly.
#
# TIME_WINDOW: Seconds of recording to analyze (from start).
#   - Default 150s. All files are trimmed to this for fair comparison.
#   - Avoids contractile rundown that occurs in longer recordings.
#
# BIN_DURATION: Size of time bins for temporal analysis (seconds).
#   - Default 10s. Creates the 10sec_Bins sheet in Excel output.
#
# FLAG_AMPLITUDE_THRESHOLD: Amplitude below which files get flagged (mN).
#   - Files are NOT excluded, just flagged for manual review.
#   - Helps catch traces where noise may have been counted as contractions.
# =============================================================================

PEAK_HEIGHT = 0.05           # mN - Minimum peak height above baseline
PEAK_PROMINENCE = 0.05       # mN - Minimum local peak prominence
PEAK_DISTANCE = 250          # samples (1.0 sec at 250 Hz)
PEAK_WIDTH = 75              # samples (0.3 sec at 250 Hz)
SAMPLING_RATE = 250          # Hz - LabChart sampling rate
TIME_WINDOW = 150            # seconds - Analysis window
BIN_DURATION = 10            # seconds - Bin size for temporal analysis
FLAG_AMPLITUDE_THRESHOLD = 0.03  # mN - Flag files with mean amp below this

# =============================================================================
# END OF USER-CONFIGURABLE PARAMETERS
# =============================================================================


def load_labchart_file(filepath):
    """
    Load a LabChart text export file.

    Attempts multiple parsing strategies to handle various LabChart export
    formats (tab-delimited, comma-delimited, varying header rows).

    Parameters
    ----------
    filepath : str or Path
        Path to LabChart .txt file

    Returns
    -------
    time : ndarray
        Time values in seconds
    force : ndarray
        Force values in mN

    Raises
    ------
    ValueError
        If file cannot be parsed
    """
    filepath = Path(filepath)

    # Try different delimiters and skip options (LabChart exports vary)
    for skiprows in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        for delimiter in ['\t', ',', ' ']:
            try:
                data = np.loadtxt(filepath, delimiter=delimiter, skiprows=skiprows)
                if data.ndim == 2 and data.shape[1] >= 2:
                    time = data[:, 0]
                    force = data[:, 1]

                    # Sanity checks
                    if len(time) > 100 and np.all(np.diff(time) > 0):
                        return time, force
            except:
                continue

    # If standard loading failed, try pandas
    try:
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=10)
        time = df.iloc[:, 0].values
        force = df.iloc[:, 1].values
        return time, force
    except:
        pass

    raise ValueError(f"Could not parse file: {filepath}")


def extract_first_n_seconds(time, force, n_seconds):
    """
    Extract the first N seconds of data for standardized analysis.

    Time is normalized to start at 0 regardless of LabChart export offset.

    Parameters
    ----------
    time : ndarray
        Time values (may start at any offset)
    force : ndarray
        Force values
    n_seconds : float
        Number of seconds to extract

    Returns
    -------
    time_segment : ndarray
        Time values normalized to start at 0
    force_segment : ndarray
        Force values for first n_seconds
    total_duration : float
        Total duration of original recording
    """
    # Normalize time to start at 0
    time_normalized = time - time[0]
    total_duration = time_normalized[-1]

    if total_duration <= n_seconds:
        return time_normalized, force, total_duration

    end_idx = np.searchsorted(time_normalized, n_seconds)
    return time_normalized[:end_idx], force[:end_idx], total_duration


def detect_contractions(time, force):
    """
    Detect contractions using fixed, reproducible parameters.

    Uses scipy.signal.find_peaks with ALL four criteria applied simultaneously:
    1. height    -- absolute minimum above baseline (filters sub-threshold noise)
    2. prominence -- local prominence (filters drift-related false peaks)
    3. distance  -- minimum spacing between peaks (prevents double-counting)
    4. width     -- minimum peak width (PRIMARY noise filter: real contractions
                    are wide, noise spikes are narrow)

    Parameters are FIXED across all files for reproducible cross-condition
    comparisons. Same thresholds for baseline, drug-treated, WT, and KO.

    Parameters
    ----------
    time : ndarray
        Time values in seconds (should start at 0)
    force : ndarray
        Force values in mN

    Returns
    -------
    peaks : ndarray
        Indices of detected contraction peaks
    properties : dict
        Peak properties from scipy.signal.find_peaks (includes widths)
    baseline : float
        Estimated baseline force level (10th percentile, mN)
    """
    # Calculate baseline as 10th percentile (robust to peaks)
    baseline = np.percentile(force, 10)

    # Subtract baseline for peak detection
    force_adjusted = force - baseline

    # Detect peaks with fixed parameters (all criteria must be met)
    peaks, properties = find_peaks(
        force_adjusted,
        height=PEAK_HEIGHT,
        prominence=PEAK_PROMINENCE,
        distance=PEAK_DISTANCE,
        width=PEAK_WIDTH,
        rel_height=0.5  # For width-at-half-maximum calculation
    )

    return peaks, properties, baseline


def detect_contraction_boundaries(time, force, peaks, baseline):
    """
    Detect start and end boundaries of each contraction.

    Contraction boundaries defined as:
    - Start: Force rises above baseline + 10% of peak amplitude
    - End: Force falls below baseline + 10% of peak amplitude

    Parameters
    ----------
    time : ndarray
        Time values
    force : ndarray
        Force values
    peaks : ndarray
        Indices of contraction peaks
    baseline : float
        Baseline force level

    Returns
    -------
    dict with boundary data, duty cycle, tonic metrics
    """
    if len(peaks) == 0:
        total_time = time[-1] - time[0] if len(time) > 1 else 0
        return {
            'contraction_starts': np.array([]),
            'contraction_ends': np.array([]),
            'contraction_durations': np.array([]),
            'intercontraction_intervals': np.array([]),
            'incomplete_relaxation': np.array([]),
            'total_contraction_time': 0,
            'total_quiescent_time': total_time,
            'duty_cycle_percent': 0,
            'percent_incomplete_relaxation': 0,
            'n_incomplete_relaxation': 0,
            'mean_quiescent_tone': baseline,
            'mean_tonic_force': baseline,
            'phasic_tonic_ratio': np.nan
        }

    contraction_starts = []
    contraction_ends = []
    contraction_durations = []

    max_search_samples = int(1.5 * SAMPLING_RATE)  # 1.5 sec search window

    for peak_idx in peaks:
        amp = force[peak_idx] - baseline
        threshold_10pct = baseline + 0.1 * amp

        # Find contraction START (searching backward from peak)
        search_start_idx = max(0, peak_idx - SAMPLING_RATE)  # 1 sec before
        pre_peak = force[search_start_idx:peak_idx]

        start_idx = search_start_idx  # default fallback
        if len(pre_peak) > 10:
            above_threshold = np.where(pre_peak >= threshold_10pct)[0]
            if len(above_threshold) > 0:
                start_idx = above_threshold[0] + search_start_idx

        # Find contraction END (searching forward from peak)
        search_end_idx = min(len(force), peak_idx + max_search_samples)
        post_peak = force[peak_idx:search_end_idx]

        end_idx = search_end_idx - 1  # default fallback
        if len(post_peak) > 10:
            below_threshold = np.where(post_peak <= threshold_10pct)[0]
            if len(below_threshold) > 0:
                end_idx = below_threshold[0] + peak_idx

        duration = time[end_idx] - time[start_idx]
        contraction_starts.append(start_idx)
        contraction_ends.append(end_idx)
        contraction_durations.append(duration)

    contraction_starts = np.array(contraction_starts)
    contraction_ends = np.array(contraction_ends)
    contraction_durations = np.array(contraction_durations)

    # Inter-contraction intervals and overlap detection
    intercontraction_intervals = []
    incomplete_relaxation = []

    for i in range(len(contraction_ends) - 1):
        interval = time[contraction_starts[i + 1]] - time[contraction_ends[i]]
        if interval < 0:
            intercontraction_intervals.append(0)
            incomplete_relaxation.append(True)
        else:
            intercontraction_intervals.append(interval)
            incomplete_relaxation.append(False)

    if len(peaks) > 1:
        incomplete_relaxation.append(False)  # Cannot determine for last

    intercontraction_intervals = np.array(intercontraction_intervals)
    incomplete_relaxation = np.array(incomplete_relaxation, dtype=bool)

    # Duty cycle
    total_recording_time = time[-1] - time[0]
    total_contraction_time = np.sum(contraction_durations)
    total_quiescent_time = max(0, total_recording_time - total_contraction_time)
    duty_cycle_percent = (total_contraction_time / total_recording_time * 100) if total_recording_time > 0 else 0

    # Tonic metrics
    n_incomplete = int(np.sum(incomplete_relaxation)) if len(incomplete_relaxation) > 0 else 0
    percent_incomplete = (n_incomplete / len(incomplete_relaxation) * 100) if len(incomplete_relaxation) > 0 else 0

    # Mean quiescent tone
    quiescent_samples = []
    for i in range(len(contraction_ends) - 1):
        if not incomplete_relaxation[i]:
            e = contraction_ends[i]
            s = contraction_starts[i + 1]
            if s > e:
                quiescent_samples.extend(force[e:s])
    mean_quiescent_tone = np.mean(quiescent_samples) if quiescent_samples else baseline

    # Mean tonic force
    tonic_samples = []
    for i in range(len(contraction_ends) - 1):
        if incomplete_relaxation[i]:
            e = contraction_ends[i]
            s = contraction_starts[i + 1]
            if s < e:
                tonic_samples.extend(force[s:e])
    mean_tonic_force = np.mean(tonic_samples) if tonic_samples else baseline

    n_complete = len(incomplete_relaxation) - n_incomplete if len(incomplete_relaxation) > 0 else 0
    phasic_tonic_ratio = (n_complete / n_incomplete) if n_incomplete > 0 else np.inf

    return {
        'contraction_starts': contraction_starts,
        'contraction_ends': contraction_ends,
        'contraction_durations': contraction_durations,
        'intercontraction_intervals': intercontraction_intervals,
        'incomplete_relaxation': incomplete_relaxation,
        'total_contraction_time': total_contraction_time,
        'total_quiescent_time': total_quiescent_time,
        'duty_cycle_percent': duty_cycle_percent,
        'percent_incomplete_relaxation': percent_incomplete,
        'n_incomplete_relaxation': n_incomplete,
        'mean_quiescent_tone': mean_quiescent_tone,
        'mean_tonic_force': mean_tonic_force,
        'phasic_tonic_ratio': phasic_tonic_ratio
    }


def calculate_rise_relax_metrics(time, force, peaks, baseline):
    """
    Calculate rise and relaxation kinetics for each contraction.

    Rise time: 10% to 90% of peak amplitude (ascending phase)
    Relax time: 90% to 10% of peak amplitude (descending phase)
    Rates: 0.8 * amplitude / time (represents 80% of the excursion)

    Also calculates waveform shape metrics:
    - Time to Peak: from 10% onset to peak maximum
    - Time from Peak: from peak maximum to 10% return
    - Rise/Fall Ratio: Time_to_Peak / Time_from_Peak
      (1.0 = symmetric, <1.0 = faster rise than fall)

    Parameters
    ----------
    time : ndarray
        Time values
    force : ndarray
        Force values
    peaks : ndarray
        Peak indices (must be valid indices into time and force arrays)
    baseline : float
        Baseline force level

    Returns
    -------
    dict with keys:
        rise_times, relax_times, rise_rates, relax_rates,
        times_to_peak, times_from_peak, rise_fall_ratios
    """
    rise_times = []
    relax_times = []
    rise_rates = []
    relax_rates = []
    times_to_peak = []
    times_from_peak = []
    rise_fall_ratios = []

    for peak_idx in peaks:
        if peak_idx >= len(force):
            continue

        amp = force[peak_idx] - baseline
        if amp <= 0:
            continue

        rise_10 = baseline + 0.1 * amp
        rise_90 = baseline + 0.9 * amp

        # ============================================================
        # RISE KINETICS (search 1 sec before peak)
        # ============================================================
        search_start = max(0, peak_idx - SAMPLING_RATE)
        pre_peak = force[search_start:peak_idx]

        onset_idx = None  # 10% crossing (for Time_to_Peak)

        if len(pre_peak) > 10:
            try:
                idx_10_candidates = np.where(pre_peak >= rise_10)[0]
                idx_90_candidates = np.where(pre_peak >= rise_90)[0]
                if len(idx_10_candidates) > 0:
                    # First crossing above 10% = contraction onset
                    onset_idx = idx_10_candidates[0] + search_start

                    if len(idx_90_candidates) > 0:
                        # FIX: Use [0] = FIRST crossing above 90%
                        # (not [-1] which was last sample above 90%,
                        # i.e. near peak, inflating rise time by ~48%)
                        idx_90 = idx_90_candidates[0] + search_start

                        if onset_idx < idx_90:
                            rt = time[idx_90] - time[onset_idx]
                            if rt > 0:
                                rise_times.append(rt)
                                rise_rates.append(0.8 * amp / rt)
            except (IndexError, ValueError):
                pass

        # ============================================================
        # RELAXATION KINETICS (search 2 sec after peak)
        # ============================================================
        search_end = min(len(force), peak_idx + 2 * SAMPLING_RATE)
        post_peak = force[peak_idx:search_end]

        offset_idx = None  # 10% crossing on fall (for Time_from_Peak)

        if len(post_peak) > 10:
            try:
                idx_90_candidates = np.where(post_peak <= rise_90)[0]
                idx_10_candidates = np.where(post_peak <= rise_10)[0]
                if len(idx_90_candidates) > 0 and len(idx_10_candidates) > 0:
                    # First crossing below 90% after peak (correct)
                    idx_90_rel = idx_90_candidates[0]
                    idx_90 = idx_90_rel + peak_idx

                    # FIX: First crossing below 10% AFTER the 90% crossing
                    # (not [-1] which grabbed end of 2-sec window,
                    # inflating relax time by ~452%)
                    after_90_mask = idx_10_candidates > idx_90_rel
                    if np.any(after_90_mask):
                        idx_10 = idx_10_candidates[after_90_mask][0] + peak_idx
                        offset_idx = idx_10  # For Time_from_Peak

                        if idx_90 < idx_10:
                            rxt = time[idx_10] - time[idx_90]
                            if rxt > 0:
                                relax_times.append(rxt)
                                relax_rates.append(0.8 * amp / rxt)
                    elif len(idx_10_candidates) > 0:
                        # Fallback: first crossing below 10% in window
                        idx_10 = idx_10_candidates[0] + peak_idx
                        offset_idx = idx_10
                        if idx_90 < idx_10:
                            rxt = time[idx_10] - time[idx_90]
                            if rxt > 0:
                                relax_times.append(rxt)
                                relax_rates.append(0.8 * amp / rxt)
            except (IndexError, ValueError):
                pass

        # ============================================================
        # WAVEFORM SHAPE METRICS
        # ============================================================
        # Time to Peak: from 10% onset to peak maximum
        if onset_idx is not None:
            ttp = time[peak_idx] - time[onset_idx]
            if ttp > 0:
                times_to_peak.append(ttp)

                # Time from Peak: peak to 10% return
                if offset_idx is not None:
                    tfp = time[offset_idx] - time[peak_idx]
                    if tfp > 0:
                        times_from_peak.append(tfp)
                        rise_fall_ratios.append(ttp / tfp)

    return {
        'rise_times': rise_times,
        'relax_times': relax_times,
        'rise_rates': rise_rates,
        'relax_rates': relax_rates,
        'times_to_peak': times_to_peak,
        'times_from_peak': times_from_peak,
        'rise_fall_ratios': rise_fall_ratios
    }


def calculate_metrics(time, force, peaks, properties, baseline):
    """
    Calculate comprehensive contraction metrics from the first TIME_WINDOW
    seconds of a recording.

    Parameters
    ----------
    time : ndarray
    force : ndarray
    peaks : ndarray
    properties : dict from find_peaks
    baseline : float

    Returns
    -------
    dict of metrics
    """
    metrics = {}
    peaks = np.array(peaks, dtype=int) if len(peaks) > 0 else np.array([], dtype=int)
    n_contractions = len(peaks)
    metrics['Num_Contractions'] = n_contractions

    duration = time[-1] - time[0] if len(time) > 1 else 0

    if n_contractions == 0:
        metrics.update({
            'Mean_Amplitude_mN': 0,
            'Amplitude_CV': 0,
            'Frequency_cpm': 0,
            'Mean_Period_sec': 0,
            'Period_CV': 0,
            'Mean_Duration_sec': 0,
            'Mean_Rise_Time_sec': 0,
            'Mean_Relax_Time_sec': 0,
            'Mean_Rise_Rate_mN_per_sec': 0,
            'Mean_Relax_Rate_mN_per_sec': 0,
            'Mean_Time_to_Peak_sec': 0,
            'Mean_Time_from_Peak_sec': 0,
            'Mean_Rise_Fall_Ratio': 0,
            'Mean_Width_Half_Max_sec': 0,
            'Integral_Force_mN_sec': 0,
            'Baseline_mN': baseline,
            'Mean_Contraction_Duration_sec': 0,
            'Mean_Intercontraction_Interval_sec': 0,
            'Duty_Cycle_percent': 0,
            'Total_Contraction_Time_sec': 0,
            'Total_Quiescent_Time_sec': duration,
            'Percent_Incomplete_Relaxation': 0,
            'N_Incomplete_Relaxation': 0,
            'Mean_Quiescent_Tone_mN': baseline,
            'Mean_Tonic_Force_mN': baseline,
            'Phasic_Tonic_Ratio': np.nan,
            'Force_Per_Contraction_mN_sec': 0,
            'Force_Per_Minute_mN_sec_per_min': 0,
            'Amplitude_Frequency_Product': 0,
            'Contraction_Work_Index': 0,
            'Amplitude_Flag': ''
        })
        return metrics

    # Amplitudes
    amplitudes = force[peaks] - baseline
    metrics['Mean_Amplitude_mN'] = np.mean(amplitudes)
    metrics['Amplitude_CV'] = (np.std(amplitudes) / np.mean(amplitudes) * 100) if np.mean(amplitudes) > 0 else 0

    # Frequency
    metrics['Frequency_cpm'] = (n_contractions / duration * 60) if duration > 0 else 0

    # Periods
    if n_contractions > 1:
        periods = np.diff(time[peaks])
        metrics['Mean_Period_sec'] = np.mean(periods)
        metrics['Period_CV'] = (np.std(periods) / np.mean(periods) * 100) if np.mean(periods) > 0 else 0
    else:
        metrics['Mean_Period_sec'] = 0
        metrics['Period_CV'] = 0

    # Width at half maximum (from find_peaks)
    if 'widths' in properties and len(properties['widths']) > 0:
        widths_sec = properties['widths'] / SAMPLING_RATE
        metrics['Mean_Width_Half_Max_sec'] = np.mean(widths_sec)
        metrics['Mean_Duration_sec'] = np.mean(widths_sec)
    else:
        metrics['Mean_Width_Half_Max_sec'] = 0
        metrics['Mean_Duration_sec'] = 0

    # Rise and relaxation kinetics
    kinetics = calculate_rise_relax_metrics(time, force, peaks, baseline)
    rise_times = kinetics['rise_times']
    relax_times = kinetics['relax_times']
    rise_rates = kinetics['rise_rates']
    relax_rates = kinetics['relax_rates']
    times_to_peak = kinetics['times_to_peak']
    times_from_peak = kinetics['times_from_peak']
    rise_fall_ratios = kinetics['rise_fall_ratios']

    metrics['Mean_Rise_Time_sec'] = np.mean(rise_times) if rise_times else 0
    metrics['Mean_Relax_Time_sec'] = np.mean(relax_times) if relax_times else 0
    metrics['Mean_Rise_Rate_mN_per_sec'] = np.mean(rise_rates) if rise_rates else 0
    metrics['Mean_Relax_Rate_mN_per_sec'] = np.mean(relax_rates) if relax_rates else 0

    # Waveform shape metrics
    metrics['Mean_Time_to_Peak_sec'] = np.mean(times_to_peak) if times_to_peak else 0
    metrics['Mean_Time_from_Peak_sec'] = np.mean(times_from_peak) if times_from_peak else 0
    metrics['Mean_Rise_Fall_Ratio'] = np.mean(rise_fall_ratios) if rise_fall_ratios else 0

    # Force integral
    force_above_baseline = np.maximum(force - baseline, 0)
    metrics['Integral_Force_mN_sec'] = np.trapz(force_above_baseline, time)

    metrics['Baseline_mN'] = baseline

    # Duty cycle and tonic metrics
    boundary_data = detect_contraction_boundaries(time, force, peaks, baseline)
    metrics['Mean_Contraction_Duration_sec'] = np.mean(boundary_data['contraction_durations']) if len(boundary_data['contraction_durations']) > 0 else 0
    metrics['Mean_Intercontraction_Interval_sec'] = np.mean(boundary_data['intercontraction_intervals']) if len(boundary_data['intercontraction_intervals']) > 0 else 0
    metrics['Duty_Cycle_percent'] = boundary_data['duty_cycle_percent']
    metrics['Total_Contraction_Time_sec'] = boundary_data['total_contraction_time']
    metrics['Total_Quiescent_Time_sec'] = boundary_data['total_quiescent_time']
    metrics['Percent_Incomplete_Relaxation'] = boundary_data['percent_incomplete_relaxation']
    metrics['N_Incomplete_Relaxation'] = boundary_data['n_incomplete_relaxation']
    metrics['Mean_Quiescent_Tone_mN'] = boundary_data['mean_quiescent_tone']
    metrics['Mean_Tonic_Force_mN'] = boundary_data['mean_tonic_force']
    metrics['Phasic_Tonic_Ratio'] = boundary_data['phasic_tonic_ratio']

    # Normalized metrics
    duration_minutes = duration / 60 if duration > 0 else 0
    metrics['Force_Per_Contraction_mN_sec'] = metrics['Integral_Force_mN_sec'] / n_contractions if n_contractions > 0 else 0
    metrics['Force_Per_Minute_mN_sec_per_min'] = metrics['Integral_Force_mN_sec'] / duration_minutes if duration_minutes > 0 else 0
    metrics['Amplitude_Frequency_Product'] = metrics['Mean_Amplitude_mN'] * metrics['Frequency_cpm']
    metrics['Contraction_Work_Index'] = metrics['Mean_Amplitude_mN'] * metrics['Mean_Duration_sec'] * metrics['Frequency_cpm']

    # Amplitude flag
    if metrics['Mean_Amplitude_mN'] < FLAG_AMPLITUDE_THRESHOLD and n_contractions > 0:
        metrics['Amplitude_Flag'] = f'LOW_AMP ({metrics["Mean_Amplitude_mN"]:.4f} mN < {FLAG_AMPLITUDE_THRESHOLD} mN) - Review validation plot'
    else:
        metrics['Amplitude_Flag'] = ''

    return metrics


def calculate_binned_metrics(time, force, peaks, properties, baseline, bin_duration, time_window):
    """
    Calculate metrics in time bins for temporal analysis.

    IMPORTANT: Peak indices are correctly remapped to bin-local coordinates
    for kinetics and boundary calculations.

    Parameters
    ----------
    time : ndarray
    force : ndarray
    peaks : ndarray
    properties : dict
    baseline : float
    bin_duration : float
    time_window : float

    Returns
    -------
    list of dict
    """
    bins_data = []
    n_bins = int(time_window // bin_duration)
    actual_duration = time[-1] - time[0] if len(time) > 0 else 0

    peaks = np.array(peaks, dtype=int) if len(peaks) > 0 else np.array([], dtype=int)
    widths = properties.get('widths', np.array([]))

    for bin_idx in range(n_bins):
        bin_start = bin_idx * bin_duration
        bin_end = (bin_idx + 1) * bin_duration

        if bin_start >= actual_duration:
            continue

        # Get bin data
        bin_mask = (time >= bin_start) & (time < bin_end)
        bin_time = time[bin_mask]
        bin_force = force[bin_mask]

        if len(bin_time) == 0:
            continue

        # Find which peaks fall in this bin
        peak_mask = (time[peaks] >= bin_start) & (time[peaks] < bin_end)
        peaks_in_bin = peaks[peak_mask]  # These are indices into FULL arrays
        n_peaks = len(peaks_in_bin)

        bin_metrics = {
            'Bin': bin_idx + 1,
            'Time_Start_sec': bin_start,
            'Time_End_sec': bin_end,
            'Contractions': n_peaks,
            'Frequency_cpm': n_peaks / bin_duration * 60,
        }

        if n_peaks > 0:
            amplitudes = force[peaks_in_bin] - baseline
            bin_metrics['Mean_Amplitude_mN'] = np.mean(amplitudes)

            # Period
            if n_peaks > 1:
                bin_metrics['Mean_Period_sec'] = np.mean(np.diff(time[peaks_in_bin]))
            else:
                bin_metrics['Mean_Period_sec'] = 0

            # Duration from widths
            if len(widths) > 0:
                widths_in_bin = widths[peak_mask]
                if len(widths_in_bin) > 0:
                    bin_metrics['Mean_Duration_sec'] = np.mean(widths_in_bin / SAMPLING_RATE)
                else:
                    bin_metrics['Mean_Duration_sec'] = 0
            else:
                bin_metrics['Mean_Duration_sec'] = 0

            # ================================================================
            # FIX: Use FULL array indices for kinetics and boundaries.
            # The rise/relax and boundary functions need to index into the
            # original time/force arrays, not sliced bin arrays.
            # ================================================================
            kinetics = calculate_rise_relax_metrics(
                time, force, peaks_in_bin, baseline
            )
            bin_metrics['Mean_Rise_Time_sec'] = np.mean(kinetics['rise_times']) if kinetics['rise_times'] else 0
            bin_metrics['Mean_Relax_Time_sec'] = np.mean(kinetics['relax_times']) if kinetics['relax_times'] else 0
            bin_metrics['Mean_Rise_Rate_mN_per_sec'] = np.mean(kinetics['rise_rates']) if kinetics['rise_rates'] else 0
            bin_metrics['Mean_Relax_Rate_mN_per_sec'] = np.mean(kinetics['relax_rates']) if kinetics['relax_rates'] else 0
            bin_metrics['Mean_Time_to_Peak_sec'] = np.mean(kinetics['times_to_peak']) if kinetics['times_to_peak'] else 0
            bin_metrics['Mean_Time_from_Peak_sec'] = np.mean(kinetics['times_from_peak']) if kinetics['times_from_peak'] else 0
            bin_metrics['Mean_Rise_Fall_Ratio'] = np.mean(kinetics['rise_fall_ratios']) if kinetics['rise_fall_ratios'] else 0

            # Boundary/duty cycle for this bin (also uses full arrays)
            boundary_data = detect_contraction_boundaries(time, force, peaks_in_bin, baseline)
            bin_metrics['Mean_Contraction_Duration_sec'] = np.mean(boundary_data['contraction_durations']) if len(boundary_data['contraction_durations']) > 0 else 0
            bin_metrics['Mean_Intercontraction_Interval_sec'] = np.mean(boundary_data['intercontraction_intervals']) if len(boundary_data['intercontraction_intervals']) > 0 else 0
            bin_metrics['Duty_Cycle_percent'] = boundary_data['duty_cycle_percent']
            bin_metrics['Total_Contraction_Time_sec'] = boundary_data['total_contraction_time']
            bin_metrics['Percent_Incomplete_Relaxation'] = boundary_data['percent_incomplete_relaxation']
            bin_metrics['N_Incomplete_Relaxation'] = boundary_data['n_incomplete_relaxation']

        else:
            bin_metrics.update({
                'Mean_Amplitude_mN': 0,
                'Mean_Period_sec': 0,
                'Mean_Duration_sec': 0,
                'Mean_Rise_Time_sec': 0,
                'Mean_Relax_Time_sec': 0,
                'Mean_Rise_Rate_mN_per_sec': 0,
                'Mean_Relax_Rate_mN_per_sec': 0,
                'Mean_Time_to_Peak_sec': 0,
                'Mean_Time_from_Peak_sec': 0,
                'Mean_Rise_Fall_Ratio': 0,
                'Mean_Contraction_Duration_sec': 0,
                'Mean_Intercontraction_Interval_sec': 0,
                'Duty_Cycle_percent': 0,
                'Total_Contraction_Time_sec': 0,
                'Percent_Incomplete_Relaxation': 0,
                'N_Incomplete_Relaxation': 0
            })

        # Integral force for this bin
        if len(bin_force) > 0:
            force_above = np.maximum(bin_force - baseline, 0)
            bin_metrics['Integral_Force_mN_s'] = np.trapz(force_above, bin_time)
        else:
            bin_metrics['Integral_Force_mN_s'] = 0

        bins_data.append(bin_metrics)

    return bins_data


def create_validation_plot(time, force, peaks, baseline, filename, output_dir, metrics=None):
    """
    Create validation plot showing detected contractions with actual thresholds.

    Parameters
    ----------
    time : ndarray
    force : ndarray
    peaks : ndarray
    baseline : float
    filename : str
    output_dir : Path
    metrics : dict, optional
        If provided, key metrics are annotated on the plot
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    # Threshold line (actual threshold used)
    threshold_line = baseline + PEAK_HEIGHT

    # --- Full trace ---
    ax1 = axes[0]
    ax1.plot(time, force, 'b-', linewidth=0.5, label='Force')
    if len(peaks) > 0:
        ax1.plot(time[peaks], force[peaks], 'ro', markersize=4, label=f'Peaks (n={len(peaks)})')
    ax1.axhline(y=baseline, color='g', linestyle='--', alpha=0.5,
                label=f'Baseline ({baseline:.3f} mN)')
    ax1.axhline(y=threshold_line, color='r', linestyle=':', alpha=0.5,
                label=f'Height Threshold ({threshold_line:.3f} mN)')
    ax1.set_xlabel('Time (sec)')
    ax1.set_ylabel('Force (mN)')
    ax1.set_title(f'{filename} - Full Trace ({TIME_WINDOW}s)')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Annotate with key metrics
    if metrics:
        flag_text = '  ** FLAGGED **' if metrics.get('Amplitude_Flag', '') else ''
        info_text = (
            f"Freq: {metrics.get('Frequency_cpm', 0):.1f} cpm  |  "
            f"Amp: {metrics.get('Mean_Amplitude_mN', 0):.3f} mN  |  "
            f"n={metrics.get('Num_Contractions', 0)}{flag_text}"
        )
        ax1.text(0.02, 0.02, info_text, transform=ax1.transAxes, fontsize=9,
                 verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # --- Zoomed view (first 60 sec) ---
    ax2 = axes[1]
    zoom_mask = time <= 60
    ax2.plot(time[zoom_mask], force[zoom_mask], 'b-', linewidth=0.5)
    if len(peaks) > 0:
        peaks_in_zoom = peaks[time[peaks] <= 60]
        ax2.plot(time[peaks_in_zoom], force[peaks_in_zoom], 'ro', markersize=5)
    ax2.axhline(y=baseline, color='g', linestyle='--', alpha=0.5)
    ax2.axhline(y=threshold_line, color='r', linestyle=':', alpha=0.5)
    ax2.set_xlabel('Time (sec)')
    ax2.set_ylabel('Force (mN)')
    ax2.set_title('Zoomed View (First 60 sec)')
    ax2.grid(True, alpha=0.3)

    # Parameters annotation on zoomed panel
    param_text = (
        f"Parameters: height={PEAK_HEIGHT} mN, prominence={PEAK_PROMINENCE} mN, "
        f"distance={PEAK_DISTANCE/SAMPLING_RATE:.1f}s, width={PEAK_WIDTH/SAMPLING_RATE:.2f}s"
    )
    ax2.text(0.02, 0.02, param_text, transform=ax2.transAxes, fontsize=7,
             verticalalignment='bottom', color='gray')

    plt.tight_layout()

    plot_path = output_dir / f"{filename}_validation.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()

    return plot_path


def analyze_folder(input_folder, output_folder):
    """
    Analyze all .txt files in a folder.

    Parameters
    ----------
    input_folder : str or Path
    output_folder : str or Path
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)
    plots_dir = output_folder / 'validation_plots'
    plots_dir.mkdir(exist_ok=True)

    txt_files = sorted(input_folder.glob('*.txt'))

    if len(txt_files) == 0:
        print(f"No .txt files found in: {input_folder}")
        return

    print(f"Input: {input_folder}")
    print(f"Found {len(txt_files)} files to analyze")
    print("\n" + "=" * 80 + "\n")

    all_overall = []
    all_10s_bins = []
    failed_files = []
    flagged_files = []

    for i, txt_file in enumerate(txt_files, 1):
        filename = txt_file.stem.strip()
        print(f"[{i}/{len(txt_files)}] Processing: {txt_file.name}")

        try:
            # Load
            time_raw, force_raw = load_labchart_file(txt_file)
            print(f"  Loaded {len(time_raw)} samples ({len(time_raw)/SAMPLING_RATE:.1f} sec)")

            # Extract first N seconds
            time, force, total_duration = extract_first_n_seconds(time_raw, force_raw, TIME_WINDOW)

            if total_duration <= TIME_WINDOW:
                print(f"  Recording is {total_duration:.1f}s (shorter than {TIME_WINDOW}s window)")
            else:
                print(f"  Using first {TIME_WINDOW}s from {total_duration:.1f}s recording")

            # Detect contractions (simple fixed parameters)
            peaks, properties, baseline = detect_contractions(time, force)
            print(f"  Detected {len(peaks)} contractions")

            # Calculate metrics
            metrics = calculate_metrics(time, force, peaks, properties, baseline)
            metrics['Filename'] = filename
            metrics['Total_Duration_sec'] = len(time) / SAMPLING_RATE

            # Check flag
            if metrics.get('Amplitude_Flag', ''):
                flagged_files.append(filename)
                print(f"  ** FLAGGED: {metrics['Amplitude_Flag']}")

            # Binned metrics
            bins_10s = calculate_binned_metrics(time, force, peaks, properties, baseline, BIN_DURATION, TIME_WINDOW)
            for b in bins_10s:
                b['Filename'] = filename

            print(f"  Calculated metrics ({len(bins_10s)} bins @ {BIN_DURATION}s)")

            # Validation plot (with metrics annotation)
            create_validation_plot(time, force, peaks, baseline, filename, plots_dir, metrics)
            print(f"  Created validation plot")

            all_overall.append(metrics)
            all_10s_bins.extend(bins_10s)
            print()

        except Exception as e:
            print(f"  ERROR: {e}")
            failed_files.append(txt_file.name)
            print()
            continue

    # Build DataFrames
    df_overall = pd.DataFrame(all_overall)
    df_10s = pd.DataFrame(all_10s_bins)

    # Column ordering
    overall_cols = ['Filename', 'Num_Contractions', 'Mean_Amplitude_mN', 'Amplitude_CV',
                    'Frequency_cpm', 'Mean_Period_sec', 'Period_CV', 'Mean_Duration_sec',
                    'Mean_Rise_Time_sec', 'Mean_Relax_Time_sec', 'Mean_Rise_Rate_mN_per_sec',
                    'Mean_Relax_Rate_mN_per_sec',
                    'Mean_Time_to_Peak_sec', 'Mean_Time_from_Peak_sec', 'Mean_Rise_Fall_Ratio',
                    'Mean_Width_Half_Max_sec',
                    'Integral_Force_mN_sec', 'Baseline_mN', 'Total_Duration_sec',
                    'Mean_Contraction_Duration_sec', 'Mean_Intercontraction_Interval_sec',
                    'Duty_Cycle_percent', 'Total_Contraction_Time_sec', 'Total_Quiescent_Time_sec',
                    'Percent_Incomplete_Relaxation', 'N_Incomplete_Relaxation',
                    'Mean_Quiescent_Tone_mN', 'Mean_Tonic_Force_mN', 'Phasic_Tonic_Ratio',
                    'Force_Per_Contraction_mN_sec', 'Force_Per_Minute_mN_sec_per_min',
                    'Amplitude_Frequency_Product', 'Contraction_Work_Index',
                    'Amplitude_Flag']
    df_overall = df_overall[[c for c in overall_cols if c in df_overall.columns]]

    bin_cols = ['Filename', 'Bin', 'Time_Start_sec', 'Time_End_sec',
                'Contractions', 'Frequency_cpm', 'Mean_Amplitude_mN',
                'Mean_Period_sec', 'Mean_Duration_sec', 'Mean_Rise_Time_sec',
                'Mean_Relax_Time_sec', 'Mean_Rise_Rate_mN_per_sec',
                'Mean_Relax_Rate_mN_per_sec',
                'Mean_Time_to_Peak_sec', 'Mean_Time_from_Peak_sec',
                'Mean_Rise_Fall_Ratio',
                'Integral_Force_mN_s',
                'Mean_Contraction_Duration_sec', 'Mean_Intercontraction_Interval_sec',
                'Duty_Cycle_percent', 'Total_Contraction_Time_sec',
                'Percent_Incomplete_Relaxation', 'N_Incomplete_Relaxation']
    df_10s = df_10s[[c for c in bin_cols if c in df_10s.columns]]

    # Save to Excel
    print("=" * 80)
    print("CREATING EXCEL OUTPUT")
    print("=" * 80 + "\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = output_folder / f"Myography_Analysis_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_overall.to_excel(writer, sheet_name='Overall_Metrics', index=False)
        df_10s.to_excel(writer, sheet_name='10sec_Bins', index=False)

    print(f"Created: {excel_path}")
    print(f"  Sheet 1: Overall_Metrics ({len(df_overall)} files, first {TIME_WINDOW}s)")
    print(f"  Sheet 2: 10sec_Bins (~{len(df_10s)} rows, first {TIME_WINDOW}s)")

    # Move processed files
    print("\n" + "=" * 80)
    print("MOVING PROCESSED FILES")
    print("=" * 80)

    processed_folder = input_folder.parent / "2_Processed"
    if processed_folder.exists():
        moved_count = 0
        for txt_file in txt_files:
            if txt_file.name not in failed_files:
                try:
                    dest = processed_folder / txt_file.name
                    shutil.move(str(txt_file), str(dest))
                    moved_count += 1
                except Exception as e:
                    print(f"  Could not move {txt_file.name}: {e}")
        print(f"\nMoved {moved_count} files to: {processed_folder}/")
    else:
        print(f"\n2_Processed folder not found")
        print(f"Files remain in: {input_folder}/")

    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Total files processed: {len(df_overall)}")
    if len(df_overall) > 0:
        print(f"Total peaks detected: {int(df_overall['Num_Contractions'].sum())}")
    print(f"\nParameters used:")
    print(f"  PEAK_HEIGHT:     {PEAK_HEIGHT} mN")
    print(f"  PEAK_PROMINENCE: {PEAK_PROMINENCE} mN")
    print(f"  PEAK_DISTANCE:   {PEAK_DISTANCE} samples ({PEAK_DISTANCE/SAMPLING_RATE:.1f} sec)")
    print(f"  PEAK_WIDTH:      {PEAK_WIDTH} samples ({PEAK_WIDTH/SAMPLING_RATE:.2f} sec)")
    print(f"  TIME_WINDOW:     {TIME_WINDOW} sec")
    print(f"\nOutput: {excel_path}")
    print(f"Plots:  {plots_dir}/")

    if flagged_files:
        print(f"\nFLAGGED ({len(flagged_files)} files - review validation plots):")
        for f in flagged_files:
            print(f"  >> {f}")

    if failed_files:
        print(f"\nFAILED ({len(failed_files)} files):")
        for f in failed_files:
            print(f"  >> {f}")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point.

    Supports two calling modes:

    Project mode (1 path):
        python3 myography_analyzer.py PROJECT_FOLDER [PEAK_HEIGHT]
        Looks for 1_RawData/ and 3_Results/ inside PROJECT_FOLDER.

    Explicit mode (2 paths):
        python3 myography_analyzer.py INPUT_FOLDER OUTPUT_FOLDER [PEAK_HEIGHT]
        Uses the two folders directly.
    """
    global PEAK_HEIGHT

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 myography_analyzer.py PROJECT_FOLDER [PEAK_HEIGHT]")
        print("  python3 myography_analyzer.py INPUT_FOLDER OUTPUT_FOLDER [PEAK_HEIGHT]")
        print("\nExamples:")
        print("  python3 myography_analyzer.py ../Projects/Piezo1_Adult")
        print("  python3 myography_analyzer.py ../Projects/Piezo1_Adult 0.05")
        print("  python3 myography_analyzer.py ./1_RawData ./3_Results")
        print("  python3 myography_analyzer.py ./1_RawData ./3_Results 0.10")
        print("\nProject mode expects this folder structure:")
        print("  ProjectFolder/")
        print("    1_RawData/      <- .txt files go here")
        print("    2_Processed/    <- files move here after analysis")
        print("    3_Results/      <- output appears here")
        print("\nRecommended PEAK_HEIGHT values:")
        print("  0.03 mN - Very sensitive (neonatal/weak contractions)")
        print("  0.05 mN - Recommended default (drug-treated tissue)")
        print("  0.08 mN - Standard (strong adult baseline contractions)")
        print("  0.10 mN - Less sensitive (noisy data)")
        print()
        sys.exit(1)

    # Determine mode: project folder (1 path) vs explicit (2 paths)
    first_arg = Path(sys.argv[1]).resolve()

    # Check if the first argument is a project folder (contains 1_RawData/)
    if (first_arg / "1_RawData").is_dir():
        # Project mode
        input_folder = str(first_arg / "1_RawData")
        results_dir = first_arg / "3_Results"
        results_dir.mkdir(exist_ok=True)
        output_folder = str(results_dir)
        print(f"\nProject: {first_arg.name}")
        print(f"  Input:  1_RawData/")
        print(f"  Output: 3_Results/\n")
        # PEAK_HEIGHT is the second argument in project mode
        if len(sys.argv) >= 3:
            try:
                PEAK_HEIGHT = float(sys.argv[2])
                if PEAK_HEIGHT < 0.01 or PEAK_HEIGHT > 0.50:
                    print(f"Warning: PEAK_HEIGHT {PEAK_HEIGHT} is outside typical range (0.01-0.50)")
                    print("Proceeding anyway...")
            except ValueError:
                print(f"Warning: Could not parse PEAK_HEIGHT '{sys.argv[2]}', using default {PEAK_HEIGHT}")
        custom_height = len(sys.argv) >= 3
    elif len(sys.argv) >= 3:
        # Explicit mode (two separate paths)
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]
        # PEAK_HEIGHT is the third argument in explicit mode
        if len(sys.argv) >= 4:
            try:
                PEAK_HEIGHT = float(sys.argv[3])
                if PEAK_HEIGHT < 0.01 or PEAK_HEIGHT > 0.50:
                    print(f"Warning: PEAK_HEIGHT {PEAK_HEIGHT} is outside typical range (0.01-0.50)")
                    print("Proceeding anyway...")
            except ValueError:
                print(f"Warning: Could not parse PEAK_HEIGHT '{sys.argv[3]}', using default {PEAK_HEIGHT}")
        custom_height = len(sys.argv) >= 4
    else:
        # Single argument but no 1_RawData found
        print(f"\nError: '{first_arg.name}' does not contain a 1_RawData/ folder.")
        print("\nEither point at a project folder with 1_RawData/ inside it:")
        print("  python3 myography_analyzer.py ../Projects/Piezo1_Adult")
        print("\nOr provide both input and output folders:")
        print("  python3 myography_analyzer.py ./1_RawData ./3_Results")
        print()
        sys.exit(1)

    # Print header
    print("=" * 80)
    print("WIRE MYOGRAPHY ANALYZER v3.1")
    print("=" * 80)
    print("\nFixed-parameter detection for reproducible cross-condition analysis.")
    print("\nParameters:")
    print(f"  Peak Height:     {PEAK_HEIGHT} mN" + (" [CUSTOM]" if custom_height else " [DEFAULT]"))
    print(f"  Peak Prominence: {PEAK_PROMINENCE} mN")
    print(f"  Peak Distance:   {PEAK_DISTANCE} samples ({PEAK_DISTANCE/SAMPLING_RATE:.1f} sec)")
    print(f"  Peak Width:      {PEAK_WIDTH} samples ({PEAK_WIDTH/SAMPLING_RATE:.2f} sec)")
    print(f"  Time Window:     FIRST {TIME_WINDOW} seconds")
    print(f"  Bin Duration:    {BIN_DURATION} sec")
    print(f"  Sampling Rate:   {SAMPLING_RATE} Hz")
    print(f"  Flag Threshold:  {FLAG_AMPLITUDE_THRESHOLD} mN")
    print("=" * 80 + "\n")

    analyze_folder(input_folder, output_folder)


if __name__ == "__main__":
    main()
