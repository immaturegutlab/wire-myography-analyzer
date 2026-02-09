# Wire Myography Analysis Toolkit v4.0

**Immature Gut Biology Lab, Division of Neonatology, UC Davis Children's Hospital**

Automated analysis of intestinal smooth muscle contractility from wire myography recordings. Detects contractions and calculates amplitude, frequency, kinetics, tone, viscoelastic properties, and more from LabChart exports.

---

## Overview

This toolkit processes raw force recordings from wire myography experiments on murine intestinal smooth muscle. It was developed for studying baseline contractility across developmental age and sex, Piezo1 mechanosensitive channel contributions, and intracellular calcium handling effects on rhythmicity and tone.

The toolkit consists of three scripts that form a pipeline:

| Script | Version | Purpose | Input | Output |
|--------|---------|---------|-------|--------|
| `myography_analyzer_v4.py` | v4.0 | Core analysis (publication code) | Raw .txt files | Excel + validation plots |
| `myography_organizer_v2_2.py` | v2.2 | Split mixed experiments | Analyzer Excel | Separate Excel per experiment |
| `smart_prism_converter_v3.py` | v3 | Format for GraphPad Prism | Any analyzer Excel | Prism-ready Excel with animal averages |

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
  2_Processed/     <-- files move here after analysis (in timestamped batch folders)
  3_Results/       <-- output goes here (created automatically)
```

### 2. Name your files

Follow this convention:

```
[Date]_[Code]_[Sex][MouseNum]_n[SegmentNum]_[Condition].txt
```

Examples:
```
20260101_R_Male1_n1_Baseline.txt       (Ryanodine experiment)
20260101_R_Male1_n1_RyR100.txt
20260101_R_Male1_n1_Y2.txt
20260101_Th_Female2_n1_Thapsi10.txt    (Thapsigargin experiment)
20260101_Px_Male1_n1_PostPax10.txt     (Paxilline experiment)
20260101_Px_Female1_n3_PrePax5.txt     (Paxilline Pre-Y2)
20260101_KO_Male3_n1_Baseline.txt      (ICC Knockout)
20260101_Male1_n1_Baseline.txt         (Yoda-only, no code needed)
20260101_CPA_Male1_n1_CPA10.txt        (any new drug -- auto-detected)
```

The project code is generic. Known codes (R, Th, Px, KO, ShWT, sham) map to friendly folder names. Any unknown code automatically creates a new experiment folder using the code itself.

Supported age prefixes: `P7NEO`, `P14NEO`, `P28NEO`, `P56NEO`, `ADULT`, `NEO`

### 3. Run the analyzer

```bash
python3 myography_analyzer_v4.py path/to/MyProject
```

The script finds `1_RawData/`, processes every `.txt` file, and writes results to `3_Results/`.

Processed raw files are moved into a timestamped batch folder inside `2_Processed/` (e.g., `Batch_20260206_143022/`). The timestamp matches the Excel output file. You can freely rename batch folders (e.g., to `Pax_Round2` or `Rerun_higher_dose`) without affecting anything downstream.

### 4. Check your validation plots

Open `3_Results/validation_plots/`. Each plot shows the raw trace (blue), detected peaks (red dots), baseline (green dashed), and threshold (pink dotted). Verify that peaks land on real contractions and no obvious contractions are missed.

### 5. Organize by experiment (if mixed)

```bash
python3 myography_organizer_v2_2.py path/to/MyProject/3_Results
```

Auto-detects project codes from filenames and creates separate folders. Unknown codes get their own folder automatically.

### 6. Convert to Prism format

```bash
python3 smart_prism_converter_v3.py path/to/Results/Ryanodine/Ryanodine.xlsx
```

Or run without arguments for a file picker dialog:

```bash
python3 smart_prism_converter_v3.py
```

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
python3 myography_analyzer_v4.py path/to/MyProject
python3 smart_prism_converter_v3.py path/to/MyProject/3_Results/Myography_Analysis_*.xlsx
```

