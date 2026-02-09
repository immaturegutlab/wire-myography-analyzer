# Wire Myography Analysis -- Student Guide v2.1

**For:** Lab students processing intestinal smooth muscle contractility data
**Updated:** February 2026
**Analyzer:** v4.0 | **Organizer:** v2.2 | **Prism Converter:** v3 (updated)

---

## How It Works (30-second version)

1. Export from LabChart (2 columns: Time, Force)
2. Name the file correctly (see below)
3. Drop it in `1_RawData/`
4. Run one command
5. Check validation plots
6. Done

---

## File Naming

This is the most important part. Every file follows the same pattern:

```
DATE_CODE_Sex#_n#_Condition.txt
```

**DATE** -- When you recorded. Always 8 digits: YYYYMMDD
- Good: `20260205`
- Bad: `2026205` (missing zero), `Feb5` (not a number)

**CODE** -- Project code that tells the system which experiment folder to create. This is optional for Yoda-only experiments.

Currently known codes and their folder names:

| Code | Folder Name | Experiment |
|------|-------------|------------|
| _(none)_ | Yoda_Only | Just Baseline then Y2, no other drugs |
| `R` | Ryanodine | RyR blocker experiment |
| `Th` | Thapsigargin | SERCA blocker experiment |
| `Px` | Paxilline | BK channel blocker experiment |
| `KO` | WT_vs_KO | ICC Knockout genotype |
| `ShWT` | WT_vs_KO | Sham WT control for KO |
| `sham` | WT_vs_KO | Sham control for KO |

**If Geoanna gives you a new code that is not on this list, just use it.** The system will automatically create a new folder using the code as the name. For example, if she says the code is `CPA`, name your files `20260301_CPA_Male1_n1_Baseline.txt` and a `CPA/` folder will appear in results. No code changes needed, no guide update needed.

**Sex#** -- Sex and animal number. The number is the biological replicate (different mice).
- `Male1`, `Male2`, `Female1`, `Female3`, etc.
- Each mouse gets a unique number within a project

**n#** -- Segment number. Technical replicate (different tissue segments from the same mouse).
- `n1`, `n2`, `n3`, etc.

**Condition** -- What was applied to the tissue when you recorded.
- `Baseline` -- Always first. No drug, just spontaneous contractions.
- `Y2` -- After Yoda2 (Piezo1 agonist)
- Drug names depend on the experiment (see examples below)

---

## Naming Examples by Experiment

**Yoda Only** (no project code):
```
20260205_Female1_n1_Baseline.txt
20260205_Female1_n1_Y2.txt
```
Sequence: Baseline, then Y2

**Ryanodine** (code: R):
```
20260205_R_Male1_n1_Baseline.txt
20260205_R_Male1_n1_RyR100.txt
20260205_R_Male1_n1_Y2.txt
```
Sequence: Baseline, then Ryanodine (100 uM), then Y2

**Thapsigargin** (code: Th):
```
20260205_Th_Female1_n2_Baseline.txt
20260205_Th_Female1_n2_Thapsi10.txt
20260205_Th_Female1_n2_Y2.txt
```
Sequence: Baseline, then Thapsigargin (10 uM), then Y2

**Paxilline -- PostPax** (code: Px):
```
20260205_Px_Male1_n1_Baseline.txt
20260205_Px_Male1_n1_Y2.txt
20260205_Px_Male1_n1_PostPax10.txt
```
Sequence: Baseline, then Y2, then Paxilline (10 uM)
The number after PostPax is the dose in uM (1, 5, or 10).

**Paxilline -- PrePax** (code: Px):
```
20260205_Px_Female1_n5_Baseline.txt
20260205_Px_Female1_n5_PrePax5.txt
20260205_Px_Female1_n5_Y2.txt
```
Sequence: Baseline, then Paxilline (5 uM), then Y2
The number after PrePax is the dose in uM (1, 5, or 10).

**ICC Knockout** (code: KO or ShWT):
```
20260205_KO_Male1_n1_Baseline.txt
20260205_KO_Male1_n1_Y2.txt
20260205_ShWT_Male1_n1_Baseline.txt
20260205_ShWT_Male1_n1_Y2.txt
```
Sequence: Baseline, then Y2 (for both genotypes)

