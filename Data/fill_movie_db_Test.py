import logging
from config.settings import START_DATE_EXTRACTION, END_DATE_EXTRACTION, INTERNAL_IMG_SAVE_PATH
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
# from datetime import datetime, timedelta
import time


#---------------------------------------
#GenreMov SECTION
#---------------------------------------
def get_genreMov(client, connection, cursor):
    paramGenreMov = endpoints.movie_genres()
    response = client.get(
            endpoint=paramGenreMov["endpoint"], 
            params = paramGenreMov["params"]
        )

    json_GenreMov  = helper.extract_genreMov_list(response)

    for genreMov in json_GenreMov:
        try:
            queries.insert_genreMov(cursor, genreMov)
        except Exception as e:
            logging.error(f"Insert Genre error: {type(e).__name__}: {e}")
        
    connection.commit()
#---------------------------------------

#---------------------------------------
#Movie SECTION
#---------------------------------------

def get_movies(client, connection, cursor, date, page):
    paramMov = endpoints.discover_movies(page,date, date)
    response = client.get(
            endpoint=paramMov["endpoint"], 
            params = paramMov["params"]
        )

    json_movies, movie_genre_json = helper.extract_movies_list(response)

    for movie in json_movies:
        try:
            paramMov = endpoints.credits_movies(movie["id_tmdb"])
            response = client.get(
                    endpoint=paramMov["endpoint"], 
                    params = paramMov["params"]
                )
            
            json_cast = response["cast"]
            df_cast = pd.DataFrame(json_cast)
            top_5_actors = df_cast.nlargest(5, 'order')['name'].tolist()
            movie["actors"] = top_5_actors

            json_crew = response["crew"]
            df_crew = pd.DataFrame(json_crew)
            director = df_crew[df_crew['job'] == 'Director']
            movie["director"] = director["name"].values[0]

            download_path = ""
            if movie["poster_path"] is not None:
                download_path = movie["poster_path"]
            else:
                download_path = movie["backdrop_path"]

            img_name = ""
            title = helper.clean_text(movie["title"])
            id_img = helper.clean_text(movie["id_tmdb"])
            img_name = id_img + "_" + title + ".jpg"
            img_path = f"{INTERNAL_IMG_SAVE_PATH}{img_name}"

            #Downlowad Image
            if download_path is not None:
                movie["img_path"] = img_path
                client.get_img(download_path, img_name)

            queries.insert_movie(cursor, movie)
        except Exception as e:
            logging.error(f"Insert Movie error: {type(e).__name__}: {e}")

    # connection.commit()
#---------------------------------------

#---------------------------------------
#Movie_Genre SECTION
#---------------------------------------
    for movie_id in movie_genre_json:
        try:
            id_mov = queries.get_movie_id(cursor, movie_id)
            for genre in movie_genre_json[movie_id]:
                id_gen = queries.get_genreMov_id(cursor, genre)
                connection.commit()
                queries.insert_movie_genres(cursor, id_mov, id_gen)
        except Exception as e:
            logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------
#Return Number of Pages of Date
    return response["total_pages"]

def get_movies_behavior(client, date, page):
    try:
        columns = ['Name', 'Popularity', 'Vote_average', 'Vote_count']
        df_dayMovies = pd.DataFrame(columns=columns)

        paramMov = endpoints.discover_movies(page, date, date)
        response = client.get(
                endpoint=paramMov["endpoint"], 
                params = paramMov["params"]
            )

        json_movies, movie_genre_json = helper.extract_movies_list(response)

        for movie in json_movies:
            df_dayMovies.loc[len(df_dayMovies)] = [movie["title"], movie["popularity"], movie["vote_average"], movie["vote_count"]]

        return response["total_pages"], df_dayMovies
    except Exception as e:
        logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")
        time.sleep(10)

