from datetime import datetime as dt
import sys
import calendar
import streamlit as st 
import pandas as pd
import numpy as np
import json

from books import get_books_df, get_books

USER_ID = "37542399-daniel-carlander"

@st.cache
def load_data(user_id=USER_ID):
	try:
		books = get_books_df(user_id)
	except:
		books = get_books_df(USER_ID)
	# books = books[~books['started_at'].isin([pd.NaT])]
	books['num_days'] = (books['read_at'] - books['started_at']).dt.days
	books['num_days'] = books['num_days'].replace(0, 1)
	books['speed'] = books['num_pages'] / books['num_days']
	return books



#######################
# STREAMLIT FUNCTIONS #
#######################

st.title("Goodreads Stats")



user_id = st.sidebar.text_input("Goodreads User ID", USER_ID)

books = load_data(user_id)

if st.checkbox('Show Data'):   
	books

###############
# Per Year #
###############

st.subheader(f"Pages per year")
st.markdown(f"Number of pages read per year")

pages_per_year = books.groupby(books['read_at'].dt.year)['num_pages'].sum()

st.vega_lite_chart(pages_per_year.reset_index(), {
	"width": "container",
	"mark": {
		"type": "line",
		"interpolate": "monotone"
	},
	"encoding": {
		"x": {"type": "quantitative", "field": "read_at", 'title' : 'Year'},
		"y": {"type": "quantitative", "field": "num_pages", 'title' : 'Number of Pages'}
	},
	
	}, use_container_width=True)

#################
# MOST ENGAGING #
#################

n_results = int(st.sidebar.slider("Number of results per stat", 1, 20, 5))

st.subheader(f"Your {n_results} most engaging books")
st.markdown(f"Calculated by pages read per day.")

most_engaging = books.sort_values('speed', ascending=False, na_position='last')[:n_results]

st.vega_lite_chart(most_engaging, {
	"width": "container",
	"mark": {"type": "bar", "cornerRadiusEnd": 4},
	"encoding": {
		"y": {"field": "title", "type": "nominal", "title": "Book Title", "sort": "-x"},
		"x": {"field": "speed", "type": "quantitative", "title": "Pages per day"}
	},
	}, use_container_width=True)

###############
# FAVOURITES #
###############

st.subheader(f"Your {n_results} favourite books")
st.markdown(f"Sorted by rating and speed of reading.")

favourite_books = books.sort_values(['rating', 'speed'], ascending=False, na_position='last')[:n_results]
favourite_books = favourite_books[['title', 'rating']]

table = '| Title | Rating |\n'
table += '| ----- | ------ |\n'

for index, row in favourite_books.iterrows():
	table +='|' + row['title'] + ' | ' + str(row['rating']) + ' |\n'

st.markdown(table)



