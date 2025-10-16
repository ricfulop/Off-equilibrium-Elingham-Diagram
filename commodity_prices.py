"""
Commodity Price Manager for Economic Analysis

Manages commodity price data from multiple sources for cost-effectiveness analysis
of reduction processes in the Ellingham diagram application.
"""

from typing import Dict, Optional, List
import json
from datetime import datetime
import os


class CommodityPriceManager:
    """Manage commodity price data from multiple sources."""
    
    def __init__(self, price_file: str = "commodity_prices.json"):
        self.price_file = price_file
        self.prices = {}
        self.load_prices()
    
    def load_prices(self):
        """Load prices from JSON file."""
        try:
            with open(self.price_file, 'r') as f:
                self.prices = json.load(f)
            print(f"Loaded commodity prices from {self.price_file}")
        except FileNotFoundError:
            print(f"Price file {self.price_file} not found, creating with default prices")
            self.prices = self._get_default_prices()
            self.save_prices()
        except json.JSONDecodeError as e:
            print(f"Error parsing price file: {e}")
            self.prices = self._get_default_prices()
            self.save_prices()
    
    def save_prices(self):
        """Save prices to JSON file."""
        try:
            with open(self.price_file, 'w') as f:
                json.dump(self.prices, f, indent=2)
            print(f"Saved commodity prices to {self.price_file}")
        except Exception as e:
            print(f"Error saving prices: {e}")
    
    def _get_default_prices(self) -> Dict:
        """Default commodity prices (USD/kg)."""
        return {
            "metals": {
                "Ti": {"price": 7.50, "date": "2024-01-01", "source": "LME"},
                "Al": {"price": 2.20, "date": "2024-01-01", "source": "LME"},
                "Zr": {"price": 35.00, "date": "2024-01-01", "source": "Market"},
                "Fe": {"price": 0.08, "date": "2024-01-01", "source": "LME"},
                "Ni": {"price": 16.50, "date": "2024-01-01", "source": "LME"},
                "Cr": {"price": 8.00, "date": "2024-01-01", "source": "Market"},
                "Mo": {"price": 42.00, "date": "2024-01-01", "source": "LME"},
                "W": {"price": 34.00, "date": "2024-01-01", "source": "Market"},
                "V": {"price": 28.00, "date": "2024-01-01", "source": "Market"},
                "Nb": {"price": 45.00, "date": "2024-01-01", "source": "Market"},
                "Ta": {"price": 280.00, "date": "2024-01-01", "source": "Market"},
                "Mg": {"price": 3.50, "date": "2024-01-01", "source": "LME"},
                "Ca": {"price": 2.00, "date": "2024-01-01", "source": "Market"},
                "Si": {"price": 1.80, "date": "2024-01-01", "source": "Market"},
                "Cu": {"price": 8.50, "date": "2024-01-01", "source": "LME"},
                "Zn": {"price": 2.80, "date": "2024-01-01", "source": "LME"},
                "Pb": {"price": 2.20, "date": "2024-01-01", "source": "LME"},
                "Sn": {"price": 25.00, "date": "2024-01-01", "source": "LME"},
                "Li": {"price": 65.00, "date": "2024-01-01", "source": "Market"},
                "Na": {"price": 2.50, "date": "2024-01-01", "source": "Market"},
                "K": {"price": 15.00, "date": "2024-01-01", "source": "Market"},
                "Co": {"price": 55.00, "date": "2024-01-01", "source": "LME"},
                "Mn": {"price": 1.80, "date": "2024-01-01", "source": "LME"}
            },
            "energy": {
                "electricity": {"price": 0.07, "unit": "USD/kWh", "date": "2024-01-01"},
                "hydrogen": {"price": 5.00, "unit": "USD/kg", "date": "2024-01-01"},
                "natural_gas": {"price": 0.15, "unit": "USD/m3", "date": "2024-01-01"}
            },
            "oxides": {
                "TiO2": {"price": 2.50, "date": "2024-01-01", "source": "Market"},
                "Al2O3": {"price": 0.45, "date": "2024-01-01", "source": "Market"},
                "Fe2O3": {"price": 0.05, "date": "2024-01-01", "source": "Market"},
                "ZrO2": {"price": 8.50, "date": "2024-01-01", "source": "Market"},
                "MgO": {"price": 0.15, "date": "2024-01-01", "source": "Market"},
                "CaO": {"price": 0.08, "date": "2024-01-01", "source": "Market"},
                "Cr2O3": {"price": 1.20, "date": "2024-01-01", "source": "Market"},
                "MoO3": {"price": 12.00, "date": "2024-01-01", "source": "Market"},
                "WO3": {"price": 8.50, "date": "2024-01-01", "source": "Market"},
                "V2O5": {"price": 6.50, "date": "2024-01-01", "source": "Market"},
                "SiO2": {"price": 0.05, "date": "2024-01-01", "source": "Market"}
            },
            "nitrides": {
                "TiN": {"price": 45.00, "date": "2024-01-01", "source": "Market"},
                "AlN": {"price": 25.00, "date": "2024-01-01", "source": "Market"},
                "Si3N4": {"price": 15.00, "date": "2024-01-01", "source": "Market"}
            },
            "carbides": {
                "TiC": {"price": 35.00, "date": "2024-01-01", "source": "Market"},
                "SiC": {"price": 8.50, "date": "2024-01-01", "source": "Market"},
                "WC": {"price": 45.00, "date": "2024-01-01", "source": "Market"}
            }
        }
    
    def get_metal_price(self, metal_symbol: str) -> Optional[float]:
        """Get current price for metal (USD/kg)."""
        return self.prices.get('metals', {}).get(metal_symbol, {}).get('price')
    
    def get_oxide_price(self, oxide_name: str) -> Optional[float]:
        """Get current price for oxide (USD/kg)."""
        return self.prices.get('oxides', {}).get(oxide_name, {}).get('price')
    
    def get_nitride_price(self, nitride_name: str) -> Optional[float]:
        """Get current price for nitride (USD/kg)."""
        return self.prices.get('nitrides', {}).get(nitride_name, {}).get('price')
    
    def get_carbide_price(self, carbide_name: str) -> Optional[float]:
        """Get current price for carbide (USD/kg)."""
        return self.prices.get('carbides', {}).get(carbide_name, {}).get('price')
    
    def get_compound_price(self, compound_name: str, category: str) -> Optional[float]:
        """Get price for any compound by category."""
        if category == 'oxides':
            return self.get_oxide_price(compound_name)
        elif category == 'nitrides':
            return self.get_nitride_price(compound_name)
        elif category == 'carbides':
            return self.get_carbide_price(compound_name)
        else:
            return None
    
    def get_energy_price(self, energy_type: str) -> Optional[float]:
        """Get energy price (USD/unit)."""
        return self.prices.get('energy', {}).get(energy_type, {}).get('price')
    
    def calculate_reduction_value(self, compound_name: str, metal_symbol: str, 
                                 energy_kWh_per_kg: float, category: str = 'oxides') -> Dict:
        """Calculate economic value of reduction process.
        
        Args:
            compound_name: Name of the compound (e.g., 'TiO2')
            metal_symbol: Metal symbol (e.g., 'Ti')
            energy_kWh_per_kg: Energy consumption in kWh per kg of metal produced
            category: Compound category ('oxides', 'nitrides', 'carbides')
        
        Returns:
            Dictionary with economic analysis results
        """
        compound_price = self.get_compound_price(compound_name, category) or 0
        metal_price = self.get_metal_price(metal_symbol) or 0
        electricity_price = self.get_energy_price('electricity') or 0.07
        
        energy_cost = energy_kWh_per_kg * electricity_price
        gross_margin = metal_price - compound_price - energy_cost
        
        return {
            'compound_name': compound_name,
            'metal_symbol': metal_symbol,
            'compound_cost': compound_price,
            'metal_value': metal_price,
            'energy_cost': energy_cost,
            'gross_margin': gross_margin,
            'margin_percent': (gross_margin / metal_price * 100) if metal_price > 0 else 0,
            'energy_kWh_per_kg': energy_kWh_per_kg,
            'category': category
        }
    
    def estimate_energy_consumption(self, dg_eff_kJ_per_mol: float, metal_symbol: str, 
                                   category: str = 'oxides') -> float:
        """Estimate energy consumption based on thermodynamic data.
        
        Args:
            dg_eff_kJ_per_mol: Effective Gibbs free energy (kJ/mol)
            metal_symbol: Metal symbol
            category: Compound category
        
        Returns:
            Estimated energy consumption in kWh/kg metal
        """
        # Molecular weights (g/mol) - simplified lookup
        molecular_weights = {
            'Ti': 47.9, 'Al': 27.0, 'Zr': 91.2, 'Fe': 55.8, 'Ni': 58.7,
            'Cr': 52.0, 'Mo': 95.9, 'W': 183.8, 'V': 50.9, 'Nb': 92.9,
            'Ta': 180.9, 'Mg': 24.3, 'Ca': 40.1, 'Si': 28.1, 'Cu': 63.5,
            'Zn': 65.4, 'Pb': 207.2, 'Sn': 118.7, 'Li': 6.9, 'Na': 23.0,
            'K': 39.1, 'Co': 58.9, 'Mn': 54.9
        }
        
        metal_mw = molecular_weights.get(metal_symbol, 50.0)  # Default assumption
        
        # Convert from kJ/mol to kWh/kg
        # 1 kJ = 0.000278 kWh, 1 mol = MW grams
        energy_kWh_per_kg = abs(dg_eff_kJ_per_mol) * 0.000278 / (metal_mw / 1000)
        
        return energy_kWh_per_kg
    
    def update_from_api(self, api_source: str = 'manual'):
        """Update prices from API (placeholder for future implementation).
        
        Supported sources (future):
        - 'lme': London Metal Exchange
        - 'kitco': Kitco metals
        - 'manual': JSON file (current)
        """
        if api_source == 'manual':
            self.load_prices()
        else:
            raise NotImplementedError(
                f"API integration for {api_source} not yet implemented. "
                "Please update commodity_prices.json manually."
            )
    
    def get_price_summary(self) -> Dict:
        """Get summary of all available prices."""
        summary = {
            'metals_count': len(self.prices.get('metals', {})),
            'oxides_count': len(self.prices.get('oxides', {})),
            'nitrides_count': len(self.prices.get('nitrides', {})),
            'carbides_count': len(self.prices.get('carbides', {})),
            'energy_sources': list(self.prices.get('energy', {}).keys()),
            'last_updated': max([
                max([data.get('date', '') for data in category.values()])
                for category in self.prices.values()
                if isinstance(category, dict)
            ], default='Unknown')
        }
        return summary


