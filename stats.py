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
	books = get_books_df(user_id)
	books['num_days'] = (books['read_at'] - books['started_at']).dt.days
	books['num_days'] = books['num_days'].replace(0, 1)
	books['speed'] = books['num_pages'] / books['num_days']
	return books



##########################
# STREAMLIT FUNCTIONS #
##########################

st.title("Goodreads Stats")

user_id = st.text_input("Goodreads User ID", USER_ID)

books = load_data(user_id)

if st.checkbox('Show Data'):   
	books

chart_data = books.sort_values('speed', ascending=False, na_position='last')

st.subheader("The most engaging books")

st.vega_lite_chart(chart_data[:10], {
	"width": "container",
	"height": 400,
	"mark": {"type": "bar", "cornerRadiusEnd": 4},
	"encoding": {
		"y": {"field": "title", "type": "nominal", "title": "Book Title", "sort": "-x"},
		"x": {"field": "speed", "type": "quantitative", "title": "Pages per day"}
	},
	}, use_container_width=True)