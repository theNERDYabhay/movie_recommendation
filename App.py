import pickle
import streamlit as st
import requests
import aiohttp
import asyncio
import os
import gdown

gdown.download("https://drive.google.com/file/d/1TJ_IKlmMvKV7Ha4xh8YcnOhg9LnTO5SN/view?usp=drive_linkK", "movies.pkl")
if not os.path.exists("recommend.pkl"):
    url = "https://drive.google.com/file/d/15Uwz5k2-pOM3a6Y3xk8KsZ8Elt4pTVMX/view?usp=drive_link"
    gdown.download(url, "recommend.pkl", quiet=False)
async def fetch_all_posters(movie_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_poster(session, mid) for mid in movie_ids]
        posters = await asyncio.gather(*tasks)
        return posters


async def fetch_single_poster(session, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=486d4e79235a1673b259c56930dd18ce"
    async with session.get(url) as response:
        data = await response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=486d4e79235a1673b259c56930dd18ce"
        )
        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except:
        return "https://via.placeholder.com/300x450?text=Error"
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[0:8]

    recommended_movies = []
    movie_ids = []

    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
        movie_ids.append(movies.iloc[i[0]].id)

    # 🔥 Run async poster fetching
    posters = asyncio.run(fetch_all_posters(movie_ids))

    return recommended_movies, posters
st.header('Movie Recommender System')
movies = pickle.load(open('movies.pkl','rb'))
similarity = pickle.load(open('recommend.pkl','rb'))
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)
if st.button("Search"):
    with st.spinner("Fetching recommendations... 🎬"):
        recommendations, posters = recommend(selected_movie)

    st.success("Enjoy!")
    st.subheader(f"Top Recommendations for: {selected_movie}")

    # 🔹 First Row (4 movies)
    row1 = st.columns(4)
    for i in range(4):
        with row1[i]:
            st.image(posters[i], use_container_width=True)
            st.markdown(
                f"<p style='text-align:center; font-weight:bold;'>{recommendations[i]}</p>",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # 🔹 Second Row (4 movies)
    row2 = st.columns(4)
    for i in range(4,8):
        with row2[i-4]:
            st.image(posters[i], use_container_width=True)
            st.markdown(
                f"<p style='text-align:center; font-weight:bold;'>{recommendations[i]}</p>",
                unsafe_allow_html=True
            )