def create_economics_table(economics_data: List[Dict]) -> str:
    """Create formatted economics analysis table."""
    if not economics_data:
        return "No economic data available."
    
    # Create HTML table instead of markdown for better rendering
    table_html = [
        "<div class='economics-table'>",
        "<h5>Economic Analysis</h5>",
        "<table class='table table-striped table-sm'>",
        "<thead class='table-dark'>",
        "<tr>",
        "<th>Material</th>",
        "<th>Metal</th>",
        "<th>Compound Cost</th>",
        "<th>Metal Value</th>",
        "<th>Energy Cost</th>",
        "<th>Gross Margin</th>",
        "<th>Margin %</th>",
        "</tr>",
        "</thead>",
        "<tbody>"
    ]
    
    for data in economics_data:
        table_html.extend([
            "<tr>",
            f"<td>{data['compound_name']}</td>",
            f"<td>{data['metal_symbol']}</td>",
            f"<td>${data['compound_cost']:.2f}</td>",
            f"<td>${data['metal_value']:.2f}</td>",
            f"<td>${data['energy_cost']:.2f}</td>",
            f"<td>${data['gross_margin']:.2f}</td>",
            f"<td>{data['margin_percent']:.1f}%</td>",
            "</tr>"
        ])
    
    table_html.extend([
        "</tbody>",
        "</table>",
        "<div class='mt-3'>",
        "<small class='text-muted'>",
        "<strong>Legend:</strong><br>",
        "• Compound Cost: Cost of starting material (USD/kg)<br>",
        "• Metal Value: Value of produced metal (USD/kg)<br>",
        "• Energy Cost: Electricity cost for reduction (USD/kg)<br>",
        "• Gross Margin: Net profit per kg metal (USD/kg)<br>",
        "• Margin %: Profit margin as percentage of metal value",
        "</small>",
        "</div>",
        "</div>"
    ])
    
    return "".join(table_html)


if __name__ == "__main__":
    # Test the price manager
    manager = CommodityPriceManager()
    
    print("Commodity Price Manager Test")
    print("=" * 40)
    
    # Test price retrieval
    ti_price = manager.get_metal_price('Ti')
    print(f"Titanium price: ${ti_price}/kg")
    
    # Test economic calculation
    economics = manager.calculate_reduction_value('TiO2', 'Ti', 2.5)
    print(f"\nTiO2 reduction economics:")
    print(f"Gross margin: ${economics['gross_margin']:.2f}/kg")
    print(f"Margin: {economics['margin_percent']:.1f}%")
    
    # Test price summary
    summary = manager.get_price_summary()
    print(f"\nPrice database summary:")
    print(f"Metals: {summary['metals_count']}")
    print(f"Oxides: {summary['oxides_count']}")
    print(f"Last updated: {summary['last_updated']}")
