import streamlit as st
import pandas as pd
import calendar
import sys
import time
from streamlit_javascript import st_javascript
from user_agents import parse
from streamlit_dynamic_filters import DynamicFilters
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Layout, LabelStyle, FontWeight, EdgeStyle
from networkx import florentine_families_graph

# ===========================================================
# Modifier en conséquence le fichier: requirements.txt
# ===========================================================
# pip install streamlit-javascript
# pip install pyyaml ua-parser user-agents
# pip install streamlit-dynamic-filters
# pip install yfiles_graphs_for_streamlit
# https://levelup.gitconnected.com/dynamic-dataframe-filtering-in-streamlit-aeae5de0f92a
# https://github.com/google/material-design-icons/blob/master/variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.codepoints
# https://www.yworks.com/products/yfiles-graphs-for-streamlit

# ===========================================================
# App sur: https://fictional-zebra-5gjww6p9wqjwf466r.github.dev/
# ===========================================================

global uploaded_file
global is_session_pc
global data_loc
global data_srv
global data_comp
global data_exp
global logo_src
global bln_with_logo
uploaded_file = None
is_session_pc = 'True'
logo_src="data_files/logo_01.jpg"
st.session_state.logo_src = logo_src
bln_with_logo = False
# bln_with_logo = True
st.session_state.bln_with_logo = bln_with_logo
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

# ===========================================================
#   Fichiers
# ===========================================================
PATH = 'data_files/PS_streamlit_US_v1.csv'
PATH_COMP = 'data_files/PS_COMP.csv'
PATH_EXP = 'data_files/PS_EXP.csv'

# ===========================================================
#   Variables => prévoir options modifications
# ===========================================================
level_bourg = 25
level_min = 0
level_max = float(level_bourg) * 10

max_mut_Energy=400000
max_mut_Crystals=300
max_mut_Pieces=975

# ===========================================================
#   Variables globales
# ===========================================================
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

def with_logo(val=None):
    if val is None:
        bln=st.session_state.bln_with_logo
    else:
        bln=val
    st.session_state.bln_with_logo = bln
    return st.session_state.bln_with_logo

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
      with st.expander(title_expander, expanded=False, width="stretch"):
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
      with st.expander(title_expander, expanded=False, width="stretch"):
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

def build_main_chart(raw_data,title_expander=None,x_axis=None,y_axis=None):
  if title_expander==None:
   title_expander="Chart"
  with st.expander(title_expander, expanded=True, width="stretch"):
    st.bar_chart(
        raw_data,
        x=x_axis,
        y=y_axis,
        horizontal=True,
    )

def build_pivot_table(raw_data,val_value: str, val_index: str, val_columns: str,title_expander=None):
  if title_expander==None:
     title_expander="Pivot table"
  palmon_types_df = raw_data.pivot_table(values=val_value, index=val_index, columns=val_columns)
  with st.expander(title_expander, expanded=True, width="stretch"):
    st.dataframe(
       palmon_types_df.style.highlight_max(axis=0),
       column_config={
          "Type": st.column_config.TextColumn( "Type", pinned = True ),
          "Attack": st.column_config.NumberColumn( "⚔ Attack", step=".01" ), #:crossed_swords:
          "Defend": st.column_config.NumberColumn( "🛡 Defend", step=".01" ), #:shield:
          "Level": st.column_config.NumberColumn( "Level", step=".01" ),
        },
       width="stretch",
       hide_index=None,
    )

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
    st.caption(f"Server files used:")
    fileinfo={
       "Data":PATH,
       "Comp":PATH_COMP,
       "EXP":PATH_EXP
    }
    st.dataframe(
        fileinfo,
        height = "content",
        width = "content",
        selection_mode = "single-row",
        hide_index=False,
        )  

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
      build_main_chart(st.session_state['data_loc'],None,'Type','Level')
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
      build_main_chart(st.session_state['data_srv'],None,'Type','Level')
   
def pg_srv_3():
   if st.session_state['data_srv'] is not None:
      build_pivot_table(st.session_state['data_srv'],'Level','Type','Skill')

def pg_srv_4():
   if with_logo==True:
      st.image("data_files/logo_03.jpg",width="stretch")
   st.session_state['data_comp'] = read_csv(PATH_COMP)
   if st.session_state['data_comp'] is not None:
      build_comp_table(st.session_state['data_comp'],'COMP costs')   

