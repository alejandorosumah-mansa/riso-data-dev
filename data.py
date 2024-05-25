import pandas as pd
import numpy as np
import json
from anyascii import anyascii
import boto3
from io import StringIO,BytesIO

class DataCollection:
    """
    A class to handle data collection from AWS S3 and perform various data operations.
    """
    def __init__(self):
        """
        Initialize a session using Amazon S3 and set up initial configurations.
        """
        # Initialize a session using Amazon S3
        self.client = boto3.client('s3', aws_access_key_id='AKIAZIUJP4LTNZC3MQ62', aws_secret_access_key='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')
        # Load bucket from S3
        self.bucket_name = 'riso-datalake'
        # Dictionary to store cached datasets
        self._datasets = {}
        
        # Additional attributes for various data mappings
        self.id_union_dict = {
            "SEN015001": [
                'Union de Dagana A',
                'Union de Debi-Tiguette',
                'Union de Kassac Nord',
                'Union de Kassac Sud',
                'Union de Mboundoum',
                'Union de Ndiaye',
                'Union de Ngomene',
                'Union de Pont-Gendarme',
                'Union de Thiagar'
            ]
        }
        self.keys = ['DAKAR', 'DIOURBEL', 'FATICK', 'KAFFRINE', 'KAOLACK', 'KEDOUGOU', 'KOLDA', 'LOUGA', 'MATAM', 'SAINT-LOUIS', 'SEDHIOU', 'TAMBACOUNDA', 'THIES', 'ZIGUINCHOR']
        self.values = ['Dakar Region', 'Diourbel Region', 'Fatick Region', 'Kaffrine Region', 'Kaolack Region', 'Kedougou Region', 'Kolda Region', 'Louga Region', 'Matam Region', 'Saint-Louis Region', 'Sedhiou Region', 'Tambacounda Region', 'Thies Region', 'Ziguinchor Region']
        self.regions_departments = {
            "Dakar": ["Dakar", "Guediawaye", "Pikine", "Rufget_district_idisque"],
            "Diourbel": ["Bambey", "Diourbel", "Mbacké"],
            "Fatick": ["Fatick", "Foundiougne", "Gossas"],
            "Kaffrine": ["Birkilane", "Kaffrine", "Koungheul", "Malem Hodar"],
            "Kaolack": ["Guinguineo", "Kaolack", "Nioro du Rip"],
            "Kedougou": ["Kedougou", "Salemata", "Saraya"],
            "Kolda": ["Kolda", "Medina Yoro Foula", "Velingara"],
            "Louga": ["Kebemer", "Linguere", "Louga"],
            "Matam": ["Kanel", "Matam", "Ranerou"],
            "Saint-Louis": ["Dagana", "Podor", "Saint-Louis"],
            "Sedhiou": ["Bounkiling", "Goudomp", "Sédhiou"],
            "Tambacounda": ["Bakel", "Goudiry", "Koumpentoum", "Tambacounda"],
            "Thies": ["Mbour", "Thies", "Tivaouane"],
            "Ziguinchor": ["Bignona", "Oussouye", "Ziguinchor"]
        }

    def _load_data_from_s3(self, file_key):
        """
        Download and load a dataset from S3.

        Args:
            file_key (str): The key of the file in the S3 bucket.

        Returns:
            DataFrame or dict: The loaded dataset.
        """
        # Download the file from S3
        s3_obj = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
        body = s3_obj['Body'].read()
        
        #print("BODY:: ", body)
        
        
        if file_key.endswith(".csv"):
            csv_string = body.decode('utf-8')
            return pd.read_csv(StringIO(csv_string))
        elif file_key.endswith(".xlsx"):
            return pd.read_excel(BytesIO(body))
        elif file_key.endswith(".geojson"):
            geojson_string = body.decode('utf-8')
            return json.loads(geojson_string)
        elif file_key.endswith(".mapbox_token"):
            # Decode the Mapbox token file
            token_string = body.decode('utf-8')
            return token_string.strip()  # Remove any leading/trailing whitespace or newline characters
        
        else:
            raise ValueError("Unsupported file format")

    def _get_dataset(self, file_key):
        """
        Retrieve a dataset, loading it from S3 if necessary.

        Args:
            file_key (str): The key of the file in the S3 bucket.

        Returns:
            DataFrame or dict: The requested dataset.
        """
        # Check if the dataset is already cached
        if file_key not in self._datasets:
            # Load the dataset and cache it
            self._datasets[file_key] = self._load_data_from_s3(file_key)
        
        return self._datasets[file_key]

    @property
    def complete_district_data(self):
        """Property to access the complete district data."""
        return self._get_dataset('district_data_complete.csv')

    @property
    def partial_district_data(self):
        """Property to access the partial district data."""
        return self._get_dataset('district_data.csv')

    @property
    def complete_FPA_data(self):
        """Property to access the complete FPA data."""
        return self._get_dataset('EAA_2017_2022_T3_Superficie_Rendement_et_Production_agricoles.xlsx')

    @property
    def partial_FPA_data(self):
        """Property to access the partial FPA data."""
        return self._get_dataset('FPA_Data.xlsx')

    @property
    def district_geojson_data(self):
        """Property to access the district GeoJSON data."""
        return self._get_dataset('district.geojson')

    @property
    def senegal_geojson_data(self):
        """Property to access the Senegal GeoJSON data."""
        return self._get_dataset('senegal-with-regions_.geojson')
    @property
    def union_geojson_data(self):
        """Property to access the Union-Level GeoJSON data."""
        return self._get_dataset('map_production.geojson')
    @property
    def mapbox_token(self):
        """Property to access the Mapbox Token."""
        return self._get_dataset(".mapbox_token")

    def load_data(self, groupby_selection="REGION"):
        """
        Load and prepare agricultural production data.

        Args:
            groupby_selection (str): The column to group by. Default is "REGION".

        Returns:
            tuple: A tuple containing the cleaned data and region-aggregated data.
        """
        # Load the dataset
        agricultural_production_df = self.complete_FPA_data

        # Data cleaning and preparation
        agricultural_production_df = agricultural_production_df.pivot_table(
            index=["Annee", "REGION", "Département", "Culture"], 
            columns='Indicateur', values='Valeur').reset_index()
        agricultural_production_df.fillna(0, inplace=True)
        agricultural_production_df["Date"] = agricultural_production_df["Annee"]
        agricultural_production_df["Quantity"] = agricultural_production_df["Culture"]
        agricultural_production_df["Country"] = "Senegal"
        agricultural_production_df["Production"] = agricultural_production_df["Production en tonne"]

        df = agricultural_production_df

        region_aggregated = agricultural_production_df.groupby(groupby_selection).agg({
            "Production en tonne": "sum",
            "Rendement kg/ha": "sum",
            "Superficie en ha": "sum"
        }).reset_index()

        return df, region_aggregated

    def load_categories(self):
        """
        Load unique categories from the agricultural production data.

        Returns:
            dict: A dictionary of categories with column names as keys and unique values as values.
        """
        agricultural_production_df = self.complete_FPA_data
        list_of_categories = {i: list(agricultural_production_df[i].unique()) for i in agricultural_production_df.columns}
        return list_of_categories

    def load_regions_geojson(self):
        """
        Load the GeoJSON data for Senegal regions.

        Returns:
            tuple: A tuple containing the GeoJSON data and the feature with the 'id' set to 'name' property.
        """
        senegal_regions_geojson = self.senegal_geojson_data
        #print("AAA: ", senegal_regions_geojson)
        for feature in senegal_regions_geojson['features']:
            feature['id'] = feature['properties']['name']  # Assuming 'name' is a unique identifier
        return senegal_regions_geojson, feature

    def load_district_geojson(self):
        """
        Load and prepare district GeoJSON data.

        Returns:
            tuple: A tuple containing a DataFrame with district information and the GeoJSON data.
        """
        geojson_data = self.district_geojson_data

        # Extract district data
        district_ids = [feature['properties']['adm2cd'] for feature in geojson_data['features']]
        district_names = [feature['properties']['adm2nm'] for feature in geojson_data['features']]

        # Create a DataFrame with unique values for each district
        data = pd.DataFrame({
            'District_ID': district_ids,
            'District_Name': district_names,
            'Value': list(range(1, len(district_ids) + 1))  # Unique value for each district
        })

        return data, geojson_data

    def get_district_id(self, district_name_filter):
        """
        Get the district ID for a given district name.

        Args:
            district_name_filter (str): The name of the district.

        Returns:
            str: The district ID or "District not found" if not found.
        """
        data, geojson_data = self.load_district_geojson()
        district_name_filter = anyascii(district_name_filter)
        try:
            return data[data['District_Name'] == district_name_filter].District_ID.values[0]
        except IndexError:
            return "District not found"

    def region_conversion(self, region, ActualNamesFirst=True):
        """
        Convert region names between keys and values.

        Args:
            region (str): The region name to convert.
            ActualNamesFirst (bool): Whether to use actual names as keys. Default is True.

        Returns:
            str: The converted region name.
        """
        if ActualNamesFirst:
            region_dict = dict(zip(self.values, self.keys))
        else:
            region_dict = dict(zip(self.keys, self.values))
        return region_dict.get(region, "Region not found")
