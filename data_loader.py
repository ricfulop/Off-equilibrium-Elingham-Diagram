"""
Data loader for JANAF thermodynamic data from pickle file.
Processes raw data into structured format for Ellingham diagram calculations.
"""

import pandas as pd
import numpy as np
import pickle
import warnings
from typing import Dict, List, Tuple, Optional
import re
from config import DATA_FILE

warnings.filterwarnings('ignore')


class JANAFDataLoader:
    """Loads and processes JANAF thermodynamic data for Ellingham diagrams."""
    
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.raw_data = None
        self.processed_data = {}
        self.oxide_species = []
        
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw data from pickle file with compatibility handling."""
        try:
            self.raw_data = pd.read_pickle(self.data_file)
            print(f"Successfully loaded data: {self.raw_data.shape}")
            return self.raw_data
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            raise
    
    def identify_oxide_species(self) -> List[str]:
        """Identify oxide species from the raw data."""
        if self.raw_data is None:
            self.load_raw_data()
            
        # Get unique species
        species_list = self.raw_data['species'].unique()
        
        # Filter for oxides (contain 'oxide' or 'dioxide' or 'trioxide' etc.)
        oxide_patterns = [
            r'.*oxide.*',
            r'.*dioxide.*', 
            r'.*trioxide.*',
            r'.*pentoxide.*',
            r'.*monoxide.*'
        ]
        
        oxides = []
        for species in species_list:
            for pattern in oxide_patterns:
                if re.match(pattern, species, re.IGNORECASE):
                    oxides.append(species)
                    break
        
        # Also include specific known oxides
        known_oxides = [
            'Titanium Dioxide (rutile)',
            'Titanium Monoxide',
            'Zirconium dioxide',
            'Niobium dioxide',
            'Niobium monoxide', 
            'Niobium pentoxide',
            'Tantalum pentoxide',
            'Molybdenum dioxide',
            'Molybdenum trioxide',
            'Tungsten dioxide',
            'Tungsten trioxide',
            'Vanadium(III) oxide',
            'Vanadium(V) oxide'
        ]
        
        for oxide in known_oxides:
            if oxide in species_list and oxide not in oxides:
                oxides.append(oxide)
        
        self.oxide_species = sorted(oxides)
        print(f"Identified {len(self.oxide_species)} oxide species:")
        for oxide in self.oxide_species:
            print(f"  - {oxide}")
            
        return self.oxide_species
    
    def extract_stoichiometry(self, species_name: str) -> Tuple[int, int]:
        """
        Extract stoichiometry from species name.
        Returns (n_electrons_per_mol_O2, oxygen_stoichiometry)
        """
        # Map common oxides to their stoichiometry
        stoichiometry_map = {
            'monoxide': (2, 1),      # MO: M + 0.5 O2 -> MO, n=2
            'dioxide': (4, 2),       # MO2: M + O2 -> MO2, n=4  
            'trioxide': (6, 3),      # MO3: M + 1.5 O2 -> MO3, n=6
            'pentoxide': (10, 5),    # M2O5: 2M + 2.5 O2 -> M2O5, n=10
        }
        
        species_lower = species_name.lower()
        
        for oxide_type, (n_electrons, n_oxygen) in stoichiometry_map.items():
            if oxide_type in species_lower:
                return n_electrons, n_oxygen
                
        # Default assumption for unknown oxides
        return 4, 2  # Assume MO2
    
    def process_oxide_data(self, species_name: str) -> Dict:
        """
        Process thermodynamic data for a single oxide species.
        Returns dictionary with temperature and Gibbs free energy data.
        """
        if self.raw_data is None:
            self.load_raw_data()
            
        # Filter data for this species
        species_data = self.raw_data[self.raw_data['species'] == species_name].copy()
        
        if species_data.empty:
            print(f"Warning: No data found for {species_name}")
            return {}
            
        # Clean data - try both Gibbs free energy columns
        if species_data['delta_G_f_kJ_per_mol'].notna().any():
            species_data = species_data.dropna(subset=['delta_G_f_kJ_per_mol'])
            delta_f_G_col = 'delta_G_f_kJ_per_mol'
        elif species_data['delta_f_G_kJ_per_mol'].notna().any():
            species_data = species_data.dropna(subset=['delta_f_G_kJ_per_mol'])
            delta_f_G_col = 'delta_f_G_kJ_per_mol'
        else:
            print(f"Warning: No Gibbs free energy data found for {species_name}")
            return {}
        
        if species_data.empty:
            print(f"Warning: No valid Gibbs free energy data for {species_name}")
            return {}
        
        # Extract temperature and Gibbs free energy
        T_K = species_data['T_K'].values
        delta_f_G = species_data[delta_f_G_col].values
        
        # Get stoichiometry
        n_electrons, n_oxygen = self.extract_stoichiometry(species_name)
        
        # Calculate ΔG per mol O2
        # For formation: M + (n_oxygen/2) O2 -> MOx
        # So ΔG_per_mol_O2 = delta_f_G / (n_oxygen/2)
        DG_per_mol_O2 = delta_f_G / (n_oxygen / 2)
        
        # Sort by temperature
        sort_idx = np.argsort(T_K)
        T_K = T_K[sort_idx]
        DG_per_mol_O2 = DG_per_mol_O2[sort_idx]
        
        # Fit polynomial for interpolation
        try:
            # Fit quadratic: DG = A + B*T + C*T^2
            coeffs = np.polyfit(T_K, DG_per_mol_O2, 2)
            fit_params = {
                'A': coeffs[2],  # Constant term
                'B': coeffs[1],  # Linear term  
                'C': coeffs[0],  # Quadratic term
                'n_electrons': n_electrons,
                'n_oxygen': n_oxygen
            }
        except:
            # Fallback to linear fit
            coeffs = np.polyfit(T_K, DG_per_mol_O2, 1)
            fit_params = {
                'A': coeffs[1],  # Constant term
                'B': coeffs[0],  # Linear term
                'C': 0.0,        # No quadratic term
                'n_electrons': n_electrons,
                'n_oxygen': n_oxygen
            }
        
        processed_data = {
            'species_name': species_name,
            'T_K': T_K,
            'DG_kJ_per_molO2': DG_per_mol_O2,
            'fit_params': fit_params,
            'n_electrons': n_electrons,
            'n_oxygen': n_oxygen
        }
        
        return processed_data
    
    def process_all_data(self) -> Dict:
        """Process all oxide species and return structured data."""
        if not self.oxide_species:
            self.identify_oxide_species()
            
        print("Processing thermodynamic data for all oxides...")
        
        for species in self.oxide_species:
            try:
                processed = self.process_oxide_data(species)
                if processed:
                    # Create a clean key for the species
                    clean_key = self._create_clean_key(species)
                    self.processed_data[clean_key] = processed
                    print(f"✓ Processed {species}")
                else:
                    print(f"✗ Failed to process {species}")
            except Exception as e:
                print(f"✗ Error processing {species}: {e}")
        
        print(f"\nSuccessfully processed {len(self.processed_data)} oxides")
        return self.processed_data
    
    def _create_clean_key(self, species_name: str) -> str:
        """Create a clean key for species lookup."""
        # Convert to simple formula format
        clean_name = species_name.lower()
        
        # Common mappings
        mappings = {
            'titanium dioxide (rutile)': 'TiO2',
            'titanium monoxide': 'TiO',
            'zirconium dioxide': 'ZrO2',
            'niobium dioxide': 'NbO2',
            'niobium monoxide': 'NbO',
            'niobium pentoxide': 'Nb2O5',
            'tantalum pentoxide': 'Ta2O5',
            'molybdenum dioxide': 'MoO2',
            'molybdenum trioxide': 'MoO3',
            'tungsten dioxide': 'WO2',
            'tungsten trioxide': 'WO3',
            'vanadium(iii) oxide': 'V2O3',
            'vanadium(v) oxide': 'V2O5'
        }
        
        return mappings.get(clean_name, species_name)
    
    def get_available_oxides(self) -> List[str]:
        """Get list of available oxide keys."""
        return list(self.processed_data.keys())
    
    def get_oxide_data(self, oxide_key: str) -> Optional[Dict]:
        """Get processed data for a specific oxide."""
        return self.processed_data.get(oxide_key)
    
    def interpolate_DG(self, oxide_key: str, T_K: np.ndarray) -> np.ndarray:
        """
        Interpolate Gibbs free energy at given temperatures using fitted polynomial.
        """
        data = self.get_oxide_data(oxide_key)
        if data is None:
            return np.full_like(T_K, np.nan)
        
        params = data['fit_params']
        # DG = A + B*T + C*T^2
        DG = params['A'] + params['B'] * T_K + params['C'] * T_K**2
        
        return DG


def load_janaf_data() -> JANAFDataLoader:
    """Convenience function to load and process all JANAF data."""
    loader = JANAFDataLoader()
    loader.load_raw_data()
    loader.identify_oxide_species()
    loader.process_all_data()
    return loader


if __name__ == "__main__":
    # Test the data loader
    loader = load_janaf_data()
    
    print("\nAvailable oxides:")
    for oxide in loader.get_available_oxides():
        print(f"  - {oxide}")
    
    # Test interpolation for TiO2
    if 'TiO2' in loader.get_available_oxides():
        T_test = np.array([1000, 1200, 1500])
        DG_test = loader.interpolate_DG('TiO2', T_test)
        print(f"\nTiO2 test interpolation:")
        print(f"T (K): {T_test}")
        print(f"ΔG (kJ/mol O2): {DG_test}")
