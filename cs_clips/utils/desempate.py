import numpy as np

def desempate_ponderato(videos):
    """
    Algoritmo di tie-break: seleziona il miglior video tra quelli con media voto massima.
    Si basa su: media voto, numero di voti, visualizzazioni, numero di commenti, tutto normalizzato.
    """
    # Estrarre tutti i valori
    num_ratings = [v.ratings.count() for v in videos]
    num_comments = [v.comments.count() for v in videos]
    num_views = [v.views for v in videos]

    # Normalizzazione percentile
    def normalize(arr):
        arr = np.array(arr)
        if arr.max() == arr.min():
            return np.ones(len(arr))
        return (arr - arr.min()) / (arr.max() - arr.min())

    n_ratings_norm = normalize(num_ratings)
    n_comments_norm = normalize(num_comments)
    n_views_norm = normalize(num_views)

    # Pesi personalizzabili!
    weights = {
        'ratings': 0.5,      # peso numero voti
        'comments': 0.2,     # peso numero commenti
        'views': 0.3,        # peso visualizzazioni
    }

    scores = (
        weights['ratings'] * n_ratings_norm +
        weights['comments'] * n_comments_norm +
        weights['views'] * n_views_norm
    )

    # Ritorna il video con score massimo
    idx = np.argmax(scores)
    return videos[idx]
