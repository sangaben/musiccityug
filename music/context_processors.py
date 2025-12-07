# music/context_processors.py

from .models import Genre  # adjust according to your model

def genres(request):
    """
    Makes all genres available in templates globally.
    """
    all_genres = Genre.objects.all()  # or whatever query you need
    return {
        'all_genres': all_genres
    }
