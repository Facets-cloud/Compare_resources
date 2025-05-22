import requests 
import json
import pandas as pd
import base64

# Configuration
CONTROL_PLANE_URL = ""
USERNAME = "@facets.cloud"
TOKEN = ""
credentials = base64.b64encode(f"{USERNAME}:{TOKEN}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

CLUSTERS = {
       "cluster_name": "cluster_id",
       "cluster_name": "cluster_id"
}

def fetch_cluster_resources_info(cluster_id):
    url = f"{CONTROL_PLANE_URL}/cc-ui/v1/dropdown/cluster/{cluster_id}/resources-info"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_resource_details(resource_name):
    # Extract project and environment from resource name
    # Assuming resource names follow a pattern like: project-name-env-name-resource
    parts = resource_name.split('-')
    if len(parts) >= 2:
        project_name = parts[0]
        env_name = parts[1]
        
        # Fetch additional details using the resource status API
        try:
            url = f"{CONTROL_PLANE_URL}/cc-ui/v1/resources/{project_name}/{env_name}/status"
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch details for {resource_name}: {str(e)}")
    
    return None

def create_status_dataframe(cluster_resources_data):
    # Create a set of all unique resource type/name combinations
    all_resources = set()
    for cluster_data in cluster_resources_data.values():
        for resource in cluster_data:
            all_resources.add((resource['resourceName'], resource['resourceType']))
    
    # Create the base dataframe
    rows = []
    for resource_name, resource_type in sorted(all_resources):
        # Fetch resource details
        details = fetch_resource_details(resource_name)
        
        row = {
            'resource_name': resource_name,
            'resource_type': resource_type,
            'project_name': details.get('projectName', 'Unknown') if details else 'Unknown',
            'environment': details.get('environmentName', 'Unknown') if details else 'Unknown'
        }
        
        # Add status for each cluster
        for cluster_name, cluster_data in cluster_resources_data.items():
            # Find matching resource for this cluster
            resource = next(
                (r for r in cluster_data 
                 if r['resourceName'] == resource_name and r['resourceType'] == resource_type),
                None
            )
            # Store the disabled status
            row[cluster_name] = "Disabled" if resource and resource.get('info', {}).get('disabled', False) else "Enabled"
        rows.append(row)
    
    return pd.DataFrame(rows)

# Main logic
print("Fetching resource statuses...")
cluster_resources_data = {}

for cluster_name, cluster_id in CLUSTERS.items():
    print(f"→ Fetching for {cluster_name}")
    try:
        resources = fetch_cluster_resources_info(cluster_id)
        cluster_resources_data[cluster_name] = resources
        print(f"Found {len(resources)} resources")
    except Exception as e:
        print(f"Error fetching data for {cluster_name}: {str(e)}")
        cluster_resources_data[cluster_name] = []

print("\nCreating comparison dataframe...")
df = create_status_dataframe(cluster_resources_data)

# Output to Excel
excel_filename = "resource_status_comparison.xlsx"
df.to_excel(excel_filename, index=False)

print(f"\n✅ Comparison complete. Results saved in '{excel_filename}'.")
print(f"DataFrame shape: {df.shape}")
print(f"DataFrame columns: {df.columns.tolist()}") 
