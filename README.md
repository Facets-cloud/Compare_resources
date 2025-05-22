# Facets Cloud Resource Analyzer

A Python-based tool for analyzing resources across Facets Cloud clusters. This tool generates detailed Excel reports about resource distribution, types, and inheritance patterns in your clusters.

## Features

- Analyzes multiple resource types:
  - Normal resources
  - Provided resources
  - Base resources
  - Inherited resources
  - Substack resources
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

## Prerequisites

- Python 3.6 or higher
- Access to Facets Cloud Control Plane
- Valid authentication credentials

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

## Configuration

Edit the configuration section in `resource_analysis.py` to set your environment details:

```python
config = {
    'control_plane_url': "https://your-cp.console.facets.cloud",
    'username': "your.username@facets.cloud",
    'token': "your-token",
    'customer_name': "CustomerName",
    'clusters': {
        "cluster-name": ("cluster-id", "display-name"),
        # Add more clusters as needed
    }
}
```

## Usage

1. Configure your credentials and cluster information in the script
2. Run the analysis:
```bash
python resource_analysis.py
```

The script will:
1. Connect to each configured cluster
2. Analyze all resources
3. Generate an Excel report named `<customer_name>_resource_analysis.xlsx`

## Output Format

The generated Excel file includes:
- Customer name
- Environment details
- Total resource counts
- Resource type breakdowns
- Resource status (enabled/disabled)
- Resource categorization (normal/provided/base/inherited/substack)

### Column Descriptions

- `Customer`: Name of the customer
- `Environment`: Cluster environment name
- `Total number of Resources`: Total count (shown once per environment)
- `Resources Type`: Type of resource (application, service, etc.)
- `Nor_of Resources`: Total number of this resource type
- `Enabled_Resources`: Number of enabled resources
- `Normal_Resources`: Count of normal resources
- `Provided_Resources`: Count of provided resources
- `Inherited_Resources`: Count of resources inherited from base
- `Base_Resources`: Count of base resources (if present)
- `Substack_Resources`: Count of substack resources (if present)

## Resource Type Detection

The tool identifies different resource types based on:
- Metadata labels
- Resource annotations
- Resource info properties
- Inheritance flags

### Detection Logic

- **Base Resources**: Identified by:
  - `resource.facets.cloud/type: base`
  - `type: base`
  - Base flags in resource info

- **Substack Resources**: Identified by:
  - `resource.facets.cloud/type: substack`
  - `type: substack`
  - Substack flags in resource info

- **Inherited Resources**: Identified by:
  - `inheritFromBase: true` in resource info

- **Provided Resources**: Identified by:
  - `resource.facets.cloud/type: provided`
  - `type: provided`
  - Provided flags in resource info

## Excel Formatting

The output Excel file includes:
- Blue header styling
- Auto-filtered columns
- Auto-adjusted column widths
- Clear environment grouping with spacing
- Border formatting for all cells
- Centered headers and left-aligned data

## Error Handling

The tool includes error handling for:
- API connection issues
- Missing resources
- Invalid configurations
- Authentication failures

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Specify your license here]
