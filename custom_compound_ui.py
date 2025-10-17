"""
Custom Compound Definition UI Components

This module provides Dash UI components for defining and managing custom compounds
in the Off-Equilibrium Ellingham Diagram application.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional, Tuple
import json

from custom_compounds import CustomCompound, CustomCompoundManager, COMPOUND_TEMPLATES, create_compound_from_template


def create_custom_compound_modal() -> dbc.Modal:
    """Create modal for adding/editing custom compounds."""
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Custom Compound Definition")),
        dbc.ModalBody([
            # Basic Information
            dbc.Row([
                dbc.Col([
                    dbc.Label("Compound Name *", html_for="custom-name"),
                    dbc.Input(
                        id="custom-name",
                        type="text",
                        placeholder="e.g., Titanium Oxide, Rutile",
                        required=True
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Chemical Formula *", html_for="custom-formula"),
                    dbc.Input(
                        id="custom-formula",
                        type="text",
                        placeholder="e.g., TiO2",
                        required=True
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Metal Element *", html_for="custom-element"),
                    dbc.Input(
                        id="custom-element",
                        type="text",
                        placeholder="e.g., Ti",
                        required=True
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Category *", html_for="custom-category"),
                    dbc.Select(
                        id="custom-category",
                        options=[
                            {"label": "Oxide", "value": "oxide"},
                            {"label": "Carbide", "value": "carbide"},
                            {"label": "Nitride", "value": "nitride"},
                            {"label": "Halide", "value": "halide"},
                            {"label": "Hydride", "value": "hydride"},
                            {"label": "Sulfide", "value": "sulfide"},
                            {"label": "Phosphide", "value": "phosphide"},
                            {"label": "Pure Element", "value": "pure_element"},
                            {"label": "Other", "value": "other"}
                        ],
                        value="oxide"
                    )
                ], width=6)
            ], className="mb-3"),
            
            # Thermodynamic Parameters
            html.Hr(),
            html.H5("Thermodynamic Parameters", className="mb-3"),
            html.P("Gibbs Free Energy Coefficients: ΔG° = A + B×T + C×T×ln(T) + D×T² (kJ/mol O₂)", 
                   className="text-muted small"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("A (kJ/mol O₂)", html_for="custom-dg-a"),
                    dbc.Input(
                        id="custom-dg-a",
                        type="number",
                        step="0.1",
                        placeholder="-944.7"
                    )
                ], width=3),
                dbc.Col([
                    dbc.Label("B (kJ/mol·K)", html_for="custom-dg-b"),
                    dbc.Input(
                        id="custom-dg-b",
                        type="number",
                        step="0.0001",
                        placeholder="0.1815"
                    )
                ], width=3),
                dbc.Col([
                    dbc.Label("C (kJ/mol·K)", html_for="custom-dg-c"),
                    dbc.Input(
                        id="custom-dg-c",
                        type="number",
                        step="0.0001",
                        placeholder="0.0"
                    )
                ], width=3),
                dbc.Col([
                    dbc.Label("D (kJ/mol·K²)", html_for="custom-dg-d"),
                    dbc.Input(
                        id="custom-dg-d",
                        type="number",
                        step="0.000001",
                        placeholder="0.0"
                    )
                ], width=3)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Temperature Range (K)", html_for="custom-temp-range"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="custom-temp-min",
                            type="number",
                            placeholder="298",
                            min=0,
                            step=1
                        ),
                        dbc.InputGroupText("to"),
                        dbc.Input(
                            id="custom-temp-max",
                            type="number",
                            placeholder="2000",
                            min=0,
                            step=1
                        )
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Label("Molecular Weight (g/mol)", html_for="custom-mw"),
                    dbc.Input(
                        id="custom-mw",
                        type="number",
                        step="0.1",
                        placeholder="79.9"
                    )
                ], width=6)
            ], className="mb-3"),
            
            # Physical Properties
            html.Hr(),
            html.H5("Physical Properties", className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Density (kg/m³)", html_for="custom-density"),
                    dbc.Input(
                        id="custom-density",
                        type="number",
                        step="10",
                        placeholder="4250"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("W_ph Constant (kJ/mol O₂)", html_for="custom-wph"),
                    dbc.Input(
                        id="custom-wph",
                        type="number",
                        step="0.1",
                        placeholder="20.0"
                    )
                ], width=6)
            ], className="mb-3"),
            
            # Metadata
            html.Hr(),
            html.H5("Metadata", className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Source", html_for="custom-source"),
                    dbc.Input(
                        id="custom-source",
                        type="text",
                        placeholder="JANAF Thermochemical Tables"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Confidence Level", html_for="custom-confidence"),
                    dbc.Select(
                        id="custom-confidence",
                        options=[
                            {"label": "High", "value": "high"},
                            {"label": "Medium", "value": "medium"},
                            {"label": "Low", "value": "low"}
                        ],
                        value="medium"
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Notes", html_for="custom-notes"),
                    dbc.Textarea(
                        id="custom-notes",
                        placeholder="Additional notes about this compound...",
                        rows=3
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Template Selection
            html.Hr(),
            html.H5("Quick Start from Template", className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Load Template", html_for="custom-template"),
                    dbc.Select(
                        id="custom-template",
                        options=[
                            {"label": "Select a template...", "value": ""},
                            {"label": "TiO2 (Titanium Oxide)", "value": "TiO2"},
                            {"label": "Al2O3 (Aluminum Oxide)", "value": "Al2O3"}
                        ],
                        value=""
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("", html_for="load-template-btn"),
                    dbc.Button(
                        "Load Template",
                        id="load-template-btn",
                        color="secondary",
                        size="sm",
                        className="mt-4"
                    )
                ], width=6)
            ], className="mb-3"),
            
            # Validation Messages
            dbc.Alert(
                id="custom-validation-alert",
                is_open=False,
                dismissable=True,
                className="mt-3"
            )
            
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "Cancel",
                id="custom-cancel-btn",
                color="secondary",
                className="me-2"
            ),
            dbc.Button(
                "Save Compound",
                id="custom-save-btn",
                color="primary"
            )
        ])
    ], id="custom-compound-modal", size="lg", is_open=False)


def create_custom_compound_management_panel() -> dbc.Card:
    """Create panel for managing custom compounds."""
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Custom Compounds", className="mb-0"),
            html.P("Define and manage your own materials with custom thermodynamic parameters", 
                   className="text-muted small mb-0")
        ]),
        dbc.CardBody([
            # Action Buttons
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Add New Compound",
                        id="add-custom-compound-btn",
                        color="primary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Import Compounds",
                        id="import-compounds-btn",
                        color="outline-secondary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Export Compounds",
                        id="export-compounds-btn",
                        color="outline-secondary",
                        size="sm"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Search and Filter
            dbc.Row([
                dbc.Col([
                    dbc.Label("Search Compounds", html_for="custom-search"),
                    dbc.Input(
                        id="custom-search",
                        type="text",
                        placeholder="Search by name, formula, or element...",
                        size="sm"
                    )
                ], width=8),
                dbc.Col([
                    dbc.Label("Category Filter", html_for="custom-category-filter"),
                    dbc.Select(
                        id="custom-category-filter",
                        options=[
                            {"label": "All Categories", "value": ""},
                            {"label": "Oxides", "value": "oxide"},
                            {"label": "Carbides", "value": "carbide"},
                            {"label": "Nitrides", "value": "nitride"},
                            {"label": "Halides", "value": "halide"},
                            {"label": "Hydrides", "value": "hydride"},
                            {"label": "Sulfides", "value": "sulfide"},
                            {"label": "Phosphides", "value": "phosphide"},
                            {"label": "Pure Elements", "value": "pure_element"},
                            {"label": "Other", "value": "other"}
                        ],
                        value="",
                        size="sm"
                    )
                ], width=4)
            ], className="mb-3"),
            
            # Custom Compounds List
            html.Div(
                id="custom-compounds-list",
                children=[
                    dbc.Alert(
                        "No custom compounds defined yet. Click 'Add New Compound' to get started.",
                        color="info",
                        className="text-center"
                    )
                ]
            ),
            
            # Import/Export Components
            dcc.Upload(
                id="upload-compounds",
                children=html.Div([
                    "Drag and Drop or ",
                    html.A("Select File")
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0'
                },
                multiple=False
            ),
            
            dcc.Download(id="download-compounds")
        ])
    ], className="mt-3")


def create_custom_compound_list_item(compound: CustomCompound, index: int) -> dbc.Card:
    """Create a list item for displaying a custom compound."""
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(compound.name, className="mb-1"),
                    html.P(f"{compound.formula} ({compound.element})", 
                           className="text-muted small mb-1"),
                    html.P(f"Category: {compound.category.title()}", 
                           className="text-muted small mb-0")
                ], width=8),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button(
                            "Edit",
                            id={"type": "edit-custom", "index": index},
                            color="outline-primary",
                            size="sm"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "delete-custom", "index": index},
                            color="outline-danger",
                            size="sm"
                        )
                    ], size="sm")
                ], width=4, className="text-end")
            ]),
            
            # Additional info in collapsible section
            dbc.Collapse([
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P(f"Temperature Range: {compound.temperature_range[0]:.0f} - {compound.temperature_range[1]:.0f} K", 
                               className="small mb-1"),
                        html.P(f"Molecular Weight: {compound.molecular_weight:.1f} g/mol", 
                               className="small mb-1"),
                        html.P(f"Density: {compound.density:.0f} kg/m³", 
                               className="small mb-0")
                    ], width=6),
                    dbc.Col([
                        html.P(f"W_ph Constant: {compound.w_ph_constant:.1f} kJ/mol O₂", 
                               className="small mb-1"),
                        html.P(f"Source: {compound.source}", 
                               className="small mb-1"),
                        html.P(f"Confidence: {compound.confidence_level.title()}", 
                               className="small mb-0")
                    ], width=6)
                ]),
                html.P(f"Notes: {compound.notes}", 
                       className="small text-muted mt-2 mb-0")
            ], id=f"custom-compound-details-{index}", is_open=False)
        ])
    ], className="mb-2")


def create_custom_compound_validation_alert(errors: List[str], warnings: List[str] = None) -> dbc.Alert:
    """Create validation alert for custom compound form."""
    
    if errors:
        return dbc.Alert([
            html.H6("Validation Errors:", className="mb-2"),
            html.Ul([html.Li(error) for error in errors])
        ], color="danger", is_open=True)
    
    if warnings:
        return dbc.Alert([
            html.H6("Warnings:", className="mb-2"),
            html.Ul([html.Li(warning) for warning in warnings])
        ], color="warning", is_open=True)
    
    return dbc.Alert("Compound data is valid!", color="success", is_open=True)


def create_custom_compound_export_data(compounds: Dict[str, CustomCompound]) -> str:
    """Create JSON export data for custom compounds."""
    
    export_data = {
        "metadata": {
            "export_date": "2025-01-27",
            "version": "1.0",
            "total_compounds": len(compounds),
            "description": "Custom compounds export from Off-Equilibrium Ellingham Diagram"
        },
        "compounds": {name: compound.to_dict() for name, compound in compounds.items()}
    }
    
    return json.dumps(export_data, indent=2)


def parse_custom_compound_import_data(content: str) -> tuple[bool, List[str], Dict[str, CustomCompound]]:
    """
    Parse imported custom compound data.
    
    Args:
        content: JSON content string
        
    Returns:
        Tuple of (success, messages, compounds_dict)
    """
    try:
        data = json.loads(content)
        
        if "compounds" not in data:
            return False, ["Invalid format: missing 'compounds' section"], {}
        
        compounds = {}
        messages = []
        
        for name, compound_data in data["compounds"].items():
            try:
                compound = CustomCompound.from_dict(compound_data)
                compounds[name] = compound
                messages.append(f"Successfully imported: {name}")
            except Exception as e:
                messages.append(f"Error importing {name}: {str(e)}")
        
        if compounds:
            messages.insert(0, f"Successfully imported {len(compounds)} compounds")
        
        return len(compounds) > 0, messages, compounds
        
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON format: {str(e)}"], {}
    except Exception as e:
        return False, [f"Import error: {str(e)}"], {}
