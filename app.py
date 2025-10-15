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
from utils import (
    kelvin_to_celsius, celsius_to_kelvin, mv_per_m_to_v_per_m, um_to_m,
    get_color_for_oxide, get_line_style, create_legend_label,
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
available_oxides = data_loader.get_available_oxides()
print(f"Loaded {len(available_oxides)} oxide materials")

# Create material options for dropdown
material_options = [
    {"label": get_material_display_name(oxide), "value": oxide}
    for oxide in available_oxides
]

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
                
                # Material Selection
                html.Div([
                    html.H6("Materials"),
                    dcc.Dropdown(
                        id='material-dropdown',
                        options=material_options,
                        value=get_default_materials(),
                        multi=True,
                        placeholder="Select materials..."
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
                            {"label": "Show Gas Ratio Scales", "value": "gas_scales"}
                        ],
                        value=["equilibrium", "gas_scales"],
                        inline=False
                    )
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
                html.H5("Thermodynamic Analysis", className="info-title"),
                html.Div(id="info-panel-content")
            ], className="info-panel")
        ])
    ], className="mt-3")
], fluid=True)


# Callbacks
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
     Input('display-options', 'value')]
)
def update_plot(materials, field_MV_m, radius_radio, radius_custom, temp_range, display_options):
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
    
    # Add traces for each material
    for material in materials:
        if material not in available_oxides:
            continue
            
        # Calculate equilibrium and off-equilibrium curves
        DG_eq = thermo_engine.calc_equilibrium_DG(material, T_K)
        DG_eff = thermo_engine.calc_off_equilibrium_DG(material, T_K, E_V_m, r_m)
        
        # Get color and group
        group = thermo_engine.get_periodic_group(material)
        color = get_color_for_oxide(material, group)
        
        # Add equilibrium line
        if 'equilibrium' in display_options:
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=DG_eq,
                    mode='lines',
                    name=create_legend_label(material, 'equilibrium', field_MV_m, r_um),
                    line=dict(color=color, width=2, dash='solid'),
                    hovertemplate=f"<b>{material}</b><br>" +
                                 "Temperature: %{x:.0f}°C<br>" +
                                 "ΔG°: %{y:.1f} kJ/mol O₂<extra></extra>"
                ),
                secondary_y=False
            )
        
        # Add off-equilibrium line
        fig.add_trace(
            go.Scatter(
                x=T_C, y=DG_eff,
                mode='lines',
                name=create_legend_label(material, 'off_eq', field_MV_m, r_um),
                line=dict(color=color, width=3, dash='dash'),
                hovertemplate=f"<b>{material}</b><br>" +
                             "Temperature: %{x:.0f}°C<br>" +
                             "ΔG_eff: %{y:.1f} kJ/mol O₂<extra></extra>"
            ),
            secondary_y=False
        )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add gas ratio scales if enabled
    if 'gas_scales' in display_options and materials:
        try:
            # Use first material for gas ratio calculation
            material = materials[0]
            DG_eq = thermo_engine.calc_equilibrium_DG(material, T_K)
            log_H2_H2O, log_CO_CO2 = thermo_engine.calc_gas_ratio_scales(T_K, DG_eq)
            
            # Calculate pO2 scale
            log_pO2 = thermo_engine.calc_pO2_scale(T_K)
            
            # Add gas ratio traces to secondary y-axis
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=log_H2_H2O,
                    mode='lines',
                    name="log(H₂/H₂O)",
                    line=dict(color='red', width=2, dash='dot'),
                    yaxis='y2'
                ),
                secondary_y=True
            )
            
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=log_CO_CO2,
                    mode='lines', 
                    name="log(CO/CO₂)",
                    line=dict(color='blue', width=2, dash='dot'),
                    yaxis='y2'
                ),
                secondary_y=True
            )
            
            fig.add_trace(
                go.Scatter(
                    x=T_C, y=log_pO2,
                    mode='lines',
                    name="log₁₀(pO₂)",
                    line=dict(color='green', width=2, dash='dot'),
                    yaxis='y2'
                ),
                secondary_y=True
            )
            
            # Update secondary y-axis with proper title
            fig.update_yaxes(
                title_text="Gas Ratios: log(H₂/H₂O), log(CO/CO₂), log₁₀(pO₂)", 
                secondary_y=True
            )
        except Exception as e:
            print(f"Warning: Could not add gas ratio scales: {e}")
            import traceback
            traceback.print_exc()
            pass
    
    # Update layout
    fig.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="ΔG (kJ/mol O₂)",
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150)
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
        if material not in available_oxides:
            continue
            
        for T_K in T_markers_K:
            if T_K >= temp_range[0] and T_K <= temp_range[1]:
                validation = thermo_engine.validate_calculation(material, T_K, E_V_m, r_m)
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
