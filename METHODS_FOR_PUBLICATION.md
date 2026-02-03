# Methods Section: Wire Myography Contractility Analysis

## For Publication -- Immature Gut Biology Lab, UC Davis

Version: 3.1 (February 2026)

---

## Full Methods Text

### Contractility Data Acquisition

Segments of murine small intestine (approximately 2-3 mm in length) were mounted on a wire myograph (DMT620M, Danish Myo Technology, Denmark) in Krebs-Ringer bicarbonate solution maintained at 37C and continuously bubbled with 95% O2/5% CO2. Tissues were equilibrated under 5 mN resting tension for 30 minutes before recordings began. Spontaneous contractile activity was recorded continuously using LabChart software (ADInstruments, Colorado Springs, CO) at a sampling rate of 250 Hz. Force data were exported as tab-delimited text files for offline analysis.

### Experimental Protocols

[ADAPT TO YOUR SPECIFIC EXPERIMENTS]

**Piezo1 mechanosensitivity:** Following stable baseline recording (150 seconds), the Piezo1 agonist Yoda2 (25 uM) was applied to the bath. Post-drug contractile activity was recorded for an additional 150 seconds.

**Ryanodine calcium store depletion:** After baseline recording, ryanodine (100 uM) was applied to deplete intracellular calcium stores via ryanodine receptor blockade. Post-drug activity was recorded, followed by washout and a second Yoda2 application to assess remaining mechanosensitivity.

**Thapsigargin calcium store depletion:** Thapsigargin (10 uM) was applied to inhibit SERCA-mediated calcium reuptake into the sarcoplasmic reticulum. Post-drug activity was recorded, followed by a Yoda2 application.

### Automated Contraction Detection and Analysis

Contractile activity was analyzed using Wire Myography Analyzer v3.1, a custom Python application (Python 3.x) utilizing NumPy, SciPy, and Pandas libraries. Automated peak detection was performed on raw force traces using SciPy's `find_peaks` algorithm with the following empirically validated parameters:

- Minimum peak prominence: 0.05 mN (local peak height relative to surrounding baseline)
- Minimum peak height: 0.05 mN (absolute height above calculated baseline)
- Minimum inter-peak distance: 1.0 second (250 samples at 250 Hz)
- Minimum peak width: 0.3 seconds (75 samples at 250 Hz)

These parameters were optimized for murine intestinal smooth muscle physiology through systematic testing across recordings from multiple developmental ages (P7 through adult), genotypes (wild-type and ICC-specific Piezo1 knockout), sexes, and pharmacological conditions. The minimum peak width filter (0.3 seconds) was calibrated to exclude electrical noise spikes while retaining faster physiological contractions observed in drug-treated and developing tissues.

### Baseline Calculation

Baseline tone for each recording was calculated as the 10th percentile of the force signal within the analysis window, providing a robust estimate of the relaxed state resistant to outliers from transient contractions or movement artifacts.

### Analysis Window Standardization

To ensure fair comparisons across recordings and experimental conditions, all metrics were calculated from a standardized 150-second analysis window beginning at the start of each recording segment. This approach avoids confounding effects from contractile rundown that occurs in longer ex vivo recordings and ensures equivalent sampling duration across all conditions.

### Contractility Metrics

For each recording, the following metrics were computed:

**Frequency and amplitude:** Contraction frequency was calculated as the number of detected peaks per minute (contractions per minute, cpm). Mean amplitude was defined as the average peak force relative to the calculated baseline (mN). Amplitude variability was expressed as the coefficient of variation (CV%) of peak amplitudes.

**Temporal parameters:** Mean contractile period was calculated as the average time between successive contraction peaks (seconds). Period variability (CV%) quantified rhythmicity, with higher values indicating more irregular contraction patterns.

**Contraction kinetics:** For each detected contraction, start and end boundaries were identified at 10% of peak amplitude above baseline. From these boundaries: total contraction duration (start to end, seconds), rise time (start to peak, seconds), relaxation time (peak to end, seconds), rise rate (amplitude divided by rise time, mN/second), and relaxation rate (amplitude divided by relaxation time, mN/second) were calculated. Width at half-maximum (FWHM) provided an independent measure of contraction duration at 50% of peak amplitude.

**Integral and tonic metrics:** Total integral force (mN-seconds) was calculated by trapezoidal integration of the force signal above baseline. Baseline tone (mN) represented the resting force level. Duty cycle (%) quantified the fraction of time the tissue spent in active contraction versus quiescence. Incomplete relaxation events, where the force between contractions did not return below 10% of peak amplitude, were quantified to assess tonic contraction behavior.

**Derived indices:** Amplitude-frequency product (mN x cpm) provided a composite measure of contractile output. Contraction work index (integral force per contraction, mN-seconds) quantified the mechanical work per contractile event. Force per minute (mN-seconds/min) normalized total contractile output to time.

### Time-Resolved Analysis

To capture dynamic changes in contractility during drug application or washout, all metrics were additionally calculated in 10-second time bins across the 150-second analysis window. This temporal resolution enabled visualization of onset kinetics, progressive effects, and recovery patterns following pharmacological interventions.

### Biological vs. Technical Replicates

Multiple tissue segments (technical replicates) from the same animal were averaged to produce a single value per animal per condition before group-level statistical analysis. This approach ensures that the experimental unit (n) represents biological replicates (individual animals) rather than inflated counts from multiple segments.

### Quality Control

