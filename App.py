import streamlit as st
import pickle
import requests
import asyncio
import aiohttp
import os
import gdown

st.set_page_config(page_title="Movie Recommender", layout="wide")

# -------------------------------
# DOWNLOAD FILES FROM DRIVE
# -------------------------------

MOVIES_FILE_ID = "1TJ_IKlmMvKV7Ha4xh8YcnOhg9LnTO5SN"
RECOMMEND_FILE_ID = "15Uwz5k2-pOM3a6Y3xk8KsZ8Elt4pTVMX"

def download_files():
    if not os.path.exists("movies.pkl"):
        gdown.download(
            f"https://drive.google.com/uc?id={MOVIES_FILE_ID}",
            "movies.pkl",
            quiet=False
        )

    if not os.path.exists("recommend.pkl"):
        gdown.download(
            f"https://drive.google.com/uc?id={RECOMMEND_FILE_ID}",
            "recommend.pkl",
            quiet=False
        )

download_files()

# -------------------------------
# LOAD DATA (CACHED)
# -------------------------------

@st.cache_resource
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("recommend.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()

# -------------------------------
# FETCH POSTERS (ASYNC)
# -------------------------------

async def fetch_single_poster(session, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_API_KEY"

    async with session.get(url) as response:
        data = await response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"

async def fetch_all_posters(movie_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_poster(session, mid) for mid in movie_ids]
        posters = await asyncio.gather(*tasks)
        return posters

# -------------------------------
# RECOMMEND FUNCTION
# -------------------------------

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:9]

    recommended_movies = []
    movie_ids = []

    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
        movie_ids.append(movies.iloc[i[0]].id)

    posters = asyncio.run(fetch_all_posters(movie_ids))

    return recommended_movies, posters

# -------------------------------
# UI
# -------------------------------

st.title("🎬 Movie Recommender System")

movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Type or select a movie",
    movie_list
)

if st.button("Search"):
    with st.spinner("Fetching recommendations..."):
        recommendations, posters = recommend(selected_movie)

    st.subheader(f"Top Recommendations for: {selected_movie}")

    cols = st.columns(4)

    for i in range(8):
        with cols[i % 4]:
            st.image(posters[i], use_container_width=True)
            st.caption(recommendations[i])