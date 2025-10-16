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

# Color palette by metal element with grouped families
COLOR_PALETTE = {
    # Group 4 metals (Ti, Zr, Hf) - Blue family
    'Ti': ['#0d47a1', '#1976d2', '#42a5f5', '#90caf9'],
    'Zr': ['#1a237e', '#303f9f', '#5c6bc0', '#9fa8da'],
    'Hf': ['#004d40', '#00695c', '#00897b', '#4db6ac'],
    
    # Group 5 metals (V, Nb, Ta) - Green family  
    'V': ['#1b5e20', '#388e3c', '#66bb6a', '#a5d6a7'],
    'Nb': ['#33691e', '#689f38', '#9ccc65', '#c5e1a5'],
    'Ta': ['#827717', '#afb42b', '#d4e157', '#e6ee9c'],
    
    # Group 6 metals (Cr, Mo, W) - Red/Purple family
    'Cr': ['#b71c1c', '#d32f2f', '#e57373', '#ef9a9a'],
    'Mo': ['#880e4f', '#c2185b', '#f06292', '#f48fb1'],
    'W': ['#4a148c', '#7b1fa2', '#ba68c8', '#e1bee7'],
    
    # Aluminum - Orange family
    'Al': ['#e65100', '#f57c00', '#ffa726', '#ffcc80'],
    
    # Iron group - Brown family
    'Fe': ['#3e2723', '#5d4037', '#8d6e63', '#bcaaa4'],
    'Ni': ['#4e342e', '#6d4c41', '#a1887f', '#d7ccc8'],
    'Co': ['#263238', '#455a64', '#78909c', '#b0bec5'],
    
    # Magnesium/Calcium - Cyan family
    'Mg': ['#006064', '#00838f', '#00acc1', '#4dd0e1'],
    'Ca': ['#01579b', '#0277bd', '#039be5', '#4fc3f7'],
    
    # Silicon - Grey family
    'Si': ['#424242', '#616161', '#9e9e9e', '#bdbdbd'],
    
    # Additional metals
    'Cu': ['#bf360c', '#d84315', '#ff5722', '#ff8a65'],
    'Zn': ['#37474f', '#455a64', '#607d8b', '#90a4ae'],
    'Pb': ['#3e2723', '#5d4037', '#8d6e63', '#bcaaa4'],
    'Sn': ['#795548', '#8d6e63', '#a1887f', '#d7ccc8'],
    'Li': ['#1a237e', '#303f9f', '#5c6bc0', '#9fa8da'],
    'Na': ['#bf360c', '#d84315', '#ff5722', '#ff8a65'],
    'K': ['#4a148c', '#7b1fa2', '#ba68c8', '#e1bee7'],
    
    # Default - Amber family
    'Other': ['#ff6f00', '#ff8f00', '#ffa726', '#ffb74d']
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

# Gas composition presets
GAS_COMPOSITION_PRESETS = {
    'N2_H2_25': {
        'name': 'N₂ 75% / H₂ 25%',
        'h2_fraction': 0.25,
        'carrier_gas': 'N₂',
        'carrier_fraction': 0.75,
        'description': 'Standard industrial mix'
    },
    'Ar_H2_5': {
        'name': 'Ar 95% / H₂ 5%',
        'h2_fraction': 0.05,
        'carrier_gas': 'Ar',
        'carrier_fraction': 0.95,
        'description': 'Low H₂ concentration for testing'
    }
}

# Default gas composition
DEFAULT_GAS_COMPOSITION = 'N2_H2_25'
