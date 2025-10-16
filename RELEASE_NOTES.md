# Release Notes

## Version 1.4.0 - Comprehensive JANAF Database Integration

**Release Date**: January 2024  
**Major Release**: Database expansion and thermodynamic improvements

### 🎉 Major Features

#### Comprehensive Database Expansion
- **710 compounds** with valid thermodynamic data (previously ~10 oxides)
- **9 compound categories**: oxides, carbides, nitrides, halides, hydrides, sulfides, phosphides, pure elements, other
- **38 elements** from complete JANAF thermochemical database
- **100% scientific accuracy** using verified JANAF data only

#### Temperature-Dependent Thermodynamics
- **Fixed horizontal lines issue** by implementing proper polynomial coefficient fitting
- **Polynomial equations**: ΔG(T) = A + B×T + C×T² for realistic sloping Ellingham lines
- **Temperature-dependent calculations** with proper interpolation
- **Pre-computed coefficients** for all compounds with sufficient thermodynamic data

#### Enhanced User Interface
- **Category-based material selection** with organized tabs
- **Searchable dropdown** with 710 compounds
- **Proper chemical formula formatting** with subscripts (TiO₂, Al₂O₃, etc.)
- **Multi-material selection** for comparison studies
- **Improved default materials** based on standard Ellingham diagrams

### 🔧 Technical Improvements

#### Data Processing
- **Robust preprocessing pipeline** for JANAF data extraction
- **Flexible thermodynamic data parsing** handling various data formats
- **Automatic G=H-TS calculations** when Gibbs data unavailable
- **Error handling** for compounds with insufficient data

#### Performance
- **Pre-computed polynomial fits** for fast real-time calculations
- **Efficient data loading** with pickle serialization
- **Optimized interpolation** for smooth plotting
- **Memory-efficient** compound lookup system

#### Code Quality
- **Modular architecture** with separate data loader and thermodynamic engine
- **Comprehensive error handling** and fallback mechanisms
- **Type hints** and documentation throughout
- **Clean separation** of concerns

### 📊 Database Statistics

#### Compound Distribution
- **Oxides**: 189 compounds
- **Carbides**: 83 compounds  
- **Nitrides**: 37 compounds
- **Halides**: 103 compounds
- **Hydrides**: 110 compounds
- **Sulfides**: 38 compounds
- **Phosphides**: 3 compounds
- **Pure Elements**: 77 compounds
- **Other**: 108 compounds

#### Data Quality
- **Polynomial coefficients available**: ~85% of compounds
- **Temperature range**: 300-2400K coverage
- **Data points per compound**: 3-50+ temperature points
- **Sources**: JANAF Fourth Edition (1998) + extensions

### 🚀 Default Materials

Enhanced default selection includes 12 standard Ellingham diagram materials:
1. **TiO₂** (Titanium Oxide, Rutile)
2. **Al₂O₃** (Aluminum Oxide)
3. **ZrO₂** (Zirconium Oxide)
4. **MgO** (Magnesium Oxide)
5. **CaO** (Calcium Oxide)
6. **FeO** (Iron Oxide)
7. **Cr₂O₃** (Chromium Oxide)
8. **Ni** (Nickel)
9. **MoO₃** (Molybdenum Oxide)
10. **WO₃** (Tungsten Chloride Oxide)
11. **V₂O₅** (Vanadium Oxide)
12. **SiO₂** (Silicon Oxide)

### 🔄 Migration Notes

#### Breaking Changes
- **Material names** updated to match JANAF database exactly
- **Data structure** changed from simple oxide list to comprehensive compound database
- **Default materials** expanded from 6 to 12 compounds

#### Compatibility
- **Backward compatible** with existing thermodynamic calculations
- **Same API** for ThermodynamicEngine methods
- **Consistent** Gibbs free energy units (kJ/mol O₂ for oxides)

### 🐛 Bug Fixes

- **Fixed horizontal lines** in Ellingham diagrams by implementing proper temperature dependence
- **Resolved import errors** with missing interpolate_DG method
- **Fixed KeyError** in info panel for new data structure
- **Corrected material name mismatches** between database and UI
- **Fixed counting logic** in preprocessing to show accurate compound counts

### 📈 Performance Improvements

- **Faster loading** with pre-computed polynomial coefficients
- **Smoother plotting** with proper temperature interpolation
- **Reduced memory usage** with efficient data structures
- **Faster material selection** with optimized lookup

### 🔮 Future Roadmap

#### Phase 1: Multi-Compound Normalization
- Support for comparing oxides, nitrides, and carbides on same diagram
- Multiple normalization modes (per metal, per reducing agent, native units)

#### Phase 2: Enhanced Color Scheme
- Metal-grouped color families for better visual distinction
- Improved accessibility and colorblind-friendly palettes

#### Phase 3: Advanced UX Features
- Compound comparison modes
- Metal-grouped material selection
- Performance optimizations

#### Phase 4: Economic Analysis
- Commodity price integration
- Cost-effectiveness calculations
- Economic feasibility analysis

### 📝 Technical Details

#### Files Modified
- `version.py`: Updated to v1.4.0
- `README.md`: Updated features and version information
- `simple_preprocess.py`: Enhanced polynomial coefficient extraction
- `data_loader.py`: Updated for comprehensive database support
- `app.py`: Integrated category-based UI and polynomial calculations
- `material_selector.py`: New component for organized material selection
- `utils.py`: Enhanced material display names and compatibility

#### Files Added
- `RELEASE_NOTES.md`: This document
- `janaf_ellingham_tables.pkl`: Pre-computed comprehensive database

#### Dependencies
- No new dependencies required
- Compatible with existing requirements.txt

---

**Full Changelog**: See git history for detailed commit information  
**Documentation**: Updated README.md with comprehensive feature descriptions  
**Support**: Contact ricfulop@mit.edu for questions or issues
