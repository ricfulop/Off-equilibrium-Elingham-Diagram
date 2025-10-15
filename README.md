# Off-Equilibrium Ellingham Diagram Interactive Dash App

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ricfulop/Off-equilibrium-Elingham-Diagram)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

An interactive web application for visualizing equilibrium and off-equilibrium Ellingham diagrams for metal oxide reduction in Plasma Flash Reactors (PFR). This tool enables researchers and engineers to analyze the thermodynamic feasibility of electric field-enhanced metal oxide reduction processes.

**Author**: Ric Fulop  
**Affiliation**: MIT Center for Bits and Atoms  
**Version**: 1.0.0

## Overview

This application implements the novel **off-equilibrium thermodynamics model** for plasma flash reduction, where strong electric fields shift the Gibbs free energy to make oxide reductions spontaneous at lower temperatures. The app visualizes both traditional equilibrium Ellingham diagrams and the enhanced off-equilibrium curves as functions of electric field strength and particle size.

### Key Features

- **Interactive Material Selection**: Choose from available metal oxides (TiO₂, ZrO₂, Nb₂O₅, Ta₂O₅, MoO₃, WO₃, etc.)
- **Electric Field Control**: Adjust field strength from 0.1 to 5.0 MV/m
- **Particle Size Effects**: Compare different particle radii (1 µm, 5 µm, custom)
- **Temperature Range**: Visualize thermodynamic behavior from 300-2400 K
- **Dual Visualization**: Overlay equilibrium and off-equilibrium curves
- **Gas Ratio Scales**: Display H₂/H₂O and CO/CO₂ ratios for reduction analysis
- **Real-time Analysis**: Instant thermodynamic feasibility assessment
- **Data Export**: Export calculated data for further analysis

## Scientific Background

### Off-Equilibrium Thermodynamics Model

The application implements the following thermodynamic model:

```
ΔG_eff(T,E,r) = ΔG°(T) - n·F·E·r - W_ph
```

Where:
- **ΔG°(T)**: Standard Gibbs free energy [kJ/mol O₂] from JANAF data
- **n**: Electrons transferred per mol O₂ (n=4 for MO₂)
- **F**: Faraday constant = 96,485 C/mol
- **E**: Electric field [V/m]
- **r**: Particle radius [m]
- **W_ph**: Phonon/plasma work [kJ/mol O₂], material-specific constant

### Plasma Flash Reactor (PFR) Concept

The PFR uses:
- **Electric field enhancement**: Strong fields (2 MV/m) reduce activation barriers
- **Plasma state**: Flash conditions create electron-rich plasma
- **Touch-free processing**: Induction coil + YSZ plasma elements
- **Scalable design**: Current-independent scaling for large-scale production

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure data file is present**:
   - The `data/Flash_JANAF_Master_ext_Tgrid_Gf.pkl` file should be in the data directory

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   - Open your browser and navigate to `http://localhost:8050`

## Usage Guide

### Basic Operation

1. **Select Materials**: Use the dropdown to choose one or more metal oxides for comparison
2. **Set Electric Field**: Adjust the slider to your desired field strength (MV/m)
3. **Choose Particle Size**: Select from presets (1 µm, 5 µm) or enter a custom value
4. **Adjust Temperature Range**: Use the range slider to focus on your temperature of interest
5. **Toggle Display Options**: Show/hide equilibrium lines and gas ratio scales

### Interpreting Results

#### Equilibrium Curves (Solid Lines)
- Show traditional Ellingham behavior
- Lower curves = more stable oxides (harder to reduce)
- Zero line (ΔG=0) indicates thermodynamic equilibrium

#### Off-Equilibrium Curves (Dashed Lines)
- Show enhanced reduction due to electric field
- Below zero line = spontaneous reduction
- Steeper slopes indicate stronger field effects

#### Gas Ratio Scales
- **Top axis**: log(H₂/H₂O) for hydrogen reduction
- **Right axis**: log(CO/CO₂) for carbon monoxide reduction
- **Bottom axis**: log₁₀(pO₂) oxygen partial pressure

#### Feasibility Analysis
- **Highly Favorable**: ΔG_eff < -50 kJ/mol O₂
- **Favorable**: ΔG_eff < 0 kJ/mol O₂
- **Marginal**: 0 < ΔG_eff < 50 kJ/mol O₂
- **Unfavorable**: ΔG_eff > 50 kJ/mol O₂

### Example Analysis: TiO₂ Reduction

For TiO₂ at 1000°C with E=2 MV/m and r=5 µm:
- **Equilibrium ΔG°**: ~-800 kJ/mol O₂ (unfavorable)
- **Electric contribution**: ~-3860 kJ/mol O₂ (strong enhancement)
- **Effective ΔG**: ~-4680 kJ/mol O₂ (highly favorable)

This demonstrates how the electric field makes TiO₂ reduction highly spontaneous.

## Technical Details

### Data Sources

- **JANAF Thermochemical Tables**: Standard thermodynamic data
- **Material-specific constants**: W_ph values for different oxides
- **Temperature range**: 300-2400 K with polynomial interpolation

### Available Materials

Currently supported oxides:
- TiO₂ (Titanium Dioxide)
- ZrO₂ (Zirconium Dioxide) 
- Nb₂O₅ (Niobium Pentoxide)
- Ta₂O₅ (Tantalum Pentoxide)
- MoO₃ (Molybdenum Trioxide)
- WO₃ (Tungsten Trioxide)
- CO₂, CO (Reference gases)

### Performance

- **Real-time calculations**: Polynomial fits enable fast interpolation
- **Responsive interface**: Optimized for smooth user interaction
- **Memory efficient**: Cached calculations for common parameters

## File Structure

```
/
├── app.py                 # Main Dash application
├── data_loader.py         # JANAF data loading & preprocessing
├── thermo_calcs.py        # Thermodynamic calculations
├── utils.py               # Helper functions
├── config.py              # Constants and configuration
├── assets/
│   └── styles.css         # Custom CSS styling
├── data/
│   └── Flash_JANAF_Master_ext_Tgrid_Gf.pkl  # Input data
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Future Enhancements

### Planned Features (v2+)
- **Extended JANAF database**: Additional elements (Mg, Al, Hf, Rare Earths)
- **Custom alloy modeling**: User-defined compositions
- **Reactor gradient visualization**: Field/size evolution along reactor length
- **Kinetics overlay**: Reduction time contours
- **Publication-quality export**: SVG/PDF figure generation
- **Batch processing**: Multiple condition analysis

### Research Applications

This tool supports research in:
- **Plasma flash sintering**: Ceramic processing
- **Metal oxide reduction**: Green metallurgy
- **Process optimization**: Field/size parameter tuning
- **Educational use**: Thermodynamics visualization

## Contributing

Contributions are welcome! Areas for improvement:
- Additional thermodynamic data sources
- Enhanced visualization features
- Performance optimizations
- Documentation improvements

## References

1. Raj, R. & Dong, Y. (2022). Flash sintering of ceramics. *Journal of the American Ceramic Society*.
2. Bamidele, A. et al. (2024). Flash sintering of nickel. *Journal of the American Ceramic Society*.
3. Mishra, S. K. (2019). On the role of Debye temperature in the onset of flash in three oxides.
4. JANAF Thermochemical Tables, 4th Edition (1998).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions, suggestions, or collaboration opportunities, please contact the development team.

---

**Note**: This application is designed for research and educational purposes. Always verify thermodynamic calculations with experimental data and consult appropriate references for industrial applications.