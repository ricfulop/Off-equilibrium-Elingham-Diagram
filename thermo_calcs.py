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
    
    def calc_off_equilibrium_DG_with_validation(self, oxide_key: str, T_K: np.ndarray, 
                                               E: float, r: float) -> Tuple[np.ndarray, Dict]:
        """
        Calculate off-equilibrium DG with comprehensive validation.
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            Tuple of (DG_eff array, validation_results)
        """
        from scientific_data import get_parameter_with_validation, W_PH_CONSTANTS_SCIENTIFIC
        from validation_module import ValidationEngine
        
        validation_results = {
            'warnings': [],
            'errors': [],
            'confidence': 'high',
            'parameter_sources': {}
        }
        
        # Validate input parameters
        if E < 0 or E > 5e6:  # 5 MV/m upper limit
            validation_results['errors'].append(f"Electric field {E/1e6:.1f} MV/m outside valid range (0-5 MV/m)")
            validation_results['confidence'] = 'low'
        
        if r < 1e-8 or r > 1e-4:  # 0.01 μm to 100 μm
            validation_results['errors'].append(f"Particle radius {r*1e6:.1f} μm outside valid range (0.01-100 μm)")
            validation_results['confidence'] = 'low'
        
        # Get scientific parameters with validation
        W_ph, warning = get_parameter_with_validation(
            W_PH_CONSTANTS_SCIENTIFIC, oxide_key, T_K[0], 20.0
        )
        if warning:
            validation_results['warnings'].append(warning)
            validation_results['confidence'] = 'medium'
        
        validation_results['parameter_sources']['W_ph'] = {
            'value': W_ph,
            'source': W_PH_CONSTANTS_SCIENTIFIC.get(oxide_key, {}).source if oxide_key in W_PH_CONSTANTS_SCIENTIFIC else 'default'
        }
        
        # Calculate off-equilibrium DG
        DG_eq = self.calc_equilibrium_DG(oxide_key, T_K)
        electric_contribution = -(4 * FARADAY_CONSTANT * E * r) / 1000  # Assume 4 electrons
        DG_eff = DG_eq + electric_contribution - W_ph
        
        # Validate against experimental data
        validation_engine = ValidationEngine()
        for i, T in enumerate(T_K):
            flash_validation = validation_engine.validate_flash_conditions(oxide_key, T, E)
            if not flash_validation['valid']:
                validation_results['warnings'].append(f"T={T:.0f}K: {flash_validation['warning']}")
                validation_results['confidence'] = 'medium'
        
        return DG_eff, validation_results
    
    def calc_equilibrium_DG_normalized(self, material_name: str, T_K: np.ndarray, 
                                      normalization: str = 'auto') -> Tuple[np.ndarray, str]:
        """Calculate normalized Gibbs free energy.
        
        Args:
            material_name: Material identifier
            T_K: Temperature array
            normalization: 'auto', 'metal', 'nonmetal', or 'reducing_agent'
        
        Returns:
            (DG_normalized, unit_label)
        """
        material_data = self.data_loader.get_material_data(material_name)
        category = material_data.get('category', 'oxides')
        
        # Get raw Gibbs free energy
        DG_raw = self.data_loader.interpolate_DG(material_name, T_K)
        
        stoich = self.data_loader.extract_compound_stoichiometry(
            material_name, 
            material_data.get('formula', ''),
            category
        )
        
        if normalization == 'auto':
            # Use native normalization (O2, N2, or C)
            return DG_raw, f"kJ/mol {stoich['nonmetal_type']}"
        elif normalization == 'metal':
            # Normalize to per mol metal atom
            DG_normalized = DG_raw * stoich['normalization_factor']
            return DG_normalized, "kJ/mol Metal"
        elif normalization == 'reducing_agent':
            # Normalize to per mol H2
            DG_normalized = DG_raw / (stoich['n_electrons'] / 2)
            return DG_normalized, "kJ/mol H2"
        else:
            # Default to auto normalization
            return DG_raw, f"kJ/mol {stoich['nonmetal_type']}"
    
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
    
    def calc_comprehensive_gas_ratios(self, T_K: np.ndarray, DG_values: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate gas ratio scales using traditional Ellingham nomographic principles.
        
        Works with both equilibrium and off-equilibrium Gibbs free energy values.
        Uses reference points and proper thermodynamic relationships.
        
        Args:
            T_K: Temperature array in Kelvin
            DG_values: Gibbs free energy values (equilibrium or off-equilibrium) in kJ/mol
        
        Returns:
            Dictionary of gas ratio arrays with keys:
            - H2_H2O, CO_CO2, H2_H2S, Cl2_HCl, H2_HCl, CO_HCl, 
              pO2, H2_O2, CO_O2, CH4_H2
        """
        R = 8.314e-3  # kJ/(mol·K)
        T_C = T_K - 273.15
        
        gas_ratios = {}
        
        # 1. Oxygen partial pressure (log₁₀(pO₂))
        # pO₂ = exp(ΔG / RT) - works for both equilibrium and off-equilibrium
        gas_ratios['pO2'] = DG_values / (R * T_K * np.log(10))
        
        # 2. CO/CO₂ ratio using correct reference point
        # Reference: CO + 1/2 O₂ → CO₂, ΔG° = -257.2 + 0.084*T kJ/mol
        DG_CO_ref = -257.2 + 0.084 * T_C
        gas_ratios['CO_CO2'] = (DG_values - DG_CO_ref) / (2 * R * T_K)
        
        # 3. H₂/H₂O ratio using correct reference point  
        # Reference: H₂ + 1/2 O₂ → H₂O, ΔG° = -237.1 + 0.043*T kJ/mol
        DG_H2_ref = -237.1 + 0.043 * T_C
        gas_ratios['H2_H2O'] = (DG_values - DG_H2_ref) / (2 * R * T_K)
        
        # 4. H₂/H₂S ratio (sulfide reduction)
        # H₂S + 1/2 O₂ → H₂O + S, ΔG° = -200.4 + 0.042*T kJ/mol
        DG_H2S_ref = -200.4 + 0.042 * T_C
        gas_ratios['H2_H2S'] = (DG_values - DG_H2S_ref) / (2 * R * T_K)
        
        # 5. Cl₂/HCl ratio (chlorine system)
        # 2 HCl + 1/2 O₂ → H₂O + Cl₂, ΔG° = -95.3 + 0.021*T kJ/mol
        DG_HCl_ref = -95.3 + 0.021 * T_C
        gas_ratios['Cl2_HCl'] = (DG_values - DG_HCl_ref) / (2 * R * T_K)
        
        # 6. H₂/HCl ratio
        gas_ratios['H2_HCl'] = gas_ratios['H2_H2O'] + 0.5 * gas_ratios['Cl2_HCl']
        
        # 7. CO/HCl ratio
        gas_ratios['CO_HCl'] = gas_ratios['CO_CO2'] + 0.5 * gas_ratios['Cl2_HCl']
        
        # 8. H₂/O₂ ratio (direct hydrogen oxidation)
        gas_ratios['H2_O2'] = -gas_ratios['H2_H2O']
        
        # 9. CO/O₂ ratio (direct CO oxidation)
        gas_ratios['CO_O2'] = -gas_ratios['CO_CO2']
        
        # 10. CH₄/H₂ ratio (methane reforming)
        # CH₄ + 2 O₂ → CO₂ + 2 H₂O, ΔG° = -800.8 + 0.205*T kJ/mol
        DG_CH4_ref = -800.8 + 0.205 * T_C
        gas_ratios['CH4_H2'] = (DG_values - DG_CH4_ref) / (2 * R * T_K)
        
        # Apply reasonable bounds to prevent unrealistic values
        for key in gas_ratios:
            # Clamp gas ratios to reasonable ranges (wider bounds)
            gas_ratios[key] = np.clip(gas_ratios[key], -50, 50)
        
        return gas_ratios

    def get_gas_ratio_metadata(self) -> Dict[str, Dict[str, str]]:
        """Get display metadata for all gas ratios."""
        return {
            'H2_H2O': {
                'label': 'log(H₂/H₂O)',
                'color': '#e74c3c',
                'description': 'Hydrogen reduction'
            },
            'CO_CO2': {
                'label': 'log(CO/CO₂)',
                'color': '#3498db',
                'description': 'Carbon monoxide reduction'
            },
            'H2_H2S': {
                'label': 'log(H₂/H₂S)',
                'color': '#f39c12',
                'description': 'Hydrogen sulfide reduction'
            },
            'Cl2_HCl': {
                'label': 'log(Cl₂/HCl)',
                'color': '#9b59b6',
                'description': 'Chlorine system'
            },
            'H2_HCl': {
                'label': 'log(H₂/HCl)',
                'color': '#e67e22',
                'description': 'Hydrogen chloride reduction'
            },
            'CO_HCl': {
                'label': 'log(CO/HCl)',
                'color': '#34495e',
                'description': 'CO chloride reduction'
            },
            'pO2': {
                'label': 'log₁₀(pO₂)',
                'color': '#2c3e50',
                'description': 'Oxygen partial pressure'
            },
            'H2_O2': {
                'label': 'log(H₂/O₂)',
                'color': '#1abc9c',
                'description': 'Direct hydrogen oxidation'
            },
            'CO_O2': {
                'label': 'log(CO/O₂)',
                'color': '#8e44ad',
                'description': 'Direct CO oxidation'
            },
            'CH4_H2': {
                'label': 'log(CH₄/H₂)',
                'color': '#27ae60',
                'description': 'Methane reforming'
            }
        }
    
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
    
    def calc_oxygen_potential_required(self, oxide_key: str, T_K: np.ndarray, E: float, r: float) -> np.ndarray:
        """
        Calculate required oxygen partial pressure for reduction under field and particle size.
        
        Implements the off-equilibrium stability condition:
        ΔB = ΔG° - nFE·r - W_ph + (x/2)RT·ln(pO₂) = 0
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            ln(pO₂_req) - natural log of required oxygen partial pressure
        """
        # Get oxide data
        oxide_data = self.data_loader.get_oxide_data(oxide_key)
        if oxide_data is None:
            return np.full_like(T_K, np.nan)
        
        n_electrons = oxide_data['n_electrons']
        x_oxygen = oxide_data['n_oxygen']
        
        # Calculate effective Gibbs free energy (off-equilibrium)
        DG_eff = self.calc_off_equilibrium_DG(oxide_key, T_K, E, r)
        
        # Calculate required oxygen potential
        # From: ΔB = ΔG_eff + (x/2)RT·ln(pO₂) = 0
        # So: ln(pO₂_req) = -2ΔG_eff/(xRT)
        R = 8.314  # J/(mol·K)
        ln_pO2_req = -2 * DG_eff * 1000 / (x_oxygen * R * T_K)  # Convert kJ to J
        
        return ln_pO2_req
    
    def calc_h2_h2o_equilibrium_constant(self, T_K: np.ndarray) -> np.ndarray:
        """
        Calculate equilibrium constant K_H for H₂ + 0.5O₂ → H₂O reaction.
        
        Uses JANAF data for H₂O and standard values for H₂.
        
        Args:
            T_K: Temperature array in Kelvin
            
        Returns:
            K_H(T) = p_H2O / (p_H2 * p_O2^0.5)
        """
        # Get H₂O formation Gibbs free energy from JANAF data
        try:
            h2o_data = self.data_loader.raw_data[self.data_loader.raw_data['species'] == 'Water (H2O)']
            if h2o_data.empty:
                # Fallback to standard values if no JANAF data
                return self._calc_h2_h2o_constant_standard(T_K)
            
            # Interpolate H₂O formation Gibbs free energy
            T_h2o = h2o_data['T_K'].values
            DG_h2o = h2o_data['delta_f_G_kJ_per_mol'].values
            
            # Remove NaN values
            valid_mask = ~np.isnan(DG_h2o)
            T_h2o = T_h2o[valid_mask]
            DG_h2o = DG_h2o[valid_mask]
            
            if len(T_h2o) == 0:
                return self._calc_h2_h2o_constant_standard(T_K)
            
            # Interpolate to requested temperatures
            DG_h2o_interp = np.interp(T_K, T_h2o, DG_h2o)
            
            # Calculate equilibrium constant
            # For H₂ + 0.5O₂ → H₂O: K_H = exp(-ΔG°/RT)
            R = 8.314  # J/(mol·K)
            K_H = np.exp(-DG_h2o_interp * 1000 / (R * T_K))  # Convert kJ to J
            
            return K_H
            
        except Exception as e:
            print(f"Warning: Could not calculate K_H from JANAF data: {e}")
            return self._calc_h2_h2o_constant_standard(T_K)
    
    def _calc_h2_h2o_constant_standard(self, T_K: np.ndarray) -> np.ndarray:
        """Calculate K_H using standard thermodynamic values."""
        # Standard formation Gibbs free energy for H₂O (kJ/mol)
        # Using approximate values: ΔG° ≈ -228 + 0.044*T (kJ/mol)
        DG_h2o_standard = -228 + 0.044 * (T_K - 298)  # kJ/mol
        
        R = 8.314  # J/(mol·K)
        K_H = np.exp(-DG_h2o_standard * 1000 / (R * T_K))  # Convert kJ to J
        
        return K_H
    
    def calc_h2_h2o_ratio_required(self, oxide_key: str, T_K: np.ndarray, E: float, r: float) -> np.ndarray:
        """
        Calculate required H₂/H₂O ratio for reduction under field and particle size.
        
        Implements the markdown method:
        1. Calculate required oxygen potential: ln(pO₂_req)
        2. Calculate H₂/H₂O equilibrium constant: K_H(T)
        3. Calculate required ratio: H₂/H₂O = 1/(K_H * √pO₂_req)
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            
        Returns:
            Required H₂/H₂O ratio
        """
        # Step 1: Calculate required oxygen potential
        ln_pO2_req = self.calc_oxygen_potential_required(oxide_key, T_K, E, r)
        pO2_req = np.exp(ln_pO2_req)
        
        # Step 2: Calculate H₂/H₂O equilibrium constant
        K_H = self.calc_h2_h2o_equilibrium_constant(T_K)
        
        # Step 3: Calculate required H₂/H₂O ratio
        # H₂/H₂O = 1/(K_H * √pO₂_req)
        h2_h2o_ratio = 1.0 / (K_H * np.sqrt(pO2_req))
        
        return h2_h2o_ratio
    
    def calc_h2_partial_pressure_required(self, oxide_key: str, T_K: np.ndarray, E: float, r: float, 
                                         p_h2o: float = 0.01) -> np.ndarray:
        """
        Calculate required H₂ partial pressure for reduction.
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            p_h2o: H₂O partial pressure in atm (default: 0.01 atm)
            
        Returns:
            Required H₂ partial pressure in atm
        """
        # Calculate required H₂/H₂O ratio
        h2_h2o_ratio = self.calc_h2_h2o_ratio_required(oxide_key, T_K, E, r)
        
        # Calculate H₂ partial pressure
        p_h2_req = h2_h2o_ratio * p_h2o
        
        return p_h2_req

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
        
        # Calculate new H₂ requirements using markdown method
        ln_pO2_req = self.calc_oxygen_potential_required(oxide_key, np.array([T_K]), E, r)[0]
        h2_h2o_ratio = self.calc_h2_h2o_ratio_required(oxide_key, np.array([T_K]), E, r)[0]
        p_h2_req = self.calc_h2_partial_pressure_required(oxide_key, np.array([T_K]), E, r)[0]
        
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
            'feasibility': self.calc_reduction_feasibility(DG_eff),
            # New H₂ calculation results
            'ln_pO2_req': ln_pO2_req,
            'h2_h2o_ratio_req': h2_h2o_ratio,
            'p_h2_req_atm': p_h2_req
        }
        
        return validation

    def calc_kinetic_analysis(self, oxide_key: str, T_K: np.ndarray, E: float, r: float, 
                             p_h2: float = 0.25, flash_state: bool = True) -> Dict:
        """
        Comprehensive kinetic analysis for reduction process with flash enhancement.
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature array in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            p_h2: H₂ partial pressure in atm
            flash_state: Whether particles are in flash state
            
        Returns:
            Dictionary with kinetic analysis results
        """
        from scientific_data import DIFFUSION_PARAMETERS_SCIENTIFIC, FLASH_ENHANCEMENT_SCIENTIFIC
        from validation_module import ValidationEngine
        
        kinetics = ValidationEngine()
        
        # Get kinetic parameters from scientific data
        if oxide_key in DIFFUSION_PARAMETERS_SCIENTIFIC:
            diff_params = DIFFUSION_PARAMETERS_SCIENTIFIC[oxide_key]
            Ea = diff_params['activation_energy'].value
            A = diff_params['pre_exponential'].value
            alpha = diff_params['field_enhancement'].value
        else:
            # Default values if not available
            Ea = 200.0
            A = 1e11
            alpha = 0.1
        
        if oxide_key in FLASH_ENHANCEMENT_SCIENTIFIC:
            beta = FLASH_ENHANCEMENT_SCIENTIFIC[oxide_key].value
            T_flash = 1200  # Default flash temperature
        else:
            beta = 30.0
            T_flash = 1200
        
        # Calculate kinetic parameters
        R = 8.314e-3  # kJ/(mol·K)
        
        # Arrhenius rate constant
        k_arrhenius = A * np.exp(-Ea / (R * T_K))
        
        # H₂ pressure dependence
        h2_dependence = p_h2
        
        # Electric field enhancement
        field_enhancement = 1 + alpha * E * r / 1e6
        
        # Flash diffusion enhancement
        if flash_state:
            temp_enhancement = np.where(
                T_K >= T_flash,
                np.exp((T_K - T_flash) / 200),
                1.0
            )
            field_enhancement_flash = (E / 1e6) ** 0.5
            flash_enhancement = 1 + beta * temp_enhancement * field_enhancement_flash
        else:
            flash_enhancement = 1.0
        
        # Total reduction rate
        reduction_rate = k_arrhenius * h2_dependence * field_enhancement * flash_enhancement
        
        # Calculate conversion time (first-order kinetics)
        conversion_time = -np.log(0.05) / reduction_rate  # 95% conversion
        
        # Calculate throughput capacity (assuming 1 L reactor)
        reactor_volume = 0.001  # m³
        particle_density = 4000  # kg/m³
        particle_volume = (4/3) * np.pi * r**3
        particle_mass = particle_density * particle_volume
        max_particles = reactor_volume / particle_volume
        throughput_capacity = (max_particles * particle_mass) / conversion_time * 3600  # kg/hr
        
        # Validate against experimental data
        validation_results = {}
        for i, T in enumerate(T_K):
            flash_validation = kinetics.validate_flash_conditions(oxide_key, T, E)
            validation_results[f'T_{T:.0f}K'] = flash_validation
        
        return {
            'oxide_key': oxide_key,
            'temperature_K': T_K,
            'temperature_C': T_K - 273.15,
            'electric_field_MV_m': E / 1e6,
            'particle_radius_um': r * 1e6,
            'h2_partial_pressure_atm': p_h2,
            'flash_state': flash_state,
            'activation_energy_kJ_mol': Ea,
            'pre_exponential_factor_s': A,
            'field_enhancement_factor': alpha,
            'flash_diffusion_factor': beta,
            'flash_temperature_threshold_K': T_flash,
            'flash_temperature_threshold_C': T_flash - 273.15,
            'reduction_rate_s': reduction_rate,
            'conversion_time_95pct_s': conversion_time,
            'throughput_capacity_kg_hr': throughput_capacity,
            'field_enhancement_factor_calc': field_enhancement,
            'flash_enhancement_factor': flash_enhancement,
            'total_enhancement_factor': field_enhancement * flash_enhancement,
            'validation_results': validation_results
        }

    def calc_residence_time_analysis(self, oxide_key: str, T_K: float, E: float, r: float, 
                                    p_h2: float = 0.25, tube_length: float = 0.30, 
                                    tube_diameter: float = 0.05, gas_velocity: float = 1.0,
                                    particle_density: float = 4000) -> Dict:
        """
        Calculate particle residence time analysis and reduction completion.
        
        Args:
            oxide_key: Oxide identifier
            T_K: Temperature in Kelvin
            E: Electric field in V/m
            r: Particle radius in m
            p_h2: H₂ partial pressure in atm
            tube_length: Reactor tube length in m
            tube_diameter: Reactor tube diameter in m
            gas_velocity: Gas velocity in m/s
            particle_density: Particle density in kg/m³
            
        Returns:
            Dictionary with residence time analysis results
        """
        from scientific_data import DIFFUSION_PARAMETERS_SCIENTIFIC, FLASH_ENHANCEMENT_SCIENTIFIC
        from validation_module import ValidationEngine
        
        kinetics = ValidationEngine()
        
        # Get kinetic parameters (adjusted for plasma flash sintering)
        if oxide_key in DIFFUSION_PARAMETERS_SCIENTIFIC:
            diff_params = DIFFUSION_PARAMETERS_SCIENTIFIC[oxide_key]
            Ea = diff_params['activation_energy'].value * 0.3  # Reduce activation energy for plasma
            A = diff_params['pre_exponential'].value * 1e12  # Much higher pre-exponential for plasma
            alpha = diff_params['field_enhancement'].value
        else:
            Ea = 60.0  # Much lower activation energy for plasma conditions
            A = 1e20  # Very high pre-exponential for plasma conditions
            alpha = 0.1
        
        if oxide_key in FLASH_ENHANCEMENT_SCIENTIFIC:
            beta = FLASH_ENHANCEMENT_SCIENTIFIC[oxide_key].value
            T_flash = 1200
        else:
            beta = 30.0
            T_flash = 1200
        
        # Calculate residence time
        residence_time = tube_length / gas_velocity  # seconds
        
        # Calculate particle settling velocity (Stokes law)
        g = 9.81  # m/s²
        air_viscosity = 1.8e-5  # Pa·s at high temperature
        particle_volume = (4/3) * np.pi * r**3
        particle_mass = particle_density * particle_volume
        settling_velocity = (2 * particle_mass * g) / (6 * np.pi * air_viscosity * r)
        
        # Effective residence time (accounting for settling)
        effective_residence_time = tube_length / (gas_velocity + settling_velocity)
        
        # Calculate reduction kinetics
        R = 8.314e-3  # kJ/(mol·K)
        
        # Check if in flash state
        in_flash_state = T_K >= T_flash
        
        # Arrhenius rate constant
        k_arrhenius = A * np.exp(-Ea / (R * T_K))
        
        # Enhancement factors
        field_enhancement = 1 + alpha * E * r / 1e6
        
        if in_flash_state:
            temp_enhancement = np.exp((T_K - T_flash) / 200)
            field_enhancement_flash = (E / 1e6) ** 0.5
            flash_enhancement = 1 + beta * temp_enhancement * field_enhancement_flash
        else:
            flash_enhancement = 1.0
        
        # Total reduction rate
        reduction_rate = k_arrhenius * p_h2 * field_enhancement * flash_enhancement
        
        # Calculate conversion percentage at exit time
        # Using first-order kinetics: C(t) = C₀ * exp(-k*t)
        conversion_at_exit = 1 - np.exp(-reduction_rate * effective_residence_time)
        conversion_percentage = conversion_at_exit * 100
        
        # Calculate time for 95% conversion
        time_95pct = -np.log(0.05) / reduction_rate
        
        # Calculate time for 99% conversion
        time_99pct = -np.log(0.01) / reduction_rate
        
        # Determine reduction status
        if conversion_percentage >= 95:
            reduction_status = "Complete"
            status_color = "success"
        elif conversion_percentage >= 80:
            reduction_status = "Near Complete"
            status_color = "warning"
        elif conversion_percentage >= 50:
            reduction_status = "Partial"
            status_color = "warning"
        else:
            reduction_status = "Incomplete"
            status_color = "danger"
        
        # Calculate thermodynamic feasibility
        DG_eq = self.calc_equilibrium_DG(oxide_key, np.array([T_K]))
        electric_contribution = -(4 * FARADAY_CONSTANT * E * r) / 1000
        W_ph = self._get_W_ph(oxide_key)
        DG_eff = DG_eq + electric_contribution - W_ph
        
        # Determine thermodynamic feasibility
        if DG_eff < 0:
            thermo_feasible = True
            thermo_status = "Thermodynamically Favorable"
            thermo_color = "success"
        else:
            thermo_feasible = False
            thermo_status = "Thermodynamically Unfavorable"
            thermo_color = "danger"
        
        # Calculate process efficiency
        if thermo_feasible and conversion_percentage >= 95:
            process_efficiency = "High"
            efficiency_color = "success"
        elif thermo_feasible and conversion_percentage >= 80:
            process_efficiency = "Medium"
            efficiency_color = "warning"
        elif thermo_feasible:
            process_efficiency = "Low"
            efficiency_color = "warning"
        else:
            process_efficiency = "Not Feasible"
            efficiency_color = "danger"
        
        # Validate against experimental data
        flash_validation = kinetics.validate_flash_conditions(oxide_key, T_K, E)
        
        return {
            'oxide_key': oxide_key,
            'temperature_K': T_K,
            'temperature_C': T_K - 273.15,
            'electric_field_MV_m': E / 1e6,
            'particle_radius_um': r * 1e6,
            'h2_partial_pressure_atm': p_h2,
            'tube_length_m': tube_length,
            'tube_diameter_m': tube_diameter,
            'gas_velocity_m_s': gas_velocity,
            'particle_density_kg_m3': particle_density,
            'residence_time_s': residence_time,
            'settling_velocity_m_s': settling_velocity,
            'effective_residence_time_s': effective_residence_time,
            'reduction_rate_s': reduction_rate,
            'conversion_percentage': conversion_percentage,
            'conversion_at_exit': conversion_at_exit,
            'time_95pct_conversion_s': time_95pct,
            'time_99pct_conversion_s': time_99pct,
            'reduction_status': reduction_status,
            'reduction_status_color': status_color,
            'thermodynamic_feasible': thermo_feasible,
            'thermodynamic_status': thermo_status,
            'thermodynamic_status_color': thermo_color,
            'DG_eff_kJ_per_molO2': DG_eff,
            'process_efficiency': process_efficiency,
            'process_efficiency_color': efficiency_color,
            'in_flash_state': in_flash_state,
            'flash_temperature_threshold_K': T_flash,
            'flash_temperature_threshold_C': T_flash - 273.15,
            'field_enhancement_factor': field_enhancement,
            'flash_enhancement_factor': flash_enhancement,
            'total_enhancement_factor': field_enhancement * flash_enhancement,
            'validation_results': flash_validation
        }


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