Automated validation plots were generated for every recording, displaying the full force trace with detected peaks marked, the calculated baseline, and the detection threshold. All plots were visually inspected to confirm accurate peak identification. Recordings with significant movement artifacts, unstable baselines, or equipment malfunctions were excluded from analysis.

### Statistical Analysis

[ADAPT TO YOUR STATISTICAL APPROACH]

Data are presented as mean +/- SEM. For within-subject comparisons (baseline vs. drug treatment in the same tissue), paired Student's t-tests were used. For between-group comparisons (e.g., male vs. female, wild-type vs. knockout), unpaired Student's t-tests (two groups) or one-way ANOVA with Tukey's HSD post-hoc test (three or more groups) were performed. Percent change from baseline was calculated for each tissue segment to normalize for inter-animal variability. Statistical significance was set at P < 0.05. Statistical analyses and graphing were performed using GraphPad Prism (version [X]).

### Data and Code Availability

The Wire Myography Analyzer source code and documentation are available at [GitHub repository URL / Zenodo DOI]. Raw LabChart recordings and processed data files are available from the corresponding author upon reasonable request.

---

## Condensed Version (for space-limited journals)

Spontaneous contractile activity of intestinal segments mounted on a wire myograph (DMT620M) was recorded at 250 Hz using LabChart (ADInstruments). Contractions were detected using automated peak detection (Wire Myography Analyzer v3.1; SciPy find_peaks) with validated parameters: prominence and height thresholds of 0.05 mN, minimum inter-peak distance of 1.0 second, and minimum peak width of 0.3 seconds. Metrics including contraction frequency (cpm), amplitude (mN), period (seconds), and kinetic parameters (duration, rise time, relaxation time, rise and relaxation rates) were calculated from standardized 150-second analysis windows. Time-resolved analysis was performed in 10-second bins. Technical replicates from the same animal were averaged before statistical comparison. All detected peaks were visually validated. Data are mean +/- SEM; P < 0.05 considered significant. Analysis code is available at [repository URL].

---

## Parameter Summary Table

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sampling rate | 250 Hz | LabChart acquisition setting |
| Peak prominence | 0.05 mN | Minimum local height to distinguish from noise |
| Peak height | 0.05 mN | Absolute threshold above baseline |
| Minimum peak distance | 1.0 sec (250 samples) | Physiological minimum for intestinal contractions |
| Minimum peak width | 0.3 sec (75 samples) | Excludes electrical noise; retains fast contractions |
| Analysis window | 150 sec | Avoids rundown; standardizes comparisons |
| Bin duration | 10 sec | Temporal resolution for drug onset/offset |
| Baseline method | 10th percentile | Robust to outlier contractions |
| Kinetic boundaries | 10% of peak amplitude | Standard threshold for contraction start/end |

---

## Software Citation

> Contractile parameters were extracted using Wire Myography Analyzer v3.1 (Bautista G, Immature Gut Biology Lab, UC Davis), a custom Python application implementing scipy.signal.find_peaks for contraction detection, pandas for data management, and matplotlib for visualization. Source code is available at [repository URL].

---

## Reviewer FAQ

**"How were detection parameters validated?"**
Parameters were empirically optimized by systematic testing across recordings spanning multiple developmental ages (P7 through adult), both sexes, wild-type and knockout genotypes, and multiple pharmacological conditions. Validation plots for every recording were visually inspected to confirm detection accuracy.

**"What about movement artifacts?"**
The minimum peak width filter (0.3 seconds) excludes sharp electrical or mechanical spikes. The minimum inter-peak distance (1.0 second) prevents double-counting. Visual validation of all recordings provides a final quality check, and recordings with significant artifacts were excluded.

**"Why 10th percentile for baseline?"**
The 10th percentile is robust to outliers and represents the true relaxed state more reliably than the minimum (which may capture transient dips) or the mean (which is pulled upward by contractions).

**"Why a 150-second analysis window?"**
Ex vivo intestinal preparations exhibit contractile rundown over extended recording periods. The first 150 seconds provides consistent baseline measurements and sufficient duration for accurate frequency and kinetic calculations while avoiding late-recording amplitude decline.

**"How do you handle tissues with very low amplitude contractions (e.g., after drug treatment)?"**
Recordings where mean amplitude falls below 0.03 mN are flagged for manual review but not automatically excluded. This allows detection of genuine low-amplitude activity while alerting the investigator to potential noise contamination in the measurement.

**"Are the kinetics measurements validated?"**
Rise time and relaxation time are calculated from contraction boundaries defined at 10% of peak amplitude, a standard electrophysiology convention. Width at half-maximum (FWHM) provides an independent kinetic measurement for cross-validation.

---

## Notes for Specific Study Types

**Piezo1 mechanosensitivity studies:**
Emphasize that detection parameters were sensitive enough to capture drug-induced changes in contraction amplitude and kinetics, not just frequency. The 0.05 mN threshold allows detection of weakened contractions following Piezo1 agonist application.

**Genotype comparisons (WT vs. KO):**
Note that irregular contraction patterns in knockout mice (reflected by higher period CV%) represent biological phenotype, not detection error. The analyzer's quality flagging system identifies recordings that may need manual review.

**Developmental studies (neonatal vs. adult):**
The 0.05 mN default threshold works across developmental ages. For very early neonatal tissue (P7) with extremely weak contractions, the threshold can be lowered to 0.03 mN via command-line parameter.

**Calcium handling studies (Ryanodine/Thapsigargin):**
When calcium store depletion abolishes contractions, the amplitude threshold prevents counting of baseline noise as contractile events. Zero-contraction recordings are reported as such rather than generating artifactual data.
