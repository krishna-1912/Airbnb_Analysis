import streamlit as st
import plotly.express as pl
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
from PIL import Image
from streamlit_option_menu import option_menu

warnings.filterwarnings('ignore')

st.set_page_config(page_title="AirBnb-Analysis", page_icon=":bar_chart:", layout="wide")
st.markdown("<h1 style='text-align: center; color: violet;'>AIRBNB - ANALYSIS</h1>", unsafe_allow_html=True)

# creating menu bar
SELECT = option_menu(
    menu_title = None,
    options = ["Home", "Explore Data"],
    icons = ["house", "bar-chart"],
    default_index = 1,
    orientation="horizontal",
    styles={"container": {"padding": "0!important", "background-color": "grey", "size": "cover", "width": "100"},
            "icon": {"color": "black", "font-size": "20px"},

            "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#6F36AD"},
            "nav-link-selected": {"background-color": "#6F36AD"}})

# home
if SELECT == "Home":
    st.header('Airbnb Analysis')

# Explore Data
if SELECT == "Explore Data":
    fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
    if fl is not None:
        filename = fl.name
        st.write(filename)
        data = pd.read_csv(filename, encoding="ISO-8859-1")
    else:
        os.chdir(r"C:/Users/pavee/OneDrive/Documents/GUVI/Airbnb_Analysis")
        data = pd.read_csv("Airbnb_Open_Data.csv", encoding="ISO-8859-1")

    st.sidebar.header("Select filters: ")

    # neighbourhood_group
    neighbourhood_group = st.sidebar.multiselect("Neighbourhood Group", data["neighbourhood_group"].unique())
    if not neighbourhood_group:
        data2 = data.copy()
    else:
        data2 = data[data["neighbourhood_group"].isin(neighbourhood_group)]

    # neighbourhood
    neighbourhood = st.sidebar.multiselect("Neighbourhood", data2["neighbourhood"].unique())
    if not neighbourhood:
        data3 = data2.copy()
    else:
        data3 = data2[data2["neighbourhood"].isin(neighbourhood)]

    # filter the data based on neighbourhood_group, neighbourhood
    if not neighbourhood_group and not neighbourhood:
        filtered_data = data
    elif not neighbourhood_group:
        filtered_data = data[data["neighbourhood"].isin(neighbourhood)]
    elif not neighbourhood:
        filtered_data = data[data["neighbourhood_group"].isin(neighbourhood_group)]
    elif neighbourhood_group:
        filtered_data = data3[data["neighbourhood_group"].isin(neighbourhood_group)]
    elif neighbourhood:
        filtered_data = data3[data["neighbourhood"].isin(neighbourhood)]
    elif neighbourhood_group and neighbourhood:
        filtered_data = data3[data["neighbourhood_group"].isin(neighbourhood_group) & data3["neighbourhood"].isin(neighbourhood)]
    else:
        filtered_data = data3[data3["neighbourhood_group"].isin(neighbourhood_group) & data3["neighbourhood"].isin(neighbourhood)]

    # room_type
    room_type_data = filtered_data.groupby(by=["room_type"], as_index=False)["price"].sum()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Room Type Data")
        fig = pl.bar(room_type_data, x="Room Type", y="Price",text=['${:,.2f}'.format(x) for x in room_type_data["price"]],
                    template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader("Neighbourhood Group Data")
        fig = pl.pie(filtered_data, values="price", names="neighbourhood_group", hole=0.5)
        fig.update_traces(text=filtered_data["neighbourhood_group"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Room Type wise Price"):
            st.write(room_type_data.style.background_gradient(cmap="Greens"))
            csv = room_type_data.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="room_type.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

    with cl2:
        with st.expander("Neighbourhood Grop wise Price"):
            neighbourhood_group = filtered_data.groupby(by="neighbourhood_group", as_index=False)["price"].sum()
            st.write(neighbourhood_group.style.background_gradient(cmap="Reds"))
            csv = neighbourhood_group.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="neighbourhood_group.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

    # scatter plot
    data1 = pl.scatter(filtered_data, x="neighbourhood_group", y="neighbourhood", color="room_type")
    data1['layout'].update(title="Room_type in the Neighbourhood and Neighbourhood_Group wise data using Scatter Plot.",
                            titlefont=dict(size=20), xaxis=dict(title="Neighbourhood_Group", titlefont=dict(size=20)),
                            yaxis=dict(title="Neighbourhood", titlefont=dict(size=20)))
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("Detailed Room Availability and Price View Data in the Neighbourhood"):
        st.write(filtered_data.iloc[:500, 1:20:2].style.background_gradient(cmap="Reds"))

    # Download orginal DataSet
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
    st.subheader(":point_right: Neighbourhood Group wise Room type and Minimum stay nights")
    with st.expander("Summary_Table"):
        data_sample = data[0:5][["neighbourhood_group", "neighbourhood", "reviews_per_month", "room_type", "price", "minimum_nights", "host_name"]]
        fig = ff.create_table(data_sample, colorscale="Cividis")
        st.plotly_chart(fig, use_container_width=True)

    # map function for room_type
    st.subheader("Airbnb Analysis in Map")
    data = data.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(data)