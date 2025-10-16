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
    Create category-based material selection UI with metal grouping option
    
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
        
        # Grouping mode selector
        html.Div([
            dbc.RadioItems(
                id='material-grouping-mode',
                options=[
                    {"label": "By Category", "value": "category"},
                    {"label": "By Metal", "value": "metal"}
                ],
                value="category",
                inline=True,
                className="mb-2"
            )
        ]),
        
        # Category tabs (shown when grouping by category)
        html.Div([
            dbc.Tabs(
                id='material-category-tabs',
                children=tabs,
                active_tab='oxides' if 'oxides' in categories_data else list(categories_data.keys())[0],
                className="mb-3"
            )
        ], id='category-tabs-container'),
        
        # Metal grouping selector (shown when grouping by metal)
        html.Div([
            dcc.Dropdown(
                id='metal-group-dropdown',
                placeholder="Select metal to view compounds...",
                searchable=True,
                clearable=True,
                style={'font-size': '14px', 'margin-bottom': '10px'}
            )
        ], id='metal-group-container', style={'display': 'none'}),
        
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
            "Use tabs to filter by compound type, or group by metal to see all compounds of a specific metal",
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


def get_available_metals(categories_data: Dict[str, List]) -> List[str]:
    """
    Extract all unique metals from the materials database
    
    Args:
        categories_data: Dictionary with category names and material lists
    
    Returns:
        List of unique metal names
    """
    metals = set()
    
    for category, materials in categories_data.items():
        for material in materials:
            # Handle both string and dict material formats
            if isinstance(material, dict):
                material_name = material.get('name', '')
            else:
                material_name = str(material)
            
            # Extract metal from material name or formula
            metal = extract_metal_from_material(material_name)
            if metal:
                metals.add(metal)
    
    # Sort metals alphabetically
    return sorted(list(metals))


def extract_metal_from_material(material_name: str) -> Optional[str]:
    """
    Extract the primary metal element from a material name
    
    Args:
        material_name: Name of the material (e.g., "Titanium Oxide, Rutile")
    
    Returns:
        Metal name (e.g., "Titanium") or None if not found
    """
    # Common metal names and their variations
    metal_mappings = {
        'titanium': ['titanium', 'ti'],
        'aluminum': ['aluminum', 'aluminium', 'al'],
        'iron': ['iron', 'fe'],
        'copper': ['copper', 'cu'],
        'nickel': ['nickel', 'ni'],
        'chromium': ['chromium', 'cr'],
        'manganese': ['manganese', 'mn'],
        'vanadium': ['vanadium', 'v'],
        'molybdenum': ['molybdenum', 'mo'],
        'tungsten': ['tungsten', 'w'],
        'zirconium': ['zirconium', 'zr'],
        'hafnium': ['hafnium', 'hf'],
        'tantalum': ['tantalum', 'ta'],
        'niobium': ['niobium', 'nb'],
        'magnesium': ['magnesium', 'mg'],
        'calcium': ['calcium', 'ca'],
        'strontium': ['strontium', 'sr'],
        'barium': ['barium', 'ba'],
        'silicon': ['silicon', 'si'],
        'germanium': ['germanium', 'ge'],
        'tin': ['tin', 'sn'],
        'lead': ['lead', 'pb'],
        'zinc': ['zinc', 'zn'],
        'cadmium': ['cadmium', 'cd'],
        'mercury': ['mercury', 'hg'],
        'cobalt': ['cobalt', 'co'],
        'rhodium': ['rhodium', 'rh'],
        'palladium': ['palladium', 'pd'],
        'platinum': ['platinum', 'pt'],
        'gold': ['gold', 'au'],
        'silver': ['silver', 'ag'],
        'ruthenium': ['ruthenium', 'ru'],
        'osmium': ['osmium', 'os'],
        'iridium': ['iridium', 'ir'],
        'uranium': ['uranium', 'u'],
        'thorium': ['thorium', 'th'],
        'cerium': ['cerium', 'ce'],
        'lanthanum': ['lanthanum', 'la'],
        'yttrium': ['yttrium', 'y'],
        'scandium': ['scandium', 'sc'],
        'lutetium': ['lutetium', 'lu'],
        'ytterbium': ['ytterbium', 'yb'],
        'thulium': ['thulium', 'tm'],
        'erbium': ['erbium', 'er'],
        'holmium': ['holmium', 'ho'],
        'dysprosium': ['dysprosium', 'dy'],
        'terbium': ['terbium', 'tb'],
        'gadolinium': ['gadolinium', 'gd'],
        'europium': ['europium', 'eu'],
        'samarium': ['samarium', 'sm'],
        'promethium': ['promethium', 'pm'],
        'neodymium': ['neodymium', 'nd'],
        'praseodymium': ['praseodymium', 'pr'],
        'lithium': ['lithium', 'li'],
        'sodium': ['sodium', 'na'],
        'potassium': ['potassium', 'k'],
        'rubidium': ['rubidium', 'rb'],
        'cesium': ['cesium', 'cs']
    }
    
    material_lower = material_name.lower()
    
    # Check for exact matches first (longest matches first)
    sorted_metals = sorted(metal_mappings.items(), key=lambda x: len(x[0]), reverse=True)
    
    for metal, variations in sorted_metals:
        for variation in variations:
            if variation in material_lower:
                return metal.capitalize()
    
    return None


def get_materials_by_metal(categories_data: Dict[str, List], metal: str) -> List[str]:
    """
    Get all materials containing a specific metal
    
    Args:
        categories_data: Dictionary with category names and material lists
        metal: Name of the metal to filter by
    
    Returns:
        List of material names containing the specified metal
    """
    materials = []
    metal_lower = metal.lower()
    
    for category, material_list in categories_data.items():
        for material in material_list:
            # Handle both string and dict material formats
            if isinstance(material, dict):
                material_name = material.get('name', '')
            else:
                material_name = str(material)
            
            material_metal = extract_metal_from_material(material_name)
            if material_metal and material_metal.lower() == metal_lower:
                materials.append(material_name)
    
    return sorted(materials)


def create_metal_group_options(categories_data: Dict[str, List]) -> List[Dict]:
    """
    Create dropdown options for metal grouping
    
    Args:
        categories_data: Dictionary with category names and material lists
    
    Returns:
        List of dropdown option dictionaries for metals
    """
    metals = get_available_metals(categories_data)
    options = []
    
    for metal in metals:
        # Count materials for this metal
        metal_materials = get_materials_by_metal(categories_data, metal)
        count = len(metal_materials)
        
        options.append({
            "label": f"{metal} ({count} compounds)",
            "value": metal,
            "search": metal.lower()
        })
    
    return options