**Future experiment with new code** (example: CPA):
```
20260301_CPA_Male1_n1_Baseline.txt
20260301_CPA_Male1_n1_CPA10.txt
20260301_CPA_Male1_n1_Y2.txt
```
Just use whatever code Geoanna assigns. The system handles the rest.

---

## Pre/Post Drug Naming

If an experiment involves giving a drug either before or after Yoda2, use the `Pre` or `Post` prefix on the condition name. The Prism converter automatically separates these into distinct columns.

- `PrePax5` = Paxilline 5 uM given BEFORE Y2
- `PostPax10` = Paxilline 10 uM given AFTER Y2
- Always include the dose number

This works for any drug name, not just Paxilline:
- `PreRyan50` would work for Ryanodine given before Y2
- `PostThap10` would work for Thapsigargin given after Y2

The Prism converter automatically detects any condition starting with `Pre` or `Post` and creates separate columns for each.

---

## Common Naming Mistakes

These are real errors that have happened and required batch fixes. Getting it right the first time saves everyone time.

**Date must be exactly 8 digits (YYYYMMDD).** Months and days under 10 need a leading zero.
- Wrong: `2025109_Px_Female1...` (October 9 written as 109 instead of 1009)
- Right: `20251009_Px_Female1...`
- Wrong: `2026205_...` (February 5 written as 205 instead of 0205)
- Right: `20260205_...`

**Always include the dose number on drug treatments.**
- Wrong: `PostPax.txt` (which dose?)
- Right: `PostPax10.txt` (10 uM), `PostPax5.txt` (5 uM), `PostPax1.txt` (1 uM)
- Same rule for PrePax, RyR, Thapsi, or any future drug

**Project code goes right after the date, before sex.**
- Wrong: `20251015_Male1_n2_PostPax10.txt` (missing Px_)
- Right: `20251015_Px_Male1_n2_PostPax10.txt`
- If the experiment uses a drug besides Y2, it needs a project code

**Use underscores, not spaces. No extra spaces.**
- Wrong: `20260205 Female1 n1 Baseline.txt`
- Right: `20260205_Female1_n1_Baseline.txt`
- Wrong: `20260205_R _Male1...` (space after R)
- Right: `20260205_R_Male1...`

**Capitalize condition names consistently.**
- Wrong: `baseline.txt`, `y2.txt`
- Right: `Baseline.txt`, `Y2.txt`

**Use Male/Female, not Mouse.**
- Wrong: `Mouse1`
- Right: `Male1` or `Female1`

---

## Folder Structure

```
Piezo1_Adult/
  1_RawData/       <-- You put new .txt files here
  2_Processed/     <-- Files move here after analysis (in timestamped batch folders)
  3_Results/       <-- All outputs appear here
    validation_plots/
    Ryanodine/     <-- Auto-created from R_ files
    Thapsigargin/  <-- Auto-created from Th_ files
    Paxilline/     <-- Auto-created from Px_ files
    WT_vs_KO/      <-- Auto-created from KO/ShWT files
    Yoda_Only/     <-- Everything else
    [NewCode]/     <-- Auto-created for any unknown code
```

Numbered folders (1, 2, 3) keep them sorted in Finder.

---

## Running the Analysis

Open Terminal (Cmd + Space, type "Terminal", hit Enter).

**Step 1: Navigate to tools folder**
```bash
cd "/Users/gbautista1/Library/CloudStorage/Box-Box/McElroy_Bautista/PROJECTS (ALL)/Master Wire Myography Folder/MyographyTools"
```

**Step 2: Run analyzer**
```bash
python3 myography_analyzer_v4.py ../Projects/Piezo1_Adult
```
This processes everything in `1_RawData/`, creates Excel + validation plots in `3_Results/`, and moves raw files to a timestamped batch folder in `2_Processed/` (e.g., `Batch_20260206_143022/`). You can rename batch folders without breaking anything.

