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
        P_H2_needed = P_H2O_assumed * np.exp(DG_eq_J / (R * T_K))
        
        # Debug: Add some debug info to see what's happening
        debug_info = f" (DG_eq={DG_eq:.1f} kJ/mol, exp={np.exp(DG_eq_J / (R * T_K)):.2e})"
        
        # Format the pressure appropriately
        if P_H2_needed < 1e-4:
            P_H2_display = f"{P_H2_needed:.2e} atm"
        else:
            P_H2_display = f"{P_H2_needed:.4f} atm"
        
        text_lines.append(f"**{oxide}** at {T_C:.0f}°C:")
        text_lines.append(f"- Electric field: {E_MV_m:.1f} MV/m")
        text_lines.append(f"- Particle radius: {r_um:.0f} µm")
        text_lines.append(f"- ΔG° (equilibrium): {DG_eq:.1f} kJ/mol O₂")
        text_lines.append(f"- ΔG_eff (off-equilibrium): {DG_eff:.1f} kJ/mol O₂")
        text_lines.append(f"- Reduction feasibility: {feasibility}")
        
        # Add H₂ partial pressure analysis
        P_H2_available = 0.25  # atm (25% of 1 atm)
        text_lines.append(f"- **H₂ partial pressure needed**: {P_H2_display}{debug_info}")
        if P_H2_needed <= P_H2_available:
            text_lines.append(f"- **✅ H₂ reduction feasible** with 25% H₂ (0.25 atm available)")
        else:
            H2_percent_needed = (P_H2_needed / P_H2_available) * 100
            text_lines.append(f"- **❌ H₂ reduction requires {H2_percent_needed:.1f}% H₂** (more than 25% available)")
        
        text_lines.append("")
    
    # Add industrial processing analysis
    text_lines.append("## 🏭 Industrial Processing Analysis")
    text_lines.append("")
    
    # Import config values
    from config import (TUBE_LENGTH, TUBE_DIAMETER, PARTICLE_DENSITY, GAS_VELOCITY, 
                       H2_EFFICIENCY, MOLECULAR_WEIGHTS, PROCESSING_RATES)
    
    # Calculate particle volume and mass
    # Use the first particle radius from the validation_results
    first_result = validation_results[0] if validation_results and len(validation_results) > 0 else None
    if first_result and 'particle_radius_um' in first_result:
        particle_radius_um = first_result['particle_radius_um']
        particle_radius_m = particle_radius_um * 1e-6  # Convert µm to m
    else:
        particle_radius_m = 1e-6  # Default 1 µm
    particle_volume = (4/3) * np.pi * particle_radius_m**3  # m³
    particle_mass = PARTICLE_DENSITY * particle_volume  # kg
    
    # Gas flow assumptions
    residence_time = TUBE_LENGTH / GAS_VELOCITY  # s
    
    # Calculate particles per kg
    particles_per_kg = 1.0 / particle_mass
    
    # Calculate H₂ consumption per kg of particles
    # Assuming complete reduction: MO + H₂ → M + H₂O
    # For TiO₂: TiO₂ + H₂ → Ti + H₂O (1 mol H₂ per mol TiO₂)
    
    # Get the oxide from the first result
    oxide = first_result['oxide'] if first_result and 'oxide' in first_result else 'TiO2'
    oxide_mw = MOLECULAR_WEIGHTS.get(oxide, 100.0)  # Default fallback
    h2_mw = 2.016  # g/mol
    
    # Moles of oxide per kg
    moles_oxide_per_kg = 1000 / oxide_mw  # mol/kg
    
    # Moles of H₂ needed per kg (1:1 stoichiometry for most oxides)
    moles_h2_per_kg = moles_oxide_per_kg  # mol/kg
    
    # Mass of H₂ needed per kg
    mass_h2_per_kg = moles_h2_per_kg * h2_mw / 1000  # kg H₂/kg oxide
    
    text_lines.append(f"**Processing Parameters:**")
    text_lines.append(f"- Tube length: {TUBE_LENGTH*100:.0f} cm")
    text_lines.append(f"- Tube diameter: {TUBE_DIAMETER*100:.0f} cm")
    text_lines.append(f"- Gas velocity: {GAS_VELOCITY:.1f} m/s")
    text_lines.append(f"- Residence time: {residence_time:.1f} s")
    text_lines.append(f"- Particle mass: {particle_mass*1e9:.1f} ng")
    text_lines.append(f"- Particles per kg: {particles_per_kg:.2e}")
    text_lines.append("")
    
    text_lines.append(f"**H₂ Consumption Analysis:**")
    text_lines.append(f"- Molecular weight of {oxide}: {oxide_mw:.1f} g/mol")
    text_lines.append(f"- H₂ needed per kg {oxide}: {mass_h2_per_kg:.3f} kg H₂/kg oxide")
    text_lines.append(f"- Molar ratio: {moles_h2_per_kg:.2f} mol H₂/kg oxide")
    text_lines.append("")
    
    text_lines.append(f"**Processing Rate Analysis:**")
    for rate in PROCESSING_RATES:
        h2_flow_rate = rate * mass_h2_per_kg  # kg H₂/hr
        h2_volumetric_flow = h2_flow_rate * 22.4 / h2_mw  # m³/hr (at STP)
        
        # Calculate required H₂ concentration in feed gas
        # Assuming 25% H₂ in feed gas
        total_gas_flow = h2_volumetric_flow / 0.25  # m³/hr
        n2_flow = total_gas_flow - h2_volumetric_flow  # m³/hr
        
        text_lines.append(f"- **{rate} kg/hr processing:**")
        text_lines.append(f"  - H₂ consumption: {h2_flow_rate:.2f} kg H₂/hr")
        text_lines.append(f"  - H₂ volumetric flow: {h2_volumetric_flow:.1f} m³/hr")
        text_lines.append(f"  - Total gas flow: {total_gas_flow:.1f} m³/hr")
        text_lines.append(f"  - N₂ flow: {n2_flow:.1f} m³/hr")
        text_lines.append("")
    
    # Add reduction kinetics analysis
    text_lines.append(f"**Reduction Kinetics:**")
    text_lines.append(f"- Single particle reduction time: ~{residence_time:.1f} s (residence time)")
    text_lines.append(f"- Reduction rate: {1/residence_time:.2f} particles/s")
    text_lines.append(f"- Mass reduction rate: {particle_mass/residence_time*3600:.2e} kg/hr per particle")
    text_lines.append("")
    
    # Add efficiency analysis
    text_lines.append(f"**Process Efficiency:**")
    text_lines.append(f"- H₂ utilization efficiency: {H2_EFFICIENCY*100:.0f}%")
    text_lines.append(f"- Actual H₂ consumption (with efficiency): {mass_h2_per_kg/H2_EFFICIENCY:.3f} kg H₂/kg oxide")
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
