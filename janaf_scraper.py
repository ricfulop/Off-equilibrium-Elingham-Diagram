#!/usr/bin/env python3
"""
JANAF Database Scraper
Extracts thermodynamic data from NIST JANAF Thermochemical Tables
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import re
import pickle
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JANAFScraper:
    """Scraper for NIST JANAF Thermochemical Tables"""
    
    def __init__(self, base_url: str = "https://janaf.nist.gov/tables/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.compounds_data = {}
        
    def get_element_compounds(self, element: str) -> List[Dict]:
        """Get list of compounds for a given element"""
        try:
            url = f"{self.base_url}{element}-index.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Could not access {element} index: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main table with compound data
            table = soup.find('table')
            if not table:
                logger.warning(f"No table found for {element}")
                return []
            
            compounds = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:  # Expect at least 6 columns
                    try:
                        cas_number = cells[0].get_text(strip=True)
                        formula = cells[1].get_text(strip=True)
                        name = cells[2].get_text(strip=True)
                        state = cells[3].get_text(strip=True)
                        
                        # Find the view link in the JANAF Table column
                        view_link = cells[4].find('a', href=True)
                        if view_link and view_link.get_text(strip=True) == 'view':
                            href = view_link.get('href', '')
                            
                            compounds.append({
                                'cas_number': cas_number,
                                'formula': formula,
                                'name': name,
                                'state': state,
                                'url': href,
                                'element': element
                            })
                    except (IndexError, AttributeError) as e:
                        logger.debug(f"Could not parse row: {e}")
                        continue
                    
            logger.info(f"Found {len(compounds)} compounds for {element}")
            return compounds
            
        except Exception as e:
            logger.error(f"Error getting compounds for {element}: {e}")
            return []
    
    def extract_compound_data(self, compound_info: Dict) -> Optional[Dict]:
        """Extract thermodynamic data for a specific compound"""
        try:
            url = f"{self.base_url}{compound_info['url']}"
            print(f"Extracting data for {compound_info['name']} from {url}")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Could not access {compound_info['url']}: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for thermodynamic data table
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this looks like a thermodynamic data table
                headers = table.find_all('th')
                if headers:
                    header_text = ' '.join([h.get_text().strip() for h in headers])
                    if any(keyword in header_text.lower() for keyword in ['t(k)', 'cp°', 's°', 'g°', 'h°', 'fh°', 'fg°']):
                        print(f"Found thermodynamic table for {compound_info['name']}")
                        
                        # Extract data rows
                        rows = table.find_all('tr')[1:]  # Skip header row
                        data = []
                        
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 7:  # Expect at least 7 columns
                                row_data = []
                                for cell in cells:
                                    text = cell.get_text().strip()
                                    # Try to convert to float, keep as string if not possible
                                    try:
                                        if text and text != '-':
                                            row_data.append(float(text))
                                        else:
                                            row_data.append(None)
                                    except ValueError:
                                        row_data.append(text)
                                
                                if len(row_data) >= 7:
                                    data.append(row_data)
                        
                        if data:
                            print(f"Extracted {len(data)} data points for {compound_info['name']}")
                            return {
                                'compound': compound_info,
                                'data': data,
                                'headers': [h.get_text().strip() for h in headers]
                            }
            
            print(f"No thermodynamic data found for {compound_info['name']}")
            return None
            
        except Exception as e:
            print(f"Error extracting data for {compound_info['name']}: {e}")
            return None
    
    def _parse_thermodynamic_data(self, data_lines: List[str]) -> List[Dict]:
        """Parse thermodynamic data lines into structured format"""
        parsed_data = []
        
        for line in data_lines:
            # Split by whitespace and clean up
            parts = re.split(r'\s+', line.strip())
            
            if len(parts) >= 7:  # Expect at least 7 columns
                try:
                    data_point = {
                        'T_K': float(parts[0]),
                        'Cp_J_per_molK': float(parts[1]) if parts[1] != '.' else np.nan,
                        'S_J_per_molK': float(parts[2]) if parts[2] != '.' else np.nan,
                        'minus_G_minus_Htr_over_T_J_per_molK': float(parts[3]) if parts[3] != '.' and parts[3] != 'INFINITE' else np.nan,
                        'H_minus_Htr_kJ_per_mol': float(parts[4]) if parts[4] != '.' else np.nan,
                        'delta_f_H_kJ_per_mol': float(parts[5]) if parts[5] != '.' else np.nan,
                        'delta_f_G_kJ_per_mol': float(parts[6]) if parts[6] != '.' else np.nan,
                        'log10_Kf': float(parts[7]) if len(parts) > 7 and parts[7] != '.' else np.nan
                    }
                    parsed_data.append(data_point)
                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not parse line: {line} - {e}")
                    continue
                    
        return parsed_data
    
    def scrape_all_compounds(self, elements: List[str] = None) -> Dict:
        """Scrape thermodynamic data for all compounds"""
        if elements is None:
            elements = ['Ti', 'C', 'N', 'Al', 'Si', 'Zr', 'Nb', 'Ta', 'Mo', 'W', 'V', 'Hf']
        
        logger.info(f"Starting scrape for elements: {elements}")
        
        all_compounds = {}
        successful_elements = 0
        failed_elements = []
        
        for i, element in enumerate(elements, 1):
            logger.info(f"Processing element {i}/{len(elements)}: {element}")
            
            try:
                # Get compounds for this element
                compounds = self.get_element_compounds(element)
                
                if not compounds:
                    logger.warning(f"No compounds found for {element}")
                    failed_elements.append(element)
                    continue
                
                element_data = []
                for j, compound in enumerate(compounds, 1):
                    logger.info(f"  Extracting data for {j}/{len(compounds)}: {compound['name']}")
                    
                    compound_data = self.extract_compound_data(compound)
                    if compound_data and compound_data.get('data'):
                        element_data.append(compound_data)
                    
                    # Be respectful to the server
                    time.sleep(0.5)
                
                all_compounds[element] = element_data
                successful_elements += 1
                logger.info(f"Completed {element}: {len(element_data)} compounds with data")
                
            except Exception as e:
                logger.error(f"Error processing element {element}: {e}")
                failed_elements.append(element)
                continue
        
        logger.info(f"Scraping complete: {successful_elements}/{len(elements)} elements successful")
        if failed_elements:
            logger.warning(f"Failed elements: {failed_elements}")
        
        return all_compounds
    
    def save_data(self, data: Dict, filename: str = "janaf_full_database.pkl"):
        """Save scraped data to pickle file"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def load_data(self, filename: str = "janaf_full_database.pkl") -> Dict:
        """Load scraped data from pickle file"""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"Data loaded from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {}

