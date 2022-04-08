# Libraries
import numpy as np
import pandas as pd
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2, country_name_to_country_alpha3
from geopy.geocoders import Nominatim
import geopandas
import pyproj
import matplotlib.pyplot as plt
import os




# Path
path = os.path.dirname(__file__)


# Files reading

# GHG emissions file reading
df_emissions = pd.read_csv(
    path + '//Data//historical_emissions_climatewatchdata.csv',
    encoding='utf-8'
    )


# To tidy
df_emissions_tidy = pd.melt(
    df_emissions, 
    id_vars=['Country', 'Data source', 'Sector', 'Gas', 'Unit'], 
    var_name='Year', 
    value_name='Emissions'
    )


# Historical population file reading
df_population = pd.read_csv(
    path + '//Data//historical_population_worldbank.csv',
    encoding='utf-8',
    skiprows=4
    )


# To tidy
df_population_tidy = pd.melt(
    df_population, 
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
    var_name='Year', 
    value_name='Population'
    )


# Cleaning
df_population_tidy = df_population_tidy[df_population_tidy['Year']!='Unnamed: 65']


# CSV writing
df_population_tidy.to_csv(
    path + '//Data//historical_population_worldbank_tidy.csv',
    sep=';',
    index=None,
    encoding='utf-8'
    )


# Energy production reading
df_energy = pd.read_csv(
    path + '//Data//historical_energy_iea.csv',
    sep=';',
    skiprows=1
    )


# Only keep 'Total energy supply (PJ)'
df_energy = df_energy[df_energy['Flow']=='Total energy supply (PJ)']


# To tidy
df_energy = pd.melt(
    df_energy, 
    id_vars=['Country', 'Product', 'Flow'], 
    var_name='Year', 
    value_name='Energy_supply'
    ).drop('Flow', axis=1)

df_energy = df_energy.pivot(index=['Country', 'Year'], columns='Product')


# CSV writing
df_energy.to_csv(
    path + '//Data//historical_energy_iea_tidy.csv',
    sep=';',
    index=None,
    encoding='utf-8'
    )


# Per capita emissions calculation

# Changing countries/area names
df_population_tidy['Country Name'].replace(
    ['European Union', 'Russian Federation', 'United States', 'Congo, Dem. Rep.', 'South Sudan', 'Czech Republic'],
    ['European Union (27)', 'Russia', 'United States of America', 'Dem. Rep. Congo', 'S. Sudan', 'Czechia'],
    inplace=True
    )
df_emissions_tidy['Country'].replace(
    ['United States', 'Democratic Republic of the Congo', 'South Sudan', 'Czech Republic'],
    ['United States of America', 'Dem. Rep. Congo', 'S. Sudan', 'Czechia'],
    inplace=True
    )


# Dataframes fusion
df_emissions_tidy = df_emissions_tidy.merge(
    df_population_tidy[['Country Name', 'Year', 'Population']],
    how='left',
    left_on=['Country', 'Year'],
    right_on=['Country Name', 'Year']
    ).drop(
        ['Country Name'], 
        axis=1
        )


# Calculate per capita emissions
df_emissions_tidy['Per_capita_emissions'] = (1e+6)*df_emissions_tidy['Emissions'] / df_emissions_tidy['Population']
df_emissions_tidy['Per_capita_emissions'] = df_emissions_tidy['Per_capita_emissions'].round(2)


# Add country code
def get_country(value):
    try:
        cn_a3_code = country_name_to_country_alpha3(value)
    except:
        cn_a3_code = 'Unknown' 
    return cn_a3_code

df_emissions_tidy['Country_code'] = df_emissions_tidy['Country'].apply(lambda country: get_country(country))


# CSV writing
df_emissions_tidy.to_csv(
    path + '//Data//historical_emissions_climatewatchdata_tidy.csv',
    sep=';',
    index=None,
    encoding='utf-8'
    )