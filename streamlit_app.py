import streamlit as st
import pandas as pd
import calendar
import sys
import time
from streamlit_javascript import st_javascript
from user_agents import parse
from streamlit_dynamic_filters import DynamicFilters

# Modifier en conséquence le fichier: requirements.txt
# pip install streamlit-javascript
# pip install pyyaml ua-parser user-agents
# pip install streamlit-dynamic-filters
# https://levelup.gitconnected.com/dynamic-dataframe-filtering-in-streamlit-aeae5de0f92a
#https://github.com/google/material-design-icons/blob/master/variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.codepoints

global uploaded_file
global is_session_pc
global data_loc
global data_srv
global data_comp
global data_exp
global logo_src
uploaded_file = None
is_session_pc = 'True'
logo_src="data_files/logo_01.jpg"
st.session_state.logo_src = logo_src
with_logo = False
# with_logo = True
st.session_state.dataframe_filters = {}
data_loc = {}
data_srv = {}
data_comp = {}
data_exp = {}
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'data_loc' not in st.session_state:
    st.session_state['data_loc'] = None
if 'data_srv' not in st.session_state:
    st.session_state['data_srv'] = None    
PATH = 'data_files/PS_streamlit_US.csv'
PATH_COMP = 'data_files/PS_COMP.csv'
PATH_EXP = 'data_files/PS_EXP.csv'

level_bourg = 25
level_min = 0
level_max = float(level_bourg) * 10

data_menu = {
   "name":["Home",
           "Select file...",
           "Table",
           "Chart",
           "Pivot"],
   "ico":[":material/home:",
          "📋",
          "📅",
          "📊",
          "📅"],
   "desc":["d1","d2","d3","d4"],
   "page":["p1","p2","p3","p4"]
}

data_page = {
    "name":["Home","Local data","Server data"],
    "pages":[{0},{1,2,3,4},{2,3,4}],
    "src":[{},{},{}]
}

option_menu = {
    0: ":material/home_app_logo:",
    1: ":material/upload:", #"📥", #"📋",
    2: ":material/table:",#"📅",
    3: ":material/bar_chart:", #"📊",
    4: ":material/pivot_table_chart:", #"📅"
    5: ":material/download:"
} 

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
        #format="localized",
        format="compact",
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
}

# ===========================================================
#   Initialisation
# ===========================================================
def init():
   ua_string = str(st_javascript("""window.navigator.userAgent;"""))
   user_agent = parse(ua_string)
   st.session_state.is_session_pc = user_agent.is_pc
   is_session_pc = str(st.session_state.is_session_pc)
   data_page.get("src")[1] = data_loc
   data_page.get("src")[2] = data_srv

# ===========================================================
#   Fonctions
# ===========================================================
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

def file_err():
   st.markdown(":orange-badge[⚠️ No file loaded]")

def check_rows(res, column, options):
    return res.loc[res[column].isin(options)]

def config_df(raw_data):
   df = raw_data.copy()
   level_values = df['Lvl from'].unique()
   cols = st.columns(4)
   level = cols[0].multiselect("Level", level_values)
   return df,level,level_values

def build_any_table(raw_data,title_expander) -> pd.DataFrame:
  df = raw_data.copy()
  level = 0
  st.write(f":material/home: Level Hall: {level_bourg}")
  if df is not None:
   #   config_df(raw_data)
   #   range_cols = st.columns(3)
   #   range_level_min, range_level_max = range_cols[0].slider("Level evolution", int(level_min), int(level_max),
   #                                           [int(level_min), int(level_max)])
   #   with st.expander(title_expander, expanded=True, width="stretch"):
   #      st.dataframe(
   #         df,
   #         use_container_width=True,
   #         hide_index=None,
   #         )
     range_level_min, range_level_max = st.slider("Level evolution", int(level_min), int(level_max), [int(level_min), int(level_max)])
     try:
      df = df.loc[(df['Lvl from'] >= range_level_min) & (df['Lvl from'] <= range_level_max)]
      st.data_editor(
         df,
         column_config={
            "Cost": st.column_config.NumberColumn(
                  "Costs",
                  min_value=0,
                  max_value=10000000000,
                  step=1,
                  format="compact",
            )
         },
         hide_index=True,
      )
      total_col = f"Total cost from {range_level_min} to {range_level_max}"
      total_cost = df.Cost.sum()
      data_df = pd.DataFrame(
         {
            "cost": [total_cost],
         }
      )
      st.data_editor(
         data_df,
         column_config={
            "cost": st.column_config.NumberColumn(
                  total_col,
                  min_value=0,
                  max_value=10000000000,
                  step=1,
                  format="compact",
            )
         },
         hide_index=True,
      )
     except:
        st.write('No filter applyed',df)
  
  return df