**Step 3: Check validation plots**
```bash
open ../Projects/Piezo1_Adult/3_Results/validation_plots/
```
Look at every plot. Red dots should sit on contraction peaks. If dots are on noise or missing obvious peaks, tell Geoanna.

**Step 4: Organize by experiment**
```bash
python3 myography_organizer_v2_2.py ../Projects/Piezo1_Adult/3_Results
```
This splits the master Excel into experiment-specific files and moves validation plots into the right subfolders. Unknown project codes automatically get their own folder.

**Step 5: Convert to Prism format (optional)**
```bash
python3 smart_prism_converter_v3.py ../Projects/Piezo1_Adult/3_Results/Yoda_Only/Yoda_Only.xlsx
```
Repeat for each experiment folder you need.

---

## Checking Validation Plots

This is the most important quality control step. Never skip it.

**Good plot:**
- Red dots centered on contraction peaks
- Dots evenly spaced (regular rhythm)
- No dots on flat baseline noise
- No dots on sharp vertical spikes (artifacts)

**Bad plot -- tell Geoanna:**
- Dots on flat sections (false positives)
- Obvious contractions with no dots (missed peaks)
- Very few dots when tissue was clearly contracting

---

## What the Analyzer Measures (20 metrics)

You do not need to memorize these, but it helps to know what they mean when you see them in the Excel.

**How many and how often:**
- Num_Contractions -- total count in 150 seconds
- Frequency_cpm -- contractions per minute

**How strong:**
- Mean_Amplitude_mN -- average peak height
- Integral_Force_mN_sec -- total area under all contractions
- Force_Per_Contraction -- average work per contraction
- Force_Per_Minute -- contractile output rate

**How fast:**
- Time_to_Peak_sec -- how long to reach peak (rise time)
- Time_from_Peak_sec -- how long to relax from peak
- Rise_Fall_Ratio -- asymmetry of contraction shape
- dF_dt_max -- peak contraction velocity (mN/s)
- dF_dt_min -- peak relaxation velocity (mN/s)

**How regular:**
- Mean_Period_sec -- average time between contractions
- Period_CV_pct -- rhythm regularity (low = regular, high = irregular)

**How long each contraction lasts:**
- Mean_Duration_sec -- contraction width
- Duty_Cycle_pct -- fraction of time spent contracting

**Baseline properties:**
- Baseline_Tone_mN -- resting tension level
- Phasic_Tonic_Ratio -- contractile vs resting force balance
- Amp_Freq_Product -- simplified force estimate

---

## Expected Values (Adult WT Small Intestine)

| Condition | Contractions | Amplitude (mN) | Frequency (cpm) |
|-----------|-------------|-----------------|------------------|
| Baseline  | 70-90       | 0.15-0.40       | 28-36            |
| After Y2  | 40-85       | 0.06-0.15       | 16-34            |
| After RyR | 0-70        | 0.04-0.10       | 0-28             |
| After Thapsi | 0-85     | 0.06-0.15       | 0-34             |

These are approximate ranges. If your values are way outside these, check the validation plot before worrying.

---

## Excel Output Structure

The analyzer creates one Excel file with 2 sheets:

**Overall_Metrics** -- One row per file. Summary of the full 150-second window. Use for paired comparisons (Baseline vs Y2).

**10sec_Bins** -- Multiple rows per file (one per 10-second window). Shows how contractions change over time within a recording. Use for time-course graphs.

---

## When to Ask Geoanna

- Validation plot looks wrong
- Error messages when running commands
- Not sure what project code to use for a new experiment
- File naming does not fit the pattern above
- Contraction counts seem too high or too low
- You accidentally deleted or moved files to the wrong place

Do not try to fix problems yourself by editing the Excel or renaming processed files. Ask first.

---

## Adding a New Experiment Type

When Geoanna starts a new drug experiment, she assigns a project code (a short abbreviation). You just name your files with that code:

```
DATE_NEWCODE_Sex#_n#_Condition.txt
```

The organizer automatically creates a folder for unknown codes. If the code is already in the known list (R, Th, Px, KO, ShWT, sham), it maps to the friendly folder name. Otherwise it uses the code itself as the folder name.

No code changes needed. No guide update needed. Just use the code.
