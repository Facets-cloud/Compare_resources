# Facets Cloud Resource Analyzer

A Python-based tool for analyzing resources across Facets Cloud clusters. This tool generates detailed Excel reports about resource distribution, types, and inheritance patterns in your clusters.

## Features

### Resource Type Analysis
- Comprehensive analysis of multiple resource types:
  - Normal resources
  - Provided resources
  - Base resources
  - Inherited resources
  - Substack resources

### Report Generation
- Generates formatted Excel reports with:
  - Resource counts by type
  - Environment grouping
  - Enabled/disabled status
  - Resource inheritance tracking
  - Auto-filtered columns
  - Professional formatting with headers and borders
  - Dynamic column generation based on resource types present
  - Environment-based grouping with clear visual separation
  - Detailed resource type detection using metadata, labels, and annotations

### Automatic Discovery
- Automatic cluster discovery across multiple API endpoints
- Dynamic column handling for Base and Substack resources
- Support for all Facets Cloud customers

## Prerequisites

- Python 3.6 or higher
- Access to Facets Cloud Control Plane
- Valid authentication credentials
- Required Python packages:
  ```
  requests>=2.25.1
  pandas>=1.2.0
  openpyxl>=3.0.7
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-analysis
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface
Run the script using the following command:
```bash
python3 general_resource_comparison.py --url <control-plane-url> --username <username> --token <token>
```

### Arguments
- `--url`: Your Facets Cloud Control Plane URL (e.g., https://customer-cp.console.facets.cloud)
- `--username`: Your Facets Cloud username
- `--token`: Your authentication token

### Example
```bash
python3 general_resource_comparison.py \
  --url https://customer-cp.console.facets.cloud \
  --username user@facets.cloud \
  --token abc123def456
```

## Output Format

### File Naming
The script generates an Excel file with the following format:
```
<customer>_resource_analysis_<timestamp>.xlsx
```
Example: `customer_resource_analysis_20240221_123456.xlsx`

### Excel Report Structure
The generated Excel report includes:

#### Column Descriptions
- **Customer**: Name of the customer
- **Environment**: Cluster environment name
- **Total number of Resources**: Total count (shown once per environment)
- **Resources Type**: Type of resource (application, service, etc.)
- **Nor_of Resources**: Total number of this resource type
- **Enabled_Resources**: Number of enabled resources
- **Normal_Resources**: Count of normal resources
- **Provided_Resources**: Count of provided resources
- **Inherited_Resources**: Count of resources inherited from base
- **Base_Resources**: Count of base resources (if present)
- **Substack_Resources**: Count of substack resources (if present)

#### Formatting Features
- Blue header styling
- Auto-filtered columns
- Auto-adjusted column widths
- Clear environment grouping with spacing
- Border formatting for all cells
- Centered headers and left-aligned data
- Empty rows between clusters for readability

## Resource Type Detection

The tool identifies different resource types based on various indicators:

### Detection Logic

#### Base Resources
Identified by:
- `resource.facets.cloud/type: base`
- `type: base`
- Base flags in resource info

#### Substack Resources
Identified by:
- `resource.facets.cloud/type: substack`
- `type: substack`
- Substack flags in resource info

#### Inherited Resources
Identified by:
- `inheritFromBase: true` in resource info

#### Provided Resources
Identified by:
- `resource.facets.cloud/type: provided`
- `type: provided`
- Provided flags in resource info

## Error Handling

The script includes robust error handling for common scenarios:

- API connection issues
- Missing resources
- Invalid configurations
- Authentication failures
- Network connectivity issues
- Missing or inaccessible clusters

If any errors occur, the script will:
1. Display meaningful error messages
2. Continue processing where possible
3. Exit gracefully if critical errors occur

## Troubleshooting

1. If no clusters are found:
   - Verify your Control Plane URL
   - Check your credentials
   - Ensure you have proper permissions

2. If the script fails to connect:
   - Check your internet connection
   - Verify the Control Plane URL is accessible
   - Ensure your token is valid and not expired

3. For authentication errors:
   - Verify your username format
   - Check if your token is still valid
   - Ensure you have the necessary permissions

