#!/usr/bin/env python3
"""
JANAF Database Preprocessor
Preprocesses the full JANAF database for use in the Ellingham diagram application
"""

import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple, Optional
import re
from collections import defaultdict

class JANAFPreprocessor:
    """Preprocesses JANAF data for the Ellingham diagram application"""
    
    def __init__(self, janaf_file: str = "janaf_full_database.pkl"):
        self.janaf_file = janaf_file
        self.data = None
        self.processed_data = {}
        
    def load_data(self):
        """Load the full JANAF database"""
        print(f"Loading JANAF data from {self.janaf_file}...")
        with open(self.janaf_file, 'rb') as f:
            self.data = pickle.load(f)
        
        total_compounds = sum(len(compounds) for compounds in self.data.values())
        print(f"Loaded {len(self.data)} elements with {total_compounds} total compounds")
        
    def categorize_compounds(self) -> Dict[str, List]:
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
        
        for element, compounds in self.data.items():
            for compound_data in compounds:
                compound_info = compound_data['compound']
                name = compound_info['name'].lower()
                formula = compound_info['formula'].lower()
                
                # Enhanced categorization logic
                if self._is_oxide(name, formula):
                    categories['oxides'].append(compound_data)
                elif self._is_carbide(name, formula):
                    categories['carbides'].append(compound_data)
                elif self._is_nitride(name, formula):
                    categories['nitrides'].append(compound_data)
                elif self._is_halide(name, formula):
                    categories['halides'].append(compound_data)
                elif self._is_hydride(name, formula):
                    categories['hydrides'].append(compound_data)
                elif self._is_sulfide(name, formula):
                    categories['sulfides'].append(compound_data)
                elif self._is_phosphide(name, formula):
                    categories['phosphides'].append(compound_data)
                elif self._is_pure_element(name, formula, element):
                    categories['pure_elements'].append(compound_data)
                else:
                    categories['other'].append(compound_data)
        
        # Print categorization summary
        print("\nCompound Categorization Summary:")
        for category, compounds in categories.items():
            print(f"  {category.capitalize()}: {len(compounds)} compounds")
        
        return categories
    
    def _is_oxide(self, name: str, formula: str) -> bool:
        """Check if compound is an oxide"""
        return ('oxide' in name or 
                'o' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k']))
    
    def _is_carbide(self, name: str, formula: str) -> bool:
        """Check if compound is a carbide"""
        return ('carbide' in name or 
                ('c' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])))
    
    def _is_nitride(self, name: str, formula: str) -> bool:
        """Check if compound is a nitride"""
        return ('nitride' in name or 
                ('n' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k'])))
    
    def _is_halide(self, name: str, formula: str) -> bool:
        """Check if compound is a halide"""
        return any(halide in name for halide in ['fluoride', 'chloride', 'bromide', 'iodide']) or \
               any(halide in formula for halide in ['f', 'cl', 'br', 'i'])
    
    def _is_hydride(self, name: str, formula: str) -> bool:
        """Check if compound is a hydride"""
        return 'hydride' in name or ('h' in formula and len(formula) > 1)
    
    def _is_sulfide(self, name: str, formula: str) -> bool:
        """Check if compound is a sulfide"""
        return 'sulfide' in name or ('s' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k']))
    
    def _is_phosphide(self, name: str, formula: str) -> bool:
        """Check if compound is a phosphide"""
        return 'phosphide' in name or ('p' in formula and any(metal in formula for metal in ['ti', 'al', 'fe', 'ni', 'cr', 'mo', 'w', 'v', 'nb', 'ta', 'zr', 'hf', 'si', 'mg', 'ca', 'sr', 'ba', 'be', 'cu', 'zn', 'hg', 'pb', 'co', 'mn', 'li', 'na', 'k']))
    
    def _is_pure_element(self, name: str, formula: str, element: str) -> bool:
        """Check if compound is a pure element"""
        return element.lower() in name and len(name.split()) == 1
    
    def extract_thermodynamic_data(self, compound_data: Dict) -> Optional[Dict]:
        """Extract thermodynamic data in the format expected by the app"""
        if not compound_data.get('data'):
            return None
        
        data = compound_data['data']
        headers = compound_data.get('headers', [])
        
        # Convert to DataFrame
        try:
            df = pd.DataFrame(data)
            
            # The headers are in the first row, data starts from row 2
            if len(df) > 1:
                # Use first row as column names, skip it from data
                df.columns = df.iloc[0].values
                df = df.iloc[1:].reset_index(drop=True)
                
                # Convert numeric columns
                for col in df.columns:
                    if col and col != 'None':
                        try:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        except:
                            pass
            else:
                return None
                
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            return None
        
        # Find temperature column
        temp_col = None
        for col in df.columns:
            if col and 't' in col.lower() and 'k' in col.lower():
                temp_col = col
                break
        
        if temp_col is None:
            return None
        
        # Find Gibbs free energy column
        gibbs_col = None
        for col in df.columns:
            if col and 'g' in col.lower() and ('f' in col.lower() or '°' in col):
                gibbs_col = col
                break
        
        # Find enthalpy column
        enthalpy_col = None
        for col in df.columns:
            if col and 'h' in col.lower() and ('f' in col.lower() or '°' in col):
                enthalpy_col = col
                break
        
        # Find entropy column
        entropy_col = None
        for col in df.columns:
            if col and 's' in col.lower() and ('°' in col or col.lower().endswith('k')):
                entropy_col = col
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
        
        if gibbs_col and temp_col:
            result['gibbs_data'] = {
                'min_temp': float(df[temp_col].min()),
                'max_temp': float(df[temp_col].max()),
                'min_gibbs': float(df[gibbs_col].min()),
                'max_gibbs': float(df[gibbs_col].max())
            }
        
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
    
    def create_compound_lookup_tables(self, categories: Dict[str, List]) -> Dict:
        """Create lookup tables for efficient compound selection"""
        print("Creating compound lookup tables...")
        
        lookup_tables = {
            'by_category': {},
            'by_element': {},
            'by_formula': {},
            'compound_metadata': {}
        }
        
        for category, compounds in categories.items():
            lookup_tables['by_category'][category] = []
            
            for compound_data in compounds:
                compound_info = compound_data['compound']
                name = compound_info['name']
                formula = compound_info['formula']
                element = compound_info['element']
                
                # Extract thermodynamic data
                thermo_data = self.extract_thermodynamic_data(compound_data)
                if not thermo_data:
                    continue
                
                compound_entry = {
                    'name': name,
                    'formula': formula,
                    'element': element,
                    'category': category,
                    'thermo_data': thermo_data
                }
                
                # Add to category lookup
                lookup_tables['by_category'][category].append(compound_entry)
                
                # Add to element lookup
                if element not in lookup_tables['by_element']:
                    lookup_tables['by_element'][element] = []
                lookup_tables['by_element'][element].append(compound_entry)
                
                # Add to formula lookup
                lookup_tables['by_formula'][formula] = compound_entry
                
                # Add metadata
                lookup_tables['compound_metadata'][name] = {
                    'formula': formula,
                    'element': element,
                    'category': category,
                    'data_points': thermo_data['data_points'],
                    'temp_range': thermo_data['temperature_range']
                }
        
        return lookup_tables
    
    def create_ellingham_compatible_data(self, categories: Dict[str, List]) -> Dict:
        """Create data structure compatible with existing Ellingham app"""
        print("Creating Ellingham-compatible data structure...")
        
        ellingham_data = {
            'oxides': {},
            'carbides': {},
            'nitrides': {},
            'metadata': {
                'total_compounds': 0,
                'categories': {},
                'elements': set()
            }
        }
        
        for category, compounds in categories.items():
            if category in ['oxides', 'carbides', 'nitrides']:
                ellingham_data[category] = {}
                
                for compound_data in compounds:
                    compound_info = compound_data['compound']
                    name = compound_info['name']
                    formula = compound_info['formula']
                    element = compound_info['element']
                    
                    # Extract thermodynamic data
                    thermo_data = self.extract_thermodynamic_data(compound_data)
                    if not thermo_data:
                        continue
                    
                    # Create entry compatible with existing app
                    ellingham_data[category][name] = {
                        'formula': formula,
                        'element': element,
                        'thermo_data': thermo_data,
                        'raw_data': compound_data['data'],
                        'headers': compound_data.get('headers', [])
                    }
                    
                    ellingham_data['metadata']['elements'].add(element)
                    ellingham_data['metadata']['total_compounds'] += 1
            
            ellingham_data['metadata']['categories'][category] = len(compounds)
        
        ellingham_data['metadata']['elements'] = list(ellingham_data['metadata']['elements'])
        
        return ellingham_data
    
    def save_processed_data(self, output_file: str = "janaf_processed.pkl"):
        """Save all processed data"""
        print(f"Saving processed data to {output_file}...")
        
        with open(output_file, 'wb') as f:
            pickle.dump(self.processed_data, f)
        
        print(f"Processed data saved successfully!")
    
    def process_all(self):
        """Run the complete preprocessing pipeline"""
        print("="*80)
        print("JANAF DATABASE PREPROCESSING")
        print("="*80)
        
        # Load data
        self.load_data()
        
        # Categorize compounds
        categories = self.categorize_compounds()
        
        # Create lookup tables
        lookup_tables = self.create_compound_lookup_tables(categories)
        
        # Create Ellingham-compatible data
        ellingham_data = self.create_ellingham_compatible_data(categories)
        
        # Store all processed data
        self.processed_data = {
            'categories': categories,
            'lookup_tables': lookup_tables,
            'ellingham_data': ellingham_data,
            'metadata': {
                'total_elements': len(self.data),
                'total_compounds': sum(len(compounds) for compounds in self.data.values()),
                'processed_compounds': sum(len(compounds) for compounds in categories.values()),
                'categories': {category: len(compounds) for category, compounds in categories.items()},
                'processing_timestamp': pd.Timestamp.now().isoformat()
            }
        }
        
        # Save processed data
        self.save_processed_data()
        
        # Print summary
        print("\n" + "="*80)
        print("PREPROCESSING COMPLETE")
        print("="*80)
        print(f"Total elements processed: {self.processed_data['metadata']['total_elements']}")
        print(f"Total compounds processed: {self.processed_data['metadata']['processed_compounds']}")
        print()
        print("Categories:")
        for category, count in self.processed_data['metadata']['categories'].items():
            print(f"  {category.capitalize()}: {count} compounds")
        print()
        print("Ellingham-compatible data:")
        for category in ['oxides', 'carbides', 'nitrides']:
            count = len(self.processed_data['ellingham_data'][category])
            print(f"  {category.capitalize()}: {count} compounds")

def main():
    """Main preprocessing function"""
    preprocessor = JANAFPreprocessor()
    preprocessor.process_all()

if __name__ == "__main__":
    main()