**Workflow B: Mixed experiment types**

```bash
python3 myography_analyzer_v4.py path/to/MyProject
python3 myography_organizer_v2_2.py path/to/MyProject/3_Results
python3 smart_prism_converter_v3.py path/to/MyProject/3_Results/Ryanodine/Ryanodine.xlsx
python3 smart_prism_converter_v3.py path/to/MyProject/3_Results/Paxilline/Paxilline.xlsx
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
python3 myography_analyzer_v4.py path/to/MyProject 0.03
```

| Threshold | When to use |
|-----------|-------------|
| 0.03 mN | Very sensitive (neonatal, weak contractions) |
| 0.05 mN | Default (drug-treated tissue, general use) |
| 0.08 mN | Standard (strong adult baseline) |
| 0.10 mN | Less sensitive (noisy recordings) |

### Output Metrics (20 total)

**Overall_Metrics sheet** (one row per file):

| Category | Metrics |
|----------|---------|
| Amplitude | Mean amplitude (mN) |
| Frequency | Frequency (cpm), mean period (sec), period CV (%) |
| Kinetics | Duration (sec), time to peak (sec), time from peak (sec), rise/fall ratio, max contraction rate (mN/s), max relaxation rate (mN/s) |
| Integral | Integral force (mN-sec), force per contraction (mN-sec), force per minute (mN-sec/min) |
| Duty cycle | Duty cycle (%) |
| Tonic | Baseline tone (mN), phasic/tonic ratio |
| Composite | Amplitude-frequency product |
| QC | Contraction count, amplitude flag |

**10sec_Bins sheet** (one row per 10-second bin per file):

Same core metrics calculated within each time bin, enabling visualization of dynamic changes during drug application or washout.

### Explicit mode (backward compatible)

You can also specify input and output folders directly:

```bash
python3 myography_analyzer_v4.py ./input_folder ./output_folder 0.05
```

---

## Organizer Details

### Auto-detection system (v2.2)

The organizer extracts the project code from the filename position (between date and sex) and routes files accordingly:

| Code | Folder Created |
|------|---------------|
| `R` | `Ryanodine/` |
| `Th` | `Thapsigargin/` |
| `Px` | `Paxilline/` |
| `KO`, `ShWT`, `sham` | `WT_vs_KO/` |
| _(none)_ | `Yoda_Only/` |
| _(any unknown code)_ | Uses code as folder name |

Unknown codes are fully supported. If a new experiment uses code `CPA`, the organizer creates a `CPA/` folder with the filtered Excel and validation plots. No code changes required.

---

## Prism Converter Details

- Auto-detects conditions from filenames (Baseline, RyR100, Thapsi10, Y2, etc.)
- Generic Pre/Post detection: any condition starting with `Pre` or `Post` automatically becomes a separate column (e.g., PrePax, PostPax, PreRyan, PostThap)
- Recognizes any project code in filename position (generic, not hardcoded)
- Recognizes age prefixes (P7NEO, P14, ADULT) for multi-age studies
- Groups by age, then by sex (Male first, then Female)
- Calculates animal averages from technical replicates (multiple segments per animal)
- Computes percent change from baseline for each condition
- Creates separate sheets for 10-second bin data (amplitude, frequency, period, duration, rise time, relaxation time, integral)
- Preserves source data in SRC_ sheets for traceability

### Condition column order

Columns are arranged to match experimental sequence:

```
Baseline | Pre[Drug] | Treatment | Y2 | Post[Drug]
```

Each gets a corresponding percent-change column calculated relative to Baseline.

---

## File Naming Conventions

The toolkit recognizes these filename patterns (in order of matching priority):

