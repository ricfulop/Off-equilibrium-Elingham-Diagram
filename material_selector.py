"""
Material Selector Component for Ellingham Diagram Application

Provides category-based material selection with tabs and searchable dropdown
to handle the large number of JANAF compounds efficiently.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Dict, List, Optional


def create_material_selector(categories_data: Dict[str, List], default_materials: List[str]) -> html.Div:
    """
    Create category-based material selection UI
    
    Args:
        categories_data: Dictionary with category names as keys and material lists as values
        default_materials: List of default material names to pre-select
    
    Returns:
        Dash HTML component with tabs and dropdown
    """
    
    # Create tabs for each category that has materials
    tabs = []
    for category, materials in categories_data.items():
        if materials and len(materials) > 0:
            tab = dbc.Tab(
                label=f"{category.capitalize()} ({len(materials)})",
                tab_id=category,
                tab_style={"margin-right": "5px"}
            )
            tabs.append(tab)
    
    return html.Div([
        html.H6("Material Selection", className="mb-2"),
        
        # Category tabs
        dbc.Tabs(
            id='material-category-tabs',
            children=tabs,
            active_tab='oxides' if 'oxides' in categories_data else list(categories_data.keys())[0],
            className="mb-3"
        ),
        
        # Material dropdown
        html.Div([
            dcc.Dropdown(
                id='material-dropdown',
                multi=True,
                placeholder="Search and select materials...",
                value=default_materials,
                searchable=True,
                clearable=True,
                optionHeight=50,
                style={'font-size': '14px'}
            )
        ], style={'margin-top': '10px'}),
        
        # Info text
        html.Small(
            "Use tabs to filter by compound type, then search and select materials",
            className="text-muted mt-2 d-block"
        )
    ], className="control-section")


def get_category_display_order() -> List[str]:
    """
    Get the preferred display order for categories
    
    Returns:
        List of category names in preferred order
    """
    return [
        'oxides',      # Most common for Ellingham diagrams
        'carbides',    # Important for metallurgy
        'nitrides',    # Important for ceramics
        'halides',     # Important for chemical processing
        'hydrides',    # Important for hydrogen storage
        'sulfides',    # Important for ore processing
        'phosphides',  # Less common but useful
        'pure_elements', # Reference materials
        'other'        # Miscellaneous compounds
    ]


def format_material_label(material_name: str, formula: str = None) -> str:
    """
    Format material name for display in dropdown
    
    Args:
        material_name: Name of the material
        formula: Optional formula for additional context
    
    Returns:
        Formatted label string
    """
    if formula:
        return f"{material_name} ({formula})"
    return material_name


def create_material_options(materials: List[Dict], max_display: int = 1000) -> List[Dict]:
    """
    Create dropdown options from material data
    
    Args:
        materials: List of material dictionaries with 'name' and 'formula' keys
        max_display: Maximum number of materials to display (for performance)
    
    Returns:
        List of dropdown option dictionaries
    """
    options = []
    
    # Sort materials alphabetically by name
    sorted_materials = sorted(materials, key=lambda x: x.get('name', ''))
    
    # Limit number of materials for performance
    if len(sorted_materials) > max_display:
        sorted_materials = sorted_materials[:max_display]
    
    for material in sorted_materials:
        name = material.get('name', 'Unknown')
        formula = material.get('formula', '')
        
        options.append({
            "label": format_material_label(name, formula),
            "value": name,
            "search": f"{name} {formula}".lower()  # For better search functionality
        })
    
    return options


def get_category_summary(categories_data: Dict[str, List]) -> str:
    """
    Get a summary string of available categories and counts
    
    Args:
        categories_data: Dictionary with category names and material lists
    
    Returns:
        Summary string
    """
    summary_parts = []
    for category in get_category_display_order():
        if category in categories_data and categories_data[category]:
            count = len(categories_data[category])
            summary_parts.append(f"{category.capitalize()}: {count}")
    
    return " | ".join(summary_parts)

