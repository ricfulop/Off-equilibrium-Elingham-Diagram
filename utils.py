"""
Utility functions for the Off-Equilibrium Ellingham Diagram App.
"""

import numpy as np
from typing import List, Dict, Tuple
from config import COLOR_PALETTE, LINE_STYLES


def kelvin_to_celsius(T_K: np.ndarray) -> np.ndarray:
    """Convert temperature from Kelvin to Celsius."""
    return T_K - 273.15


def celsius_to_kelvin(T_C: np.ndarray) -> np.ndarray:
    """Convert temperature from Celsius to Kelvin."""
    return T_C + 273.15


def mv_per_m_to_v_per_m(E_MV_m: float) -> float:
    """Convert electric field from MV/m to V/m."""
    return E_MV_m * 1e6


def v_per_m_to_mv_per_m(E_V_m: float) -> float:
    """Convert electric field from V/m to MV/m."""
    return E_V_m / 1e6


def um_to_m(r_um: float) -> float:
    """Convert particle radius from micrometers to meters."""
    return r_um * 1e-6


def m_to_um(r_m: float) -> float:
    """Convert particle radius from meters to micrometers."""
    return r_m * 1e6


def get_color_for_oxide(oxide_key: str, group: str) -> str:
    """Get color for oxide based on periodic table group."""
    group_colors = COLOR_PALETTE.get(group, COLOR_PALETTE['Other'])
    
    # Simple hash-based color selection for multiple oxides in same group
    hash_val = hash(oxide_key) % len(group_colors)
    return group_colors[hash_val]


def get_line_style(line_type: str) -> str:
    """Get line style for different curve types."""
    return LINE_STYLES.get(line_type, 'solid')


def format_scientific(value: float, precision: int = 2) -> str:
    """Format scientific notation for display."""
    if abs(value) >= 1000:
        return f"{value/1000:.{precision}f}k"
    elif abs(value) >= 1:
        return f"{value:.{precision}f}"
    elif abs(value) >= 0.01:
        return f"{value:.{precision}f}"
    else:
        return f"{value:.2e}"


def create_legend_label(oxide_key: str, line_type: str, E_MV_m: float, r_um: float) -> str:
    """Create legend label for plot traces."""
    if line_type == 'equilibrium':
        return f"{oxide_key} (Equilibrium)"
    else:
        return f"{oxide_key} (E={E_MV_m:.1f} MV/m, r={r_um:.0f} µm)"


def validate_inputs(E_MV_m: float, r_um: float, T_range: Tuple[float, float]) -> Tuple[bool, str]:
    """
    Validate user inputs.
    
    Returns:
        (is_valid, error_message)
    """
    # Validate electric field
    if E_MV_m < 0.1 or E_MV_m > 10.0:
        return False, "Electric field must be between 0.1 and 10.0 MV/m"
    
    # Validate particle radius
    if r_um < 0.1 or r_um > 100.0:
        return False, "Particle radius must be between 0.1 and 100.0 µm"
    
    # Validate temperature range
    T_min, T_max = T_range
    if T_min < 300 or T_max > 3000:
        return False, "Temperature range must be between 300 and 3000 K"
    
    if T_min >= T_max:
        return False, "Minimum temperature must be less than maximum temperature"
    
    return True, ""


def create_temperature_ticks(T_range: Tuple[float, float]) -> List[float]:
    """Create appropriate temperature tick marks."""
    T_min, T_max = T_range
    
    # Convert to Celsius for display
    T_min_C = kelvin_to_celsius(np.array([T_min]))[0]
    T_max_C = kelvin_to_celsius(np.array([T_max]))[0]
    
    # Create ticks every 200°C
    ticks_C = np.arange(
        np.ceil(T_min_C / 200) * 200,
        np.floor(T_max_C / 200) * 200 + 1,
        200
    )
    
    return ticks_C.tolist()


def create_gas_ratio_ticks(log_ratios: np.ndarray) -> List[float]:
    """Create appropriate tick marks for gas ratio scales."""
    # Find nice round numbers for ticks
    min_val = np.min(log_ratios)
    max_val = np.max(log_ratios)
    
    # Create ticks at integer values
    ticks = np.arange(
        np.ceil(min_val),
        np.floor(max_val) + 1,
        1
    )
    
    return ticks.tolist()


