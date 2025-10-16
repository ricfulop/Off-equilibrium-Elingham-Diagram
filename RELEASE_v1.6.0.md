# Release v1.6.0 - Gas Composition Selection

**Release Date:** December 2024  
**Version:** 1.6.0  
**Author:** Ric Fulop, MIT Center for Bits and Atoms

## 🎉 New Features

### Gas Composition Selection
- **N₂ 75% / H₂ 25%**: Standard industrial gas mixture (default)
- **Ar 95% / H₂ 5%**: Low H₂ concentration for testing and validation
- Real-time switching between gas compositions
- Dynamic feasibility analysis based on selected gas composition

### Enhanced Industrial Processing Analysis
- Carrier gas flow calculations (N₂ or Ar) update automatically
- Processing rate analysis shows correct gas flows for selected composition
- Feasibility indicators adjust to actual H₂ availability
- Clear labeling of active gas composition in analysis panel

## 🔧 Technical Improvements

### Fixed Gas Calculation Bug
- Replaced placeholder values (0.0) with proper thermodynamic calculations
- H₂ partial pressure, H₂/H₂O ratio, and oxygen potential now show real calculated values
- Gas calculations use proper thermodynamic engine methods

### Updated Callbacks
- Added gas composition input to main plot callback
- Updated info panel callback to handle gas composition parameter
- All calculations update automatically when gas composition changes

### Configuration Updates
- Added `GAS_COMPOSITION_PRESETS` to config.py
- Extensible design for adding more gas compositions in future
- Default gas composition set to N₂ 75% / H₂ 25%

## 🎯 User Experience Improvements

### Control Panel Enhancements
- New gas composition radio buttons in control panel
- Clear labeling and helpful descriptions
- Intuitive placement between particle radius and temperature controls

### Analysis Panel Updates
- Shows active gas composition at top of analysis
- Feasibility messages update with actual H₂ percentages
- Carrier gas flow rates display correctly (N₂ or Ar)
- Processing calculations adjust to selected gas composition

## 🔬 Scientific Impact

### Practical Applications
- **Testing**: Ar 95%/H₂ 5% allows testing with very low H₂ concentrations
- **Industrial Design**: N₂ 75%/H₂ 25% represents real-world gas compositions
- **Process Optimization**: Easy comparison of different gas compositions
- **Feasibility Analysis**: Accurate assessment of reduction requirements

### Research Benefits
- More realistic process modeling
- Better understanding of gas composition effects
- Easier validation of theoretical calculations
- Improved industrial process design

## 📊 What's New in the Interface

1. **Gas Composition Selector**: Radio buttons to choose between gas mixtures
2. **Dynamic Analysis**: All calculations update when gas composition changes
3. **Enhanced Display**: Shows which gas composition is active
4. **Realistic Calculations**: Proper thermodynamic calculations instead of placeholders

## 🚀 Getting Started

1. **Select Materials**: Choose oxides or other compounds to analyze
2. **Set Parameters**: Adjust electric field, particle radius, temperature range
3. **Choose Gas Composition**: Select N₂ 75%/H₂ 25% or Ar 95%/H₂ 5%
4. **Analyze Results**: View feasibility analysis and processing calculations
5. **Compare**: Switch gas compositions to see the difference

## 🔧 Technical Details

### Files Modified
- `app.py`: Added gas composition UI and callbacks
- `config.py`: Added gas composition presets
- `utils.py`: Updated analysis functions to handle gas composition
- `version.py`: Updated to version 1.6.0

### Dependencies
- No new dependencies required
- Compatible with existing requirements.txt

## 🎯 Future Enhancements

- Additional gas compositions (CO/CO₂, H₂/He, etc.)
- Custom gas composition input
- Gas cost analysis
- Environmental impact calculations

---

**For questions or support, contact:** ricfulop@mit.edu  
**Repository:** Off-equilibrium-Elingham-Diagram  
**License:** MIT
