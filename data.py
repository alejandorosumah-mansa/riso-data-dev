import pandas as pd
import numpy as np
import json
import pandas as pd
import numpy as np
from unidecode import unidecode

def id_to_union(id):
    id_union_dict = {
        "SEN015001":['Union de Dagana A',
                    'Union de Debi-Tiguette',
                    'Union de Kassac Nord',
                    'Union de Kassac Sud',
                    'Union de Mboundoum',
                    'Union de Ndiaye',
                    'Union de Ngomene',
                    'Union de Pont-Gendarme',
                    'Union de Thiagar']
    }
    return id_union_dict[id]
def load_data(groupby_selection="REGION"):
   # Load the dataset
    agricultural_production_df = pd.read_excel("assets/EAA_2017_2022_T3_Superficie_Rendement_et_Production_agricoles.xlsx")

    # Data cleaning and preparation
    agricultural_production_df = agricultural_production_df.pivot_table(index=["Annee", "REGION", "Département", "Culture"], 
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
    return df,region_aggregated
def load_district_data():
   df = pd.read_csv("district_data.csv")
   return df

def load_categories():
   agricultural_production_df = pd.read_excel("assets/EAA_2017_2022_T3_Superficie_Rendement_et_Production_agricoles.xlsx")
   list_of_categories = {}
   for i in agricultural_production_df.columns:
      list_of_categories[i] = list(agricultural_production_df[i].unique())
   return list_of_categories
def load_regions_geojson():
   # Load GeoJSON
   with open('assets/senegal-with-regions_.geojson', 'r') as f:
      senegal_regions_geojson = json.load(f)
   for feature in senegal_regions_geojson['features']:
        feature['id'] = feature['properties']['name']  # Assuming 'name' is a unique identifier
   return senegal_regions_geojson,feature
def load_district_geojson():
   with open('assets/regions/district_senegal/district.geojson', 'r') as file:
    geojson_data = json.load(file)

   # Extract district data
   district_ids = [feature['properties']['adm2cd'] for feature in geojson_data['features']]
   district_names = [feature['properties']['adm2nm'] for feature in geojson_data['features']]

   # Create a DataFrame with unique values for each district
   data = pd.DataFrame({
      'District_ID': district_ids,
      'District_Name': district_names,
      'Value': list(range(1, len(district_ids) + 1))  # Unique value for each district
   })
   return data,geojson_data
def get_district_id(district_name_filter):
   data,geojson_data = load_district_geojson()
   district_name_filter = unidecode(district_name_filter)
   try:
      return data[data['District_Name'] == district_name_filter].District_ID.values[0]
   except:
      return "District not found"
def region_conversion(region, ActualNamesFirst=True):
   keys = ['DAKAR', 'DIOURBEL', 'FATICK', 'KAFFRINE', 'KAOLACK', 'KEDOUGOU', 'KOLDA', 'LOUGA', 'MATAM', 'SAINT-LOUIS', 'SEDHIOU', 'TAMBACOUNDA', 'THIES', 'ZIGUINCHOR']
   values = ['Dakar Region', 'Diourbel Region', 'Fatick Region', 'Kaffrine Region', 'Kaolack Region', 'Kedougou Region', 'Kolda Region', 'Louga Region', 'Matam Region', 'Saint-Louis Region', 'Sedhiou Region', 'Tambacounda Region', 'Thies Region', 'Ziguinchor Region']
   if ActualNamesFirst:
      region_dict = dict(zip(values, keys))
   else:
      region_dict = dict(zip(keys, values))
   region_to_return = region_dict[region]
   return region_to_return

def departments_given_region(region):
   regions_departments = {
    "Dakar": ["Dakar", "Guediawaye", "Pikine", "Rufisque"],
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
   return regions_departments[region]



