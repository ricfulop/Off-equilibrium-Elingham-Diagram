#!/usr/bin/env python3
"""
JANAF Scraper Monitor
Monitors the progress of the full JANAF database extraction
"""

import time
import os
import pickle
from datetime import datetime

def check_progress():
    """Check the progress of the scraper"""
    print("="*80)
    print("JANAF SCRAPER PROGRESS MONITOR")
    print("="*80)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if the scraper is still running
    scraper_processes = []
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'janaf_scraper.py' in line and 'python3' in line:
                scraper_processes.append(line.strip())
    except:
        pass
    
    if scraper_processes:
        print("✓ Scraper is running")
        for process in scraper_processes:
            print(f"  Process: {process}")
    else:
        print("✗ Scraper is not running")
    
    print()
    
    # Check for output files
    files_to_check = [
        'janaf_full_database.pkl',
        'janaf_test_database.pkl',
        'janaf_categorized_data.pkl'
    ]
    
    print("File Status:")
    for filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
            print(f"✓ {filename}: {size:,} bytes (modified: {mod_time.strftime('%H:%M:%S')})")
            
            # Try to load and analyze the data
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                
                if isinstance(data, dict):
                    total_compounds = sum(len(compounds) for compounds in data.values())
                    print(f"  Elements: {len(data)}")
                    print(f"  Total compounds: {total_compounds}")
                    
                    # Show breakdown by element
                    print("  Breakdown by element:")
                    for element, compounds in sorted(data.items()):
                        print(f"    {element}: {len(compounds)} compounds")
                else:
                    print(f"  Data type: {type(data)}")
                    
            except Exception as e:
                print(f"  Error loading data: {e}")
        else:
            print(f"✗ {filename}: Not found")
    
    print()
    
    # Estimate progress
    expected_elements = 38
    expected_compounds = 4459
    
    if os.path.exists('janaf_full_database.pkl'):
        try:
            with open('janaf_full_database.pkl', 'rb') as f:
                data = pickle.load(f)
            
            elements_done = len(data)
            compounds_done = sum(len(compounds) for compounds in data.values())
            
            element_progress = (elements_done / expected_elements) * 100
            compound_progress = (compounds_done / expected_compounds) * 100
            
            print("Progress Estimation:")
            print(f"Elements: {elements_done}/{expected_elements} ({element_progress:.1f}%)")
            print(f"Compounds: {compounds_done:,}/{expected_compounds:,} ({compound_progress:.1f}%)")
            
            if elements_done > 0:
                avg_compounds_per_element = compounds_done / elements_done
                remaining_elements = expected_elements - elements_done
                estimated_remaining_compounds = remaining_elements * avg_compounds_per_element
                print(f"Estimated remaining compounds: {estimated_remaining_compounds:.0f}")
                
        except Exception as e:
            print(f"Error analyzing progress: {e}")

def main():
    """Main monitoring function"""
    while True:
        check_progress()
        print("\nPress Ctrl+C to stop monitoring")
        print("="*80)
        
        try:
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break

if __name__ == "__main__":
    main()

