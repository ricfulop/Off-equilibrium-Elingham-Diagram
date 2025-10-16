#!/usr/bin/env python3
"""
Simple JANAF Preprocessor
Creates pre-computed tables for the Ellingham diagram application
"""

import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

def load_janaf_data(filename: str = "janaf_full_database.pkl"):
    """Load the full JANAF database"""
    print(f"Loading JANAF data from {filename}...")
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    
    total_compounds = sum(len(compounds) for compounds in data.values())
    print(f"Loaded {len(data)} elements with {total_compounds} total compounds")
    return data

def categorize_compounds(data: Dict) -> Dict[str, List]:
    """Categorize compounds into oxides, carbides, nitrides, etc."""
    print("Categorizing compounds...")
    
    categories = {
        'oxides': [],
        'carbides': [],
        'nitrides': [],
        'halides': [],
        'hydrides': [],
        'sulfides': [],
        'phosphides': [],
        'pure_elements': [],
        'other': []
    }
    
    for element, compounds in data.items():
        for compound_data in compounds:
            compound_info = compound_data['compound']
            name = compound_info['name'].lower()
            formula = compound_info['formula'].lower()
            
            # Categorize based on name and formula
            if 'oxide' in name or ('o' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])):
                categories['oxides'].append(compound_data)
            elif 'carbide' in name or ('c' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])):
                categories['carbides'].append(compound_data)
            elif 'nitride' in name or ('n' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])):
                categories['nitrides'].append(compound_data)
            elif any(halide in name for halide in ['fluoride', 'chloride', 'bromide', 'iodide']):
                categories['halides'].append(compound_data)
            elif 'hydride' in name or ('h' in formula and len(formula) > 1):
                categories['hydrides'].append(compound_data)
            elif 'sulfide' in name or ('s' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])):
                categories['sulfides'].append(compound_data)
            elif 'phosphide' in name or ('p' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])):
                categories['phosphides'].append(compound_data)
            elif element.lower() in name and len(name.split()) == 1:
                categories['pure_elements'].append(compound_data)
            else:
                categories['other'].append(compound_data)
    
    # Print categorization summary
    print("\nCompound Categorization Summary:")
    for category, compounds in categories.items():
        print(f"  {category.capitalize()}: {len(compounds)} compounds")
    
    return categories

