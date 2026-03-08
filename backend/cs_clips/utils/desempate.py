import numpy as np


def desempate_ponderato(videos):
    """
    Algoritmo di tie-break: seleziona il miglior video
    tra quelli con media voto massima.
    Si basa su: numero di voti, visualizzazioni,
    numero di like, tutto normalizzato.
    """
    if not videos:
        return None
    if len(videos) == 1:
        return videos[0]

    # Estrarre tutti i valori
    num_ratings = [v.ratings.count() for v in videos]
    num_likes = [v.likes.count() for v in videos]
    num_views = [v.views for v in videos]

    # Normalizzazione percentile
    def normalize(arr):
        arr = np.array(arr)
        if arr.max() == arr.min():
            return np.ones(len(arr))
        return (arr - arr.min()) / (arr.max() - arr.min())

    n_ratings_norm = normalize(num_ratings)
    n_likes_norm = normalize(num_likes)
    n_views_norm = normalize(num_views)

    # Pesi personalizzabili!
    weights = {
        "ratings": 0.5,  # peso numero voti
        "likes": 0.2,  # peso numero like
        "views": 0.3,  # peso visualizzazioni
    }

    scores = (
        weights["ratings"] * n_ratings_norm
        + weights["likes"] * n_likes_norm
        + weights["views"] * n_views_norm
    )

    # Ritorna il video con score massimo
    idx = np.argmax(scores)
    return videos[idx]
