# Wire Myography Workflow Guide

## Quick Decision Tree

```
Do you have MIXED experiment types in one project folder?
(e.g., Ryanodine + Thapsigargin + WT_vs_KO files together)

YES → Use Organizer first, then Prism Converter on each
NO  → Go straight to Prism Converter
```

---

## Workflow A: Single Experiment Type (Most Common)

All your files are the same experiment (e.g., all Ryanodine, or all just Baseline vs Y2).

```bash
cd MyographyTools

# Step 1: Analyze
python3 myography_analyzer.py ../Projects/MyProject

# Step 2: Convert to Prism format
python3 smart_prism_converter_v3.py "../Projects/MyProject/3_Results/Myography_Analysis_*.xlsx"
```

Output: `Myography_Analysis_*_Prism.xlsx` ready for GraphPad Prism

---

## Workflow B: Mixed Experiment Types

Your 1_RawData has files from different experiments mixed together.

```bash
cd MyographyTools

# Step 1: Analyze (same as before)
python3 myography_analyzer.py ../Projects/MyProject

# Step 2: Organize by experiment type
python3 myography_organizer.py ../Projects/MyProject/3_Results ../Projects/MyProject

# Step 3: Convert each experiment to Prism format
python3 smart_prism_converter_v3.py ../Projects/MyProject/3_Results/Ryanodine/Ryanodine.xlsx
python3 smart_prism_converter_v3.py ../Projects/MyProject/3_Results/Thapsigargin/Thapsigargin.xlsx
```

Output: Separate `_Prism.xlsx` files for each experiment type

---

## What Each Script Does

| Script | Input | Output | When to Use |
|--------|-------|--------|-------------|
| `myography_analyzer.py` | Raw .txt files | Master Excel + plots | Always first |
| `myography_organizer.py` | Master Excel | Separate Excel per experiment | Mixed experiments only |
| `smart_prism_converter_v3.py` | Any analyzer Excel | Prism-ready Excel | Before Prism |

---

## Supported Filename Formats

The Prism converter recognizes these patterns:

| Format | Example | Detected As |
|--------|---------|-------------|
| Age + Sex | `20251216_P7NEO_Male1_n1_Baseline` | P7_M1 |
| Age + Sex | `20251216_ADULT_Female2_n1_Y2` | ADULT_F2 |
| Experiment + Sex | `20251216_R_Male1_n1_Baseline` | ADULT_M1 |
| Experiment + Sex | `20251216_Th_Female1_n1_Thapsi10` | ADULT_F1 |
| Simple | `20251216_Male1_n1_Baseline` | ADULT_M1 |

The organizer classifies by these keywords:
- **Ryanodine**: `R_`, `RyR`, `Ryanodine`
- **Thapsigargin**: `Th_`, `Thapsi`, `Thapsigargin`
- **WT_vs_KO**: `KO`, `ShWT`, `sham`
- **Yoda_Only**: Everything else (catch-all)

---

## Folder Structure

```
MyProject/
  1_RawData/           ← Put .txt files here
  2_Processed/         ← Files move here after analysis
  3_Results/
    Myography_Analysis_*.xlsx     ← Master output
    validation_plots/             ← Check these!
    Ryanodine/                    ← If organized
      Ryanodine.xlsx
      Ryanodine_Prism.xlsx
      validation_plots/
    Thapsigargin/                 ← If organized
      Thapsigargin.xlsx
      Thapsigargin_Prism.xlsx
      validation_plots/
```
