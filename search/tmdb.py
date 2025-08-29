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


def parse_multiple_directors(director_string: str) -> List[str]:
    """
    Parse a string that may contain multiple directors separated by commas, &, or 'and'.
    
    Args:
        director_string: String containing one or more director names
        
    Returns:
        List of individual director names
    """
    import re
    
    if not director_string or not director_string.strip():
        return []
    
    # Replace common separators with commas for consistent splitting
    # Handle various formats: &, and, +, /
    normalized = re.sub(r'\s*[&+/]\s*|\s+and\s+|\s*,\s*', ',', director_string.strip())
    
    # Split by comma and clean up each name
    directors = []
    for name in normalized.split(','):
        name = name.strip()
        if name and len(name) > 1:  # Avoid single character names
            directors.append(name)
    
    return directors


def search_single_director(director_name: str, limit: int = 3, verbose: bool = False) -> List[str]:
    """
    Search for movies by a single director.
    
    Args:
        director_name: Name of a single director
        limit: Number of movies to return
        verbose: Whether to show detailed output
        
    Returns:
        List of movie titles
    """
    try:
        if verbose:
            print_colored(f"    🔍 Searching for: {director_name}", Colors.BLUE)
        
        # Search for the director
        try:
            search_results = person.search(director_name)
        except Exception as search_error:
            if verbose:
                print_colored(f"    ⚠️  Not found: {director_name}", Colors.YELLOW)
            return []
        
        # Validate and safely access search results
        try:
            # Check if we have valid results
            if not search_results:
                if verbose:
                    print_colored(f"    ⚠️  Not found: {director_name}", Colors.YELLOW)
                return []
            
            # Try to get the length safely
            try:
                results_length = len(search_results)
                if results_length == 0:
                    if verbose:
                        print_colored(f"    ⚠️  Not found: {director_name}", Colors.YELLOW)
                    return []
            except (TypeError, AttributeError):
                # If we can't get length, try to access first element directly
                pass
            
            # Get the first director result (most relevant)
            director = search_results[0]
            
        except (IndexError, TypeError, AttributeError):
            if verbose:
                print_colored(f"    ⚠️  Not found: {director_name}", Colors.YELLOW)
            return []
        
        # Safely get director attributes with multiple fallback methods
        director_id = None
        director_display_name = director_name
        
        try:
            # Try different ways to access the ID
            if hasattr(director, 'id'):
                director_id = director.id
            elif hasattr(director, '__dict__') and 'id' in director.__dict__:
                director_id = director.__dict__['id']
            elif isinstance(director, dict) and 'id' in director:
                director_id = director['id']
            
            # Try different ways to access the name
            if hasattr(director, 'name'):
                director_display_name = director.name
            elif hasattr(director, '__dict__') and 'name' in director.__dict__:
                director_display_name = director.__dict__['name']
            elif isinstance(director, dict) and 'name' in director:
                director_display_name = director['name']
                
        except Exception as e:
            if verbose:
                print_colored(f"    ❌ Error accessing director attributes for '{director_name}': {e}", Colors.RED)
            return []
        
        if director_id is None:
            if verbose:
                print_colored(f"    ❌ No valid ID found for director: {director_name}", Colors.RED)
            return []
        
        if verbose:
            print_colored(f"    👤 Found: {director_display_name} (ID: {director_id})", Colors.GREEN)
        
        # Get director's movie credits
        try:
            credits = person.movie_credits(director_id)
        except Exception as e:
            if verbose:
                print_colored(f"    ❌ Failed to get credits for '{director_display_name}': {e}", Colors.RED)
            return []
        
        # Filter for directing credits and sort by popularity
        directed_movies = []
        
        try:
            crew_list = getattr(credits, 'crew', [])
        except Exception:
            crew_list = []
        
        for movie in crew_list:
            try:
                # Safely extract movie data
                job = getattr(movie, 'job', '')
                title = getattr(movie, 'title', '')
                
                if job == "Director" and title:
                    directed_movies.append({
                        "title": title,
                        "popularity": getattr(movie, 'popularity', 0),
                        "release_date": getattr(movie, 'release_date', ''),
                        "vote_average": getattr(movie, 'vote_average', 0)
                    })
            except Exception:
                # Skip movies with invalid data
                continue
        
        # Sort by popularity (descending) and take top results
        directed_movies.sort(key=lambda x: x["popularity"], reverse=True)
        top_movies = directed_movies[:limit]
        
        movie_titles = [movie["title"] for movie in top_movies]
        
        if verbose and movie_titles:
            print_colored(f"    🎬 Found {len(movie_titles)} films by {director_display_name}:", Colors.GREEN)
            for i, movie in enumerate(top_movies, 1):
                year = movie["release_date"][:4] if movie["release_date"] else "N/A"
                rating = movie["vote_average"]
                print(f"      {i}. {movie['title']} ({year}) - Rating: {rating}/10")
        
        return movie_titles
        
    except Exception as e:
        if verbose:
            print_colored(f"    ❌ Error searching for '{director_name}': {e}", Colors.RED)
        return []


def get_director_popular_movies(director_name: str, current_movie_title: str = "", limit: int = 3, verbose: bool = False) -> List[str]:
    """
    Get the most popular movies by director(s) from TMDb.
    Handles multiple directors separated by commas, &, or 'and'.
    
    Args:
        director_name: Name(s) of the director(s) to search for
        current_movie_title: Title of the current movie to exclude from results
        limit: Number of movies to return (default: 3)
        verbose: Whether to show detailed output
        
    Returns:
        List of movie titles (up to limit, excluding current movie)
    """
    if not tmdb.api_key:
        if verbose:
            print_colored("  ⚠️  TMDb API key not found in .env file", Colors.YELLOW)
        return []
    
    try:
        if verbose:
            print_colored(f"  🔍 Processing director(s): {director_name}", Colors.BLUE)
        
        # Parse multiple directors
        directors = parse_multiple_directors(director_name)
        
        if verbose and len(directors) > 1:
            print_colored(f"  👥 Found {len(directors)} directors: {', '.join(directors)}", Colors.BLUE)
        
        # Collect movies from all directors
        all_movies = []
        movies_per_director = max(1, limit // len(directors)) if len(directors) > 1 else limit
        
        for director in directors:
            director_movies = search_single_director(director, movies_per_director, verbose)
            all_movies.extend(director_movies)
        
        # Remove duplicates and exclude current movie
        seen = set()
        unique_movies = []
        current_title_lower = current_movie_title.lower().strip() if current_movie_title else ""
        
        for movie in all_movies:
            movie_lower = movie.lower().strip()
            
            # Skip if already seen
            if movie in seen:
                continue
                
            # Skip if it matches the current movie (only if current_movie_title is provided)
            if current_title_lower and (
                movie_lower == current_title_lower or 
                current_title_lower in movie_lower or 
                movie_lower in current_title_lower
            ):
                continue
                
            seen.add(movie)
            unique_movies.append(movie)
        
        # Return up to the requested limit
        result = unique_movies[:limit]
        
        if verbose and current_movie_title:
            print_colored(f"  🚫 Excluded current movie: {current_movie_title}", Colors.YELLOW)
        
        if verbose:
            print_colored(f"  🎭 Total unique films found: {len(result)}", Colors.GREEN)
        
        return result
        
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
