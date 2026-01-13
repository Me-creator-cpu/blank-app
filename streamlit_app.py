import streamlit as st
import pandas as pd

st.title("🎈 CSV file app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
  df = pd.read_csv(uploaded_file)
  with st.expander("Raw data"):
    st.write(df)
  st.data_editor(
    df,
    column_config={
        "Level": st.column_config.ProgressColumn(
            "Level",
            help="Palmon level",
            format="%f",
            min_value=100,
            max_value=250,
            color="#006699"
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
    hide_index=False,
)
  #st.dataframe(df.style.highlight_max(color='yellow',axis=0))
  #st.bar_chart(data=None, *, x=None, y=None, x_label=None, y_label=None, color=None, horizontal=False, sort=True, stack=None, width="stretch", height="content", use_container_width=None)
  with st.expander("Chart"):
    st.bar_chart(df,x="Type",y="Level")
  palmon_types_df = df.pivot_table(values='Level', index='Type', columns='Skill')
  with st.expander("Pivot table"):
    st.dataframe(palmon_types_df, use_container_width=True)
