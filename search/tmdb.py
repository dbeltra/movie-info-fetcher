"""TMDb API integration for finding director's popular movies using tmdbv3api."""

import os
from typing import List, Optional
from dotenv import load_dotenv
from tmdbv3api import TMDb, Person

from utils.colors import print_colored, Colors

# Load environment variables
load_dotenv()

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = 'en'
tmdb.debug = False

person = Person()


def get_director_popular_movies(director_name: str, limit: int = 3, verbose: bool = False) -> List[str]:
    """
    Get the most popular movies by a director from TMDb.
    
    Args:
        director_name: Name of the director to search for
        limit: Number of movies to return (default: 3)
        verbose: Whether to show detailed output
        
    Returns:
        List of movie titles (up to limit)
    """
    if not tmdb.api_key:
        if verbose:
            print_colored("  ⚠️  TMDb API key not found in .env file", Colors.YELLOW)
        return []
    
    try:
        if verbose:
            print_colored(f"  🔍 Searching TMDb for director: {director_name}", Colors.BLUE)
        
        # Search for the director
        search_results = person.search(director_name)
        
        if not search_results:
            if verbose:
                print_colored(f"  ⚠️  Director not found: {director_name}", Colors.YELLOW)
            return []
        
        # Get the first director result (most relevant)
        director = search_results[0]
        director_id = director.id
        
        if verbose:
            print_colored(f"  👤 Found director: {director.name} (ID: {director_id})", Colors.GREEN)
        
        # Get director's movie credits
        credits = person.movie_credits(director_id)
        
        # Filter for directing credits and sort by popularity
        directed_movies = []
        for movie in credits.crew:
            if movie.job == "Director" and hasattr(movie, 'title') and movie.title:
                directed_movies.append({
                    "title": movie.title,
                    "popularity": getattr(movie, 'popularity', 0),
                    "release_date": getattr(movie, 'release_date', ''),
                    "vote_average": getattr(movie, 'vote_average', 0)
                })
        
        # Sort by popularity (descending) and take top results
        directed_movies.sort(key=lambda x: x["popularity"], reverse=True)
        top_movies = directed_movies[:limit]
        
        movie_titles = [movie["title"] for movie in top_movies]
        
        if verbose and movie_titles:
            print_colored(f"  🎬 Found {len(movie_titles)} popular films:", Colors.GREEN)
            for i, movie in enumerate(top_movies, 1):
                year = movie["release_date"][:4] if movie["release_date"] else "N/A"
                rating = movie["vote_average"]
                print(f"    {i}. {movie['title']} ({year}) - Rating: {rating}/10")
        
        return movie_titles
        
    except Exception as e:
        if verbose:
            print_colored(f"  ❌ TMDb API error for '{director_name}': {e}", Colors.RED)
        return []


def format_related_films(movies: List[str]) -> str:
    """Format the list of movies for CSV storage."""
    if not movies:
        return ""
    return " | ".join(movies)


def test_tmdb_connection() -> bool:
    """Test if TMDb API is accessible with the current key."""
    if not tmdb.api_key:
        return False
    
    try:
        # Try a simple search to test the connection
        test_results = person.search("Christopher Nolan")
        return len(test_results) > 0
    except:
        return False
