# /// script
# requires-python = "==3.11"
# dependencies = [
#   "numpy",
# ]
# ///

import numpy as np  # type: ignore[import]

def main(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 6371  # Earth radius in kilometers
    
    # Convert to radians using numpy
    coords = np.radians([lat1, lon1, lat2, lon2])
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = coords
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c