def main():
    """Main function to run the scraper"""
    scraper = JANAFScraper()
    
    # All available elements in JANAF database
    all_elements = [
        'Ti', 'C', 'N', 'O', 'H', 'Al', 'Si', 'Fe', 'Ni', 'Cr', 'Mo', 'W', 
        'V', 'Nb', 'Ta', 'Zr', 'Hf', 'B', 'P', 'S', 'F', 'Cl', 'Br', 'I',
        'Li', 'Na', 'K', 'Mg', 'Ca', 'Sr', 'Ba', 'Be', 'Cu', 'Zn', 'Hg', 'Pb',
        'Co', 'Mn'
    ]
    
    logger.info("Starting FULL JANAF data extraction...")
    logger.info(f"Processing {len(all_elements)} elements: {all_elements}")
    
    data = scraper.scrape_all_compounds(all_elements)
    
    # Save the data
    scraper.save_data(data, "janaf_full_database.pkl")
    
    # Print summary
    total_compounds = sum(len(compounds) for compounds in data.values())
    logger.info(f"Extraction complete! Total compounds: {total_compounds}")
    
    for element, compounds in data.items():
        logger.info(f"{element}: {len(compounds)} compounds")
    
    # Calculate coverage
    logger.info(f"Coverage: {len(data)}/{len(all_elements)} elements = {len(data)/len(all_elements)*100:.1f}%")

if __name__ == "__main__":
    main()
