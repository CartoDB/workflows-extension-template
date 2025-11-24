# User Defined Functions (UDFs)

Extensions can now include custom User Defined Functions (UDFs) alongside components. UDFs are reusable functions that can be called from SQL queries and other components within your workflows.

## Overview

UDFs in CARTO Workflows extensions support:
- **SQL Functions**: Direct SQL function definitions
- **Python Functions**: Python-based functions with automatic dependency management
- **Cross-Provider Compatibility**: Functions that work on both BigQuery and Snowflake
- **Integrated Testing**: UDFs are tested alongside components using the same framework

## Function Structure

Functions are organized in the `functions/` directory with the following structure:

```
functions/
├── my_sql_function/
│   ├── metadata.json
│   └── src/
│       └── definition.sql
└── my_python_function/
    ├── metadata.json
    └── src/
        └── definition.py
```

Each function requires:
1. **metadata.json**: Function signature and configuration
2. **src/definition.sql** or **src/definition.py**: Function implementation

> 💡 **Function Type Detection**
>
> The function type (SQL or Python) is automatically inferred from the definition file extension:
> - `.sql` files → SQL functions
> - `.py` files → Python functions

## Function Metadata

### Basic Structure

```json
{
    "name": "function_name",
    "title": "Human Readable Function Title",
    "description": "Brief description of what the function does",
    "version": "1.0.0",
    "signature": {
        "name": "FUNCTION_NAME",
        "parameters": [
            {
                "name": "param1",
                "type": "STRING",
                "description": "Description of parameter 1"
            },
            {
                "name": "param2", 
                "type": "FLOAT64",
                "description": "Description of parameter 2"
            }
        ],
        "returnType": "STRING",
        "description": "Description of return value"
    }
}
```

### Metadata Properties

- **name**: Unique identifier matching the folder name
- **title**: Display name for the function
- **description**: Brief explanation of functionality
- **version**: Semantic version number
- **signature**: Function signature definition
  - **name**: SQL function name (usually uppercase)
  - **parameters**: Array of parameter definitions
  - **returnType**: SQL data type of return value
  - **description**: Description of what the function returns

### Parameter Types

Support for standard SQL data types:
- **STRING**: Text values
- **INT64** / **INTEGER**: Integer numbers
- **FLOAT64** / **FLOAT**: Decimal numbers
- **BOOLEAN**: True/false values
- **GEOGRAPHY**: Spatial data types
- **JSON** / **VARIANT**: JSON objects (provider-specific)
- **ARRAY**: Array types (specify element type)

## SQL Functions

### Simple Example

**functions/format_coordinates/metadata.json**:
```json
{
    "name": "format_coordinates",
    "title": "Format Coordinates",
    "description": "Format latitude and longitude as a string",
    "version": "1.0.0",
    "signature": {
        "name": "FORMAT_COORDINATES",
        "parameters": [
            {
                "name": "lat",
                "type": "FLOAT64",
                "description": "Latitude coordinate"
            },
            {
                "name": "lng",
                "type": "FLOAT64", 
                "description": "Longitude coordinate"
            }
        ],
        "returnType": "STRING",
        "description": "Formatted coordinate string"
    }
}
```

**functions/format_coordinates/src/definition.sql**:
```sql
CREATE OR REPLACE FUNCTION `@@workflows_temp@@`.FORMAT_COORDINATES(lat FLOAT64, lng FLOAT64)
RETURNS STRING
LANGUAGE SQL
AS (
    CONCAT(CAST(lat AS STRING), ', ', CAST(lng AS STRING))
);
```

### Provider-Specific Considerations

The function definition will be automatically adapted for different providers:

- **BigQuery**: Uses backticks and specific SQL syntax
- **Snowflake**: Adapts to Snowflake's function syntax and data types

Use the `@@workflows_temp@@` placeholder which will be replaced with the appropriate destination during deployment.

## Python Functions

### PEP 723 Metadata

Python functions support [PEP 723](https://peps.python.org/pep-0723/) metadata for dependency management:

**functions/calculate_distance/src/definition.py**:
```python
#!/usr/bin/env python3
"""
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "numpy>=1.21.0",
# ]
# ///

Calculate distance between two geographic points using the Haversine formula.
"""

import math
import numpy as np

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r
```

**functions/calculate_distance/metadata.json**:
```json
{
    "name": "calculate_distance",
    "title": "Calculate Distance",
    "description": "Calculate distance between two geographic points using Haversine formula",
    "version": "1.0.0",
    "signature": {
        "name": "CALCULATE_DISTANCE",
        "parameters": [
            {
                "name": "lat1",
                "type": "FLOAT64",
                "description": "Latitude of first point"
            },
            {
                "name": "lon1",
                "type": "FLOAT64",
                "description": "Longitude of first point"
            },
            {
                "name": "lat2",
                "type": "FLOAT64",
                "description": "Latitude of second point"
            },
            {
                "name": "lon2",
                "type": "FLOAT64",
                "description": "Longitude of second point"
            }
        ],
        "returnType": "FLOAT64",
        "description": "Distance in kilometers"
    }
}
```

### Python Function Requirements

1. **Function Name**: Must match the function name in metadata
2. **Type Hints**: Recommended for better documentation and validation
3. **Docstring**: Required for function documentation
4. **PEP 723 Block**: Include dependencies in the script metadata
5. **Return Type**: Must match the declared return type in metadata

## Adding Functions to Extensions

### 1. Register Functions in Extension Metadata

Update your extension's `metadata.json` to include the functions:

```json
{
    "name": "my_extension",
    "title": "My Extension",
    "description": "Extension with components and functions",
    "version": "1.0.0",
    "provider": "bigquery",
    "components": [
        "my_component"
    ],
    "functions": [
        "format_coordinates",
        "calculate_distance"
    ]
}
```

### 2. Function Discovery

Functions are automatically discovered from the `functions/` directory. The extension tool will:

1. Scan the `functions/` directory for subdirectories
2. Load `metadata.json` from each subdirectory
3. Validate function definitions
4. Generate provider-specific SQL code