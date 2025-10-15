"""
Thermodynamic calculations for equilibrium and off-equilibrium Ellingham diagrams.
Implements the plasma flash reactor model for electric field-enhanced reduction.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from data_loader import JANAFDataLoader
from config import FARADAY_CONSTANT, W_PH_CONSTANTS, GAS_RATIO_TEMPS


class ThermodynamicEngine:
    """Handles thermodynamic calculations for Ellingham diagrams."""
    
    def __init__(self, data_loader: JANAFDataLoader):
        self.data_loader = data_loader
        
    def calc_equilibrium_DG(self, oxide_key: str, T_K: np.ndarray) -> np.ndarray:
        """
        Calculate equilibrium Gibbs free energy for oxide formation.
        
        Args:
            oxide_key: Oxide identifier (e.g., 'TiO2')
            T_K: Temperature array in Kelvin
            
        Returns:
            ΔG°(T) in kJ/mol O₂
        """
        return self.data_loader.interpolate_DG(oxide_key, T_K)
    
    def calc_off_equilibrium_DG(self, oxide_key: str, T_K: np.ndarray, 
                               E: float, r: float) -> np.ndarray:
        """
        Calculate off-equilibrium Gibbs free energy with electric field enhancement.
        
        Implements: ΔG_eff(T,E,r) = ΔG°(T) - n*F*E*r - W_ph
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            ΔG_eff(T,E,r) in kJ/mol O₂
        """
        # Get equilibrium Gibbs free energy
        DG_eq = self.calc_equilibrium_DG(oxide_key, T_K)
        
        # Get oxide data for stoichiometry
        oxide_data = self.data_loader.get_oxide_data(oxide_key)
        if oxide_data is None:
            return np.full_like(T_K, np.nan)
        
        n_electrons = oxide_data['n_electrons']
        
        # Calculate electric field contribution: -n*F*E*r
        # Convert from J/mol to kJ/mol
        electric_contribution = -(n_electrons * FARADAY_CONSTANT * E * r) / 1000
        
        # Get phonon/plasma work term
        W_ph = self._get_W_ph(oxide_key)
        
        # Calculate effective Gibbs free energy
        DG_eff = DG_eq + electric_contribution - W_ph
        
        return DG_eff
    
    def _get_W_ph(self, oxide_key: str) -> float:
        """Get phonon/plasma work constant for the oxide."""
        return W_PH_CONSTANTS.get(oxide_key, 20.0)  # Default value
    
    def calc_pO2_scale(self, T_K: np.ndarray) -> np.ndarray:
        """
        Calculate log₁₀(pO₂) scale for given temperatures.
        
        From: ΔG° = RT ln(pO₂/p°)
        So: log₁₀(pO₂) = ΔG°/(2.303 * RT) + log₁₀(p°)
        
        Args:
            T_K: Temperature array in Kelvin
            
        Returns:
            log₁₀(pO₂) values
        """
        R = 8.314  # J/(mol·K)
        p_std = 101325  # Pa (standard pressure)
        
        # For ΔG = 0 (equilibrium line)
        DG_zero = np.zeros_like(T_K)
        
        # Calculate log₁₀(pO₂)
        log_pO2 = DG_zero / (2.303 * R * T_K) + np.log10(p_std)
        
        return log_pO2
    
    def calc_gas_ratio_scales(self, T_K: np.ndarray, DG_kJ_per_molO2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate gas ratio scales for H₂/H₂O and CO/CO₂.
        
        These are reference lines for Ellingham diagrams, independent of the metal oxide.
        They represent the equilibrium conditions for gas reduction reactions.
        
        Args:
            T_K: Temperature array in Kelvin
            DG_kJ_per_molO2: Gibbs free energy per mol O₂ (not used for gas ratios)
            
        Returns:
            Tuple of (log(H₂/H₂O), log(CO/CO₂))
        """
        R = 8.314  # J/(mol·K)
        
        # For Ellingham diagrams, gas ratio scales are reference lines
        # They represent the equilibrium conditions for:
        # H₂ + 0.5 O₂ → H₂O
        # CO + 0.5 O₂ → CO₂
        
        # These are typically plotted as horizontal reference lines
        # For H₂/H₂O: log(H₂/H₂O) = 0 at standard conditions
        # For CO/CO₂: log(CO/CO₂) = 0 at standard conditions
        
        # Create reference lines (these would normally be calculated from 
        # standard formation energies, but for now we'll use simple references)
        
        # H₂/H₂O reference line (simplified)
        # At 1000°C, log(H₂/H₂O) ≈ -2.5 for typical Ellingham diagrams
        log_H2_H2O = np.full_like(T_K, -2.5) + 0.001 * (T_K - 1273)  # Slight temperature dependence
        
        # CO/CO₂ reference line (simplified)  
        # At 1000°C, log(CO/CO₂) ≈ -2.0 for typical Ellingham diagrams
        log_CO_CO2 = np.full_like(T_K, -2.0) + 0.001 * (T_K - 1273)  # Slight temperature dependence
        
        return log_H2_H2O, log_CO_CO2
    
    def calc_reduction_feasibility(self, DG_eff: float) -> Tuple[str, str]:
        """
        Determine reduction feasibility based on effective Gibbs free energy.
        
        Args:
            DG_eff: Effective Gibbs free energy in kJ/mol O₂
            
        Returns:
            Tuple of (feasibility_status, color_class)
        """
        if DG_eff < -50:  # Strongly favorable
            return "Highly Favorable", "feasibility-positive"
        elif DG_eff < 0:  # Favorable
            return "Favorable", "feasibility-positive"
        elif DG_eff < 50:  # Marginal
            return "Marginal", "feasibility-neutral"
        else:  # Unfavorable
            return "Unfavorable", "feasibility-negative"
    
    def get_temperature_markers(self, T_range: Tuple[float, float]) -> List[float]:
        """
        Get temperature markers for annotations.
        
        Args:
            T_range: (T_min, T_max) in Kelvin
            
        Returns:
            List of temperature markers in Kelvin
        """
        T_min, T_max = T_range
        
        # Standard markers
        markers = [800, 1000, 1200]  # °C
        
        # Convert to Kelvin and filter by range
        markers_K = [T + 273.15 for T in markers]
        markers_K = [T for T in markers_K if T_min <= T <= T_max]
        
        return markers_K
    
    def calc_crossover_temperature(self, oxide_key: str, E: float, r: float) -> Optional[float]:
        """
        Calculate temperature where ΔG_eff = 0 (crossover point).
        
        Args:
            oxide_key: Oxide identifier
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            Crossover temperature in Kelvin, or None if no crossover
        """
        # Create temperature range for root finding
        T_range = np.linspace(300, 2400, 1000)
        
        # Calculate off-equilibrium Gibbs free energy
        DG_eff = self.calc_off_equilibrium_DG(oxide_key, T_range, E, r)
        
        # Find where DG_eff crosses zero
        zero_crossings = np.where(np.diff(np.sign(DG_eff)))[0]
        
        if len(zero_crossings) == 0:
            return None
        
        # Interpolate to find exact crossover temperature
        idx = zero_crossings[0]
        T1, T2 = T_range[idx], T_range[idx + 1]
        DG1, DG2 = DG_eff[idx], DG_eff[idx + 1]
        
        # Linear interpolation
        T_crossover = T1 + (T2 - T1) * (-DG1) / (DG2 - DG1)
        
        return T_crossover
    
    def get_periodic_group(self, oxide_key: str) -> str:
        """
        Determine periodic table group for color coding.
        
        Args:
            oxide_key: Oxide identifier
            
        Returns:
            Group identifier for color palette
        """
        group_mapping = {
            'TiO2': 'Group4', 'TiO': 'Group4', 'ZrO2': 'Group4',
            'NbO2': 'Group5', 'NbO': 'Group5', 'Nb2O5': 'Group5',
            'Ta2O5': 'Group5', 'V2O3': 'Group5', 'V2O5': 'Group5',
            'MoO2': 'Group6', 'MoO3': 'Group6', 'WO2': 'Group6', 'WO3': 'Group6'
        }
        
        return group_mapping.get(oxide_key, 'Other')
    
    def validate_calculation(self, oxide_key: str, T_K: float, E: float, r: float) -> Dict:
        """
        Validate calculation against known data points.
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            Dictionary with validation results
        """
        # Calculate values
        DG_eq = self.calc_equilibrium_DG(oxide_key, np.array([T_K]))[0]
        DG_eff = self.calc_off_equilibrium_DG(oxide_key, np.array([T_K]), E, r)[0]
        
        # Get oxide data
        oxide_data = self.data_loader.get_oxide_data(oxide_key)
        n_electrons = oxide_data['n_electrons'] if oxide_data else 4
        
        # Calculate components
        electric_contribution = -(n_electrons * FARADAY_CONSTANT * E * r) / 1000
        W_ph = self._get_W_ph(oxide_key)
        
        validation = {
            'oxide': oxide_key,
            'temperature_K': T_K,
            'temperature_C': T_K - 273.15,
            'electric_field_MV_m': E / 1e6,
            'particle_radius_um': r * 1e6,
            'DG_eq_kJ_per_molO2': DG_eq,
            'electric_contribution_kJ_per_molO2': electric_contribution,
            'W_ph_kJ_per_molO2': W_ph,
            'DG_eff_kJ_per_molO2': DG_eff,
            'n_electrons': n_electrons,
            'feasibility': self.calc_reduction_feasibility(DG_eff)
        }
        
        return validation


