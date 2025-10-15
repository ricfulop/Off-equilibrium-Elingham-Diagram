"""
Configuration constants for the Off-Equilibrium Ellingham Diagram App
"""

# Physical constants
FARADAY_CONSTANT = 96485  # C/mol

# Phonon/plasma work constants [kJ/mol O₂]
W_PH_CONSTANTS = {
    'TiO2': 20.0,
    'ZrO2': 22.0,
    'MgO': 22.6,
    'Al2O3': 20.2,
    'Nb2O5': 24.0,
    'Ta2O5': 26.0,
    'MoO3': 21.0,
    'WO3': 23.0,
    'CeO2': 27.3,
    'Cu2O': 18.3,
    'V2O3': 19.0,
    'V2O5': 21.0,
    'NbO': 20.0,
    'MoO2': 20.0,
    'WO2': 22.0,
}

# Default presets
DEFAULT_FIELD_PRESETS = [0.2e6, 0.5e6, 2.0e6]  # V/m
DEFAULT_RADIUS_PRESETS = [1e-6, 5e-6]  # m
DEFAULT_TEMP_RANGE = [300, 2400]  # K

# UI Configuration
TEMP_MARKERS = [800, 1000, 1200]  # °C for annotations
GAS_RATIO_TEMPS = [1000, 1200, 1500]  # °C for gas ratio scales

# Color palette by periodic table group
COLOR_PALETTE = {
    'Group4': ['#1f77b4', '#aec7e8'],  # Ti, Zr - Blue shades
    'Group5': ['#2ca02c', '#98df8a'],  # Nb, Ta, V - Green shades
    'Group6': ['#d62728', '#ff9896'],  # Mo, W - Red shades
    'Other': ['#ff7f0e', '#ffbb78'],    # Other metals - Orange shades
}

# Line styles for off-equilibrium curves
LINE_STYLES = {
    'equilibrium': 'solid',
    'off_eq_1um': 'dot',
    'off_eq_5um': 'dash',
}

# File paths
DATA_FILE = 'Flash_JANAF_Master_ext_Tgrid_Gf.pkl'

# Industrial processing parameters
TUBE_LENGTH = 0.30  # m (30 cm)
TUBE_DIAMETER = 0.05  # m (5 cm)
PARTICLE_DENSITY = 4500  # kg/m³ (typical for metal oxides)
GAS_VELOCITY = 1.0  # m/s (typical for fluidized bed)
H2_EFFICIENCY = 0.95  # H₂ utilization efficiency (95%)

# Molecular weights (g/mol)
MOLECULAR_WEIGHTS = {
    'TiO2': 79.9,
    'ZrO2': 123.2,
    'Nb2O5': 265.8,
    'MoO3': 143.9,
    'WO3': 231.8,
    'CeO2': 172.1,
    'Cu2O': 143.1,
    'Ta2O5': 441.9,
    'V2O3': 149.9,
    'V2O5': 181.9,
    'NbO': 108.9,
    'MoO2': 127.9,
    'WO2': 215.8,
}

# Processing rates to analyze (kg/hr)
PROCESSING_RATES = [1, 10, 100, 1000]