def build_exp_table(raw_data,title_expander) -> pd.DataFrame:
  df = raw_data.copy()
  level = 0
  st.subheader("Level evolution", divider=False)
  st.write(f":material/home: Level Hall: {level_bourg}")
  if df is not None:
     range_level_min, range_level_max = st.slider("Choose range:", int(level_min), int(level_max), [int(level_min), int(level_max)])
     try:
      df = df.loc[(df['Lvl from'] >= range_level_min) & (df['Lvl from'] <= range_level_max)]
      with st.expander(title_expander, expanded=True, width="stretch"):
         st.data_editor(
            df,
            column_config={
               "Cost": st.column_config.NumberColumn(
                     "Costs",
                     min_value=0,
                     max_value=10000000000,
                     step=1,
                     format="compact",
               )
            },
            hide_index=True,
         )
      total_col = f"Total cost from {range_level_min} to {range_level_max}"
      total_cost = df.Cost.sum()
      data_df = pd.DataFrame(
         {
            "cost": [total_cost],
         }
      )
      st.data_editor(
         data_df,
         column_config={
            "cost": st.column_config.NumberColumn(
                  total_col,
                  min_value=0,
                  max_value=10000000000,
                  step=1,
                  format="compact",
            )
         },
         hide_index=True,
      )
     except:
        st.write('No filter applyed',df)
  return df

def build_comp_table(raw_data,title_expander) -> pd.DataFrame:
  df = raw_data.copy()
  level = 0
  comp_level_min = 0
  comp_level_max = 30
  st.subheader("Competency evolution", divider=False)
  if df is not None:
     range_level_min, range_level_max = st.slider("Choose range:", int(comp_level_min), int(comp_level_max), [int(comp_level_min), int(comp_level_max)])
     try:
      df = df.loc[(df['Lvl from'] >= range_level_min) & (df['Lvl from'] <= range_level_max)]
      with st.expander(title_expander, expanded=True, width="stretch"):
         st.data_editor(
            df,
            column_config={
               "Cost": st.column_config.NumberColumn(
                     "Costs",
                     min_value=0,
                     max_value=10000000,
                     step=1,
                     format="compact",
               )
            },
            hide_index=True,
         )
      total_col = f"Total cost from {range_level_min} to {range_level_max}"
      total_cost = df.Cost.sum()
      data_df = pd.DataFrame(
         {
            "cost": [total_cost],
         }
      )
      st.data_editor(
         data_df,
         column_config={
            "cost": st.column_config.NumberColumn(
                  total_col,
                  min_value=0,
                  max_value=10000000000,
                  step=1,
                  format="compact",
            )
         },
         hide_index=True,
      )
     except:
        st.write('No filter applyed',df)
  return df

def build_main_table(raw_data) -> pd.DataFrame:
  df = raw_data
#   if st.session_state['data_loc'] is not None:
  if df is not None:
     df2 = df.copy()
     dynamic_filters = DynamicFilters(df=df2, filters=['Type', 'Skill', 'Team'])

     with st.expander("Filtered data", expanded=False, width="stretch"):
        dynamic_filters.display_filters()
        #dynamic_filters.display_filters(location='sidebar')
        dynamic_filters.display_df(
           height = "content",
           width = "content",
           column_config=column_config,
           hide_index=True
        )

  with st.expander("Raw data", expanded=True, width="stretch"):
    st.dataframe(
        df,
        height = "content",
        width = "content",
        selection_mode = "single-row",
        column_config=column_config,
        hide_index=True,
        )   

def build_main_chart(raw_data):
  with st.expander("Chart", expanded=True, width="stretch"):
    st.bar_chart(
       raw_data,
       x="Type",
       y="Level",
       horizontal=True
    )

def build_pivot_table(raw_data,val_value: str, val_index: str, val_columns: str):
  palmon_types_df = raw_data.pivot_table(values=val_value, index=val_index, columns=val_columns)
  with st.expander("Pivot table", expanded=True, width="stretch"):
    st.dataframe(
       palmon_types_df.style.highlight_max(axis=0),
       column_config={
          "Type": st.column_config.TextColumn( "Type", pinned = True ),
          "Attack": st.column_config.NumberColumn( "⚔ Attack", step=".01" ), #:crossed_swords:
          "Defend": st.column_config.NumberColumn( "🛡 Defend", step=".01" ), #:shield:
        },
       use_container_width=True,
       hide_index=None,
    )
#st.dataframe(df.style.highlight_max(axis=0))

# ===========================================================
#   Pages
# ===========================================================
def pg_home(): 
    abbr = dict(enumerate(calendar.month_abbr))
    abbr.pop(0)
    if with_logo == True:
       #logo_ico=st.image(logo_src, width=32)
       st.logo(logo_src,size="large", link=None, icon_image=None)
       st.image(logo_src) #, caption="data_files/Logo_01.jpg")
    st.title(body="File data test", text_alignment="center")
    st.header(str(time.localtime().tm_mday) + "/" + abbr[time.localtime().tm_mon] + "/" + str(time.localtime().tm_year), divider=True)
    st.subheader("Choose local data (to upload) or server data (git)", divider=True)

