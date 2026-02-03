# Wire Myography Analysis Toolkit v3.1

**Immature Gut Biology Lab, Division of Neonatology, UC Davis Children's Hospital**

Automated analysis of intestinal smooth muscle contractility from wire myography recordings. Detects contractions and calculates amplitude, frequency, kinetics, tone, viscoelastic properties, and more from LabChart exports.

---

## Overview

This toolkit processes raw force recordings from wire myography experiments on murine intestinal smooth muscle. It was developed for studying baseline contractility across developmental age and sex, Piezo1 mechanosensitive channel contributions, and intracellular calcium handling effects on rhythmicity and tone.

The toolkit consists of three scripts that form a pipeline:

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `myography_analyzer.py` | Core analysis (publication code) | Raw .txt files | Excel + validation plots |
| `myography_organizer.py` | Split mixed experiments | Analyzer Excel | Separate Excel per experiment |
| `smart_prism_converter_v3.py` | Format for GraphPad Prism | Any analyzer Excel | Prism-ready Excel with animal averages |

---

## Requirements

- Python 3.8 or later
- Dependencies:

```bash
pip3 install numpy pandas scipy openpyxl matplotlib
```

---

## Quick Start

### 1. Set up your project folder

```
MyProject/
  1_RawData/       <-- put your LabChart .txt exports here
  2_Processed/     <-- files move here after analysis
  3_Results/       <-- output goes here (created automatically)
```

### 2. Name your files

Follow this convention:

```
[Date]_[Marker]_[Sex][MouseNum]_n[SegmentNum]_[Condition].txt
```

Examples:
```
20260101_R_Male1_n1_Baseline.txt
20260101_R_Male1_n1_RyR100.txt
20260101_R_Male1_n1_Y2.txt
20260101_Th_Female2_n1_Baseline.txt
20260101_Th_Female2_n1_Thapsi10.txt
20260101_KO_Male3_n1_Baseline.txt
20260101_Male1_n1_Baseline.txt        (no experiment marker is fine too)
```

Supported experiment markers: `R_`, `Th_`, `KO_`, `WT_`, `ShWT_`, `sham_`

Supported age prefixes: `P7NEO`, `P14NEO`, `P28NEO`, `P56NEO`, `ADULT`, `NEO`

### 3. Run the analyzer

```bash
python3 myography_analyzer.py path/to/MyProject
```

That's it. The script finds `1_RawData/`, processes every `.txt` file, and writes results to `3_Results/`.

### 4. Check your validation plots

Open `3_Results/validation_plots/`. Each plot shows the raw trace (blue), detected peaks (red dots), baseline (green dashed), and threshold (pink dotted). Verify that peaks land on real contractions and no obvious contractions are missed.

### 5. Convert to Prism format

```bash
python3 smart_prism_converter_v3.py
```

A file picker opens. Select your Excel file. The converter creates a `_Prism.xlsx` file with animal averages, percent changes, and time-binned data formatted for direct import into GraphPad Prism.

---

## Workflow Decision

```
Are your raw files a MIX of different experiment types?
(Ryanodine + Thapsigargin + Yoda-only all in one folder)

YES --> Analyze --> Organize --> Convert each
NO  --> Analyze --> Convert directly
```

**Workflow A: Single experiment type (most common)**

```bash
python3 myography_analyzer.py path/to/MyProject
python3 smart_prism_converter_v3.py          # pick the Excel file
```

**Workflow B: Mixed experiment types**

```bash
python3 myography_analyzer.py path/to/MyProject
python3 myography_organizer.py path/to/MyProject/3_Results path/to/MyProject
python3 smart_prism_converter_v3.py          # pick Ryanodine/Ryanodine.xlsx
python3 smart_prism_converter_v3.py          # pick Thapsigargin/Thapsigargin.xlsx
```

---

## Analyzer Details

### Detection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Peak height | 0.05 mN | Minimum absolute height above baseline |
| Peak prominence | 0.05 mN | Minimum local height relative to surroundings |
| Peak distance | 1.0 sec | Minimum spacing between contractions |
| Peak width | 0.3 sec | Minimum contraction duration (filters noise) |
| Analysis window | 150 sec | Standardized window from start of recording |
| Bin duration | 10 sec | Time resolution for temporal analysis |
| Sampling rate | 250 Hz | LabChart acquisition rate |
| Baseline method | 10th percentile | Robust estimate of relaxed state |

### Custom peak height

For weak contractions (neonatal tissue, drug-treated):

```bash
python3 myography_analyzer.py path/to/MyProject 0.03
```

| Threshold | When to use |
|-----------|-------------|
| 0.03 mN | Very sensitive (neonatal, weak contractions) |
| 0.05 mN | Default (drug-treated tissue, general use) |
| 0.08 mN | Standard (strong adult baseline) |
| 0.10 mN | Less sensitive (noisy recordings) |

### Output Metrics (34 total)

**Overall_Metrics sheet** (one row per file):

| Category | Metrics |
|----------|---------|
| Amplitude | Mean amplitude (mN), amplitude CV (%) |
| Frequency | Frequency (cpm), mean period (sec), period CV (%) |
| Kinetics | Duration (sec), rise time (sec), relaxation time (sec), rise rate (mN/sec), relaxation rate (mN/sec), time to peak (sec), time from peak (sec), rise/fall ratio, FWHM (sec) |
| Integral | Integral force (mN-sec), baseline tone (mN) |
| Duty cycle | Duty cycle (%), total contraction time (sec), total quiescent time (sec) |
| Tonic | Incomplete relaxation count and percentage, quiescent tone (mN), mean tonic force (mN), phasic/tonic ratio |
| Composite | Force per contraction (mN-sec), force per minute (mN-sec/min), amplitude-frequency product, contraction work index |
| QC | Amplitude flag |

