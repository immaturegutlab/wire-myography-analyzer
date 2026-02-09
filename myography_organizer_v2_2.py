#!/usr/bin/env python3
"""
Myography Organizer v2.2 - Splits master Excel by experiment type
Works with 2-sheet (v4.0) or 3-sheet (v3.1) Excel structure

Auto-detects project codes from filenames. Known codes get friendly names,
unknown codes automatically create new folders -- no code changes needed.

Author: Geoanna Bautista, Immature Gut Biology Lab
Version: 2.2
Date: February 2026
"""

import pandas as pd
from pathlib import Path
import shutil
import sys
import re

# Known project codes -> friendly folder names
# If a code is NOT here, the code itself becomes the folder name
KNOWN_CODES = {
    'R':    'Ryanodine',
    'Th':   'Thapsigargin',
    'Px':   'Paxilline',
    'KO':   'WT_vs_KO',
    'ShWT': 'WT_vs_KO',
    'sham': 'WT_vs_KO',
}

def extract_project_code(filename):
    """
    Extract project code from filename.
    
    Pattern: DATE_CODE_Sex#_n#_Condition
    Examples:
        20251015_Px_Male1_n2_Baseline  -> 'Px'
        20251001_R_Female1_n3_Y2       -> 'R'
        20251001_Male1_n1_Baseline     -> None (no code)
        20251001_CPA_Male1_n1_Y2       -> 'CPA' (unknown, auto-creates folder)
    """
    # After the 8-digit date and underscore, look for a code before Sex
    # Code is anything that is NOT a sex indicator (Male/Female/M/F followed by digit)
    match = re.match(
        r'\d{8}_'                                    # date
        r'([A-Za-z][A-Za-z0-9]*)_'                   # candidate code (starts with letter)
        r'(?:Male|Female|M|F)\d',                     # followed by sex indicator
        filename, re.IGNORECASE
    )
    if match:
        code = match.group(1)
        # Make sure it's actually a code, not the sex itself
        if code.upper() not in ['MALE', 'FEMALE', 'M', 'F']:
            return code
    return None

def classify_file(filename):
    """
    Classify file by project code extracted from filename.
    
    Known codes -> friendly folder name (e.g., R -> Ryanodine)
    Unknown codes -> code used as folder name (e.g., CPA -> CPA)
    No code -> Yoda_Only
    """
    code = extract_project_code(filename)
    if code is None:
        return 'Yoda_Only'
    
    # Check known mappings (case-insensitive lookup)
    for known_code, folder_name in KNOWN_CODES.items():
        if code.lower() == known_code.lower():
            return folder_name
    
    # Unknown code: use as-is for folder name
    return code


