"""
Custom Compound Definition Module

This module handles user-defined materials with custom thermodynamic parameters
for the Off-Equilibrium Ellingham Diagram application.
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime

@dataclass
class CustomCompound:
    """Data structure for custom compounds with thermodynamic parameters."""
    
    # Basic identification
    name: str
    formula: str
    element: str
    category: str  # 'oxide', 'carbide', 'nitride', etc.
    
    # Thermodynamic parameters (temperature-dependent)
    # Format: [A, B, C, D] where ΔG° = A + B*T + C*T*ln(T) + D*T²
    # Units: kJ/mol O₂
    dg_coefficients: List[float]  # [A, B, C, D]
    temperature_range: Tuple[float, float]  # (T_min, T_max) in K
    
    # Physical properties
    molecular_weight: float  # g/mol
    density: float  # kg/m³
    
    # Plasma/Flash parameters
    w_ph_constant: float  # kJ/mol O₂ (phonon/plasma work constant)
    diffusion_enhancement: float  # Enhancement factor in flash conditions
    
    # Metadata
    source: str  # Literature source or "User-defined"
    confidence_level: str  # 'high', 'medium', 'low'
    notes: str
    created_date: str
    last_modified: str
    
    def __post_init__(self):
        """Validate the compound data after initialization."""
        if len(self.dg_coefficients) != 4:
            raise ValueError("DG coefficients must have exactly 4 values [A, B, C, D]")
        
        if self.temperature_range[0] >= self.temperature_range[1]:
            raise ValueError("Temperature range must have T_min < T_max")
        
        if self.molecular_weight <= 0:
            raise ValueError("Molecular weight must be positive")
        
        if self.density <= 0:
            raise ValueError("Density must be positive")
    
    def calculate_dg(self, T_K: np.ndarray) -> np.ndarray:
        """
        Calculate Gibbs free energy of formation using polynomial coefficients.
        
        Args:
            T_K: Temperature array in Kelvin
            
        Returns:
            ΔG°(T) in kJ/mol O₂
        """
        A, B, C, D = self.dg_coefficients
        
        # Standard thermodynamic polynomial: ΔG° = A + B*T + C*T*ln(T) + D*T²
        dg = A + B * T_K + C * T_K * np.log(T_K) + D * T_K**2
        
        return dg
    
    def validate_temperature_range(self, T_K: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Validate temperature range and return warnings.
        
        Args:
            T_K: Temperature array in Kelvin
            
        Returns:
            Tuple of (validated_T_K, warning_messages)
        """
        warnings = []
        T_min, T_max = self.temperature_range
        
        # Check if temperatures are within valid range
        out_of_range = (T_K < T_min) | (T_K > T_max)
        if np.any(out_of_range):
            warnings.append(f"Temperature(s) outside valid range [{T_min:.0f}K, {T_max:.0f}K]")
        
        return T_K, warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomCompound':
        """Create CustomCompound from dictionary."""
        return cls(**data)


