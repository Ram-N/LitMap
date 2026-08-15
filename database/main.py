# LitMap Data Manager — operates on litmap-data.geojson (no Firebase)

import os
import streamlit as st

from geojson_client import GeoJSONClient
from tab_viewer import render_viewer_tab
from tab_db_manage import render_db_manage_tab
from tab_isbn import render_isbn_tab
from tab_covers import render_covers_tab

###########################################################################
# Initialize GeoJSON client
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "..", "vue-app", "public", "litmap-data.geojson")
geojson_client = GeoJSONClient(GEOJSON_PATH)

######## S T R E A M L I T ##########################

# Page configuration
st.set_page_config(layout="wide")

# Streamlit App UI
st.title("LitMap Data Manager")

# Create tabs
view_tab, db_tab, isbn_tab, covers_tab, h_tab = st.tabs(
    ["Data Viewer", "DB-Manage", "ISBN Manager", "Book Covers", "Help"]
)

# Add custom CSS to align the label to the left of the selectbox
st.markdown(
    """
    <style>
    .stSelectbox > label {
        display: inline-block;
        width: 30%;
        text-align: left;
        vertical-align: middle;
        margin-right: 10px;
    }
    .stSelectbox > div {
        display: inline-block;
        width: 65%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

all_books = geojson_client.get_all_books()

# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Viewer"

# Render each tab
placeholder_viewer = render_viewer_tab(view_tab, geojson_client, all_books)
placeholder_db = render_db_manage_tab(db_tab, geojson_client, all_books)
render_isbn_tab(isbn_tab, geojson_client, all_books)
render_covers_tab(covers_tab, geojson_client, all_books)

# Help Tab (small enough to keep inline)
with h_tab:
    st.session_state.current_tab = "Help"

    top_options = {
        0: "Select",
        1: "Document Count",
        2: "List All Book Titles",
        3: "List All Authors",
        4: "Show All Locations",
        5: "Find Duplicates",
        6: "Compare 2 Books",
    }

    st.selectbox(
        label="Choose action for Help",
        options=top_options.values(),
    )

    placeholder_h = st.empty()
    with placeholder_h.container():
        st.header("Help")
        st.write("Here are the help docs and resources.")
        st.markdown("""
        - **Getting Started:** [link]
        - **FAQ:** [link]
        - **Support:** [link]
        """)

# Global clear button (outside tabs)
if st.sidebar.button("Clear All Tabs"):
    print('clear')
    placeholder_viewer.empty()
    placeholder_db.empty()
    placeholder_h.empty()
