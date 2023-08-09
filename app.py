import pickle
import streamlit as st
import pandas as pd
import requests
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

async def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id,api_key)
    data = requests.get(url)
    data.raise_for_status()
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

async def recommend(movie):
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in movies_list:
        recommended_movie_names.append(new_df.iloc[i[0]].title)
        recommended_movie_posters.append(await fetch_poster(new_df.iloc[i[0]].id))

    return recommended_movie_names, recommended_movie_posters

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title('Movie Recommender System')

movies = pickle.load(open('pickle_data/movie_list.pkl', 'rb'))
similarity = pickle.load(open('pickle_data/similarity.pkl', 'rb'))

new_df = pd.DataFrame(movies)
movie_list = new_df['title']

st.sidebar.markdown("Select a movie from the dropdown and click 'Show Recommendation'.")
selected_movie = st.sidebar.selectbox("Select a movie", movie_list)

if st.sidebar.button('Show Recommendation', key="recommendation_btn"):
    with st.spinner("Fetching recommendations..."):
        async def movie():
            recommended_movie_names, recommended_movie_posters = await recommend(selected_movie)
            return recommended_movie_names, recommended_movie_posters
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        names, posters = loop.run_until_complete(movie())

        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])

st.sidebar.markdown("Vikas Rajpurohit | [GitHub](https://github.com/Vikas-Rajpurohit)")
st.sidebar.markdown("Movie data from The Movie Database API")
