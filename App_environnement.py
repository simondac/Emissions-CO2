# Todo
# Relative change from 1990
# Heatmap avec pour chaque pays un carré par année avec une couleur en fonction du niveau d'émissions
# heatmap avec tous les pays pour une année donnée (carré + grand et/ou plus foncé pour les plus émetteurs), choix de l'année avec 
    # un curseur
# Replace source file by emissions per capita data to avoid merging population and emissions
# Add evolution of energetical mix per country


from matplotlib.pyplot import legend
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.models import Span, Label
from bokeh.palettes import Category20
from bokeh.util.hex import hexbin
from bokeh.transform import linear_cmap
import streamlit as st
import matplotlib.pyplot as plt
import geopandas as gpd
import pyproj
import plotly.express as px


# Path
home_path = 'D:\\OneDrive\\Data Science\\Data\\CO2\\'


# Files reading

# GHG emissions file reading
df_emissions = pd.read_csv(
    (home_path + 'historical_emissions_climatewatchdata_tidy.csv'),
    # index_col=[0],
    encoding='utf-8',
    sep=';'
    )


# Preparation of geopandas file
pyproj.datadir.set_data_dir('C:\\Users\\simon\\anaconda3\\envs\\geo_env\\Library\\share\\proj')
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
geo_df_emissions = gpd.GeoDataFrame(df_emissions)
# geo_df_emissions_2018 = geo_df_emissions[(geo_df_emissions['Year']==2018)]


# Countries filter
choice_country = list(df_emissions['Country'].unique())
countries = st.sidebar.multiselect('Countries', options=choice_country)
df_emissions = df_emissions[df_emissions['Country'].isin(countries)]


# Absolute/relative choice
absolute_relative = st.sidebar.selectbox('Values', options=['Absolute', 'Relative to 1990'])


# Total/Per capita choice
total_per_capita = st.sidebar.selectbox('Total or per capita emissions?', options=['Emissions', 'Per_capita_emissions'])


# Streamlit customisation
header_1 = st.container()
viz = st.container()
header_2 = st.container()
map = st.container()


# Title container
with header_1:
    st.title('GHG ' + total_per_capita + ' in ' + ", ".join(countries))


# Viz container
with viz:
    p = figure(
        title='Emissions from land use change – which can be positive or negative – are taken into account.\nCarbon dioxide, methane, nitrous oxide, and F-gases – are summed up and measured in tonnes of \ncarbon-dioxide equivalents (CO₂e),\nSource: Climatewatchdata (GHG emissions), World Bank (population)',
        x_axis_label='Year',
        y_axis_label=total_per_capita,
        )


    # Graph customisation
    p.y_range.start = 0  
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_dash = 'dotted'

    # Graph per country
    for index, country in enumerate(countries):

        r1 = p.line(
            x='Year',
            y=total_per_capita, 
            source=df_emissions[df_emissions['Country']==country],
            line_alpha=0.9,
            color=Category20[20][index],
            legend_label=country,
            line_width=2,
            hover_alpha=0.8,
            )

        
        r2 = p.circle(
            x='Year',
            y=total_per_capita, 
            source=df_emissions[df_emissions['Country']==country],
            fill_color="white",
            size=6
            )
        

        # Hover effect
        hover = HoverTool(renderers = [r1],
            tooltips = [
                ('Country','@Country'),
                ('Year', '@Year'),
                ('Emissions', '@{Emissions}{0.2f} tonnes'),
                ('Per capita emissions', '@{Per_capita_emissions}{0.2f} t/capita')
            ]
            )
        p.add_tools(hover)

    if total_per_capita=='Per_capita_emissions':
        # 2t/capita goal
        two_tones = Span(
            dimension = 'width',
            location = 2,
            line_dash='dashed',
            line_color = 'red',
            line_alpha=0.5
            )
        p.add_layout(two_tones)

        my_label = Label(x=1989, y=2.2, text='2t/capita goal', text_color='red')
        p.add_layout(my_label)

    st.bokeh_chart(p, use_container_width=True)


# Map title container
with header_2:
    st.title('Map')


# Map
with map:
    year = st.slider('Select year', 1990, 2018)

    fig = px.choropleth(
        geo_df_emissions[geo_df_emissions['Year']==year], 
        locations=geo_df_emissions[geo_df_emissions['Year']==year]["Country_code"],
        color="Per_capita_emissions",
        labels={'Per_capita_emissions':'Emissions per capita',
        'Country_code':'Code'},
        hover_name="Country",
        range_color=(0, 35),
        color_continuous_scale=px.colors.sequential.Reds,
        )
    st.plotly_chart(fig, use_container_width=True)