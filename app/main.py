import streamlit as st

st.set_page_config(
    page_title = "PlayLog",
    page_icon = "🎮",
    layout = "wide"
)

st.title("PlayLog")
st.subheader("Your gaming journey, logged.")

st.write(
    "Discover games, build your library, track your progress, "
    "analyze your gaming habits, and find what to play next."
)