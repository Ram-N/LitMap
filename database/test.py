import streamlit as st

# Update sidebar content based on the current tab
def update_sidebar():
    sidebar_placeholder = st.sidebar.empty()


# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Tab 1"

# Create tabs
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

# Sidebar
sidebar_placeholder = st.sidebar.empty()

# Trigger a re-render of the sidebar when the current tab changes
if "previous_tab" not in st.session_state or st.session_state.current_tab != st.session_state.previous_tab:
    st.session_state.previous_tab = st.session_state.current_tab
    update_sidebar()


# Tab 1
with tab1:
    st.session_state.current_tab = "Tab 1"
    # Tab 1 content
    st.write("This is Tab 1")
    update_sidebar()

# Tab 2 
with tab2:
    st.session_state.current_tab = "Tab 2"
    # Tab 2 content
    st.write("This is Tab 2")
    update_sidebar()

# Tab 3
with tab3:
    st.session_state.current_tab = "Tab 3"
    # Tab 3 content
    st.write("This is Tab 3")
    update_sidebar()

