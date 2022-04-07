import numpy as np
import pandas as pd


# Path
home_path = 'D:\\OneDrive\\Data Science\\Data\\CO2\\'


# GHG emissions file reading
df_emissions_tidy = pd.read_csv(
    (home_path + 'historical_emissions_climatewatchdata_tidy.csv'),
    encoding='utf-8',
    sep=';'
    )


# Population historical file reading
df_population = pd.read_csv(
    (home_path + 'historical_population_worldbank_tidy.csv'),
    encoding='utf-8',
    sep=';'
    )


# Dataframes fusion
df_emissions_tidy = df_emissions_tidy.merge(
    df_population[['Country Name', 'Year', 'Population']],
    how='left',
    left_on=['Country', 'Year'],
    right_on=['Country Name', 'Year']
    ).drop(['Country Name'], axis=1)

df_emissions_tidy['Per_capita_emissions'] = (1e+6)*df_emissions_tidy['Emissions'] / df_emissions_tidy['Population']
df_emissions_tidy['Per_capita_emissions'] = df_emissions_tidy['Per_capita_emissions'].round(2)


# CSV writing
df_emissions_tidy.to_csv(
    (home_path + 'historical_emissions_climatewatchdata_tidy.csv'),
    sep=';',
    index=None,
    encoding='utf-8'
    )