def export_data_to_csv(oxide_data: Dict, filename: str) -> str:
    """
    Export calculated data to CSV format.
    
    Args:
        oxide_data: Dictionary with calculated data
        filename: Output filename
        
    Returns:
        CSV content as string
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Oxide', 'Temperature_C', 'Temperature_K', 'DG_eq_kJ_per_molO2', 
                    'DG_eff_kJ_per_molO2', 'Electric_Field_MV_m', 'Particle_Radius_um'])
    
    # Write data
    for oxide_key, data in oxide_data.items():
        T_C = kelvin_to_celsius(data['T_K'])
        T_K = data['T_K']
        DG_eq = data['DG_eq']
        DG_eff = data['DG_eff']
        E_MV_m = data['E_MV_m']
        r_um = data['r_um']
        
        for i in range(len(T_K)):
            writer.writerow([
                oxide_key,
                f"{T_C[i]:.1f}",
                f"{T_K[i]:.1f}",
                f"{DG_eq[i]:.2f}",
                f"{DG_eff[i]:.2f}",
                f"{E_MV_m:.2f}",
                f"{r_um:.2f}"
            ])
    
    return output.getvalue()


def create_info_text(validation_results: List[Dict]) -> str:
    """Create formatted info text for display."""
    if not validation_results:
        return "No data to display"
    
    text_lines = []
    text_lines.append("**Thermodynamic Analysis**")
    text_lines.append("")
    
    for result in validation_results:
        oxide = result['oxide']
        T_C = result['temperature_C']
        T_K = result['temperature_K']
        E_MV_m = result['electric_field_MV_m']
        r_um = result['particle_radius_um']
        DG_eq = result['DG_eq_kJ_per_molO2']
        DG_eff = result['DG_eff_kJ_per_molO2']
        feasibility, color_class = result['feasibility']
        
        # Calculate H₂ partial pressure requirement for reduction
        # For H₂ reduction: MO + H₂ → M + H₂O
        # The reaction quotient Q = P_H₂O / P_H₂
        # For reduction to be favorable: ΔG = ΔG° + RT ln(Q) < 0
        # So: ΔG° + RT ln(P_H₂O/P_H₂) < 0
        # Therefore: ln(P_H₂O/P_H₂) < -ΔG°/(RT)
        # So: P_H₂O/P_H₂ < exp(-ΔG°/RT)
        # And: P_H₂ > P_H₂O × exp(ΔG°/RT)
        
        R = 8.314  # J/(mol·K)
        DG_eq_J = DG_eq * 1000  # Convert to J/mol
        
        # Assume a reasonable H₂O pressure (e.g., 0.01 atm from atmosphere)
        P_H2O_assumed = 0.01  # atm
        
        # Calculate minimum H₂ pressure needed for reduction
        # P_H₂_min = P_H₂O × exp(ΔG°/RT)
        if DG_eq_J < 0:  # If ΔG° is negative (favorable)
            # For very negative ΔG°, we need very little H₂
            P_H2_needed = P_H2O_assumed * np.exp(DG_eq_J / (R * T_K))
            # Cap the minimum at a reasonable value
            P_H2_needed = max(P_H2_needed, 1e-6)  # Minimum 1 ppm
        else:  # If ΔG° is positive (unfavorable)
            # For positive ΔG°, we need high H₂ pressure
            P_H2_needed = P_H2O_assumed * np.exp(DG_eq_J / (R * T_K))
        
        text_lines.append(f"**{oxide}** at {T_C:.0f}°C:")
        text_lines.append(f"- Electric field: {E_MV_m:.1f} MV/m")
        text_lines.append(f"- Particle radius: {r_um:.0f} µm")
        text_lines.append(f"- ΔG° (equilibrium): {DG_eq:.1f} kJ/mol O₂")
        text_lines.append(f"- ΔG_eff (off-equilibrium): {DG_eff:.1f} kJ/mol O₂")
        text_lines.append(f"- Reduction feasibility: {feasibility}")
        
        # Add H₂ partial pressure analysis
        P_H2_available = 0.25  # atm (25% of 1 atm)
        if P_H2_needed < float('inf'):
            text_lines.append(f"- **H₂ partial pressure needed**: {P_H2_needed:.4f} atm")
            if P_H2_needed <= P_H2_available:
                text_lines.append(f"- **✅ H₂ reduction feasible** with 25% H₂ (0.25 atm available)")
            else:
                H2_percent_needed = (P_H2_needed / P_H2_available) * 100
                text_lines.append(f"- **❌ H₂ reduction requires {H2_percent_needed:.1f}% H₂** (more than 25% available)")
        else:
            text_lines.append(f"- **H₂ partial pressure needed**: Very high (reduction unfavorable)")
        
        text_lines.append("")
    
    return "\n".join(text_lines)


def get_default_materials() -> List[str]:
    """Get list of default materials to show."""
    return ['TiO2', 'ZrO2', 'Nb2O5', 'Ta2O5', 'MoO3', 'WO3']


def get_material_display_name(oxide_key: str) -> str:
    """Get display name for material in dropdown."""
    display_names = {
        'TiO2': 'TiO₂ (Titanium Dioxide)',
        'TiO': 'TiO (Titanium Monoxide)',
        'ZrO2': 'ZrO₂ (Zirconium Dioxide)',
        'NbO2': 'NbO₂ (Niobium Dioxide)',
        'NbO': 'NbO (Niobium Monoxide)',
        'Nb2O5': 'Nb₂O₅ (Niobium Pentoxide)',
        'Ta2O5': 'Ta₂O₅ (Tantalum Pentoxide)',
        'MoO2': 'MoO₂ (Molybdenum Dioxide)',
        'MoO3': 'MoO₃ (Molybdenum Trioxide)',
        'WO2': 'WO₂ (Tungsten Dioxide)',
        'WO3': 'WO₃ (Tungsten Trioxide)',
        'V2O3': 'V₂O₃ (Vanadium(III) Oxide)',
        'V2O5': 'V₂O₅ (Vanadium(V) Oxide)'
    }
    
    return display_names.get(oxide_key, oxide_key)
