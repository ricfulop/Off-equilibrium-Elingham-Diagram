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
    
    def __init__(self, data_file: str = "janaf_ellingham_tables.pkl"):
        self.data_file = data_file
        self.raw_data = None
        self.processed_data = {}
        self.oxide_species = []
        self.categories_data = {}
        
    def load_raw_data(self) -> Dict:
        """Load pre-computed JANAF data from pickle file."""
        try:
            with open(self.data_file, 'rb') as f:
                self.raw_data = pickle.load(f)
            print(f"Successfully loaded comprehensive JANAF database: {self.raw_data['metadata']['total_compounds']} compounds")
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
            
        # Clean data - try both Gibbs free energy columns, then calculate from H and S
        if species_data['delta_G_f_kJ_per_mol'].notna().any():
            species_data = species_data.dropna(subset=['delta_G_f_kJ_per_mol'])
            delta_f_G_col = 'delta_G_f_kJ_per_mol'
        elif species_data['delta_f_G_kJ_per_mol'].notna().any():
            species_data = species_data.dropna(subset=['delta_f_G_kJ_per_mol'])
            delta_f_G_col = 'delta_f_G_kJ_per_mol'
        elif (species_data['delta_f_H_kJ_per_mol'].notna().any() and 
              species_data['S_J_per_molK'].notna().any()):
            # Calculate Gibbs free energy from enthalpy and entropy: G = H - TS
            species_data = species_data.dropna(subset=['delta_f_H_kJ_per_mol', 'S_J_per_molK'])
            # Calculate delta_f_G = delta_f_H - T * S (convert S from J/mol·K to kJ/mol·K)
            species_data['delta_f_G_kJ_per_mol'] = (
                species_data['delta_f_H_kJ_per_mol'] - 
                species_data['T_K'] * species_data['S_J_per_molK'] / 1000
            )
            delta_f_G_col = 'delta_f_G_kJ_per_mol'
            print(f"✓ Calculated Gibbs free energy from H and S for {species_name}")
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
    
    def interpolate_DG(self, material_name: str, temperature_K: float) -> float:
        """
        Interpolate Gibbs free energy at given temperature using polynomial coefficients.
        
        Args:
            material_name: Name of the material
            temperature_K: Temperature in Kelvin (can be array or scalar)
            
        Returns:
            Gibbs free energy in kJ/mol O₂
        """
        material_data = self.get_material_data(material_name)
        if not material_data:
            return 0.0
        
        thermo_data = material_data.get('thermo_data', {})
        gibbs_data = thermo_data.get('gibbs_data', {})
        
        if not gibbs_data:
            return 0.0
        
        # Check if we have polynomial coefficients
        fit_coeffs = gibbs_data.get('fit_coefficients')
        if fit_coeffs:
            A = fit_coeffs['A']
            B = fit_coeffs['B'] 
            C = fit_coeffs['C']
            
            # Calculate: G(T) = A + B*T + C*T^2
            if isinstance(temperature_K, np.ndarray):
                return A + B * temperature_K + C * temperature_K**2
            else:
                return A + B * temperature_K + C * temperature_K**2
        
        # Fallback to constant value if no coefficients
        return gibbs_data.get('min_gibbs', 0.0)
    
    def get_oxide_data(self, oxide_key: str) -> Optional[Dict]:
        """
        Get oxide data for compatibility with ThermodynamicEngine.
        This method provides compatibility with the existing thermodynamic calculations.
        
        Args:
            oxide_key: Name of the oxide
            
        Returns:
            Dictionary with oxide data including n_electrons and n_oxygen
        """
        material_data = self.get_material_data(oxide_key)
        if not material_data:
            return None
        
        processed_data = self.process_material_for_ellingham(oxide_key)
        if not processed_data:
            return None
        
        return {
            'n_electrons': processed_data['fit_params']['n_electrons'],
            'n_oxygen': processed_data['fit_params']['n_oxygen'],
            'formula': processed_data.get('formula', ''),
            'element': processed_data.get('element', ''),
            'category': processed_data.get('category', '')
        }
    
    
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
    
    def get_available_materials(self, category: str = None) -> List[str]:
        """
        Get list of available materials, optionally filtered by category.
        
        Args:
            category: Optional category filter ('oxides', 'carbides', 'nitrides', etc.)
        
        Returns:
            List of material names
        """
        if self.raw_data is None:
            self.load_raw_data()
        
        if category:
            if category in self.raw_data:
                return list(self.raw_data[category].keys())
            else:
                return []
        else:
            # Return all materials from all categories
            all_materials = []
            for cat in ['oxides', 'carbides', 'nitrides', 'halides', 'hydrides', 'sulfides', 'phosphides', 'pure_elements', 'other']:
                if cat in self.raw_data:
                    all_materials.extend(list(self.raw_data[cat].keys()))
            return all_materials
    
    def get_categories_data(self) -> Dict[str, List[Dict]]:
        """
        Get materials organized by category for the UI.
        
        Returns:
            Dictionary with category names as keys and lists of material info as values
        """
        if self.raw_data is None:
            self.load_raw_data()
        
        categories_data = {}
        for category in ['oxides', 'carbides', 'nitrides', 'halides', 'hydrides', 'sulfides', 'phosphides', 'pure_elements', 'other']:
            if category in self.raw_data:
                materials = []
                for name, data in self.raw_data[category].items():
                    materials.append({
                        'name': name,
                        'formula': data.get('formula', ''),
                        'element': data.get('element', ''),
                        'category': category
                    })
                categories_data[category] = materials
        
        return categories_data
    
    def get_material_data(self, material_name: str) -> Optional[Dict]:
        """
        Get processed data for a specific material from any category.
        
        Args:
            material_name: Name of the material
        
        Returns:
            Dictionary with material data or None if not found
        """
        if self.raw_data is None:
            self.load_raw_data()
        
        # Check compound lookup first
        if 'compound_lookup' in self.raw_data and material_name in self.raw_data['compound_lookup']:
            return self.raw_data['compound_lookup'][material_name]
        
        # Fallback: search all categories
        for category in ['oxides', 'carbides', 'nitrides', 'halides', 'hydrides', 'sulfides', 'phosphides', 'pure_elements', 'other']:
            if category in self.raw_data and material_name in self.raw_data[category]:
                return self.raw_data[category][material_name]
        
        return None
    
    def process_material_for_ellingham(self, material_name: str) -> Optional[Dict]:
        """
        Process material data for Ellingham diagram calculations.
        Converts raw thermodynamic data to Ellingham-compatible format.
        
        Args:
            material_name: Name of the material
        
        Returns:
            Dictionary with processed Ellingham data or None if processing fails
        """
        material_data = self.get_material_data(material_name)
        if not material_data:
            return None
        
        thermo_data = material_data.get('thermo_data', {})
        if not thermo_data:
            return None
        
        # Extract temperature and Gibbs free energy data
        if 'gibbs_data' not in thermo_data:
            return None
        
        gibbs_data = thermo_data['gibbs_data']
        
        # Extract polynomial coefficients from thermodynamic data
        fit_coeffs = gibbs_data.get('fit_coefficients')
        
        if fit_coeffs:
            # Use actual polynomial coefficients from thermodynamic data
            fit_params = {
                'A': fit_coeffs['A'],
                'B': fit_coeffs['B'],
                'C': fit_coeffs['C'],
                'n_electrons': 4,  # Default assumption - could be improved
                'n_oxygen': 2     # Default assumption - could be improved
            }
        else:
            # Fallback to simplified approach if no coefficients available
            fit_params = {
                'A': gibbs_data.get('min_gibbs', 0),
                'B': 0.0,  # No temperature dependence
                'C': 0.0,
                'n_electrons': 4,  # Default assumption
                'n_oxygen': 2     # Default assumption
            }
        
        processed_data = {
            'species_name': material_name,
            'formula': material_data.get('formula', ''),
            'element': material_data.get('element', ''),
            'category': material_data.get('category', ''),
            'fit_params': fit_params,
            'n_electrons': fit_params['n_electrons'],
            'n_oxygen': fit_params['n_oxygen'],
            'temperature_range': thermo_data.get('temperature_range', {}),
            'data_points': thermo_data.get('data_points', 0)
        }
        
        return processed_data


def load_janaf_data() -> JANAFDataLoader:
    """Convenience function to load and process all JANAF data."""
    loader = JANAFDataLoader()
    loader.load_raw_data()
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
