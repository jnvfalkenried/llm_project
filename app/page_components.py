import streamlit as st

def set_page_config():
    """
    Sets the page configuration for the app.
    """
    st.set_page_config(
        layout="centered",
        page_title="StreamWise",
        initial_sidebar_state="expanded",
        menu_items={
            "Report a bug": "mailto:dixon.jonas@gmail.com?subject=Bug report"
        },
    )


def add_page_selector():
    # st.image("data/ressources/img/TwelveEdu.png")
    st.page_link("app.py", label="Home")
    st.page_link("pages/recommendation.py", label="StreamWise Chat")
    st.page_link("pages/about.py", label="About")


def add_common_page_elements():
    """
    Sets page config, injects local CSS, adds page selector and login button.
    Returns a container that MUST be used instead of st.sidebar in the rest of the app.
    
    Returns:
        sidebar_container: A container in the sidebar to hold all other sidebar elements.
    """
    # Set page config must be the first st. function called
    set_page_config()
    # Insert local CSS as fast as possible for better display
    # insert_local_css()
    # Create a page selector

    page_selector_container = st.sidebar.container()

    with page_selector_container:
        add_page_selector()

    page_selector_container.divider()

    return page_selector_container 