```
20260101_P7NEO_Male1_n1_Baseline.txt       (age prefix, no project code)
20260101_ADULT_Male1_n1_Y2.txt              (age prefix, no project code)
20260101_R_Male1_n1_Baseline.txt            (project code, defaults to ADULT)
20260101_Px_Female2_n1_PostPax10.txt        (project code with Pre/Post condition)
20260101_CPA_Male1_n1_CPA10.txt             (unknown code, auto-detected)
20260101_Male1_n1_Baseline.txt              (simple format, defaults to ADULT)
```

Segment notation: `n1`, `n2`, `n1,1` (comma notation for sub-segments)

---

## Folder Structure

```
Master Wire Myography Folder/
  MyographyTools/
    myography_analyzer_v4.py
    myography_organizer_v2_2.py
    smart_prism_converter_v3.py
    README.md
    METHODS_FOR_PUBLICATION.md
    STUDENT_GUIDE.md
  Projects/
    Piezo1_Adult/
      1_RawData/
      2_Processed/
        Batch_20260206_143022/   (auto-created, renameable)
        Batch_20260210_091500/
      3_Results/
        Myography_Analysis_YYYYMMDD_HHMMSS.xlsx
        validation_plots/
        Ryanodine/           (auto-created by organizer)
        Thapsigargin/        (auto-created by organizer)
        Paxilline/           (auto-created by organizer)
        WT_vs_KO/            (auto-created by organizer)
        Yoda_Only/           (auto-created by organizer)
        [NewCode]/           (auto-created for unknown codes)
```

---

## Troubleshooting

**"No such file or directory"**
Check your path with `ls`. The most common issue is a typo or being in the wrong directory.

**"No module named numpy"**
Run: `pip3 install numpy pandas scipy openpyxl matplotlib`

**"0 contractions detected" but contractions are visible in LabChart**
Check the validation plot. If signal is below 0.05 mN, try: `python3 myography_analyzer_v4.py path/to/Project 0.03`

**"does not contain a 1_RawData/ folder"**
You pointed at the wrong folder. The script expects `1_RawData/` inside the folder you specify.

**Prism converter says "WARNING: Could not auto-detect"**
Your filenames do not match any recognized pattern. Check the File Naming Conventions section above.

**Doubled dates in Prism output (e.g., 20251015_20251015_...)**
Your project code is not being recognized. Make sure the code is a single token between the date and sex (e.g., `20251015_Px_Male1...` not `20251015_Paxilline_Male1...`).

**PrePax and PostPax collapsed into one "Treatment" column**
Update to the latest smart_prism_converter_v3.py. Pre/Post conditions are now auto-separated.

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

See VERSION_HISTORY.md for full changelog.

- **v4.0** (Feb 2026) -- Generic project code system (no hardcoded experiment lists). Pre/Post condition auto-separation in Prism converter. Paxilline experiment support. Organizer auto-creates folders for unknown codes. Batch subfolders in 2_Processed for run isolation. Fixed doubled-date parsing bug for new project codes.
- **v3.1** (Feb 2026) -- Single-command project mode. Fixed kinetics calculations. Added time-to-peak, time-from-peak, rise/fall ratio. Width filter reduced to 0.3 seconds.
- **v3.0** (Feb 2026) -- Fixed-parameter detection for reproducibility. Amplitude flagging. Comprehensive duty cycle and tonic metrics.
- **v2.7** (Jan 2026) -- CRITICAL FIX: Duration calculation error (was 2x too large in v2.6).
- **v1.0-v2.6** -- Initial development. Deprecated (duration values incorrect).

---

## Citation

If you use this software in published work, please cite:

> Bautista G. Wire Myography Analysis Toolkit v4.0. Immature Gut Biology Lab, Division of Neonatology, UC Davis Children's Hospital. 2026. DOI: 10.5281/zenodo.18472624

See METHODS_FOR_PUBLICATION.md for ready-to-use methods text.

---

## License

This software is provided for academic and research use. See LICENSE for details.

---

## Contact

Geoanna Bautista, Assistant Professor
Division of Neonatology, UC Davis Children's Hospital
Immature Gut Biology Lab