def make_histogram(dataframe, column_name, file_name):

     # Create figure
    plt.figure(figsize=(12, 7))
    
    # Get data (drop NaN values)
    data = dataframe[column_name].dropna()
    
    # Calculate statistics
    max_val = data.max()
    min_val = data.min()
    avg_val = data.mean()
    median_val = data.median()

    plt.hist(data, bins=20, alpha=0.7, edgecolor='black', color='skyblue', label='Distribution')
        
    # Add reference lines
    plt.axvline(avg_val, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_val:.2f}')
    plt.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
    
    title = f'Histogram Analysis: {column_name}'
    ylabel = 'Frequency'

    # Customize plot
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(column_name, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='upper left' if pd.api.types.is_numeric_dtype(data) else 'best')
    
    # Add statistics box
    stats_text = f"""Statistics Summary:
                Maximum: {max_val:.2f}
                Minimum: {min_val:.2f}
                Average: {avg_val:.2f}
                Median: {median_val:.2f}
                Count: {len(data):,}"""

    plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9,
                      edgecolor='gold'))
    
    # Add subtitle with file info
    plt.figtext(0.5, 0.01, f"Saved as: {file_name}", 
                ha='center', fontsize=9, style='italic', color='gray')
    
    # Save and close
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":

    logging.basicConfig(
        filename="../logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

    client = TMDBClient()
    # connection = get_connection()
    # cursor = connection.cursor()
    
    #Get Genders of Movies
    #get_genreMov(client, connection, cursor)
    
    #Get Movies
    # dateList = helper.generate_dateList(START_DATE_EXTRACTION, END_DATE_EXTRACTION)
    # for date in dateList:
    #     try:
    #         page = 1
    #         pageNum = get_movies(client, connection, cursor, str(date), int(page))
    #         while page < pageNum:
    #             page += 1
    #             get_movies(client, connection, cursor, str(date), int(page))
    #     except Exception as e:
    #         logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")
    #         time.sleep(10)
    #         continue

    #Get Movies Behavior

    # columns = ['Name', 'Popularity', 'Vote_average', 'Vote_count']
    # df_allMovies = pd.DataFrame(columns=columns)

    # dateList = helper.generate_dateList(START_DATE_EXTRACTION, END_DATE_EXTRACTION)
    # for date in dateList:
    #     try:
    #         page = 1
    #         pageNum, df_dayMovies = get_movies_behavior(client, str(date), int(page))
    #         df_allMovies = pd.concat([df_allMovies, df_dayMovies], ignore_index=True)
    #         while page < pageNum:
    #             page += 1
    #             pageNum, df_dayMovies = get_movies_behavior(client, str(date), int(page))
    #             df_allMovies = pd.concat([df_allMovies, df_dayMovies], ignore_index=True)
    #     except Exception as e:
    #         logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")
    #         time.sleep(10)
    #         continue
    
    # #print(df_allMovies)
    # make_histogram(df_allMovies, "Popularity", "graphs/Popularity_histogram_80_26.png")
    # make_histogram(df_allMovies, "Vote_average", "graphs/Vote_average_histogram_80_26.png")
    # make_histogram(df_allMovies, "Vote_count", "graphs/Vote_count_histogram_80_26.png")

    #call movie_cast
    # paramMov = endpoints.credits_movies("631132")
    # response = client.get(
    #         endpoint=paramMov["endpoint"], 
    #         params = paramMov["params"]
    #     )
    
    # json_cast = response["cast"]
    # df_cast = pd.DataFrame(json_cast)
    # top_5_actors = df_cast.nlargest(5, 'order')['name'].tolist()
    # print("Actors:", top_5_actors)

    # json_crew = response["crew"]
    # df_crew = pd.DataFrame(json_crew)
    # director = df_crew[df_crew['job'] == 'Director']
    # print("Director:", director["name"].values[0])

    # json_movies, movie_genre_json = helper.extract_movies_list(response)

    # cursor.close()
    # connection.close()