class CustomCompoundManager:
    """Manages custom compounds database and operations."""
    
    def __init__(self, database_file: str = "custom_compounds.json"):
        self.database_file = database_file
        self.compounds: Dict[str, CustomCompound] = {}
        self.load_database()
    
    def load_database(self) -> None:
        """Load custom compounds from JSON file."""
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r') as f:
                    data = json.load(f)
                
                for name, compound_data in data.items():
                    self.compounds[name] = CustomCompound.from_dict(compound_data)
                
                print(f"Loaded {len(self.compounds)} custom compounds from {self.database_file}")
                
            except Exception as e:
                print(f"Error loading custom compounds database: {e}")
                self.compounds = {}
        else:
            print(f"Custom compounds database {self.database_file} not found. Starting with empty database.")
            self.compounds = {}
    
    def save_database(self) -> None:
        """Save custom compounds to JSON file."""
        try:
            data = {name: compound.to_dict() for name, compound in self.compounds.items()}
            
            with open(self.database_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved {len(self.compounds)} custom compounds to {self.database_file}")
            
        except Exception as e:
            print(f"Error saving custom compounds database: {e}")
    
    def add_compound(self, compound: CustomCompound) -> bool:
        """
        Add a new custom compound.
        
        Args:
            compound: CustomCompound instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate compound
            compound.validate_temperature_range(np.array([1000.0]))  # Test validation
            
            # Update timestamps
            compound.last_modified = datetime.now().isoformat()
            
            self.compounds[compound.name] = compound
            self.save_database()
            
            print(f"Added custom compound: {compound.name}")
            return True
            
        except Exception as e:
            print(f"Error adding custom compound {compound.name}: {e}")
            return False
    
    def update_compound(self, name: str, compound: CustomCompound) -> bool:
        """
        Update an existing custom compound.
        
        Args:
            name: Name of compound to update
            compound: Updated CustomCompound instance
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.compounds:
            print(f"Compound {name} not found for update")
            return False
        
        try:
            # Validate compound
            compound.validate_temperature_range(np.array([1000.0]))  # Test validation
            
            # Update timestamps
            compound.last_modified = datetime.now().isoformat()
            
            self.compounds[name] = compound
            self.save_database()
            
            print(f"Updated custom compound: {compound.name}")
            return True
            
        except Exception as e:
            print(f"Error updating custom compound {compound.name}: {e}")
            return False
    
    def delete_compound(self, name: str) -> bool:
        """
        Delete a custom compound.
        
        Args:
            name: Name of compound to delete
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.compounds:
            print(f"Compound {name} not found for deletion")
            return False
        
        try:
            del self.compounds[name]
            self.save_database()
            
            print(f"Deleted custom compound: {name}")
            return True
            
        except Exception as e:
            print(f"Error deleting custom compound {name}: {e}")
            return False
    
    def get_compound(self, name: str) -> Optional[CustomCompound]:
        """Get a custom compound by name."""
        return self.compounds.get(name)
    
    def get_all_compounds(self) -> Dict[str, CustomCompound]:
        """Get all custom compounds."""
        return self.compounds.copy()
    
    def get_compounds_by_category(self, category: str) -> Dict[str, CustomCompound]:
        """Get custom compounds by category."""
        return {name: compound for name, compound in self.compounds.items() 
                if compound.category == category}
    
    def search_compounds(self, query: str) -> Dict[str, CustomCompound]:
        """
        Search custom compounds by name, formula, or element.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            Dictionary of matching compounds
        """
        query_lower = query.lower()
        matches = {}
        
        for name, compound in self.compounds.items():
            if (query_lower in name.lower() or 
                query_lower in compound.formula.lower() or 
                query_lower in compound.element.lower()):
                matches[name] = compound
        
        return matches
    
    def validate_compound_data(self, compound_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate compound data before creating CustomCompound instance.
        
        Args:
            compound_data: Dictionary with compound parameters
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'formula', 'element', 'category', 'dg_coefficients', 
                          'temperature_range', 'molecular_weight', 'density', 'w_ph_constant']
        
        for field in required_fields:
            if field not in compound_data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate DG coefficients
        if len(compound_data['dg_coefficients']) != 4:
            errors.append("DG coefficients must have exactly 4 values [A, B, C, D]")
        
        # Validate temperature range
        temp_range = compound_data['temperature_range']
        if len(temp_range) != 2 or temp_range[0] >= temp_range[1]:
            errors.append("Temperature range must have T_min < T_max")
        
        # Validate numeric fields
        numeric_fields = ['molecular_weight', 'density', 'w_ph_constant']
        for field in numeric_fields:
            if not isinstance(compound_data[field], (int, float)) or compound_data[field] <= 0:
                errors.append(f"{field} must be a positive number")
        
        return len(errors) == 0, errors


# Predefined compound templates for common materials
COMPOUND_TEMPLATES = {
    'TiO2': {
        'name': 'Titanium Oxide, Rutile',
        'formula': 'TiO2',
        'element': 'Ti',
        'category': 'oxide',
        'dg_coefficients': [-944.7, 0.1815, 0, 0],  # Standard TiO2 parameters
        'temperature_range': [298, 2000],
        'molecular_weight': 79.9,
        'density': 4250,
        'w_ph_constant': 20.0,
        'diffusion_enhancement': 1.0,
        'source': 'JANAF Thermochemical Tables',
        'confidence_level': 'high',
        'notes': 'Standard rutile TiO2',
        'created_date': datetime.now().isoformat(),
        'last_modified': datetime.now().isoformat()
    },
    'Al2O3': {
        'name': 'Aluminum Oxide',
        'formula': 'Al2O3',
        'element': 'Al',
        'category': 'oxide',
        'dg_coefficients': [-1675.7, 0.3235, 0, 0],  # Standard Al2O3 parameters
        'temperature_range': [298, 2000],
        'molecular_weight': 101.96,
        'density': 3950,
        'w_ph_constant': 20.2,
        'diffusion_enhancement': 1.0,
        'source': 'JANAF Thermochemical Tables',
        'confidence_level': 'high',
        'notes': 'Standard alpha-Al2O3',
        'created_date': datetime.now().isoformat(),
        'last_modified': datetime.now().isoformat()
    }
}


def create_compound_from_template(template_name: str, custom_name: str = None) -> CustomCompound:
    """
    Create a CustomCompound from a predefined template.
    
    Args:
        template_name: Name of template (e.g., 'TiO2')
        custom_name: Custom name for the compound (optional)
        
    Returns:
        CustomCompound instance
    """
    if template_name not in COMPOUND_TEMPLATES:
        raise ValueError(f"Template {template_name} not found")
    
    template_data = COMPOUND_TEMPLATES[template_name].copy()
    
    if custom_name:
        template_data['name'] = custom_name
    
    return CustomCompound.from_dict(template_data)


def get_available_templates() -> List[str]:
    """Get list of available compound templates."""
    return list(COMPOUND_TEMPLATES.keys())
