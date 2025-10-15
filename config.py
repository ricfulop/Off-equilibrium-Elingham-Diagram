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