def extract_thermodynamic_data_simple(compound_data: Dict) -> Optional[Dict]:
    """Extract thermodynamic data using a more flexible approach"""
    if not compound_data.get('data'):
        return None
    
    data = compound_data['data']
    
    try:
        df = pd.DataFrame(data)
        
        # More flexible header detection - look for temperature patterns
        header_row = None
        temp_patterns = ['T/K', 'T', 'Temperature', 'Temp', 'T(K)', 'T_K']
        
        for i in range(min(5, len(df))):  # Check more rows
            row = df.iloc[i]
            for cell in row.values:
                cell_str = str(cell).lower()
                if any(pattern.lower() in cell_str for pattern in temp_patterns):
                    header_row = i
                    break
            if header_row is not None:
                break
        
        if header_row is None:
            # Try to use first row as header if it looks like headers
            if len(df) > 0:
                first_row = df.iloc[0]
                if any(isinstance(cell, str) and len(cell) > 0 for cell in first_row.values):
                    header_row = 0
        
        if header_row is None:
            return None
        
        # Use the header row as column names
        df.columns = df.iloc[header_row].values
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Convert numeric columns
        for col in df.columns:
            if col and str(col) != 'None' and str(col) != 'nan':
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        
        # More flexible temperature column detection
        temp_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if any(pattern.lower() in col_str for pattern in temp_patterns):
                temp_col = col
                break
        
        if temp_col is None:
            return None
        
        # More flexible Gibbs free energy column detection
        gibbs_col = None
        gibbs_patterns = ['fG°', 'G°', 'Gibbs', 'delta_f_G', 'delta_G_f', 'G_f', 'fG']
        for pattern in gibbs_patterns:
            for col in df.columns:
                if col and pattern in str(col):
                    gibbs_col = col
                    break
            if gibbs_col:
                break
        
        # More flexible enthalpy column detection
        enthalpy_col = None
        enthalpy_patterns = ['fH°', 'H°', 'Enthalpy', 'delta_f_H', 'delta_H_f', 'H_f', 'fH']
        for pattern in enthalpy_patterns:
            for col in df.columns:
                if col and pattern in str(col):
                    enthalpy_col = col
                    break
            if enthalpy_col:
                break
        
        # More flexible entropy column detection
        entropy_col = None
        entropy_patterns = ['S°', 'Entropy', 'S_J_per_molK', 'S', 'S_J']
        for pattern in entropy_patterns:
            for col in df.columns:
                if col and pattern in str(col):
                    entropy_col = col
                    break
            if entropy_col:
                break
        
        # Extract data
        result = {
            'compound_name': compound_data['compound']['name'],
            'formula': compound_data['compound']['formula'],
            'element': compound_data['compound']['element'],
            'data_points': len(df),
            'temperature_range': {
                'min': float(df[temp_col].min()) if temp_col in df.columns else None,
                'max': float(df[temp_col].max()) if temp_col in df.columns else None
            }
        }
        
        # Try to get Gibbs data directly and fit polynomial
        if gibbs_col and temp_col:
            # Clean the data - remove NaN values
            clean_df = df[[temp_col, gibbs_col]].dropna()
            
            if len(clean_df) >= 3:  # Need at least 3 points for polynomial fitting
                T_clean = clean_df[temp_col].values
                G_clean = clean_df[gibbs_col].values
                
                # Fit polynomial: G(T) = A + B*T + C*T^2
                try:
                    coeffs = np.polyfit(T_clean, G_clean, 2)  # 2nd degree polynomial
                    A, B, C = coeffs[2], coeffs[1], coeffs[0]  # polyfit returns [C, B, A]
                    
                    result['gibbs_data'] = {
                        'min_temp': float(T_clean.min()),
                        'max_temp': float(T_clean.max()),
                        'min_gibbs': float(G_clean.min()),
                        'max_gibbs': float(G_clean.max()),
                        'fit_coefficients': {
                            'A': float(A),
                            'B': float(B), 
                            'C': float(C)
                        },
                        'data_points': len(clean_df)
                    }
                    
                except np.linalg.LinAlgError:
                    # If polynomial fitting fails, fall back to min/max
                    result['gibbs_data'] = {
                        'min_temp': float(T_clean.min()),
                        'max_temp': float(T_clean.max()),
                        'min_gibbs': float(G_clean.min()),
                        'max_gibbs': float(G_clean.max()),
                        'fit_coefficients': None
                    }
            else:
                # Not enough data points
                result['gibbs_data'] = {
                    'min_temp': float(df[temp_col].min()),
                    'max_temp': float(df[temp_col].max()),
                    'min_gibbs': float(df[gibbs_col].min()),
                    'max_gibbs': float(df[gibbs_col].max()),
                    'fit_coefficients': None
                }
        
        # If no Gibbs data, try to calculate from H and S
        elif enthalpy_col and entropy_col and temp_col:
            # Calculate G = H - TS (convert S from J/mol·K to kJ/mol·K)
            df['calculated_G'] = df[enthalpy_col] - df[temp_col] * df[entropy_col] / 1000
            
            # Clean the data
            clean_df = df[[temp_col, 'calculated_G']].dropna()
            
            if len(clean_df) >= 3:
                T_clean = clean_df[temp_col].values
                G_clean = clean_df['calculated_G'].values
                
                # Fit polynomial
                try:
                    coeffs = np.polyfit(T_clean, G_clean, 2)
                    A, B, C = coeffs[2], coeffs[1], coeffs[0]
                    
                    result['gibbs_data'] = {
                        'min_temp': float(T_clean.min()),
                        'max_temp': float(T_clean.max()),
                        'min_gibbs': float(G_clean.min()),
                        'max_gibbs': float(G_clean.max()),
                        'fit_coefficients': {
                            'A': float(A),
                            'B': float(B),
                            'C': float(C)
                        },
                        'data_points': len(clean_df),
                        'calculated_from_H_S': True
                    }
                except np.linalg.LinAlgError:
                    result['gibbs_data'] = {
                        'min_temp': float(T_clean.min()),
                        'max_temp': float(T_clean.max()),
                        'min_gibbs': float(G_clean.min()),
                        'max_gibbs': float(G_clean.max()),
                        'fit_coefficients': None,
                        'calculated_from_H_S': True
                    }
            else:
                result['gibbs_data'] = {
                    'min_temp': float(df[temp_col].min()),
                    'max_temp': float(df[temp_col].max()),
                    'min_gibbs': float(df['calculated_G'].min()),
                    'max_gibbs': float(df['calculated_G'].max()),
                    'fit_coefficients': None,
                    'calculated_from_H_S': True
                }
        else:
            # Include compounds with only temperature data (no thermodynamic data)
            result['temperature_only'] = True
        
        # Add enthalpy and entropy data if available
        if enthalpy_col and temp_col:
            result['enthalpy_data'] = {
                'min_temp': float(df[temp_col].min()),
                'max_temp': float(df[temp_col].max()),
                'min_enthalpy': float(df[enthalpy_col].min()),
                'max_enthalpy': float(df[enthalpy_col].max())
            }
        
        if entropy_col and temp_col:
            result['entropy_data'] = {
                'min_temp': float(df[temp_col].min()),
                'max_temp': float(df[temp_col].max()),
                'min_entropy': float(df[entropy_col].min()),
                'max_entropy': float(df[entropy_col].max())
            }
        
        return result
        
    except Exception as e:
        print(f"Error processing {compound_data['compound']['name']}: {e}")
        return None

