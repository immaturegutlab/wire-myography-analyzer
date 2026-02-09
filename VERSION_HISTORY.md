# Version History -- Wire Myography Toolkit

## Current Versions (February 6, 2026)

| Component | Version | Status |
|-----------|---------|--------|
| myography_analyzer_v4.py | v4.0 | Production |
| myography_organizer_v2_2.py | v2.2 | Production |
| smart_prism_converter_v3.py | v3 (updated) | Production |

---

## myography_analyzer_v4.py

### v4.0 (February 2026) -- CURRENT
- 20 output metrics (streamlined from 34 in v3.1)
- 2-sheet Excel output: Overall_Metrics + 10sec_Bins
- Removed 30sec_Bins sheet
- Batch subfolders in 2_Processed: processed files grouped by run timestamp (renameable)
- Validated on 120+ files across multiple experiment types
- Force_Per_Contraction outlier warning: exclude files with <5 contractions
- Single-command project mode: `python3 myography_analyzer_v4.py path/to/Project`
- Fixed kinetics: corrected relaxation time (was inflated 5.3x) and rise time (inflated 32%)
- Width filter reduced from 0.6 to 0.3 seconds for faster contractions
- Detection: 0.05 mN threshold, 0.05 mN prominence, 1.0 sec distance, 150 sec window

### v3.1 (February 2026)
- 34 output metrics including FWHM, contraction work index, incomplete relaxation tracking
- 3-sheet Excel output: Overall_Metrics + 10sec_Bins + 30sec_Bins
- Single-command project mode introduced
- Filename whitespace stripping

### v3.0 (February 2026)
- Fixed-parameter detection for reproducibility
- Amplitude flagging system
- Comprehensive duty cycle and tonic metrics

### v2.9 (January 2026)
- Standardized ALL metrics to use FIRST 150 seconds
- Added per-contraction and per-minute normalized metrics
- Added contractility indices (amplitude x frequency)

### v2.8 (January 2026)
- Added inter-contraction interval calculation
- Added duty cycle (% time contracting)
- Added tonic contraction detection
- Added quiescent tone vs tonic force measurement

### v2.7 (January 2026) -- CRITICAL FIX
- **FIXED: Duration calculation error** (was 2x too large in v2.6)
- Improved rise/relax rate robustness
- Changed default PEAK_HEIGHT to 0.05 mN

### v2.6 and earlier
- DEPRECATED: Duration values are incorrect (2x too large)
- Do not use for new analyses

---

## myography_organizer_v2_2.py

### v2.2 (February 6, 2026) -- CURRENT
- **Generic project code detection**: extracts code from filename position instead of keyword matching
- Known codes map to friendly folder names: R -> Ryanodine, Th -> Thapsigargin, Px -> Paxilline, KO/ShWT/sham -> WT_vs_KO
- Unknown codes automatically create folders using the code itself (e.g., CPA -> CPA/)
- No code changes needed for new experiment types
- Single-argument mode: auto-finds most recent Excel in results folder
- Compatible with both 2-sheet (v4.0) and 3-sheet (v3.1) Excel structure

### v2.1 (February 2026)
- Added Paxilline category (Px_, Pax, PrePax, PostPax keywords)
- Single-argument mode introduced
- Auto-creates experiment folders with mkdir(parents=True)

### v2.0 (February 2026)
- Keyword-based classification: Ryanodine, Thapsigargin, WT_vs_KO, Yoda_Only
- Copies validation plots to experiment subfolders
- Compatible with 2-sheet and 3-sheet Excel

### v1.4 and earlier
- 3-sheet only support
- Hardcoded experiment categories

---

## smart_prism_converter_v3.py

### v3 updated (February 6, 2026) -- CURRENT
- **Generic Pre/Post condition detection**: any condition starting with Pre or Post automatically becomes a separate column (e.g., PrePax, PostPax, PreRyan, PostThap)
- **Generic project code parsing**: Pattern 3 accepts any alphanumeric code, not a hardcoded list
- **Fixed doubled-date bug**: Px_ and other new codes no longer cause date duplication in subject IDs
- Percent change columns auto-generated for all non-Baseline conditions
- Condition column order: Baseline | Pre[Drug] | Treatment | Y2 | Post[Drug]

### v3 original (February 2026)
- Auto-detects conditions from filenames
- Recognizes experiment markers: R_, Th_, KO_, WT_, ShWT_, sham_
- Groups by age, then by sex
- Calculates animal averages from technical replicates
- Computes percent change from baseline
- 10-second bin sheets for temporal data
- Source data preservation in SRC_ sheets

### v2 (January 2026)
- Yoda-to-Prism format only
- Manual subject ID assignment
- Single condition support (Baseline + Y2)

---

## Compatibility Matrix

| Analyzer | Organizer | Prism Converter | Notes |
|----------|-----------|-----------------|-------|
| v4.0 | v2.2 | v3 (updated) | Current recommended |
| v4.0 | v2.1 | v3 (original) | Works but Px_ may misparse in converter |
| v3.1 | v2.0+ | v3 | 3-sheet Excel, all tools compatible |
| v2.9 | v1.4 | v2 | Legacy, do not use for new work |

---

## Breaking Changes Log

| Version | Change | Impact |
|---------|--------|--------|
| Analyzer v4.0 | Reduced from 34 to 20 metrics, removed 30sec_Bins | Older organizers that expect 3 sheets still work (graceful fallback) |
| Analyzer v2.7 | Duration fix (2x correction) | All data from v2.6 and earlier must be reanalyzed or manually corrected |
| Converter v3 (updated) | Pre/Post split into separate columns | Paxilline data from original v3 had PrePax/PostPax collapsed into "Treatment" -- re-run converter |
