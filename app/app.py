import streamlit as st
from page_components import add_common_page_elements

sidebar_container = add_common_page_elements()
# page_container = st.sidebar.container()
# sidebar_container = st.sidebar.container()

st.divider()

# Homepage Title
st.title("Welcome to StreamWise 🎬")

# Homepage Description
st.write("""
StreamWise is your ultimate movie companion designed to elevate your streaming experience! 
Discover personalized recommendations, explore various genres, and find your next favorite film with ease.
""")

# Key Features Section
st.header("Why Choose StreamWise?")

st.markdown("""
- **Personalized Recommendations**: Get tailored movie suggestions based on your viewing habits and preferences.
- **Diverse Genres**: Explore a wide variety of genres, from thrillers and comedies to documentaries and more!
- **Community Insights**: Join our community of movie enthusiasts, share your thoughts, and discover trending films.
- **User-Friendly Interface**: Navigate seamlessly through our platform to find what you love.
- **Stay Updated**: Be the first to know about new releases and trending shows on your favorite streaming platforms.
""")

# Call to Action
st.header("Get Started")
st.write("Ready to discover your next favorite movie? Use the sidebar to navigate and explore!")

# Footer
st.write("---")
st.write("Built with ❤️ by the StreamWise Team")