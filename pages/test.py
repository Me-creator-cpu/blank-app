import streamlit as st

btn = st.multiselect(
    "Some text", [2, 4, 6, 8, 10], format_func=lambda x: "option " + str(x)
)

btn