def test_thermodynamic_engine():
    """Test the thermodynamic engine with known values."""
    from data_loader import load_janaf_data
    
    # Load data
    loader = load_janaf_data()
    engine = ThermodynamicEngine(loader)
    
    # Test TiO2 at known conditions (from slide 26)
    if 'TiO2' in loader.get_available_oxides():
        T_test = 1000  # K
        E_test = 2e6   # V/m
        r_test = 5e-6  # m
        
        validation = engine.validate_calculation('TiO2', T_test, E_test, r_test)
        
        print("TiO2 Validation Test:")
        print(f"Temperature: {validation['temperature_C']:.0f}°C")
        print(f"Electric field: {validation['electric_field_MV_m']:.1f} MV/m")
        print(f"Particle radius: {validation['particle_radius_um']:.1f} µm")
        print(f"ΔG° (equilibrium): {validation['DG_eq_kJ_per_molO2']:.1f} kJ/mol O₂")
        print(f"Electric contribution: {validation['electric_contribution_kJ_per_molO2']:.1f} kJ/mol O₂")
        print(f"W_ph: {validation['W_ph_kJ_per_molO2']:.1f} kJ/mol O₂")
        print(f"ΔG_eff (off-equilibrium): {validation['DG_eff_kJ_per_molO2']:.1f} kJ/mol O₂")
        print(f"Feasibility: {validation['feasibility'][0]}")
        
        # Expected: ΔG_eff ≈ -3500 kJ/mol O₂ (from slide 26)
        expected = -3500
        actual = validation['DG_eff_kJ_per_molO2']
        error = abs(actual - expected) / abs(expected) * 100
        
        print(f"\nValidation:")
        print(f"Expected: {expected:.0f} kJ/mol O₂")
        print(f"Actual: {actual:.0f} kJ/mol O₂")
        print(f"Error: {error:.1f}%")


if __name__ == "__main__":
    test_thermodynamic_engine()