def pg_loc_0():
   uploaded_file = st.file_uploader("Choose a file")
   st.session_state.uploaded_file = uploaded_file
   if uploaded_file is not None:
    df_loc = pd.read_csv(uploaded_file)
    data_loc = pd.DataFrame(df_loc)
    fileinfo={
       "Name":uploaded_file.name,
       "Type":uploaded_file.type,
       "Size":uploaded_file.size
    }
    st.dataframe(
        fileinfo,
        height = "content",
        width = "content",
        selection_mode = "single-row",
        hide_index=False,
        )  
    st.session_state['data_loc'] = data_loc
    st.toast("File loaded", icon="🎉")
    st.balloons()

def pg_loc_1():
   try:
      build_main_table(st.session_state['data_loc'])
   except:
      file_err()
      
def pg_loc_2():
   try:
      build_main_chart(st.session_state['data_loc'])
   except:
      file_err()

def pg_loc_3():
   try:
      build_pivot_table(st.session_state['data_loc'],'Level','Type','Skill')
   except:
      file_err()

def pg_srv_1():
   if st.session_state['data_srv'] is not None:
      build_main_table(st.session_state['data_srv'])

def pg_srv_2():
   if st.session_state['data_srv'] is not None:
      build_main_chart(st.session_state['data_srv'])
   
def pg_srv_3():
   if st.session_state['data_srv'] is not None:
      build_pivot_table(st.session_state['data_srv'],'Level','Type','Skill')

def pg_srv_4():
   if with_logo==True:
      st.image("data_files/logo_03.jpg")
   st.session_state['data_comp'] = read_csv(PATH_COMP)
   if st.session_state['data_comp'] is not None:
      build_comp_table(st.session_state['data_comp'],'COMP costs')   

def pg_srv_5():
   col1, col2 = st.columns([1, 3])
   if with_logo==True:
      col1.image("data_files/logo_02.jpg")
   st.session_state['data_exp'] = read_csv(PATH_EXP)
   if st.session_state['data_exp'] is not None:
      with col2.container():
         build_exp_table(st.session_state['data_exp'],'EXP costs')  

def pg_download() -> st.Page:
   if with_logo==True:
      st.image("data_files/logo_05.jpg")
   st.title(body="Download file data test", text_alignment="center")
   st.subheader("Choose local data (csv)", divider=False)

   range_cols = st.columns(3)
   range_cols[0].download_button(
    label="Database costs",
    data=df_srv.to_csv().encode("utf-8"),
    file_name="base_data.csv",
    mime="text/csv",
    icon=":material/download:",
   )
   range_cols[1].download_button(
    label="EXP costs",
    data=data_exp.to_csv().encode("utf-8"),
    file_name="exp_data.csv",
    mime="text/csv",
    icon=":material/download:",
   )
   range_cols[2].download_button(
    label="COMP costs",
    data=data_comp.to_csv().encode("utf-8"),
    file_name="comp_data.csv",
    mime="text/csv",
    icon=":material/download:",
   )
   # st.download_button(
   #  label="Download CSV",
   #  data=df_srv.to_csv().encode("utf-8"),
   #  file_name="data.csv",
   #  mime="text/csv",
   #  icon=":material/download:",
   # )
   
def pg_tests():
   st.page_link("pages/home.py", query_params={"diaplayLogo": str(st.session_state.is_session_pc) != 'True'})

# ===========================================================
#   Lancement
# ===========================================================
df_srv = read_csv(PATH)
time.sleep(2)  # Wait 2 seconds
data_comp = read_csv(PATH_COMP)
data_exp = read_csv(PATH_EXP)

init()

if df_srv is not None:
   data_srv = df_srv
   st.session_state['data_srv'] = df_srv

if uploaded_file is not None:
  df_loc = pd.read_csv(uploaded_file)
  st.session_state['data_loc'] = df_loc
  data_loc = df_loc
with_logo=True
#var_server=st.markdown(":violet-badge[:material/star: Favorite]")
pages = {
    "Home" : [ st.Page("pages/home.py", title="Home", icon=":material/home:") ],
    # "Home" : [ st.Page(pg_home, title="Home", icon=":material/home:") ],
    "Local data": [
        st.Page(pg_loc_0, title="Select file...", icon=option_menu[1]),
        st.Page(pg_loc_1, title="Table", icon=option_menu[2]),
        st.Page(pg_loc_2, title="Chart", icon=option_menu[3]),
        st.Page(pg_loc_3, title="Pivot", icon=option_menu[4]),
    ],
    "Server data": [
        st.Page(pg_srv_1, title="Table", icon=option_menu[2]),
        st.Page(pg_srv_2, title="Chart", icon=option_menu[3]),
        st.Page(pg_srv_3, title="Pivot", icon=option_menu[4]),
        st.Page(pg_srv_4, title="Competencies", icon=option_menu[2]),
        st.Page(pg_srv_5, title="EXP", icon=option_menu[2]),
        st.Page(pg_download, title="Download Data", icon=option_menu[5]),
    ],
    "Tests":[
       st.Page(pg_tests, title="Test01", icon=option_menu[2]),
    ],
}
if str(st.session_state.is_session_pc) != 'True':
   pages.pop("Local data")
 
pg = st.navigation(pages)
pg.run()