def pg_srv_5():
   if with_logo==True:
      st.image("data_files/logo_02.jpg",width="stretch")
   st.session_state['data_exp'] = read_csv(PATH_EXP)
   if st.session_state['data_exp'] is not None:
      build_exp_table(st.session_state['data_exp'],'EXP costs')

def pg_srv_6():
   col_border=False 
   #with_logo(False)
   column='Type'
   if with_logo==True:
      row0 = st.columns([1, 3, 1], border=col_border)
      with row0[1]:
         st.image("data_files/logo_03.jpg",width="stretch")
   else:
      row0 = st.header("Dashboad", divider=True) 

   if st.session_state['data_srv'] is not None:
      df = st.session_state['data_srv']
      options = st.multiselect(f"Filter values for {column}:", df[column].unique(), default=list(df[column].unique()))
      filtered_df = df[df[column].isin(options)]

      row1 = st.columns(2,border=col_border, width="stretch")
      row2 = st.columns(2,border=col_border, width="stretch")  
      row3 = st.columns(2,border=col_border, width="stretch")
      row4 = st.columns(2,border=col_border, width="stretch")

      with st.spinner("Wait for it...", show_time=True):
         with row1[0]:
            build_pivot_table(filtered_df,'Level','Type','Skill','Average level overview')
         with row1[1]:
            build_main_chart(filtered_df,"Level total",'Type','Level')
         with row2[0]:
            build_pivot_table(filtered_df,'Level','Skill', None, 'Average level per skill')
         with row2[1]:
            build_pivot_table(filtered_df,'Level','Type', None, 'Average level per type')
         with row3[0]:
            df_gr = filtered_df[['Name', 'Type', 'Skill', 'Level','Rank']]
            regular_search_term = df_gr.groupby(['Type'])['Rank'].head(7)
            build_pivot_table(df_gr[filtered_df['Rank'].isin(regular_search_term)],'Level','Type', None, 'Average Top 7 per type')
         with row3[1]:
            df_gr = filtered_df[['Name', 'Type', 'Skill', 'Level','Rank']]
            regular_search_term = df_gr.groupby(['Type'])['Rank'].head(2)
            st.write(df_gr[filtered_df['Rank'].isin(regular_search_term)])
         with row4[0]:
            avg_df = df_gr.groupby('Type').apply(lambda x: x['Level'].sum() / x['Level'].count(), include_groups=False).to_frame('Level')
            avg_df
         with row4[1]:
             avg_df = df_gr.set_index('Type').groupby('Type').apply(lambda x: x['Level'].sum() / x['Level'].count(), include_groups=True).to_frame('Level')
             build_main_chart(avg_df,"Level Average",None,'Level')

def func_avg():
    return None

def pg_download() -> st.Page:
   if with_logo==True:
      st.image("data_files/logo_05.jpg",width="stretch")
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
   st.page_link("pages/home.py", label="page Home", query_params={"diaplayLogo": str(st.session_state.is_session_pc) != 'True'})

def is_in_medici_line(node_id: int) -> bool:
    """Return True if the node represents a Medici marriage line node"""
    for node in graph.nodes:
        if node.get("id") == node_id:
            label = (
                    node.get("properties", {}).get("label")
                    or node.get("label")  # fallback if properties.label missing
            )
            return label in medici_line if label is not None else False
    return False

