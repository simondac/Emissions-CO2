# Todo
# Relative change from 1990
# Heatmap avec pour chaque pays un carré par année avec une couleur en fonction du niveau d'émissions
# heatmap avec tous les pays pour une année donnée (carré + grand et/ou plus foncé pour les plus émetteurs), choix de l'année avec 
    # un curseur
# Replace source file by emissions per capita data to avoid merging population and emissions
# Add evolution of energy mix per country and compare it with emissions
# Add emissions up to 2020


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
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import geopandas as gpd
import pyproj
import plotly.express as px
import os




st.cache()

# Page configuration
st.set_page_config(
     page_title="Environment data",
    #  page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

# Path
path = os.path.dirname(__file__)


# Files reading

# Energy supply file reading
df_energy = pd.read_csv(
    (path + '\\Data\\historical_energy_iea_tidy.csv'),
    encoding='utf-8',
    sep=';'
    )


# GHG emissions file reading
df_emissions = pd.read_csv(
    (path + '\\Data\\historical_emissions_climatewatchdata_tidy.csv'),
    encoding='utf-8',
    sep=';'
    )


# Preparation of geopandas file
pyproj.datadir.set_data_dir('C:\\Users\\simon\\anaconda3\\envs\\geo_env\\Library\\share\\proj')
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
geo_df_emissions = gpd.GeoDataFrame(df_emissions)



# Sidebar
with st.sidebar:
    # Menu
    choose = option_menu("Navigation", ["GHG emissions", "Energy mix"],
                            icons=['house', 'camera fill'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "15px"}, 
        "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#02ab21"},
    }
    )

if choose=='GHG emissions':
    
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


        # 2t/capita goal
        if total_per_capita=='Per_capita_emissions':
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

    
else:
    # Streamlit customisation
    header_1 = st.container()
    viz = st.container()
    header_2 = st.container()

    # Countries filter
    choice_country = list(df_emissions['Country'].unique())
    countries = st.sidebar.multiselect('Countries', options=choice_country)
    df_emissions = df_emissions[df_emissions['Country'].isin(countries)]


    with viz:
        p = figure(
        title='Emissions from land use change – which can be positive or negative – are taken into account.\nCarbon dioxide, methane, nitrous oxide, and F-gases – are summed up and measured in tonnes of \ncarbon-dioxide equivalents (CO₂e),\nSource: Climatewatchdata (GHG emissions), World Bank (population)',
        x_axis_label='Year',
        y_axis_label='Energy supply',
        )


        # Graph customisation
        p.y_range.start = 0
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_dash = 'dotted'


        for index, country in enumerate(countries):
            # for index, i in enumerate(df_energy['Energy_supply'].unique()):
            r1 = p.varea_stack(
                x='Year',
                stackers=df_energy[df_energy['Country']==country],
                source=df_energy[df_energy['Country']==country]
                )

            
            # r2 = p.circle(
            #     x='Year',
            #     y='Energy_supply', 
            #     source=df_energy[df_energy['Country']==country],
            #     fill_color="white",
            #     size=6
            #     )
            

            # # Hover effect
            # hover = HoverTool(renderers = [r1],
            #     tooltips = [
            #         ('Country','@Country'),
            #         ('Year', '@Year'),
            #         ('Emissions', '@{Emissions}{0.2f} tonnes'),
            #         ('Per capita emissions', '@{Per_capita_emissions}{0.2f} t/capita')
            #     ]
            #     )
            # p.add_tools(hover)
            
            st.bokeh_chart(p, use_container_width=True)
