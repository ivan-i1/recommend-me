import numpy as np
import faiss

def get_distance_vectors(dimension, vectors, movie_vec, num_vec):
    index = faiss.IndexFlatL2(dimension)
    index.add(np.vstack(vectors))
    query = np.array(movie_vec, dtype=np.float32).reshape(1, -1)
    D, I = index.search(query, num_vec)
    return I