def pg_test_graph():
   st.set_page_config(
      page_title="yFiles Graphs for Streamlit",
      layout="wide",
   )
   # st.markdown("---")
   # st.title("Data-driven visualization")
   # medici_line = ["Acciaiuoli", "Medici", "Albizzi", "Guadagni", "Lamberteschi"]
   # graph = StreamlitGraphWidget.from_graph(
   #    # import NetworkX sample graph
   #    graph = florentine_families_graph(),
   #    # color Medici marriage line
   #    node_color_mapping = lambda node: "#FF5722" if node["properties"]["label"] in medici_line else "#BDBDBD",
   #    # increase node sizes of Medici marriage line
   #    node_size_mapping = lambda node: (85, 85) if node["properties"]["label"] in medici_line else (55, 55),
   #    # apply a heat mapping to the Medici marriage line
   #    heat_mapping = lambda item: 0.5 if item["properties"]["label"] in medici_line else 0.0,
   #    # highlight edges between Medici marriage line nodes
   #    edge_styles_mapping = lambda edge: EdgeStyle(
   #       color = "#FF0000" if is_in_medici_line(edge["start"]) and is_in_medici_line(edge["end"]) else "#BDBDBD",
   #       thickness = 6 if is_in_medici_line(edge["start"]) and is_in_medici_line(edge["end"]) else 1
   #    ),
   #    # emphasize Medici marriage line node labels
   #    node_label_mapping = lambda n: LabelStyle(
   #       text = n["properties"]["label"],
   #       font_weight = FontWeight.BOLD if n["properties"]["label"] in medici_line else FontWeight.NORMAL,
   #       font_size = 16 if n["properties"]["label"] in medici_line else 12
   #    )
   # )

   # # render the component
   # graph.show(graph_layout=Layout.HIERARCHIC)

   # st.markdown("---")

   #Graphe Costs
   # if st.session_state['data_exp'] is not None:
   #    df = st.session_state['data_exp'][['Lvl from', 'Cost']]
   #    st.line_chart(df['Cost'])

   #Graphe per type
   chart = {
    "mark": "point",
    "params": [
      {"name": "interval_selection", "select": "interval"},
      {"name": "point_selection", "select": "point"},
    ],
    "encoding": {
        "x": {
            "field": "Stars",
            "type": "quantitative",
        },
        "y": {
            "field": "Level",
            "type": "quantitative",
        },
        "size": {"field": "Achievement", "type": "quantitative"},
        "color": {"field": "Skill", "type": "nominal"},
        "shape": {"field": "Type", "type": "nominal"},
    },
   }
   column='Type'
   # source = df_srv
   options = st.multiselect(f"Filter values for {column}:", df_srv[column].unique(), default=list(df_srv[column].unique()))
   source = df_srv[df_srv[column].isin(options)]   
   tab1, tab2 = st.tabs(["Streamlit theme (default)", "Vega-Lite native theme"])
   with tab1:
      st.vega_lite_chart(
         #source, chart, theme="streamlit", use_container_width=True
         source, chart, theme="streamlit", width="stretch"
      )
   with tab2:
      event = st.vega_lite_chart(
         #source, chart, theme=None, use_container_width=True, on_select="rerun"
         source, chart, theme=None, on_select="rerun", width="stretch"
      )
   try:
      df_level = event.selection.interval_selection.Level
      df_stars = event.selection.interval_selection.Stars
      min_val_level, max_val_level = df_level[0], df_level[1]
      min_val_stars, max_val_stars = df_stars[0], df_stars[1]
      df_selection = df_srv[(df_srv['Level'] >= min_val_level) & (df_srv['Level'] <= max_val_level)]
      df_selection = df_selection[(df_selection['Stars'] >= min_val_stars) & (df_selection['Stars'] <= max_val_stars)]
   except:
      df_selection=source[['Name', 'Type', 'Skill', 'Level', 'Stars', 'URL']]
   # st.write(df_selection)
   #st.dataframe(
   #     df_selection,
   #     # height = "content",
   #     width = "stretch",
   #     selection_mode = "single-row",
   #     column_config=column_config,
   #     hide_index=True,
   #)
   data_to_tiles(df_selection)

def pg_test_tiles():
    data_to_tiles()

def data_to_tiles(df_data=None): #<========================================================================
    palidx=0
    if df_data is None:
        source = df_srv[['Name', 'Type', 'Skill', 'Level', 'Stars', 'URL']]
    else:
        source = df_data
    #st.write(source)
    trows= len(source['Name'])
    if trows > 5:
        total_cells_per_row_or_col = 5
    else:
        total_cells_per_row_or_col = trows
    for i in range(1, (total_cells_per_row_or_col)):
        tlst = ([1] * total_cells_per_row_or_col) + [2] # 2 = rt side padding
        globals()['cols' + str(i)] = st.columns(tlst)
        for j in range(len(tlst)-1):
            try:
                cont = globals()['cols' + str(i)][j].container(border=True)
                with cont:
                    build_tile_pic(source.URL[palidx])
                    st.markdown(source.Name[palidx])
                    col1, col2 = st.columns(2)
                    #st.columns(2,border=col_border, width="stretch")
                    col1.write('Type')
                    col2.write(source.Type[palidx])
                    #st.markdown(build_tile(source.Name[palidx],source.URL[palidx],int(source.Level[palidx]),int(source.Stars[palidx]),source.Skill[palidx],source.Type[palidx]))
            except:
                strContent=''
            #globals()['cols' + str(i)][j].markdown(strContent, unsafe_allow_html=True)
            palidx=palidx+1

