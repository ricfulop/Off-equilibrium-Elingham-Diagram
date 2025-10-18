"""
Off-Equilibrium Ellingham Diagram Interactive Dash App

Main application for visualizing equilibrium and off-equilibrium Ellingham diagrams
for metal oxide reduction in Plasma Flash Reactors (PFR).
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from typing import List, Dict, Tuple

# Import our modules
from data_loader import load_janaf_data
from thermo_calcs import ThermodynamicEngine
from material_selector import create_material_selector, create_material_options
from utils import (
    kelvin_to_celsius, celsius_to_kelvin, mv_per_m_to_v_per_m, um_to_m,
    get_color_for_oxide, get_color_for_material, get_line_style, create_legend_label,
    validate_inputs, create_temperature_ticks, create_gas_ratio_ticks,
    create_info_text, get_default_materials, get_material_display_name
)
from config import DEFAULT_FIELD_PRESETS, DEFAULT_RADIUS_PRESETS, DEFAULT_TEMP_RANGE, TEMP_MARKERS, GAS_RATIO_TEMPS

# Import custom compound modules
from custom_compounds import CustomCompound, CustomCompoundManager, create_compound_from_template
from custom_compound_ui import (
    create_custom_compound_modal, create_custom_compound_management_panel,
    create_custom_compound_list_item, create_custom_compound_validation_alert,
    create_custom_compound_export_data, parse_custom_compound_import_data
)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Off-Equilibrium Ellingham Diagrams"

# Authentication setup
import os
from dash_auth import BasicAuth

# Environment-based credentials for security
USERNAME_PASSWORD_PAIRS = {
    os.getenv('ADMIN_USER', 'admin'): os.getenv('ADMIN_PASS', 'ellingham2025'),
    os.getenv('RESEARCHER_USER', 'researcher'): os.getenv('RESEARCHER_PASS', 'research2025'),
    os.getenv('STUDENT_USER', 'student'): os.getenv('STUDENT_PASS', 'student2025')
}

# Apply authentication
auth = BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# Load data
print("Loading JANAF thermodynamic data...")
data_loader = load_janaf_data()
thermo_engine = ThermodynamicEngine(data_loader)

# Initialize custom compound manager
custom_compound_manager = CustomCompoundManager()

# Get categories data for material selector
categories_data = data_loader.get_categories_data()
print(f"Loaded {data_loader.raw_data['metadata']['total_compounds']} compounds across {len(categories_data)} categories")

# Get default materials
default_materials = get_default_materials()
print(f"Default materials: {default_materials}")

# App layout
app.layout = dbc.Container([
    # Header
    html.Div([
        html.Div([
            html.H1("Off-Equilibrium Ellingham Diagrams", className="app-title"),
            html.P("Plasma Flash Reactor (PFR) Thermodynamic Analysis", className="app-subtitle"),
            html.P("Interactive visualization of electric field-enhanced metal oxide reduction", className="app-subtitle"),
            html.Div([
                html.P("Ric Fulop", className="mit-attribution"),
                html.P("Center for Bits and Atoms", className="mit-affiliation")
            ], className="author-info")
        ], className="header-left"),
        html.Div([
            html.Img(
                src="assets/mit_lockup_std-three-line_rgb_silver-gray.svg",
                className="mit-logo",
                style={"height": "60px", "width": "auto", "margin-bottom": "10px"},
                alt="MIT Logo"
            )
        ], className="header-right")
    ], className="app-header"),
    
    dbc.Row([
        # Control Panel
        dbc.Col([
            html.Div([
                html.H5("Control Panel", className="mb-3"),
                
        # Material Selection with Category Tabs
        create_material_selector(
            categories_data=categories_data,
            default_materials=default_materials
        ),
        
        # Comparison Mode Controls
        html.Div([
            html.H6("Comparison Mode", className="mb-2"),
            dbc.RadioItems(
                id='comparison-mode',
                options=[
                    {"label": "Individual Compounds", "value": "individual"},
                    {"label": "Compare by Metal", "value": "by_metal"},
                    {"label": "Compare by Type", "value": "by_type"}
                ],
                value="individual",
                inline=True,
                className="mb-3"
            )
        ], className="control-section"),
                
                # Electric Field (Updated with scientific validation)
                html.Div([
                    html.H6("Electric Field"),
                    dcc.Slider(
                        id='field-slider',
                        min=0.1,
                        max=2.5,
                        step=0.1,
                        value=1.0,
                        marks={0.1: '0.1', 0.5: '0.5', 1.0: '1.0', 1.5: '1.5', 2.0: '2.0', 2.5: '2.5'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Small("MV/m (Validated range: 0.1-2.5 MV/m)", className="text-muted"),
                    html.Br(),
                    html.Small("🟢 High confidence | 🟡 Medium confidence | 🔴 Low confidence", className="text-muted")
                ], className="control-section"),
                
                # Particle Radius
                html.Div([
                    html.H6("Particle Radius"),
                    dbc.RadioItems(
                        id='radius-radio',
                        options=[
                            {"label": "1 µm", "value": 1.0},
                            {"label": "5 µm", "value": 5.0},
                            {"label": "Custom", "value": "custom"}
                        ],
                        value=5.0,
                        inline=True
                    ),
                    dbc.Input(
                        id='radius-custom',
                        type='number',
                        min=0.1,
                        max=100.0,
                        step=0.1,
                        value=5.0,
                        style={'display': 'none'}
                    )
                ], className="control-section"),
                
                # Gas Composition
                html.Div([
                    html.H6("Gas Composition"),
                    dbc.RadioItems(
                        id='gas-composition-radio',
                        options=[
                            {"label": "N₂ 75% / H₂ 25%", "value": "N2_H2_25"},
                            {"label": "Ar 95% / H₂ 5%", "value": "Ar_H2_5"}
                        ],
                        value="N2_H2_25",
                        inline=True
                    ),
                    html.Small("Select gas composition for feasibility analysis", className="text-muted")
                ], className="control-section"),
                
                # Entry Temperature
                html.Div([
                    html.H6("Entry Temperature"),
                    dcc.Slider(
                        id='entry-temp-slider',
                        min=300,
                        max=800,
                        step=25,
                        value=300,
                        marks={300: '27°C', 400: '127°C', 500: '227°C', 600: '327°C', 700: '427°C', 800: '527°C'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Small("Material temperature entering the reactor tube", className="text-muted")
                ], className="control-section"),
                
                # Temperature Range
                html.Div([
                    html.H6("Temperature Range"),
                    dcc.RangeSlider(
                        id='temp-range-slider',
                        min=300,
                        max=2400,
                        step=50,
                        value=DEFAULT_TEMP_RANGE,
                        marks={i: f"{i-273:.0f}°C" for i in range(500, 2500, 400)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], className="control-section"),
                
                # Display Options
                html.Div([
                    html.H6("Display Options"),
                    dbc.Checklist(
                        id='display-options',
                        options=[
                            {"label": "Show Equilibrium Lines", "value": "equilibrium"},
                            {"label": "Show Off-Equilibrium Lines", "value": "off_equilibrium"}
                        ],
                        value=["equilibrium", "off_equilibrium"],
                        inline=False
                    )
                ], className="control-section"),
                
                # Nomographic Gas Scales (collapsible)
                html.Div([
                    dbc.Button(
                        "Nomographic Gas Scales",
                        id="collapse-gas-scales-button",
                        color="light",
                        size="sm",
                        className="mb-2",
                        n_clicks=0
                    ),
                    dbc.Collapse([
                        dbc.Checklist(
                            id='gas-scale-options',
                            options=[
                                {"label": "H₂/H₂O", "value": "H2_H2O"},
                                {"label": "CO/CO₂", "value": "CO_CO2"},
                                {"label": "H₂/H₂S", "value": "H2_H2S"},
                                {"label": "Cl₂/HCl", "value": "Cl2_HCl"},
                                {"label": "H₂/HCl", "value": "H2_HCl"},
                                {"label": "CO/HCl", "value": "CO_HCl"},
                                {"label": "log₁₀(pO₂)", "value": "pO2"},
                                {"label": "H₂/O₂", "value": "H2_O2"},
                                {"label": "CO/O₂", "value": "CO_O2"},
                                {"label": "CH₄/H₂", "value": "CH4_H2"}
                            ],
                            value=["H2_H2O", "CO_CO2", "pO2"],
                            inline=False,
                            className="gas-scale-checklist"
                        )
                    ], id="collapse-gas-scales", is_open=False)
                ], className="control-section"),
                
                # Export Button
                html.Div([
                    dbc.Button("Export Data", id="export-btn", color="secondary", size="sm"),
                    dcc.Download(id="download-data")
                ], className="control-section"),
                
                # Validation Status Panel
                html.Div([
                    html.H6("Validation Status"),
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="validation-status", children=[
                                html.P("🟢 High Confidence", className="text-success mb-1"),
                                html.Small("Scientific parameters validated", className="text-muted")
                            ])
                        ])
                    ], color="light", outline=True),
                    html.Br(),
                    dbc.Button("View Sources", id="sources-btn", color="info", size="sm", outline=True),
                    dbc.Modal([
                        dbc.ModalHeader("Scientific Sources & Citations"),
                        dbc.ModalBody(id="sources-content"),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close-sources", className="ms-auto", n_clicks=0)
                        ),
                    ], id="sources-modal", is_open=False)
                ], className="control-section")
                
            ], className="control-panel")
        ], width=3),
        
        # Main Plot Area
        dbc.Col([
            html.Div([
                dcc.Graph(
                    id='ellingham-plot',
                    style={'height': '600px'},
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                    }
                ),
                # Export buttons
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button(
                            "Export as SVG",
                            id="export-svg-btn",
                            color="primary",
                            size="sm",
                            className="me-1"
                        ),
                        dbc.Button(
                            "Export as PDF",
                            id="export-pdf-btn",
                            color="secondary",
                            size="sm"
                        )
                    ], className="mt-2")
                ], className="d-flex justify-content-end"),
                # Download components
                dcc.Download(id="download-svg"),
                dcc.Download(id="download-pdf")
            ], className="plot-container")
        ], width=9)
    ]),
    
    # Info Panel
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Thermodynamic Analysis"),
                    html.Div(id="info-panel-content")
                ], className="info-panel")
            ], width=12)
        ], className="mt-3"),
        
        # Custom Compound Management Panel
        dbc.Row([
            dbc.Col([
                create_custom_compound_management_panel()
            ], width=12)
        ], className="mt-3"),
        
        # Custom Compound Modal
        create_custom_compound_modal()
], fluid=True)


# Callbacks
# Add client-side callback to preserve material selection
app.clientside_callback(
    """
    function(active_tab, current_selection) {
        // Preserve current selection when switching tabs
        return current_selection || [];
    }
    """,
    Output('material-dropdown', 'value', allow_duplicate=True),
    [Input('material-category-tabs', 'active_tab')],
    [State('material-dropdown', 'value')],
    prevent_initial_call=True
)

@app.callback(
    Output("collapse-gas-scales", "is_open"),
    [Input("collapse-gas-scales-button", "n_clicks")],
    [State("collapse-gas-scales", "is_open")]
)
def toggle_gas_scales_collapse(n_clicks, is_open):
    """Toggle gas scales section visibility."""
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('material-dropdown', 'options'),
    [Input('material-category-tabs', 'active_tab'),
     Input('metal-group-dropdown', 'value'),
     Input('material-grouping-mode', 'value')]
)
def update_material_options(active_tab, selected_metal, grouping_mode):
    """Update dropdown options based on selected category tab or metal grouping."""
    
    try:
        if grouping_mode == 'metal' and selected_metal:
            # Metal grouping mode
            from material_selector import get_materials_by_metal
            materials = get_materials_by_metal(categories_data, selected_metal)
        else:
            # Category grouping mode
            if active_tab is None:
                active_tab = 'oxides'
            materials = data_loader.get_available_materials(category=active_tab)
        
        # Create options with proper formatting
        options = []
        for material in materials:
            material_data = data_loader.get_material_data(material)
            if material_data:
                formula = material_data.get('formula', '')
                options.append({
                    "label": get_material_display_name(material),
                    "value": material,
                    "search": f"{material} {formula}".lower()
                })
        
        return options
        
    except Exception as e:
        print(f"Error updating material options: {e}")
        return []


@app.callback(
    Output('radius-custom', 'style'),
    Input('radius-radio', 'value')
)
def toggle_custom_radius(radius_value):
    """Show/hide custom radius input based on radio selection."""
    if radius_value == 'custom':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    [Output('category-tabs-container', 'style'),
     Output('metal-group-container', 'style'),
     Output('metal-group-dropdown', 'options')],
    [Input('material-grouping-mode', 'value')]
)
def toggle_grouping_mode(grouping_mode):
    """Toggle between category tabs and metal grouping based on mode selection."""
    
    if grouping_mode == 'metal':
        # Show metal grouping, hide category tabs
        category_style = {'display': 'none'}
        metal_style = {'display': 'block'}
        
        # Get metal options
        from material_selector import create_metal_group_options
        metal_options = create_metal_group_options(categories_data)
        
    else:
        # Show category tabs, hide metal grouping
        category_style = {'display': 'block'}
        metal_style = {'display': 'none'}
        metal_options = []
    
    return category_style, metal_style, metal_options


@app.callback(
    Output('material-dropdown', 'value', allow_duplicate=True),
    [Input('material-grouping-mode', 'value')],
    [State('material-dropdown', 'value')],
    prevent_initial_call=True
)
def preserve_material_selection(grouping_mode, current_selection):
    """Preserve material selection when switching grouping modes."""
    return current_selection


@app.callback(
    Output('ellingham-plot', 'figure'),
    [Input('material-dropdown', 'value'),
     Input('field-slider', 'value'),
     Input('radius-radio', 'value'),
     Input('radius-custom', 'value'),
     Input('temp-range-slider', 'value'),
     Input('display-options', 'value'),
     Input('comparison-mode', 'value'),
     Input('gas-scale-options', 'value'),
     Input('gas-composition-radio', 'value')]  # New input
)
def update_plot(materials, field_MV_m, radius_radio, radius_custom, temp_range, display_options, comparison_mode, gas_scales, gas_composition):
    """Update the Ellingham diagram plot."""
    if not materials:
        return go.Figure()
    
    # Get particle radius
    if radius_radio == 'custom':
        r_um = radius_custom if radius_custom is not None else 5.0  # Default to 5.0 μm if custom is empty
    else:
        r_um = radius_radio
    
    # Convert units
    E_V_m = mv_per_m_to_v_per_m(field_MV_m)
    r_m = um_to_m(r_um)
    T_min_K, T_max_K = temp_range
    
    # Create temperature array
    T_K = np.linspace(T_min_K, T_max_K, 200)
    T_C = kelvin_to_celsius(T_K)
    
    # Create subplot with secondary axes
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )
    
    # Detect compound types in selection
    categories = set()
    for material in materials:
        material_data = data_loader.get_material_data(material)
        if material_data:
            categories.add(material_data.get('category', 'oxides'))
    
    # Determine normalization strategy
    if len(categories) == 1:
        normalization = 'auto'  # Use native units
        y_label = "ΔG (kJ/mol O₂/N₂/C)"
    else:
        normalization = 'metal'  # Normalize to metal for comparison
        y_label = "ΔG (kJ/mol Metal)"
    
    # Add traces for each material
    for material in materials:
        # Get material data from the new structure
        material_data = data_loader.get_material_data(material)
        if not material_data:
            continue
            
        # Process material for Ellingham calculations
        processed_data = data_loader.process_material_for_ellingham(material)
        if not processed_data:
            continue
            
        # Calculate equilibrium and off-equilibrium curves using normalized method
        DG_eq, unit = thermo_engine.calc_equilibrium_DG_normalized(material, T_K, normalization)
        DG_eff = thermo_engine.calc_off_equilibrium_DG(material, T_K, E_V_m, r_m)
        
        # Get color and group using new metal-based system
        element = processed_data.get('element', 'Unknown')
        formula = material_data.get('formula', '')
        category = material_data.get('category', 'oxides')
        color = get_color_for_material(material, formula, category)
        
        # Add equilibrium line with professional styling
        if 'equilibrium' in display_options:
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=DG_eq,
                    mode='lines',
                    name=create_legend_label(material, 'equilibrium', field_MV_m, r_um),
                    line=dict(
                        color=color, 
                        width=3, 
                        dash='solid',
                        shape='spline',  # Smooth curves like professional diagrams
                        smoothing=0.3
                    ),
                    hovertemplate=f"<b>{material}</b><br>" +
                                 f"Formula: {formula}<br>" +
                                 f"Category: {category.capitalize()}<br>" +
                                 f"Element: {element}<br>" +
                                 "Temperature: %{x:.0f}°C<br>" +
                                 f"ΔG°: %{{y:.1f}} {unit}<br>" +
                                 f"Field: {field_MV_m:.1f} MV/m<br>" +
                                 f"Radius: {r_um:.1f} μm<extra></extra>",
                    showlegend=True,
                    legendgroup=f"material_{material}",
                    legendgrouptitle_text=material
                ),
                secondary_y=False
            )
        
        # Add off-equilibrium line with professional styling
        if 'off_equilibrium' in display_options:
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=DG_eff,
                    mode='lines',
                    name=create_legend_label(material, 'off_eq', field_MV_m, r_um),
                    line=dict(
                        color=color, 
                        width=2, 
                        dash='dash',
                        shape='spline',  # Smooth curves
                        smoothing=0.3
                    ),
                    hovertemplate=f"<b>{material}</b><br>" +
                                 f"Formula: {formula}<br>" +
                                 f"Category: {category.capitalize()}<br>" +
                                 f"Element: {element}<br>" +
                                 "Temperature: %{x:.0f}°C<br>" +
                                 f"ΔG_eff: %{{y:.1f}} {unit}<br>" +
                                 f"Field: {field_MV_m:.1f} MV/m<br>" +
                                 f"Radius: {r_um:.1f} μm<extra></extra>",
                    showlegend=True,
                    legendgroup=f"material_{material}",
                    legendgrouptitle_text=material
                ),
                secondary_y=False
            )
    
    # Add zero line with professional styling
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="rgba(0,0,0,0.6)", 
        line_width=2,
        opacity=0.8,
        annotation_text="ΔG = 0",
        annotation_position="top right",
        annotation_font_size=12,
        annotation_font_color="rgba(0,0,0,0.7)"
    )
    
    # Add nomographic gas ratio scales
    if gas_scales and len(gas_scales) > 0 and materials:
        try:
            # Use first material for gas ratio calculation
            material = materials[0]
            
            # Calculate gas ratios based on what's being displayed
            if 'equilibrium' in display_options and 'off_equilibrium' in display_options:
                # If both are shown, use equilibrium for gas ratios (standard practice)
                DG_for_gas_ratios = thermo_engine.calc_equilibrium_DG(material, T_K)
                gas_ratio_label_suffix = " (Equilibrium)"
            elif 'equilibrium' in display_options:
                DG_for_gas_ratios = thermo_engine.calc_equilibrium_DG(material, T_K)
                gas_ratio_label_suffix = " (Equilibrium)"
            elif 'off_equilibrium' in display_options:
                # Use off-equilibrium values for gas ratios
                DG_for_gas_ratios = thermo_engine.calc_off_equilibrium_DG(material, T_K, E_V_m, r_m)
                gas_ratio_label_suffix = " (Off-Equilibrium)"
            else:
                # Default to equilibrium
                DG_for_gas_ratios = thermo_engine.calc_equilibrium_DG(material, T_K)
                gas_ratio_label_suffix = " (Equilibrium)"
            
            # Calculate all gas ratios using the appropriate DG values
            all_ratios = thermo_engine.calc_comprehensive_gas_ratios(T_K, DG_for_gas_ratios)
            metadata = thermo_engine.get_gas_ratio_metadata()
            
            # Add selected gas ratio traces
            for gas_key in gas_scales:
                if gas_key in all_ratios:
                    gas_info = metadata[gas_key]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=T_C,
                            y=all_ratios[gas_key],
                            mode='lines',
                            name=gas_info['label'] + gas_ratio_label_suffix,
                            line=dict(
                                color=gas_info['color'],
                                width=1.5,
                                dash='dot',
                                shape='spline',
                                smoothing=0.3
                            ),
                            yaxis='y2',
                            hovertemplate=f"<b>{gas_info['label']}</b><br>" +
                                         f"{gas_info['description']}<br>" +
                                         f"Based on: {gas_ratio_label_suffix.strip(' ()')}<br>" +
                                         "Temperature: %{x:.0f}°C<br>" +
                                         "Log Value: %{y:.2f}<br>" +
                                         f"Actual Ratio: {10**all_ratios[gas_key][0]:.1e}<extra></extra>",
                            showlegend=True,
                            legendgroup='gas_ratios'
                        ),
                        secondary_y=True
                    )
            
            # Configure secondary y-axis with nomographic styling
            if fig.data:  # Only if traces were added
                fig.update_yaxes(
                    title=dict(
                        text=f"Gas Ratios (log scale){gas_ratio_label_suffix}",
                        font=dict(size=12, family="Arial, sans-serif")
                    ),
                    overlaying="y",
                    side="right",
                    tickfont=dict(size=10, family="Arial, sans-serif"),
                    gridcolor='rgba(128,128,128,0.1)',
                    gridwidth=0.5,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='rgba(0,0,0,0.3)',
                    zerolinewidth=1,
                    linecolor='rgba(0,0,0,0.3)',
                    linewidth=1,
                    secondary_y=True
                )
                
        except Exception as e:
            print(f"Warning: Could not add nomographic gas ratio scales: {e}")
            import traceback
            traceback.print_exc()
    
    # Determine plot title based on display options and comparison mode
    if 'equilibrium' in display_options and 'off_equilibrium' in display_options:
        plot_title = "Off-Equilibrium Ellingham Diagram"
    elif 'equilibrium' in display_options:
        plot_title = "Equilibrium Ellingham Diagram"
    elif 'off_equilibrium' in display_options:
        plot_title = "Off-Equilibrium Ellingham Diagram"
    else:
        plot_title = "Ellingham Diagram"
    
    # Add comparison mode to title
    if comparison_mode == 'by_metal':
        plot_title += " - Grouped by Metal"
    elif comparison_mode == 'by_type':
        plot_title += " - Grouped by Compound Type"
    
    # Professional formatting based on PNG analysis
    fig.update_layout(
        title=dict(
            text=plot_title,
            font=dict(size=18, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text="Temperature (°C)",
                font=dict(size=14, family="Arial, sans-serif")
            ),
            tickfont=dict(size=12, family="Arial, sans-serif"),
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            linecolor='black',
            linewidth=1
        ),
        yaxis=dict(
            title=dict(
                text=y_label,
                font=dict(size=14, family="Arial, sans-serif")
            ),
            tickfont=dict(size=12, family="Arial, sans-serif"),
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            linecolor='black',
            linewidth=1
        ),
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=11, family="Arial, sans-serif"),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            # Enhanced legend grouping
            groupclick="togglegroup",   # Clicking a group toggles the group
            itemclick="toggle",         # Clicking an item toggles it
            itemdoubleclick="toggleothers"  # Double-click toggles others
        ),
        margin=dict(r=200, t=80, b=60, l=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    # Add temperature markers
    for T_marker in TEMP_MARKERS:
        T_marker_C = T_marker
        if T_marker_C >= T_C.min() and T_marker_C <= T_C.max():
            fig.add_vline(
                x=T_marker_C,
                line_dash="dot",
                line_color="gray",
                opacity=0.7,
                annotation_text=f"{T_marker_C}°C"
            )
    
    return fig


@app.callback(
    Output('info-panel-content', 'children'),
    [Input('material-dropdown', 'value'),
     Input('field-slider', 'value'),
     Input('radius-radio', 'value'),
     Input('radius-custom', 'value'),
     Input('temp-range-slider', 'value'),
     Input('gas-composition-radio', 'value'),
     Input('entry-temp-slider', 'value')]  # New input
)
def update_info_panel(materials, field_MV_m, radius_radio, radius_custom, temp_range, gas_composition, entry_temp_K):
    """Update the info panel with thermodynamic analysis."""
    if not materials:
        return "Select materials to see thermodynamic analysis."
    
    # Get particle radius
    if radius_radio == 'custom':
        r_um = radius_custom if radius_custom is not None else 5.0  # Default to 5.0 μm if custom is empty
    else:
        r_um = radius_radio
    
    # Convert units
    E_V_m = mv_per_m_to_v_per_m(field_MV_m)
    r_m = um_to_m(r_um)
    
    # Calculate validation results for temperature markers
    validation_results = []
    T_markers_K = [celsius_to_kelvin(np.array([T]))[0] for T in TEMP_MARKERS]
    
    for material in materials:
        # Get material data from the new structure
        material_data = data_loader.get_material_data(material)
        if not material_data:
            continue
            
        # Process material for Ellingham calculations
        processed_data = data_loader.process_material_for_ellingham(material)
        if not processed_data:
            continue
            
        for T_K in T_markers_K:
            if T_K >= temp_range[0] and T_K <= temp_range[1]:
                # Create validation result with all required fields
                DG_eq = processed_data['fit_params']['A']  # Simplified
                DG_eff = DG_eq - processed_data['fit_params']['n_electrons'] * 96485 * E_V_m * r_m / 1000
                
                # Calculate proper gas ratios using thermodynamic engine
                ln_pO2_req = thermo_engine.calc_oxygen_potential_required(material, np.array([T_K]), E_V_m, r_m)[0]
                h2_h2o_ratio = thermo_engine.calc_h2_h2o_ratio_required(material, np.array([T_K]), E_V_m, r_m)[0]
                p_h2_req = thermo_engine.calc_h2_partial_pressure_required(material, np.array([T_K]), E_V_m, r_m)[0]
                
                validation = {
                    'material': material,
                    'oxide': material,  # For compatibility with existing code
                    'formula': processed_data.get('formula', ''),
                    'element': processed_data.get('element', ''),
                    'category': processed_data.get('category', ''),
                    'temperature_K': T_K,
                    'temperature_C': kelvin_to_celsius(T_K),
                    'electric_field_MV_m': field_MV_m,
                    'field_MV_m': field_MV_m,
                    'particle_radius_um': r_um,
                    'radius_um': r_um,
                    'DG_eq_kJ_per_molO2': DG_eq,
                    'DG_eff_kJ_per_molO2': DG_eff,
                    'n_electrons': processed_data['fit_params']['n_electrons'],
                    'n_oxygen': processed_data['fit_params']['n_oxygen'],
                    'feasibility': ('Feasible', 'success'),  # Simplified feasibility
                    'p_h2_req_atm': p_h2_req,  # Now using proper calculation
                    'h2_h2o_ratio_req': h2_h2o_ratio,  # Now using proper calculation
                    'ln_pO2_req': ln_pO2_req  # Now using proper calculation
                }
                validation_results.append(validation)
    
    # Create info text
    info_text = create_info_text(validation_results, gas_composition, entry_temp_K)
    
    return dcc.Markdown(info_text)


@app.callback(
    Output('download-data', 'data'),
    Input('export-btn', 'n_clicks'),
    [State('material-dropdown', 'value'),
     State('field-slider', 'value'),
     State('radius-radio', 'value'),
     State('radius-custom', 'value'),
     State('temp-range-slider', 'value')],
    prevent_initial_call=True
)
def export_data(n_clicks, materials, field_MV_m, radius_radio, radius_custom, temp_range):
    """Export calculated data to CSV."""
    if not materials or not n_clicks:
        return None
    
    # Get particle radius
    if radius_radio == 'custom':
        r_um = radius_custom if radius_custom is not None else 5.0  # Default to 5.0 μm if custom is empty
    else:
        r_um = radius_radio
    
    # Convert units
    E_V_m = mv_per_m_to_v_per_m(field_MV_m)
    r_m = um_to_m(r_um)
    T_min_K, T_max_K = temp_range
    
    # Create temperature array
    T_K = np.linspace(T_min_K, T_max_K, 100)
    
    # Collect data for export
    export_data = {}
    
    for material in materials:
        DG_eq = thermo_engine.calc_equilibrium_DG(material, T_K)
        DG_eff = thermo_engine.calc_off_equilibrium_DG(material, T_K, E_V_m, r_m)
        
        export_data[material] = {
            'T_K': T_K,
            'DG_eq': DG_eq,
            'DG_eff': DG_eff,
            'E_MV_m': field_MV_m,
            'r_um': r_um
        }
    
    # Create CSV content
    from utils import export_data_to_csv
    csv_content = export_data_to_csv(export_data, "ellingham_data.csv")
    
    return dict(content=csv_content, filename="ellingham_data.csv")


# Sources modal callbacks
@app.callback(
    Output("sources-modal", "is_open"),
    [Input("sources-btn", "n_clicks"), Input("close-sources", "n_clicks")],
    [State("sources-modal", "is_open")],
)
def toggle_sources_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("sources-content", "children"),
    [Input("sources-btn", "n_clicks")]
)
def update_sources_content(n_clicks):
    """Update sources content with scientific citations."""
    if n_clicks is None:
        return ""
    
    from documentation import generate_bibliography, generate_parameter_report
    
    # Generate bibliography
    bibliography = generate_bibliography()
    
    # Generate parameter report for common materials
    common_materials = ['TiO2', 'ZrO2', 'Al2O3', 'MgO', 'Fe2O3']
    parameter_reports = []
    
    for material in common_materials:
        report = generate_parameter_report(material)
        parameter_reports.append(dbc.Card([
            dbc.CardHeader(material),
            dbc.CardBody([
                html.Pre(report, style={'font-size': '12px', 'white-space': 'pre-wrap'})
            ])
        ], className="mb-3"))
    
    return html.Div([
        html.H5("Scientific Sources & Citations"),
        html.P("All parameters are sourced from peer-reviewed literature with proper citations."),
        html.Hr(),
        html.H6("Bibliography"),
        html.Pre(bibliography, style={'font-size': '12px', 'white-space': 'pre-wrap'}),
        html.Hr(),
        html.H6("Parameter Details"),
        html.Div(parameter_reports)
    ])


@app.callback(
    Output("validation-status", "children"),
    [Input("field-slider", "value"), Input("radius-radio", "value"), Input("radius-custom", "value")]
)
def update_validation_status(field_MV_m, radius_radio, radius_custom):
    """Update validation status based on current parameters."""
    from documentation import get_confidence_indicator
    from config import VALIDATION_SETTINGS
    
    if not VALIDATION_SETTINGS.get('show_confidence_indicators', True):
        return html.Div([
            html.P("Validation disabled", className="text-muted mb-1"),
            html.Small("Enable in settings", className="text-muted")
        ])
    
    # Determine radius value
    if radius_radio == 'custom':
        r_um = radius_custom if radius_custom is not None else 5.0  # Default to 5.0 μm if custom is empty
    else:
        r_um = radius_radio
    
    # Validate parameters
    confidence = 'high'
    warnings = []
    
    # Check field range
    if field_MV_m < 0.1 or field_MV_m > 2.5:
        confidence = 'low'
        warnings.append("Field outside validated range")
    elif field_MV_m < 0.5 or field_MV_m > 2.0:
        confidence = 'medium'
        warnings.append("Field near range limits")
    
    # Check radius range
    if r_um < 0.1 or r_um > 100:
        confidence = 'low'
        warnings.append("Radius outside typical range")
    elif r_um < 1 or r_um > 50:
        confidence = 'medium'
        warnings.append("Radius near range limits")
    
    # Get confidence indicator
    indicator = get_confidence_indicator(confidence)
    
    # Create status message
    if confidence == 'high':
        status_text = f"{indicator} High Confidence"
        status_class = "text-success"
        detail_text = "All parameters within validated ranges"
    elif confidence == 'medium':
        status_text = f"{indicator} Medium Confidence"
        status_class = "text-warning"
        detail_text = "Some parameters near range limits"
    else:
        status_text = f"{indicator} Low Confidence"
        status_class = "text-danger"
        detail_text = "Parameters outside validated ranges"
    
    return html.Div([
        html.P(status_text, className=f"{status_class} mb-1"),
        html.Small(detail_text, className="text-muted"),
        html.Br(),
        html.Small(f"Field: {field_MV_m:.1f} MV/m, Radius: {r_um:.1f} μm", className="text-muted")
    ])


# SVG Export callback
@app.callback(
    Output('download-svg', 'data'),
    Input('export-svg-btn', 'n_clicks'),
    State('ellingham-plot', 'figure'),
    prevent_initial_call=True
)
def export_svg(n_clicks, figure):
    """Export current plot as SVG file with publication-quality formatting."""
    if not figure or n_clicks is None:
        return None
    
    # Convert figure dict to Plotly figure object
    import plotly.graph_objects as go
    export_figure = go.Figure(figure)
    
    # Optimize layout for publication quality
    export_figure.update_layout(
        # Increase margins to prevent text overlap
        margin=dict(l=80, r=200, t=80, b=80),
        
        # Optimize legend for publication
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            itemwidth=30,
            itemsizing="constant"
        ),
        
        # Improve title and axis formatting
        title=dict(
            font=dict(size=16, family="Arial, sans-serif"),
            x=0.5,
            xanchor="center"
        ),
        
        # Optimize axis labels
        xaxis=dict(
            title_font=dict(size=12, family="Arial, sans-serif"),
            tickfont=dict(size=10, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=0.5
        ),
        
        yaxis=dict(
            title_font=dict(size=12, family="Arial, sans-serif"),
            tickfont=dict(size=10, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=0.5
        ),
        
        # Optimize secondary y-axis for gas scales
        yaxis2=dict(
            title_font=dict(size=12, family="Arial, sans-serif"),
            tickfont=dict(size=10, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.1)',
            gridwidth=0.5
        ),
        
        # Set figure size for publication quality
        width=1000,
        height=700,
        
        # Improve overall appearance
        plot_bgcolor='white',
        paper_bgcolor='white',
        
        # Optimize hover behavior for SVG
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.3)",
            font_size=10,
            font_family="Arial, sans-serif"
        )
    )
    
    # Convert figure to SVG string with high quality
    import plotly.io as pio
    svg_bytes = pio.to_image(export_figure, format='svg', width=1000, height=700, scale=2)
    
    # Return as downloadable file
    return dict(
        content=svg_bytes.decode('utf-8'),
        filename='ellingham_diagram.svg',
        type='image/svg+xml'
    )


# PDF Export callback
@app.callback(
    Output('download-pdf', 'data'),
    Input('export-pdf-btn', 'n_clicks'),
    State('ellingham-plot', 'figure'),
    prevent_initial_call=True
)
def export_pdf(n_clicks, figure):
    """Export current plot as PDF file with publication-quality formatting."""
    if not figure or n_clicks is None:
        return None
    
    # Convert figure dict to Plotly figure object
    import plotly.graph_objects as go
    export_figure = go.Figure(figure)
    
    # Optimize layout for PDF publication quality
    export_figure.update_layout(
        # Optimize margins for PDF printing
        margin=dict(l=100, r=150, t=100, b=100),
        
        # Optimize legend for PDF
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.3)",
            borderwidth=1,
            itemwidth=35,
            itemsizing="constant"
        ),
        
        # Improve title and axis formatting for PDF
        title=dict(
            font=dict(size=18, family="Arial, sans-serif"),
            x=0.5,
            xanchor="center"
        ),
        
        # Optimize axis labels for PDF
        xaxis=dict(
            title_font=dict(size=14, family="Arial, sans-serif"),
            tickfont=dict(size=12, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.3)',
            gridwidth=0.8
        ),
        
        yaxis=dict(
            title_font=dict(size=14, family="Arial, sans-serif"),
            tickfont=dict(size=12, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.3)',
            gridwidth=0.8
        ),
        
        # Optimize secondary y-axis for gas scales (PDF)
        yaxis2=dict(
            title_font=dict(size=14, family="Arial, sans-serif"),
            tickfont=dict(size=12, family="Arial, sans-serif"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=0.8
        ),
        
        # Set figure size for PDF publication quality
        width=1200,
        height=800,
        
        # Improve overall appearance for PDF
        plot_bgcolor='white',
        paper_bgcolor='white',
        
        # Optimize hover behavior for PDF
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.4)",
            font_size=11,
            font_family="Arial, sans-serif"
        )
    )
    
    # Convert figure to PDF bytes with high quality
    import plotly.io as pio
    pdf_bytes = pio.to_image(export_figure, format='pdf', width=1200, height=800, scale=2)
    
    # Return as downloadable file
    return dict(
        content=pdf_bytes,
        filename='ellingham_diagram.pdf',
        type='application/pdf'
    )


# Custom Compound Callbacks

@app.callback(
    Output("custom-compound-modal", "is_open"),
    [Input("add-custom-compound-btn", "n_clicks"),
     Input("custom-save-btn", "n_clicks"),
     Input("custom-cancel-btn", "n_clicks")],
    [State("custom-compound-modal", "is_open")]
)
def toggle_custom_compound_modal(add_clicks, save_clicks, cancel_clicks, is_open):
    """Toggle custom compound modal visibility."""
    if add_clicks or save_clicks or cancel_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("custom-compounds-list", "children"),
    [Input("custom-search", "value"),
     Input("custom-category-filter", "value"),
     Input("add-custom-compound-btn", "n_clicks"),
     Input("custom-save-btn", "n_clicks")]
)
def update_custom_compounds_list(search_query, category_filter, add_clicks, save_clicks):
    """Update the custom compounds list display."""
    compounds = custom_compound_manager.get_all_compounds()
    
    # Apply search filter
    if search_query:
        compounds = custom_compound_manager.search_compounds(search_query)
    
    # Apply category filter
    if category_filter:
        compounds = {name: compound for name, compound in compounds.items() 
                    if compound.category == category_filter}
    
    if not compounds:
        return dbc.Alert(
            "No custom compounds found. Click 'Add New Compound' to get started.",
            color="info",
            className="text-center"
        )
    
    # Create list items
    list_items = []
    for i, (name, compound) in enumerate(compounds.items()):
        list_items.append(create_custom_compound_list_item(compound, i))
    
    return list_items


@app.callback(
    [Output("custom-name", "value"),
     Output("custom-formula", "value"),
     Output("custom-element", "value"),
     Output("custom-category", "value"),
     Output("custom-dg-a", "value"),
     Output("custom-dg-b", "value"),
     Output("custom-dg-c", "value"),
     Output("custom-dg-d", "value"),
     Output("custom-temp-min", "value"),
     Output("custom-temp-max", "value"),
     Output("custom-mw", "value"),
     Output("custom-density", "value"),
     Output("custom-wph", "value"),
     Output("custom-source", "value"),
     Output("custom-confidence", "value"),
     Output("custom-notes", "value")],
    [Input("load-template-btn", "n_clicks")],
    [State("custom-template", "value")]
)
def load_template_data(n_clicks, template_name):
    """Load template data into form fields."""
    if not n_clicks or not template_name:
        return [None] * 16
    
    try:
        compound = create_compound_from_template(template_name)
        
        return [
            compound.name,
            compound.formula,
            compound.element,
            compound.category,
            compound.dg_coefficients[0],
            compound.dg_coefficients[1],
            compound.dg_coefficients[2],
            compound.dg_coefficients[3],
            compound.temperature_range[0],
            compound.temperature_range[1],
            compound.molecular_weight,
            compound.density,
            compound.w_ph_constant,
            compound.source,
            compound.confidence_level,
            compound.notes
        ]
    except Exception as e:
        print(f"Error loading template: {e}")
        return [None] * 16


@app.callback(
    Output("custom-validation-alert", "children"),
    Output("custom-validation-alert", "is_open"),
    [Input("custom-save-btn", "n_clicks")],
    [State("custom-name", "value"),
     State("custom-formula", "value"),
     State("custom-element", "value"),
     State("custom-category", "value"),
     State("custom-dg-a", "value"),
     State("custom-dg-b", "value"),
     State("custom-dg-c", "value"),
     State("custom-dg-d", "value"),
     State("custom-temp-min", "value"),
     State("custom-temp-max", "value"),
     State("custom-mw", "value"),
     State("custom-density", "value"),
     State("custom-wph", "value"),
     State("custom-source", "value"),
     State("custom-confidence", "value"),
     State("custom-notes", "value")]
)
def validate_and_save_custom_compound(n_clicks, name, formula, element, category, dg_a, dg_b, dg_c, dg_d,
                                    temp_min, temp_max, mw, density, wph, source, confidence, notes):
    """Validate and save custom compound."""
    if not n_clicks:
        return "", False
    
    # Prepare compound data
    compound_data = {
        'name': name or '',
        'formula': formula or '',
        'element': element or '',
        'category': category or 'oxide',
        'dg_coefficients': [dg_a or 0, dg_b or 0, dg_c or 0, dg_d or 0],
        'temperature_range': [temp_min or 298, temp_max or 2000],
        'molecular_weight': mw or 100,
        'density': density or 1000,
        'w_ph_constant': wph or 20,
        'diffusion_enhancement': 1.0,
        'source': source or 'User-defined',
        'confidence_level': confidence or 'medium',
        'notes': notes or '',
        'created_date': '2025-01-27T00:00:00',
        'last_modified': '2025-01-27T00:00:00'
    }
    
    # Validate data
    is_valid, errors = custom_compound_manager.validate_compound_data(compound_data)
    
    if not is_valid:
        return create_custom_compound_validation_alert(errors), True
    
    # Create and save compound
    try:
        compound = CustomCompound.from_dict(compound_data)
        success = custom_compound_manager.add_compound(compound)
        
        if success:
            return create_custom_compound_validation_alert([]), True
        else:
            return create_custom_compound_validation_alert(["Failed to save compound"]), True
            
    except Exception as e:
        return create_custom_compound_validation_alert([f"Error creating compound: {str(e)}"]), True


@app.callback(
    Output("download-compounds", "data"),
    Input("export-compounds-btn", "n_clicks"),
    prevent_initial_call=True
)
def export_custom_compounds(n_clicks):
    """Export custom compounds to JSON file."""
    if not n_clicks:
        return None
    
    compounds = custom_compound_manager.get_all_compounds()
    export_data = create_custom_compound_export_data(compounds)
    
    return dict(
        content=export_data,
        filename="custom_compounds.json",
        type="application/json"
    )


@app.callback(
    Output("custom-compounds-list", "children", allow_duplicate=True),
    Input("upload-compounds", "contents"),
    prevent_initial_call=True
)
def import_custom_compounds(contents):
    """Import custom compounds from uploaded file."""
    if not contents:
        return None
    
    try:
        import base64
        import json
        
        # Decode uploaded content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        
        # Parse and import compounds
        success, messages, compounds = parse_custom_compound_import_data(decoded)
        
        if success:
            # Add compounds to manager
            for name, compound in compounds.items():
                custom_compound_manager.add_compound(compound)
            
            # Update display
            return update_custom_compounds_list(None, None, None, None)
        else:
            return dbc.Alert([
                html.H6("Import Failed"),
                html.Ul([html.Li(msg) for msg in messages])
            ], color="danger")
            
    except Exception as e:
        return dbc.Alert(f"Import error: {str(e)}", color="danger")


if __name__ == '__main__':
    # Port configuration:
    # - Railway deployment: Uses PORT=8050 (set in railway.toml)
    # - Local development: Uses port 8051 (to avoid conflicts with other apps)
    port = int(os.getenv('PORT', 8051))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
