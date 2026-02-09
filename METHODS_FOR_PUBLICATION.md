# METHODS SECTION - Wire Myography Analysis

## For Publication in Methods Section

---

## Contractility Data Acquisition and Analysis

### Tissue Preparation and Recording
Segments of small intestine (approximately 2-3 mm in length) were mounted on a wire myograph (DMT620M, Danish Myo Technology, Denmark) in Krebs-Ringer solution maintained at 37Â°C and continuously bubbled with 95% Oâ‚‚/5% COâ‚‚. Tissues were equilibrated under 5 mN resting tension for 30 minutes before baseline recordings. Spontaneous contractile activity was recorded continuously using LabChart software (ADInstruments) at a sampling rate of 250 Hz.

### Experimental Protocol
[ADAPT THIS SECTION TO YOUR SPECIFIC EXPERIMENTS]

Following baseline recording, tissues were exposed to [drug/treatment]. For mechanosensitivity experiments, [describe your mechanical stretch protocol]. For calcium handling experiments, tissues were treated with [ryanodine/thapsigargin concentrations]. For Piezo1 agonist experiments, Yoda2 (25 ÂµM) was applied following stable baseline recordings.

### Contraction Detection and Quantification
Contractile activity was analyzed using custom Python scripts (Python 3.x with NumPy, SciPy, and Pandas libraries). Raw force traces were exported from LabChart as tab-delimited text files containing time and force data. Automated peak detection was performed using SciPy's `find_peaks` function with the following validated criteria:

**Detection Parameters:**
- Peak height: >=0.05 mN (absolute height above baseline)
- Peak prominence: >=0.05 mN (local peak height relative to surrounding baseline)
- Minimum peak distance: 250 samples (1.0 second at 250 Hz sampling rate)
- Minimum peak width: 75 samples (0.3 seconds)
- Analysis window: first 150 seconds of each recording

These parameters were empirically optimized to reliably detect physiological contractions while filtering baseline noise and movement artifacts.

### Baseline Calculation
The baseline tone for each recording was calculated as the 10th percentile of the force signal, providing a robust estimate of the relaxed state that is resistant to outliers and transient contractions.

### Overall Contractility Metrics
For each recording, the following metrics were calculated:

**Frequency and Amplitude:**
- Contraction frequency: Number of detected peaks per minute (contractions per minute, cpm)
- Mean amplitude: Average peak force relative to baseline (mN)
- Amplitude variability: Coefficient of variation (CV%) of peak amplitudes

**Temporal Parameters:**
- Mean period: Average time between successive contractions (seconds)
- Period variability: Coefficient of variation (CV%) of inter-contraction intervals

**Contraction Kinetics:**
Kinetic parameters were calculated for each contraction by detecting contraction start and end points at 10% of peak amplitude:
- Duration: Total contraction time from start to end (seconds)
- Rise time: Time from contraction start to peak (seconds)
- Relaxation time: Time from peak to contraction end (seconds)
- Rise/fall ratio: Ratio of rise time to relaxation time (dimensionless)
- Maximum contraction rate (dF/dt max): Peak rate of force development (mN/second)
- Maximum relaxation rate (dF/dt min): Peak rate of force decline (mN/second)

**Integral and Normalized Metrics:**
- Total integral force: Area under the force-time curve above baseline (mN*seconds), calculated using trapezoidal integration
- Force per contraction: Total integral divided by number of contractions (mN*seconds)
- Force per minute: Total integral normalized to recording duration (mN*seconds/min)
- Duty cycle: Percentage of recording time spent in active contraction (%)

**Tonic Properties:**
- Baseline tone: Resting force level, 10th percentile of force signal (mN)
- Phasic/tonic ratio: Ratio of phasic contractile force to tonic baseline force
- Incomplete relaxation: Percentage of contractions where the trough before next contraction remains above baseline + 10% of amplitude (%)

### Time-Resolved Analysis
To assess temporal changes in contractility (e.g., during drug washout or following interventions), metrics were also calculated in 10-second time bins throughout each recording. This binned analysis included amplitude, frequency, period, contraction duration, rise time, and relaxation time, allowing visualization of dynamic changes in contractile behavior.

