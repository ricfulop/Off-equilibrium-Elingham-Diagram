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

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Off-Equilibrium Ellingham Diagrams"

# Load data
print("Loading JANAF thermodynamic data...")
data_loader = load_janaf_data()
thermo_engine = ThermodynamicEngine(data_loader)

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
                
                # Electric Field
                html.Div([
                    html.H6("Electric Field"),
                    dcc.Slider(
                        id='field-slider',
                        min=0.1,
                        max=5.0,
                        step=0.1,
                        value=2.0,
                        marks={i: f"{i:.1f}" for i in np.arange(0.5, 5.5, 0.5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Small("MV/m", className="text-muted")
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
                
                # Temperature Range
                html.Div([
                    html.H6("Temperature Range"),
                    dcc.RangeSlider(
                        id='temp-range-slider',
                        min=300,
                        max=2400,
                        step=50,
                        value=DEFAULT_TEMP_RANGE,
                        marks={i: f"{i-273:.0f}°C" for i in range(500, 2500, 200)},
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
                            value=["H2_H2O", "CO_CO2"],
                            inline=False,
                            className="gas-scale-checklist"
                        )
                    ], id="collapse-gas-scales", is_open=False)
                ], className="control-section"),
                
                # Export Button
                html.Div([
                    dbc.Button("Export Data", id="export-btn", color="secondary", size="sm"),
                    dcc.Download(id="download-data")
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
                )
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
        ], className="mt-3")
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
    Input('material-category-tabs', 'active_tab')
)
def update_material_options(active_tab):
    """Update dropdown options based on selected category tab."""
    if active_tab is None:
        active_tab = 'oxides'
    
    try:
        # Get materials for the selected category
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
    Output('ellingham-plot', 'figure'),
    [Input('material-dropdown', 'value'),
     Input('field-slider', 'value'),
     Input('radius-radio', 'value'),
     Input('radius-custom', 'value'),
     Input('temp-range-slider', 'value'),
     Input('display-options', 'value'),
     Input('comparison-mode', 'value'),
     Input('gas-scale-options', 'value')]  # New input
)
def update_plot(materials, field_MV_m, radius_radio, radius_custom, temp_range, display_options, comparison_mode, gas_scales):
    """Update the Ellingham diagram plot."""
    if not materials:
        return go.Figure()
    
    # Get particle radius
    if radius_radio == 'custom':
        r_um = radius_custom
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
                                 "Temperature: %{x:.0f}°C<br>" +
                                 f"ΔG°: %{{y:.1f}} {unit}<extra></extra>",
                    showlegend=True
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
                                 "Temperature: %{x:.0f}°C<br>" +
                                 f"ΔG_eff: %{{y:.1f}} {unit}<extra></extra>",
                    showlegend=True
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
                                         "Value: %{y:.2f}<extra></extra>",
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
            borderwidth=1
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
     Input('temp-range-slider', 'value')]
)
def update_info_panel(materials, field_MV_m, radius_radio, radius_custom, temp_range):
    """Update the info panel with thermodynamic analysis."""
    if not materials:
        return "Select materials to see thermodynamic analysis."
    
    # Get particle radius
    if radius_radio == 'custom':
        r_um = radius_custom
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
                    'p_h2_req_atm': 0.0,  # Placeholder - would need proper calculation
                    'h2_h2o_ratio_req': 0.0,  # Placeholder
                    'ln_pO2_req': 0.0  # Placeholder
                }
                validation_results.append(validation)
    
    # Create info text
    info_text = create_info_text(validation_results)
    
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
        r_um = radius_custom
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
        if material not in available_oxides:
            continue
            
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
