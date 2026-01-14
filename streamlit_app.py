import streamlit as st
import pandas as pd
import calendar
import sys
import time
from streamlit_javascript import st_javascript
from user_agents import parse

global uploaded_file
global is_session_pc
uploaded_file = None
is_session_pc = 'True'

def init():
   ua_string = str(st_javascript("""window.navigator.userAgent;"""))
   user_agent = parse(ua_string)
   st.session_state.is_session_pc = user_agent.is_pc
   #st.info(ua_string)
   #st.info(st.session_state.is_session_pc)
   is_session_pc = str(st.session_state.is_session_pc)
   #st.text("This is text\n[and more text](that's not a Markdown link).")

def read_csv(PATH: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(PATH)
    except:
        sys.exit('Unable to read the data, kindly verify the source and try again')
    #abbr = dict(enumerate(calendar.month_abbr))
    #abbr.pop(0)
    #df['Type'] = pd.Categorical(
    #    df['Type'], categories=list(abbr.values()), ordered=True)
    return df

def build_main_table(raw_data) -> pd.DataFrame:
  df = raw_data
  with st.expander("Raw data", expanded=True):
    # st.write(df)
    #st.data_editor(
    st.dataframe(
        df,
        column_config={
            "Name": st.column_config.TextColumn( "Name", pinned = True ),
            "Type": st.column_config.TextColumn( "Type", pinned = True ),
            "Skill": st.column_config.TextColumn( "Skill", pinned = True ),
            "Level": st.column_config.ProgressColumn(
                "Level",
                help="Palmon level",
                format="%f",
                min_value=100,
                max_value=250,
                color="#006699"
            ),
            "Step": st.column_config.NumberColumn(
                "Step",
                min_value=0,
                max_value=5,
                format="%d ⭐",
            ),
            "Achievement": st.column_config.NumberColumn(
                "Achievement",
                min_value=0,
                max_value=100,
                format="percent",
            ),
            "Cost to max": st.column_config.NumberColumn(
                "Cost to max",
                format="localized",
            ),
            "RankPower": st.column_config.NumberColumn(
                "RankPower",
                format="localized",
            ),
            "URL": st.column_config.ImageColumn(
                "Base preview",
                width="small"
            ),
            "URL Mutation": st.column_config.ImageColumn(
                "Mutation preview",
                width="small"
            )
        },
        hide_index=True,
        )   

def build_main_chart(raw_data):
  with st.expander("Chart", expanded=True):
    st.bar_chart(
       raw_data,
       x="Type",
       y="Level",
       horizontal=True
    )

def build_pivot_table(raw_data,val_value: str, val_index: str, val_columns: str):
  palmon_types_df = raw_data.pivot_table(values=val_value, index=val_index, columns=val_columns)
  with st.expander("Pivot table", expanded=True):
    st.dataframe(
       palmon_types_df,
       column_config={
          "Type": st.column_config.TextColumn( "Type", pinned = True ),
          "Attack": st.column_config.NumberColumn( "⚔ Attack", step=".01" ), #:crossed_swords:
          "Defend": st.column_config.NumberColumn( "🛡 Defend", step=".01" ), #:shield:
        },
       use_container_width=True,
       hide_index=None
    )

def pg_home(): 
    # init()
    st.header("File data test", divider="blue")
    st.subheader("Choose local data (to upload) or server data (git)", divider=True)

def pg_loc_0():
   uploaded_file = st.file_uploader("Choose a file")
   if uploaded_file is not None:
    df_loc = pd.read_csv(uploaded_file)
    st.session_state['data_loc'] = df_loc
    st.toast("File loaded", icon="🎉")
    st.balloons()

def pg_loc_1():
   if st.session_state['data_loc'] is not None:
      build_main_table(st.session_state['data_loc'])

def pg_loc_2():
   if st.session_state['data_loc'] is not None:
      build_main_chart(st.session_state['data_loc'])

def pg_loc_3():
   if st.session_state['data_loc'] is not None:
      build_pivot_table(st.session_state['data_loc'],'Level','Type','Skill')
         
def pg_srv_1():
   if st.session_state['data_srv'] is not None:
      build_main_table(st.session_state['data_srv'])

def pg_srv_2():
   if st.session_state['data_srv'] is not None:
      build_main_chart(st.session_state['data_srv'])
   
def pg_srv_3():
   if st.session_state['data_srv'] is not None:
      build_pivot_table(st.session_state['data_srv'],'Level','Type','Skill')

# st.title("🎈 CSV file app")
# st.write(
#     "Palmon data test"
# )
#uploaded_file = st.file_uploader("Choose a file")

PATH = 'data_files/PS_streamlit_US.csv'
df_srv = read_csv(PATH)

if 'data_srv' not in st.session_state:
   st.session_state['data_srv'] = {}

if 'data_loc' not in st.session_state:
   st.session_state['data_loc'] = {}

if df_srv is not None:
   st.session_state['data_srv'] = df_srv

if uploaded_file is not None:
  df_loc = pd.read_csv(uploaded_file)
  st.session_state['data_loc'] = df_loc

init()
time.sleep(2)  # Wait 2 seconds
#st.warning(st.session_state.is_session_pc)

if str(st.session_state.is_session_pc) == 'True':
    pages = {
        "Home" : [ st.Page(pg_home, title="Home", icon=":material/home:") ],
        "Local data": [
            st.Page(pg_loc_0, title="Select file...", icon="📋"),
            st.Page(pg_loc_1, title="Table", icon="📅"),
            st.Page(pg_loc_2, title="Chart", icon="📊"),
            st.Page(pg_loc_3, title="Pivot", icon="📅"),
        ],
        "Server data": [
            st.Page(pg_srv_1, title="Table", icon="📅"),
            st.Page(pg_srv_2, title="Chart", icon="📊"),
            st.Page(pg_srv_3, title="Pivot", icon="📅"),
        ],
    }

if str(st.session_state.is_session_pc) != 'True':
    pages = {
        "Home" : [ st.Page(pg_home, title="Home", icon=":material/home:") ],
        "Server data": [
            st.Page(pg_srv_1, title="Table", icon="📅"),
            st.Page(pg_srv_2, title="Chart", icon="📊"),
            st.Page(pg_srv_3, title="Pivot", icon="📅"),
        ],
    }    

pg = st.navigation(pages)
pg.run()