def create_ellingham_tables(categories: Dict[str, List]) -> Dict:
    """Create tables optimized for the Ellingham diagram application"""
    print("Creating Ellingham-compatible tables...")
    
    ellingham_tables = {
        'oxides': {},
        'carbides': {},
        'nitrides': {},
        'compound_lookup': {},
        'element_lookup': {},
        'metadata': {
            'total_compounds': 0,
            'elements': set(),
            'categories': {}
        }
    }
    
    for category, compounds in categories.items():
        # Include ALL categories - no filtering
        ellingham_tables[category] = {}
        
        for compound_data in compounds:
            compound_info = compound_data['compound']
            name = compound_info['name']
            formula = compound_info['formula']
            element = compound_info['element']
            
            # Extract thermodynamic data
            thermo_data = extract_thermodynamic_data_simple(compound_data)
            if not thermo_data:
                continue
            
            # Create entry
            entry = {
                'name': name,
                'formula': formula,
                'element': element,
                'category': category,
                'thermo_data': thermo_data,
                'raw_data': compound_data['data']
            }
            
            ellingham_tables[category][name] = entry
            ellingham_tables['compound_lookup'][name] = entry
            
            if element not in ellingham_tables['element_lookup']:
                ellingham_tables['element_lookup'][element] = []
            ellingham_tables['element_lookup'][element].append(entry)
            
            ellingham_tables['metadata']['elements'].add(element)
            ellingham_tables['metadata']['total_compounds'] += 1
        
        ellingham_tables['metadata']['categories'][category] = len(ellingham_tables[category])
    
    ellingham_tables['metadata']['elements'] = list(ellingham_tables['metadata']['elements'])
    
    # Correct the total count to match actual processed compounds
    ellingham_tables['metadata']['total_compounds'] = len(ellingham_tables['compound_lookup'])
    
    return ellingham_tables

def main():
    """Main preprocessing function"""
    print("="*80)
    print("JANAF DATABASE PREPROCESSING")
    print("="*80)
    
    # Load data
    data = load_janaf_data()
    
    # Categorize compounds
    categories = categorize_compounds(data)
    
    # Create Ellingham tables
    ellingham_tables = create_ellingham_tables(categories)
    
    # Save processed data
    output_file = "janaf_ellingham_tables.pkl"
    print(f"\nSaving Ellingham tables to {output_file}...")
    with open(output_file, 'wb') as f:
        pickle.dump(ellingham_tables, f)
    
    # Print summary
    print("\n" + "="*80)
    print("PREPROCESSING COMPLETE")
    print("="*80)
    print(f"Total compounds processed: {ellingham_tables['metadata']['total_compounds']}")
    print(f"Elements covered: {len(ellingham_tables['metadata']['elements'])}")
    print()
    print("Comprehensive JANAF database:")
    for category in ['oxides', 'carbides', 'nitrides', 'halides', 'hydrides', 'sulfides', 'phosphides', 'pure_elements', 'other']:
        count = len(ellingham_tables[category])
        print(f"  {category.capitalize()}: {count} compounds")
    
    print(f"\nData saved to {output_file}")
    print("Ready for integration into Ellingham diagram application!")

if __name__ == "__main__":
    main()
