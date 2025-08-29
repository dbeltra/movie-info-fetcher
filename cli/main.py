"""Command-line interface for the Movie Trailer Finder."""

import argparse
from utils.colors import print_colored, Colors
from core.processor import update_csv_with_trailers


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="🎬 Movie Trailer Finder - Automatically add YouTube trailer links and related films to movie CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s movies.csv                    # Process movies.csv with default settings
  %(prog)s data.csv --verbose            # Show detailed progress
  %(prog)s films.csv --delay 1.0         # Faster processing (1 second delay)
  %(prog)s movies.csv --dry-run          # Preview what would be processed
  %(prog)s data.csv --force              # Skip confirmation prompts

The tool automatically detects:
  - CSV delimiter (comma, semicolon, etc.)
  - Title, Director, Year columns (flexible matching)
  - Existing Trailer and Related films columns or creates them

Features:
  - YouTube trailer search
  - TMDb integration for director's popular films
  - Only processes missing data (won't overwrite existing content)
        """
    )
    
    parser.add_argument(
        'file',
        help='CSV file containing movie data'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=2.0,
        help='Delay between YouTube searches in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress and search results'
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Preview processing without making changes'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '--no-related',
        action='store_true',
        help='Skip adding related films from TMDb'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Movie Trailer Finder 1.0.0'
    )
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate delay
    if args.delay < 0.1:
        print_colored("⚠️  Warning: Very short delay may cause rate limiting", Colors.YELLOW)
    
    update_csv_with_trailers(
        input_file=args.file,
        delay=args.delay,
        verbose=args.verbose,
        dry_run=args.dry_run,
        force=args.force,
        include_related=not args.no_related
    )