**10sec_Bins sheet** (one row per 10-second bin per file):

Same core metrics calculated within each time bin, enabling visualization of dynamic changes during drug application or washout.

### Explicit mode (backward compatible)

You can also specify input and output folders directly:

```bash
python3 myography_analyzer.py ./input_folder ./output_folder 0.05
```

---

## Organizer Details

Classifies files by experiment type based on filename keywords:

| Experiment | Keywords |
|------------|----------|
| Ryanodine | `R_`, `RyR`, `Ryanodine` |
| Thapsigargin | `Th_`, `Thapsi`, `Thapsigargin` |
| WT_vs_KO | `KO`, `ShWT`, `sham` |
| Yoda_Only | Everything else |

Creates separate subfolders in `3_Results/` with filtered Excel files and validation plots for each experiment type.

---

## Prism Converter Details

- Auto-detects conditions from filenames (Baseline, RyR100, Thapsi10, Y2, etc.)
- Recognizes age prefixes (P7NEO, P14, ADULT) and experiment markers (R_, Th_, KO_)
- Groups by age, then by sex (Male first, then Female)
- Calculates animal averages from technical replicates (multiple segments per animal)
- Computes percent change from baseline for each condition
- Creates separate sheets for 10-second bin data (amplitude, frequency, period, duration, rise time, relaxation time, integral)
- Preserves source data in SRC_ sheets for traceability

---

## File Naming Conventions

The toolkit recognizes these filename patterns (in order of matching priority):

```
20260101_P7NEO_Male1_n1_Baseline.txt       (age prefix, no experiment marker)
20260101_ADULT_Male1_n1_Y2.txt              (age prefix, no experiment marker)
20260101_R_Male1_n1_Baseline.txt            (experiment marker, defaults to ADULT)
20260101_Th_Female2_n1_Thapsi10.txt         (experiment marker, defaults to ADULT)
20260101_KO_Male3_n1_Baseline.txt           (experiment marker, defaults to ADULT)
20260101_Male1_n1_Baseline.txt              (simple format, defaults to ADULT)
```

Segment notation: `n1`, `n2`, `n1,1` (comma notation for sub-segments)

---

## Folder Structure

```
Master Wire Myography Folder/
  MyographyTools/
    myography_analyzer.py
    myography_organizer.py
    smart_prism_converter_v3.py
    README.md
    METHODS_FOR_PUBLICATION.md
    WORKFLOW_GUIDE.md
  Projects/
    Piezo1_Adult/
      1_RawData/
      2_Processed/
      3_Results/
        Myography_Analysis_YYYYMMDD_HHMMSS.xlsx
        validation_plots/
        Ryanodine/           (if organized)
        Thapsigargin/        (if organized)
```

---

## Troubleshooting

**"No such file or directory"**
Check your path with `ls`. The most common issue is a typo or being in the wrong directory.

**"No module named numpy"**
Run: `pip3 install numpy pandas scipy openpyxl matplotlib`

**"0 contractions detected" but contractions are visible in LabChart**
Check the validation plot. If signal is below 0.05 mN, try: `python3 myography_analyzer.py path/to/Project 0.03`

**"does not contain a 1_RawData/ folder"**
You pointed at the wrong folder. The script expects `1_RawData/` inside the folder you specify.

**Prism converter says "WARNING: Could not auto-detect"**
Your filenames do not match any recognized pattern. Check the File Naming Conventions section above.

**Trailing spaces in filenames cause scattered data**
Fixed in v3.1. The analyzer and converter both strip whitespace from filenames automatically.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >= 1.20 | Array operations |
| pandas | >= 1.3 | Data management, Excel I/O |
| scipy | >= 1.7 | Peak detection (signal.find_peaks) |
| openpyxl | >= 3.0 | Excel file writing |
| matplotlib | >= 3.4 | Validation plots |
| tkinter | (built-in) | File picker dialog (converter only) |

---

## Version History

- **v3.1** (Feb 2026) -- Single-command project mode. Fixed kinetics calculations (relaxation time was inflated 5.3x, rise time inflated 32% in earlier versions). Added time-to-peak, time-from-peak, rise/fall ratio metrics. Width filter reduced from 0.6 to 0.3 seconds to capture faster contractions. Filename whitespace stripping. Prism converter support for experiment marker filenames (R_, Th_, KO_, etc.).
- **v3.0** (Feb 2026) -- Fixed-parameter detection for reproducibility. Amplitude flagging system. Comprehensive duty cycle and tonic metrics.
- **v2.7-v2.9** -- Duration correction (v2.7 fixed 2x overcount), parameter tuning, neonatal tissue support.
- **v1.0-v2.6** -- Initial development, iterative refinement.

---

## Citation

If you use this software in published work, please cite:

> Bautista G. Wire Myography Analyzer v3.1. Immature Gut Biology Lab, Division of Neonatology, UC Davis Children's Hospital. 2026. Available at: [repository URL]

See METHODS_FOR_PUBLICATION.md for ready-to-use methods text.

---

## License

This software is provided for academic and research use. See LICENSE for details.

---

## Contact

Geoanna Bautista, Assistant Professor
Division of Neonatology, UC Davis Children's Hospital
Immature Gut Biology Lab
