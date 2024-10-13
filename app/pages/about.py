import streamlit as st
from page_components import add_common_page_elements

sidebar_container = add_common_page_elements()

st.divider()

displaytext= ('''## About StreamWise''')

st.markdown(displaytext)

displaytext = ('''
Welcome to StreamWise, your ultimate movie companion designed to elevate your streaming experience! In a world overflowing with content, finding the perfect film or series can feel like searching for a needle in a haystack. That’s where we come in!

At StreamWise, we believe that every movie night should be a memorable adventure. Our innovative recommendation engine harnesses the power of advanced algorithms and user preferences to curate a personalized list of films and shows just for you. Whether you’re in the mood for heartwarming rom-coms, edge-of-your-seat thrillers, or mind-bending sci-fi, we’ve got you covered!

### What We Offer:
- Tailored Recommendations: No more scrolling endlessly! Our smart recommendations adapt to your viewing habits, ensuring you discover hidden gems and classic favorites that match your taste.
- User-Friendly Interface: Designed with simplicity in mind, StreamWise makes finding your next binge-worthy series a breeze. Just tell us what you like, and let the magic happen!
- Community Insights: Join a community of fellow movie lovers! Share your favorites, read reviews, and see what’s trending among your peers.
- Diverse Genres: From blockbuster hits to indie treasures, StreamWise celebrates the art of cinema across all genres and cultures. Explore a world of storytelling at your fingertips!
- Stay Updated: Never miss out on new releases again! With StreamWise, you’ll get timely updates on the latest additions to your favorite streaming platforms.

### Join the StreamWise Family
Let’s make movie nights a breeze and transform your streaming habits into a delightful journey. With StreamWise, your next favorite film is just a click away! So, grab some popcorn, get cozy, and let’s explore the limitless universe of cinema together.

StreamWise—Where Great Movies Find You!
''')

st.markdown(displaytext)