import streamlit as st
import calendar
import time

with_logo = False

abbr = dict(enumerate(calendar.month_abbr))
abbr.pop(0)
if with_logo == True:
    logo_src="data_files/logo_01.jpg"
    #logo_ico=st.image(logo_src, width=32)
    st.logo(logo_src,size="large", link=None, icon_image=None)
    st.image(logo_src) #, caption="data_files/Logo_01.jpg")
st.title(body="File data test", text_alignment="center")
st.header(str(time.localtime().tm_mday) + "/" + abbr[time.localtime().tm_mon] + "/" + str(time.localtime().tm_year), divider=True)
st.subheader("Choose local data (to upload) or server data (git)", divider=True)

if st.button("Switch to Page 2"):
    st.switch_page("pages/test.py", query_params={"utm_source": "home.py"})