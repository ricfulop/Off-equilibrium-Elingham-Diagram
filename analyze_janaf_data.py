#!/usr/bin/env python3
"""
JANAF Data Analysis Script
Analyzes and categorizes scraped JANAF thermodynamic data
"""

import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Set
import re

def load_janaf_data(filename: str = "janaf_test_database.pkl") -> Dict:
    """Load scraped JANAF data"""
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        print(f"Loaded data for {len(data)} elements")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def categorize_compounds(data: Dict) -> Dict[str, List]:
    """Categorize compounds into oxides, carbides, nitrides, and others"""
    categories = {
        'oxides': [],
        'carbides': [],
        'nitrides': [],
        'halides': [],
        'hydrides': [],
        'pure_elements': [],
        'other': []
    }
    
    for element, compounds in data.items():
        for compound_data in compounds:
            compound_info = compound_data['compound']
            name = compound_info['name'].lower()
            formula = compound_info['formula'].lower()
            
            # Categorize based on name and formula
            if 'oxide' in name or 'o' in formula:
                categories['oxides'].append(compound_data)
            elif 'carbide' in name or 'c' in formula:
                categories['carbides'].append(compound_data)
            elif 'nitride' in name or 'n' in formula:
                categories['nitrides'].append(compound_data)
            elif any(halogen in name for halogen in ['fluoride', 'chloride', 'bromide', 'iodide']):
                categories['halides'].append(compound_data)
            elif 'hydride' in name or 'h' in formula:
                categories['hydrides'].append(compound_data)
            elif element.lower() in name and len(name.split()) == 1:
                categories['pure_elements'].append(compound_data)
            else:
                categories['other'].append(compound_data)
    
    return categories

def analyze_thermodynamic_data(compound_data: Dict) -> Dict:
    """Analyze thermodynamic data for a compound"""
    if not compound_data.get('data'):
        return {'error': 'No thermodynamic data'}
    
    data = compound_data['data']
    headers = compound_data.get('headers', [])
    
    # Convert to DataFrame for analysis - handle mismatched columns
    try:
        # Create DataFrame without specifying columns first
        df = pd.DataFrame(data)
        
        # If we have headers, try to use them
        if headers and len(headers) == len(df.columns):
            df.columns = headers
        else:
            # Create generic column names
            df.columns = [f'col_{i}' for i in range(len(df.columns))]
            
    except Exception as e:
        return {'error': f'DataFrame creation failed: {e}'}
    
    # Find temperature column
    temp_col = None
    for col in df.columns:
        if 't' in col.lower() and 'k' in col.lower():
            temp_col = col
            break
    
    if temp_col is None:
        return {'error': 'No temperature column found'}
    
    # Find Gibbs free energy column
    gibbs_col = None
    for col in df.columns:
        if 'g' in col.lower() and ('f' in col.lower() or '°' in col):
            gibbs_col = col
            break
    
    analysis = {
        'compound_name': compound_data['compound']['name'],
        'formula': compound_data['compound']['formula'],
        'element': compound_data['compound']['element'],
        'data_points': len(data),
        'columns': len(df.columns),
        'temperature_range': {
            'min': float(df[temp_col].min()) if temp_col in df.columns else None,
            'max': float(df[temp_col].max()) if temp_col in df.columns else None
        },
        'has_gibbs_data': gibbs_col is not None,
        'headers': headers
    }
    
    if gibbs_col and temp_col:
        analysis['gibbs_data'] = {
            'min_temp': float(df[temp_col].min()),
            'max_temp': float(df[temp_col].max()),
            'min_gibbs': float(df[gibbs_col].min()),
            'max_gibbs': float(df[gibbs_col].max())
        }
    
    return analysis

def print_summary(categories: Dict[str, List]):
    """Print summary of categorized compounds"""
    print("\n" + "="*80)
    print("JANAF DATABASE ANALYSIS SUMMARY")
    print("="*80)
    
    total_compounds = sum(len(compounds) for compounds in categories.values())
    print(f"Total compounds analyzed: {total_compounds}")
    print()
    
    for category, compounds in categories.items():
        print(f"{category.upper()}: {len(compounds)} compounds")
        
        # Show first few examples
        if compounds:
            print("  Examples:")
            for i, compound in enumerate(compounds[:5]):
                compound_info = compound['compound']
                print(f"    - {compound_info['name']} ({compound_info['formula']})")
            if len(compounds) > 5:
                print(f"    ... and {len(compounds) - 5} more")
        print()

def analyze_oxides(categories: Dict[str, List]):
    """Detailed analysis of oxides"""
    oxides = categories['oxides']
    print("\n" + "="*80)
    print("DETAILED OXIDE ANALYSIS")
    print("="*80)
    
    print(f"Total oxides found: {len(oxides)}")
    print()
    
    # Group by element
    element_oxides = {}
    for oxide in oxides:
        element = oxide['compound']['element']
        if element not in element_oxides:
            element_oxides[element] = []
        element_oxides[element].append(oxide)
    
    print("Oxides by element:")
    for element, element_oxides_list in element_oxides.items():
        print(f"  {element}: {len(element_oxides_list)} oxides")
        for oxide in element_oxides_list:
            compound_info = oxide['compound']
            analysis = analyze_thermodynamic_data(oxide)
            if 'error' not in analysis:
                print(f"    - {compound_info['name']} ({compound_info['formula']}) - {analysis['data_points']} data points")
            else:
                print(f"    - {compound_info['name']} ({compound_info['formula']}) - {analysis['error']}")
        print()

def analyze_carbides_nitrides(categories: Dict[str, List]):
    """Detailed analysis of carbides and nitrides"""
    print("\n" + "="*80)
    print("CARBIDE AND NITRIDE ANALYSIS")
    print("="*80)
    
    for compound_type in ['carbides', 'nitrides']:
        compounds = categories[compound_type]
        print(f"\n{compound_type.upper()}: {len(compounds)} compounds")
        
        # Group by element
        element_compounds = {}
        for compound in compounds:
            element = compound['compound']['element']
            if element not in element_compounds:
                element_compounds[element] = []
            element_compounds[element].append(compound)
        
        print(f"{compound_type.capitalize()} by element:")
        for element, element_compounds_list in element_compounds.items():
            print(f"  {element}: {len(element_compounds_list)} {compound_type}")
            for compound in element_compounds_list:
                compound_info = compound['compound']
                analysis = analyze_thermodynamic_data(compound)
                if 'error' not in analysis:
                    print(f"    - {compound_info['name']} ({compound_info['formula']}) - {analysis['data_points']} data points")
                else:
                    print(f"    - {compound_info['name']} ({compound_info['formula']}) - {analysis['error']}")
        print()

def main():
    """Main analysis function"""
    print("Loading JANAF data...")
    data = load_janaf_data()
    
    if not data:
        print("No data loaded. Exiting.")
        return
    
    print("Categorizing compounds...")
    categories = categorize_compounds(data)
    
    print_summary(categories)
    analyze_oxides(categories)
    analyze_carbides_nitrides(categories)
    
    # Save categorized data
    print("Saving categorized data...")
    with open('janaf_categorized_data.pkl', 'wb') as f:
        pickle.dump(categories, f)
    print("Categorized data saved to janaf_categorized_data.pkl")

if __name__ == "__main__":
    main()