def organize_results(master_excel, output_base):
    """
    Organize master Excel and validation plots by experiment type
    
    Parameters:
    -----------
    master_excel : str or Path
        Path to master Excel file
    output_base : str or Path
        Base folder where experiment folders will be created (usually same folder as master Excel)
    """
    master_excel = Path(master_excel)
    output_base = Path(output_base)
    
    print("="*80)
    print("MYOGRAPHY ORGANIZER v2.2")
    print("="*80)
    print(f"\nMaster Excel: {master_excel}")
    print(f"Output base: {output_base}\n")
    
    if not master_excel.exists():
        print(f"âŒ ERROR: Excel file not found: {master_excel}")
        return False
    
    # Read sheets (v4.0 has 2 sheets; older versions had 3)
    print("Reading Excel sheets...")
    try:
        df_overall = pd.read_excel(master_excel, sheet_name='Overall_Metrics')
        df_bins_10s = pd.read_excel(master_excel, sheet_name='10sec_Bins')
        xlsx_sheets = pd.ExcelFile(master_excel).sheet_names
        if '30sec_Bins' in xlsx_sheets:
            df_bins_30s = pd.read_excel(master_excel, sheet_name='30sec_Bins')
            has_30s = True
        else:
            df_bins_30s = None
            has_30s = False
        n_sheets = 3 if has_30s else 2
        print(f"âœ“ Loaded {n_sheets} sheets successfully\n")
    except Exception as e:
        print(f"âŒ ERROR reading Excel: {e}")
        return False
    
    # Get unique filenames
    all_filenames = df_overall['Filename'].unique()
    print(f"Total files: {len(all_filenames)}\n")
    
    # Classify files
    file_classification = {}
    for filename in all_filenames:
        experiment = classify_file(filename)
        if experiment not in file_classification:
            file_classification[experiment] = []
        file_classification[experiment].append(filename)
    
    # Print classification summary
    print("Classification Summary:")
    print("-" * 80)
    for experiment, files in sorted(file_classification.items()):
        print(f"  {experiment}: {len(files)} files")
    print("-" * 80 + "\n")
    
    # Create organized folders
    for experiment, filenames in file_classification.items():
        print(f"Processing {experiment}...")
        
        # Create experiment folder
        exp_folder = output_base / experiment
        exp_folder.mkdir(parents=True, exist_ok=True)
        
        plots_subfolder = exp_folder / 'validation_plots'
        plots_subfolder.mkdir(exist_ok=True)
        
        # Filter each sheet for this experiment's files
        exp_overall = df_overall[df_overall['Filename'].isin(filenames)].copy()
        exp_bins_10s = df_bins_10s[df_bins_10s['Filename'].isin(filenames)].copy()
        exp_bins_30s = df_bins_30s[df_bins_30s['Filename'].isin(filenames)].copy() if has_30s else None
        
        # Create experiment-specific Excel with 3 sheets
        exp_excel_path = exp_folder / f"{experiment}.xlsx"
        with pd.ExcelWriter(exp_excel_path, engine='openpyxl') as writer:
            exp_overall.to_excel(writer, sheet_name='Overall_Metrics', index=False)
            exp_bins_10s.to_excel(writer, sheet_name='10sec_Bins', index=False)
            if has_30s and exp_bins_30s is not None:
                exp_bins_30s.to_excel(writer, sheet_name='30sec_Bins', index=False)
        
        print(f"  âœ“ Created {experiment}.xlsx with {n_sheets} sheets ({len(filenames)} files)")
        
        # Copy validation plots
        plots_source = output_base / 'validation_plots'
        if plots_source.exists():
            copied_plots = 0
            for filename in filenames:
                # Plot filename is [filename]_validation.png
                plot_file = f"{filename}_validation.png"
                source_plot = plots_source / plot_file
                
                if source_plot.exists():
                    dest_plot = plots_subfolder / plot_file
                    try:
                        shutil.copy2(str(source_plot), str(dest_plot))
                        copied_plots += 1
                    except Exception as e:
                        print(f"  âš ï¸  Could not copy {plot_file}: {e}")
            
            print(f"  âœ“ Copied {copied_plots} validation plots\n")
        else:
            print(f"  âš ï¸  No validation_plots folder found\n")
    
    # Summary
    print("="*80)
    print("ORGANIZATION COMPLETE!")
    print("="*80)
    print(f"\nOrganized into {len(file_classification)} experiment folders:")
    for experiment, files in sorted(file_classification.items()):
        folder_path = output_base / experiment
        print(f"\n  {experiment}/")
        print(f"    â”œâ”€â”€ {experiment}.xlsx ({n_sheets} sheets, {len(files)} files)")
        print(f"    â””â”€â”€ validation_plots/ ({len(files)} plots)")
    
    print("\n" + "="*80)
    print("\nâœ… Ready for analysis!")
    print(f"\nOpen experiment Excel files in: {output_base}/[Experiment]/")
    print("="*80 + "\n")
    
    return True


def main():
    """Main entry point"""
    
    if len(sys.argv) == 2:
        # Single argument: treat as folder, auto-find the Excel file
        folder = Path(sys.argv[1])
        if folder.is_dir():
            excels = sorted(folder.glob("Myography_Analysis_*.xlsx"))
            if len(excels) == 0:
                print(f"\nERROR: No Myography_Analysis_*.xlsx found in {folder}")
                sys.exit(1)
            if len(excels) > 1:
                print(f"\nMultiple analysis files found, using most recent:")
                for e in excels:
                    print(f"  {e.name}")
            master_excel = str(excels[-1])
            output_base = str(folder)
            print(f"Found: {excels[-1].name}")
        else:
            print(f"\nERROR: {folder} is not a directory")
            sys.exit(1)
    elif len(sys.argv) == 3:
        master_excel = sys.argv[1]
        output_base = sys.argv[2]
    else:
        print("\nUsage:")
        print("  python3 myography_organizer_v2_1.py [results_folder]")
        print("  python3 myography_organizer_v2_1.py [master_excel] [output_folder]")
        print("\nExamples:")
        print("  python3 myography_organizer_v2_1.py Projects/Piezo1_Adult/3_Results")
        print("  python3 myography_organizer_v2_1.py Results/Myography_Analysis_20260101.xlsx Results/")
        sys.exit(1)
    
    success = organize_results(master_excel, output_base)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