### Quality Control and Validation
All detected peaks were visually validated using automatically generated validation plots showing the full force trace with detected peaks marked. A zoomed view of the first 60 seconds was included to verify accurate detection of individual contractions. Recordings with significant movement artifacts or unstable baselines were excluded from analysis.

### Statistical Analysis
[ADAPT THIS SECTION TO YOUR STATISTICAL APPROACH]

Data are presented as mean Â± SEM. For paired comparisons (e.g., baseline vs. drug treatment in the same tissue), paired Student's t-tests were used. For comparisons between genotypes or treatment groups, unpaired Student's t-tests or one-way ANOVA with post-hoc tests were performed as appropriate. Statistical significance was set at P < 0.05. All statistical analyses were performed using GraphPad Prism [version].

### Data and Code Availability
The Python analysis scripts used in this study are available at [GitHub repository / supplementary materials]. Raw LabChart files and processed data are available upon reasonable request.

---

## Alternative Condensed Version (for space-limited journals):

### Contractility Analysis
Spontaneous contractile activity of intestinal segments mounted on a wire myograph was recorded at 250 Hz using LabChart (ADInstruments). Contractions were detected using automated peak detection (SciPy find_peaks) with validated parameters: prominence >=0.05 mN, height >=0.05 mN, minimum spacing 1.0 second, minimum width 0.3 seconds, standardized to the first 150 seconds of each recording. Metrics calculated included contraction frequency (cpm), amplitude (mN), period (seconds), and kinetic parameters (duration, rise time, relaxation time). Time-resolved analysis was performed in 10-second bins. All detected peaks were visually validated. Statistical comparisons were made using [appropriate tests]. Data are mean Â± SEM; P < 0.05 considered significant.

---

## Key Points for Methods Section:

### What to Include:
âœ… Sampling rate (250 Hz)
âœ… Detection algorithm (SciPy find_peaks)
âœ… Detection parameters with justification
âœ… Baseline calculation method
âœ… Metrics calculated
âœ… Quality control approach
âœ… Statistical methods

### What to Cite:
- LabChart software (ADInstruments)
- Python libraries (NumPy, SciPy, Pandas)
- Wire myograph system (DMT or equivalent)
- Statistical software (GraphPad Prism or equivalent)

### Optional Supplementary Information:
- Full Python code
- Example validation plots
- Parameter optimization details
- Comparison with manual analysis

---

## Suggested Figures for Methods:

**Figure/Supplementary Figure:**
"Representative force trace showing automated contraction detection"
- Panel A: Full 2-minute baseline recording with detected peaks marked
- Panel B: Zoomed view showing individual contraction with kinetic measurements (duration, rise time, relaxation time) annotated
- Panel C: Example of rejected artifact (sharp vertical spike)
- Panel D: Validation of automated vs. manual detection (correlation plot)

---

## Common Reviewer Questions - Be Prepared to Address:

1. **"How were detection parameters validated?"**
   â†’ Systematic testing on subset of recordings, comparison with manual counting, optimization to minimize false positives/negatives

2. **"What about movement artifacts?"**
   â†’ Visual validation of all recordings, exclusion criteria, minimum distance requirement filters rapid artifacts

3. **"Why 10th percentile for baseline?"**
   â†’ Robust to outliers, represents true relaxed state, less sensitive to occasional deep relaxations than minimum value

4. **"How reproducible is the method?"**
   â†’ Analysis of same file produces identical results (fully automated), technical replicates show expected similarity

5. **"Why these specific parameter values?"**
   â†’ Optimized for intestinal smooth muscle physiology (typical contraction duration ~1-2 sec, frequency 20-30 cpm), validated across multiple recordings and conditions

---

## Notes for Your Specific Paper:

**If studying Piezo1:**
Emphasize that detection parameters were optimized to capture potential drug-induced changes in contraction frequency/kinetics, not just baseline activity.

**If comparing genotypes:**
Note that irregular contractions in knockout mice (higher CV%) represent biological variability, not detection errors.

**If studying development:**
May need to mention if different parameters were used for neonatal tissue (if you end up needing different settings).

**If studying calcium handling:**
Emphasize that amplitude threshold prevents counting baseline noise when contractions are abolished by calcium store depletion.

---

**This methods section can be adapted to your specific journal's requirements and word limits.**