def data_to_tiles_v1(df_data=None):
    total_cells_per_row_or_col = 5
    palidx=0
    if df_data is None:
        source = df_srv[['Name', 'Type', 'Skill', 'Level', 'Stars', 'URL']]
    else:
        source = df_data
    #st.write(source)
    for i in range(1, (total_cells_per_row_or_col)):
        tlst = ([1] * total_cells_per_row_or_col) + [2] # 2 = rt side padding
        globals()['cols' + str(i)] = st.columns(tlst)
        for j in range(len(tlst)-1):
            try:
                strContent=build_tile_v2(source.Name[palidx],source.URL[palidx],int(source.Level[palidx]),int(source.Stars[palidx]),source.Skill[palidx],source.Type[palidx])
            except:
                strContent=''
            globals()['cols' + str(i)][j].markdown(strContent, unsafe_allow_html=True)
            palidx=palidx+1
            
def build_tile_pic(sUrl=""):
    #st.image(image, caption=None, width="content", use_column_width=None, clamp=False, channels="RGB", output_format="auto", *, use_container_width=None)
    return st.image(sUrl, caption=None, width="content", clamp=False, channels="RGB", output_format="auto")

def build_tile(name="Caption Tile",image_url="",level=1,stars=0,skill="",type=""):
    cont = st.container(border=True)
    row0 = cont.build_tile_pic(image_url)
    rowName = cont.write(name)
    row1 = cont.columns(2,border=col_border, width="stretch")
    row1[0] = cont.write('Type')
    row1[0] = cont.write(type)
    return cont

def build_tile_v2(name="Caption Tile",image_url="",level=1,stars=0,skill="",type=""):
    strHtml='<span>'
    strHtml=strHtml+'<table>'
    strHtml=strHtml+'<tr><td colspan=2><img height="200px" src="'+image_url+'"></td></tr>'
    strHtml=strHtml+'<tr><td colspan=2><b>'+name+'</b></td></tr>'
    strHtml=strHtml+'<tr><td>Type</td><td>'+type+'</td></tr>'
    strHtml=strHtml+'<tr><td>Skill</td><td>'+skill+'</td></tr>'
    strHtml=strHtml+'<tr><td>Level</td><td>'+str(level)+'</td></tr>'
    strHtml=strHtml+'<tr><td>Stars</td><td>'+str(stars)+'</td></tr>'
    strHtml=strHtml+'<tr><td>Cell</td><td>Cell</td></tr>'
    strHtml=strHtml+'</table></span>'
    return strHtml

def pg_options():
    st.header("Options", divider=True)
    if st.session_state.bln_with_logo==True:
        on_logo = st.toggle("Activate images", value=True)
    else:
        on_logo = st.toggle("Activate images", value=False)
    if on_logo:
        st.write(f"Feature activated! ({on_logo})")
    with_logo(on_logo)
    st.session_state.bln_with_logo = on_logo

# ===========================================================
#   Lancement
# ===========================================================
df_srv = read_csv(PATH)
time.sleep(2)  # Wait 2 seconds
data_comp = read_csv(PATH_COMP)
data_exp = read_csv(PATH_EXP)

init()
with_logo(False)
if df_srv is not None:
   data_srv = df_srv
   st.session_state['data_srv'] = df_srv

if uploaded_file is not None:
  df_loc = pd.read_csv(uploaded_file)
  st.session_state['data_loc'] = df_loc
  data_loc = df_loc

#var_server=st.markdown(":violet-badge[:material/star: Favorite]")
pages = {
   #  "Home" : [ st.Page("pages/home.py", title="Home", icon=":material/home:") ],
    "Home":[ st.Page(pg_home, title="Home", icon=":material/home:") ],
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
        st.Page(pg_srv_6, title="Dashboard", icon=option_menu[2]),
        st.Page(pg_download, title="Download Data", icon=option_menu[5]),
    ],
    "Tests":[
        st.Page(pg_tests, title="Test page", icon=option_menu[2]),
        st.Page(pg_test_graph,title="Test graph",icon=option_menu[1]),
        st.Page(pg_test_tiles,title="Test tiles",icon=option_menu[2]),        
    ],
    "Parameters":[st.Page(pg_options, title="Options", icon=option_menu[2])],
}
if str(st.session_state.is_session_pc) != 'True':
   pages.pop("Local data")
 
pg = st.navigation(pages)
pg.run()
