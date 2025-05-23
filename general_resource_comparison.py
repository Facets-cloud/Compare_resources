#!/usr/bin/env python3
import requests
import json
import pandas as pd
import base64
from datetime import datetime
import openpyxl
import argparse
import sys
import os

class ResourceAnalyzer:
    def __init__(self, control_plane_url, username, token):
        """
        Initialize the Resource Analyzer
        
        Args:
            control_plane_url (str): The control plane URL
            username (str): Username for authentication
            token (str): Authentication token
        """
        self.control_plane_url = control_plane_url.rstrip('/')
        self.customer_name = self._extract_customer_name(control_plane_url)
        
        # Setup authentication
        credentials = base64.b64encode(f"{username}:{token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }

    def _extract_customer_name(self, url):
        """Extract customer name from control plane URL"""
        return url.split('-cp')[0].split('/')[-1].capitalize()

    def get_cluster_mapping(self):
        """Get mapping of cluster names to their IDs"""
        clusters = {}
        
        # Try different API endpoints
        endpoints = [
            '/cc-ui/v1/stacks/running-base-clusters',
            '/cc-ui/v1/stacks/clusters',
            '/cc-ui/v1/stacks/getAllClusters'
        ]
        
        print("Fetching cluster information from multiple API endpoints...\n")
        
        for endpoint in endpoints:
            url = f"{self.control_plane_url}{endpoint}"
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, list):
                    for cluster in data:
                        cluster_id = cluster.get('id') or cluster.get('clusterId')
                        cluster_name = cluster.get('name') or cluster.get('clusterName')
                        if cluster_id and cluster_name:
                            clusters[cluster_name] = cluster_id
                            print(f"Found cluster: {cluster_name} (ID: {cluster_id})")
            except Exception as e:
                print(f"Warning: Could not fetch clusters from {endpoint}: {str(e)}\n")
        
        # Try fetching from individual stacks if needed
        if not clusters:
            print("Fetching clusters from individual stacks...")
            stacks = self.fetch_all_stacks()
            for stack in stacks:
                stack_clusters = self.fetch_stack_clusters(stack['name'])
                for cluster in stack_clusters:
                    cluster_name = cluster.get('name')
                    cluster_id = cluster.get('id')
                    if cluster_name and cluster_id:
                        clusters[cluster_name] = cluster_id
                        print(f"Found cluster from stack {stack['name']}: {cluster_name} (ID: {cluster_id})")
        
        print(f"\nTotal unique clusters found: {len(clusters)}")
        return clusters

    def fetch_all_stacks(self):
        """Fetch all available stacks"""
        url = f"{self.control_plane_url}/cc-ui/v1/stacks/"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch stacks: {str(e)}")
            return []

    def fetch_stack_clusters(self, stack_name):
        """Fetch clusters for a specific stack"""
        url = f"{self.control_plane_url}/cc-ui/v1/stacks/{stack_name}/clusters"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def fetch_cluster_resources_info(self, cluster_id):
        """Fetch detailed resources info for a cluster"""
        url = f"{self.control_plane_url}/cc-ui/v1/dropdown/cluster/{cluster_id}/resources-info"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching resources info: {str(e)}")
            return []

    def create_resource_summary(self, cluster_resources_data):
        """Create a summary of resources by type for each cluster"""
        summary_data = []
        has_base_resources = False
        has_substack_resources = False
        
        # Process each cluster
        for cluster_name, resources in cluster_resources_data.items():
            # Initialize counters for each resource type
            resource_types = {}
            total_resources = len(resources)
            
            # Count resources by type
            for resource in resources:
                resource_type = resource['resourceType'].lower()
                resource_info = resource.get('info', {})
                
                if resource_type not in resource_types:
                    resource_types[resource_type] = {
                        'total': 0,
                        'enabled': 0,
                        'normal': 0,
                        'provided': 0,
                        'base': 0,
                        'inherited': 0,
                        'substack': 0
                    }
                
                stats = resource_types[resource_type]
                stats['total'] += 1
                if not resource_info.get('disabled', False):
                    stats['enabled'] += 1
                
                # Update resource category counts
                if resource_info.get('isNormal', False):
                    stats['normal'] += 1
                elif resource_info.get('isProvided', False):
                    stats['provided'] += 1
                elif resource_info.get('isBase', False):
                    stats['base'] += 1
                    has_base_resources = True
                elif resource_info.get('isInherited', False):
                    stats['inherited'] += 1
                elif resource_info.get('isSubstack', False):
                    stats['substack'] += 1
                    has_substack_resources = True
            
            # Create rows for this cluster
            is_first_row_of_cluster = True
            for resource_type in sorted(resource_types.keys()):
                stats = resource_types[resource_type]
                row = {
                    'Customer': self.customer_name if is_first_row_of_cluster else '',
                    'Environment': cluster_name if is_first_row_of_cluster else '',
                    'Total number of Resources': total_resources if is_first_row_of_cluster else '',
                    'Resources Type': resource_type,
                    'Nor_of Resources': stats['total'],
                    'Enabled_Resources': stats['enabled'],
                    'Normal_Resources': stats['normal'],
                    'Provided_Resources': stats['provided'],
                    'Inherited_Resources': stats['inherited']
                }
                
                # Only add Base_Resources if we found base resources
                if has_base_resources:
                    row['Base_Resources'] = stats['base']
                
                # Only add Substack_Resources if we found substack resources
                if has_substack_resources:
                    row['Substack_Resources'] = stats['substack']
                
                summary_data.append(row)
                is_first_row_of_cluster = False
            
            # Add empty row between clusters
            empty_row = {
                'Customer': '',
                'Environment': '',
                'Total number of Resources': '',
                'Resources Type': '',
                'Nor_of Resources': '',
                'Enabled_Resources': '',
                'Normal_Resources': '',
                'Provided_Resources': '',
                'Inherited_Resources': ''
            }
            
            # Add dynamic columns to empty row if needed
            if has_base_resources:
                empty_row['Base_Resources'] = ''
            if has_substack_resources:
                empty_row['Substack_Resources'] = ''
                
            summary_data.append(empty_row)
        
        # Create DataFrame
        df = pd.DataFrame(summary_data)
        
        # Build column order dynamically
        column_order = [
            'Customer',
            'Environment',
            'Total number of Resources',
            'Resources Type',
            'Nor_of Resources',
            'Enabled_Resources',
            'Normal_Resources',
            'Provided_Resources',
            'Inherited_Resources'
        ]
        
        # Add optional columns if resources were found
        if has_base_resources:
            column_order.append('Base_Resources')
        if has_substack_resources:
            column_order.append('Substack_Resources')
        
        df = df[column_order]
        return df

    def save_formatted_excel(self, df, filename):
        """Save the DataFrame to Excel with proper formatting"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write main sheet
            df.to_excel(writer, index=False, sheet_name='Resource Summary')
            
            # Get the worksheet
            worksheet = writer.sheets['Resource Summary']
            
            # Define styles
            header_style = openpyxl.styles.NamedStyle(name='header_style')
            header_style.font = openpyxl.styles.Font(bold=True)
            header_style.fill = openpyxl.styles.PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid')
            header_style.border = openpyxl.styles.Border(bottom=openpyxl.styles.Side(style='thin'))
            
            # Apply header style
            for cell in worksheet[1]:
                cell.style = header_style
            
            # Auto-adjust column widths
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            # Add borders to all cells
            thin_border = openpyxl.styles.Border(
                left=openpyxl.styles.Side(style='thin'),
                right=openpyxl.styles.Side(style='thin'),
                top=openpyxl.styles.Side(style='thin'),
                bottom=openpyxl.styles.Side(style='thin')
            )
            
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.border = thin_border

    def analyze(self):
        """Run the complete analysis"""
        # Get clusters
        clusters = self.get_cluster_mapping()
        if not clusters:
            print("No clusters found. Exiting...")
            return
        
        print("\nStarting resource analysis...")
        cluster_resources_data = {}

        # Fetch data for each cluster
        for cluster_name, cluster_id in clusters.items():
            print(f"\nProcessing cluster: {cluster_name}")
            
            # Fetch resources
            print("→ Fetching resource information...")
            resources = self.fetch_cluster_resources_info(cluster_id)
            cluster_resources_data[cluster_name] = resources
            print(f"  Found {len(resources)} resources")

        # Create summary
        print("\nCreating resource summary...")
        df = self.create_resource_summary(cluster_resources_data)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"{self.customer_name.lower()}_resource_analysis_{timestamp}.xlsx"
        
        # Save to Excel
        print(f"\nFormatting and saving Excel file to {excel_filename}...")
        self.save_formatted_excel(df, excel_filename)

        print(f"\n✅ Analysis complete! Results saved in '{excel_filename}'")
        print(f"Total resource types analyzed: {len(df['Resources Type'].unique())}")
        print(f"Clusters included: {', '.join(sorted(clusters.keys()))}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Facets Cloud cluster resources')
    parser.add_argument('--url', required=True, help='Control plane URL (e.g., https://customer-cp.console.facets.cloud)')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--token', required=True, help='Authentication token')
    
    args = parser.parse_args()
    
    try:
        analyzer = ResourceAnalyzer(args.url, args.username, args.token)
        analyzer.analyze()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 