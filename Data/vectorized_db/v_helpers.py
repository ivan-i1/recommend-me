from db.connection import get_connection
from db import queries
import pandas as pd
import random
import mmh3
import numpy as np
import gensim.downloader as api
import ast
import faiss

model = api.load("glove-wiki-gigaword-50")
def movie_top_words_5_vector(list_text, reducir_a_5D=True):

    if list_text == "" or list_text == None or list_text == []:
        return np.zeros(5, dtype=np.float32)

    top_5_vectors = []
    for text in list_text:
    
        words = text.lower().split()
        words_vectors = []
    
        for word in words:
            try:
                vector_50d = model[word]
            except KeyError:
                vector_50d = np.zeros(50)
            
            if not reducir_a_5D:
                return vector_50d
            
            vector_5d = np.zeros(5)
            bloque = 50 // 5 
    
            for i in range(5):
                inicio = i * bloque
                fin = inicio + bloque
                vector_5d[i] = np.mean(vector_50d[inicio:fin])
                
            words_vectors.append(vector_5d)
        top_5_vectors.append(np.mean(words_vectors, axis=0))
        
    return np.round(np.mean(top_5_vectors, axis=0), 7)

def movie_multiply_num_vector(num, dimensions=2):
    vector = []

    for i in range(dimensions):
        vector.append(float(num))

    return vector

def movie_hashing_trick(text, dimensions=64, seed_offset=0):

    if text == "" or text == None or text == []:
        return np.zeros(dimensions, dtype=np.float32)

    if not text or not isinstance(text, str):
        text = str(text)
    
    hash_num = mmh3.hash(text, seed=42)
    
    vector = np.zeros(dimensions, dtype=np.float32)
    
    prime1 = 2654435761  
    prime2 = 5915587277
    
    for i in range(dimensions):

        seed = (hash_num ^ (i * prime1) ^ (seed_offset * prime2)) & 0xFFFFFFFF
        
        rng = np.random.RandomState(seed)

        value = rng.uniform(low=-10.0, high=10.0)
        vector[i] = value
    
    return vector


def movie_hashing_trick_list(list_text, dimensions=64, seed_offset=0):

    if list_text == "" or list_text == None or list_text == []:
        return np.zeros(dimensions, dtype=np.float32)

    text_vectors = []
    for text in list_text:
        if not text or not isinstance(text, str):
            text = str(text)
        
        hash_num = mmh3.hash(text, seed=42)
        
        vector = np.zeros(dimensions, dtype=np.float32)
        
        prime1 = 2654435761  
        prime2 = 5915587277
        
        for i in range(dimensions):
    
            seed = (hash_num ^ (i * prime1) ^ (seed_offset * prime2)) & 0xFFFFFFFF
            
            rng = np.random.RandomState(seed)
    
            value = rng.uniform(low=-10.0, high=10.0)
            vector[i] = value
            text_vectors.append(vector)
    
    return np.mean(text_vectors, axis=0)

def movie_date_vector(release_date, num=3):
    year = str(release_date).split('-')[0]
    year = int(year) - 2000
    return movie_multiply_num_vector(year, num)

def safe_literal_eval(x):
    if pd.isna(x):
        return []
    
    if isinstance(x, list):
        return x  # Ya es lista
    
    if isinstance(x, str):
        x = x.strip()
        if x and x.startswith('[') and x.endswith(']'):
            try:
                return ast.literal_eval(x)
            except:
                pass
        return [x] if x else []
    
    return []

def movie_get_gender_movie(cursor, movie_id, dimension=7):

    gender = queries.get_gender_movie(cursor, movie_id)
    if gender == "" or gender == None:
        return np.zeros(dimension, dtype=np.float32)
    return movie_hashing_trick_list(gender,dimension)

def movie_vectorized_table(cursor, movie_df: pd.DataFrame) -> pd.DataFrame:
    df_vectorized = pd.DataFrame({
        "id": movie_df['id'],
        'adult': movie_df['adult'].apply(lambda x: movie_multiply_num_vector(x, 2)),
        'original_lenguaje': movie_df['original_lenguaje'].apply(lambda x: movie_hashing_trick(x, 4)),
        'title': movie_df['title'].apply(lambda x: movie_hashing_trick_list(x, 3)),
        'keywords': movie_df['keywords'].apply(lambda x: movie_top_words_5_vector(ast.literal_eval(x))),
        'popularity': movie_df['popularity'].apply(lambda x: movie_multiply_num_vector(x, 3)),
        'release_date': movie_df['release_date'].apply(lambda x: movie_date_vector(x, 3)),
        'director': movie_df['director'].apply(lambda x: movie_hashing_trick(x, 5)),
        'actors': movie_df['actors'].apply(lambda x: movie_hashing_trick_list(safe_literal_eval(x), 5)),
        'vote_average': movie_df['vote_average'].apply(lambda x: movie_multiply_num_vector(x, 3)),
        'vote_count': movie_df['vote_count'].apply(lambda x: movie_multiply_num_vector(float(x) / 1000, 3)),
        'gender': movie_df['id'].apply(lambda x: movie_get_gender_movie(cursor, x,7))
    })

    vector_columns = ['adult','original_lenguaje','title','keywords','popularity',
                    'release_date', 'director', 'actors', 'vote_average',
                    'vote_count', 'gender']
    df_vectorized['movie_vector'] = df_vectorized[vector_columns].apply(
        lambda row: np.concatenate([row[col] for col in vector_columns]),
        axis=1
    )
    return df_vectorized