
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import logging

# ----------------------------
# Configure Logging
# ----------------------------
logging.basicConfig(
    filename='imdb_dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

st.title("🎬 IMDb Movies Analysis Dashboard")

try:
    # ----------------------------
    # Load dataset
    # ----------------------------
    try:
        df = pd.read_csv("imdb_movies.csv")
        logging.info("Dataset loaded successfully.")
    except FileNotFoundError:
        st.error("Dataset not found. Please make sure 'imdb_movies.csv' is in the working directory.")
        logging.error("imdb_movies.csv not found.")
        st.stop()

    # ----------------------------
    # Data Cleaning
    # ----------------------------
    df.drop_duplicates(inplace=True)
    df.dropna(subset=['title', 'genre', 'rating'], inplace=True)

    numeric_cols = ['release_year', 'rating', 'votes', 'budget', 'revenue']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=numeric_cols, inplace=True)
    logging.info("Data cleaned successfully.")

    # ----------------------------
    # Create SQLite DB
    # ----------------------------
    conn = sqlite3.connect('imdb.db')
    df.to_sql('movies', conn, if_exists='replace', index=False)
    logging.info("Database created and data inserted.")

    # ----------------------------
    # Analysis Options
    # ----------------------------
    option = st.selectbox(
        "Choose an Analysis Option:",
        [
            "1. Top Rated Movies",
            "2. Top Directors by Avg Rating",
            "3. Movies Released per Year",
            "4. Avg Budget & Revenue by Genre",
            "5. Most Common Genres",
            "6. Revenue vs Budget Scatter Plot",
            "7. Top 10 by Votes",
            "8. Movies by Language",
            "9. Average Rating by Country",
            "10. Most Profitable Movies"        

        ]
    )

    if option == "1. Top Rated Movies":
        st.subheader("Top 5 Highest Rated Movies")
        result = pd.read_sql_query("SELECT title, rating FROM movies ORDER BY rating DESC LIMIT 5", conn)
        st.dataframe(result)
    elif option == "2. Top Directors by Avg Rating":
        st.subheader("Top 5 Directors by Average Rating")
        result = pd.read_sql_query("""
            SELECT director, AVG(rating) AS avg_rating 
            FROM movies 
            GROUP BY director 
            ORDER BY avg_rating DESC 
            LIMIT 5
        """, conn)
        st.dataframe(result)

    elif option == "3. Movies Released per Year":
        st.subheader("Movie Count by Year")
        result = pd.read_sql_query("""
            SELECT release_year, COUNT(*) AS movie_count 
            FROM movies 
            GROUP BY release_year 
            ORDER BY release_year
        """, conn)
        st.line_chart(result.set_index("release_year"))

    elif option == "4. Avg Budget & Revenue by Genre":
        st.subheader("Average Budget and Revenue by Genre")
        result = pd.read_sql_query("""
            SELECT genre, AVG(budget) AS avg_budget, AVG(revenue) AS avg_revenue 
            FROM movies 
            GROUP BY genre 
            ORDER BY avg_revenue DESC 
            LIMIT 5
        """, conn)
        st.bar_chart(result.set_index("genre"))

    elif option == "5. Most Common Genres":
        st.subheader("Top 5 Most Common Genres")
        genre_counts = df['genre'].value_counts().head(5)
        st.bar_chart(genre_counts)

    elif option == "6. Revenue vs Budget Scatter Plot":
        st.subheader("Revenue vs Budget")
        fig, ax = plt.subplots()
        ax.scatter(df['budget'], df['revenue'], alpha=0.6, color='green')
        ax.set_xlabel("Budget")
        ax.set_ylabel("Revenue")
        st.pyplot(fig)

    elif option == "7. Top 10 by Votes":
        st.subheader("Top 10 Movies by Vote Count")
        result = df.sort_values(by='votes', ascending=False).head(10)[['title', 'votes']]
        st.dataframe(result)
    elif option == "8. Movies by Language":
        st.subheader("Top 5 Languages by Movie Count")
        result = pd.read_sql_query("""
        SELECT language, COUNT(*) as count 
        FROM movies 
        GROUP BY language 
        ORDER BY count DESC 
        LIMIT 5
        """, conn)
        st.bar_chart(result.set_index("language"))
    elif option == "9. Average Rating by Country":
        st.subheader("Average Movie Rating by Country")
        result = pd.read_sql_query("""
        SELECT country, AVG(rating) as avg_rating 
        FROM movies 
        GROUP BY country 
        ORDER BY avg_rating DESC 
        LIMIT 5
        """, conn)
        st.dataframe(result)
    elif option == "10. Most Profitable Movies":
        st.subheader("Top 5 Most Profitable Movies (Revenue - Budget)")
        df['profit'] = df['revenue'] - df['budget']
        top_profit = df.sort_values(by='profit', ascending=False).head(5)[['title', 'budget', 'revenue', 'profit']]
        st.dataframe(top_profit)




except Exception as e:
    st.error("An unexpected error occurred. Please check the log file for more details.")
    logging.exception("Unhandled Exception occurred:")

finally:
    try:
        conn.close()
        logging.info("Database connection closed.")
    except Exception as e:
        logging.warning("Failed to close database connection.")
