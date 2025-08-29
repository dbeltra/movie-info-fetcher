"""Main processing logic for updating CSV files with trailer links."""

import csv
import sys
from pathlib import Path
from time import sleep

from utils.colors import print_colored, print_progress_bar, Colors
from csv_handler.parser import detect_delimiter, find_column_indices
from search.youtube import search_youtube


def update_csv_with_trailers(input_file: str, delay: float = 2.0, verbose: bool = False, 
                           dry_run: bool = False, force: bool = False) -> None:
    """Main function to update CSV with trailer links"""
    
    # Validate input file
    if not Path(input_file).exists():
        print_colored(f"❌ Error: File '{input_file}' not found.", Colors.RED)
        sys.exit(1)
    
    if not input_file.lower().endswith('.csv'):
        print_colored(f"⚠️  Warning: '{input_file}' doesn't have .csv extension", Colors.YELLOW)
    
    print_colored(f"🎬 Movie Trailer Finder", Colors.BOLD)
    print_colored(f"📁 Processing file: {input_file}", Colors.BLUE)
    
    try:
        # Auto-detect delimiter
        delimiter = detect_delimiter(input_file)
        if verbose:
            print_colored(f"📋 Detected delimiter: '{delimiter}'", Colors.BLUE)
        
        # Read all rows first to modify in place
        rows = []
        with open(input_file, "r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=delimiter)
            header = next(reader)
            rows = list(reader)
        
        # Find column indices
        title_col, director_col, year_col, trailer_col = find_column_indices(header)
        
        # Validate required columns
        missing_cols = []
        if title_col is None:
            missing_cols.append("title")
        if director_col is None:
            missing_cols.append("director")
        if year_col is None:
            missing_cols.append("year")
            
        if missing_cols:
            print_colored(f"❌ Error: Could not find required columns: {', '.join(missing_cols)}", Colors.RED)
            print_colored(f"Available columns: {', '.join(header)}", Colors.YELLOW)
            sys.exit(1)
        
        # Add trailer column if it doesn't exist
        trailer_added = False
        if trailer_col is None:
            if not force and not dry_run:
                response = input(f"Add 'Trailer' column to the file? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print_colored("Operation cancelled.", Colors.YELLOW)
                    return
            
            header.append("Trailer")
            trailer_col = len(header) - 1
            trailer_added = True
            # Extend existing rows with empty trailer field
            for row in rows:
                row.append("")
        
        # Display column mapping
        print_colored(f"📊 Column mapping:", Colors.GREEN)
        print(f"  Title: {header[title_col]} (column {title_col + 1})")
        print(f"  Director: {header[director_col]} (column {director_col + 1})")
        print(f"  Year: {header[year_col]} (column {year_col + 1})")
        print(f"  Trailer: {header[trailer_col]} (column {trailer_col + 1})" + 
              (" - NEW" if trailer_added else ""))
        
        total_rows = len(rows)
        processed = 0
        skipped = 0
        found = 0
        
        print_colored(f"\n🔍 Processing {total_rows} movies...", Colors.BLUE)
        
        for i, row in enumerate(rows):
            # Ensure row has enough columns
            while len(row) <= max(title_col, director_col, year_col, trailer_col):
                row.append("")
            
            # Skip if trailer already exists and is not empty
            if row[trailer_col] and row[trailer_col].strip():
                if verbose:
                    print_colored(f"  ⏭️  Skipping: {row[title_col]} (trailer exists)", Colors.YELLOW)
                skipped += 1
                continue
            
            movie_title = row[title_col]
            movie_director = row[director_col]
            movie_year = row[year_col]
            
            if not movie_title or not movie_director or not movie_year:
                if verbose:
                    print_colored(f"  ⏭️  Skipping: Missing data in row {i+1}", Colors.YELLOW)
                skipped += 1
                continue
            
            if verbose:
                print_colored(f"  🎯 Searching: {movie_title} ({movie_year})", Colors.BLUE)
            else:
                print_progress_bar(i + 1, total_rows)

            if not dry_run:
                trailer_link = search_youtube(
                    f"{movie_title} +movie +trailer {movie_director} after:{int(movie_year) - 1}-01-01",
                    verbose=verbose
                )
                if trailer_link:
                    if verbose:
                        print_colored(f"  ✅ Found: {trailer_link}", Colors.GREEN)
                    row[trailer_col] = trailer_link
                    found += 1
                else:
                    row[trailer_col] = ""
                
                sleep(delay)
            
            processed += 1
        
        if not verbose:
            print()  # New line after progress bar
        
        # Write back to file (unless dry run)
        if not dry_run:
            with open(input_file, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile, delimiter=delimiter)
                writer.writerow(header)
                writer.writerows(rows)
        
        # Summary
        print_colored(f"\n📈 Summary:", Colors.BOLD)
        print(f"  Total movies: {total_rows}")
        print(f"  Processed: {processed}")
        print(f"  Skipped: {skipped}")
        print(f"  Trailers found: {found}")
        
        if dry_run:
            print_colored(f"🔍 Dry run complete - no changes made", Colors.YELLOW)
        else:
            print_colored(f"✅ Processing complete! File updated: {input_file}", Colors.GREEN)

    except FileNotFoundError:
        print_colored(f"❌ Error: File '{input_file}' not found.", Colors.RED)
        sys.exit(1)
    except PermissionError:
        print_colored(f"❌ Error: Permission denied writing to '{input_file}'.", Colors.RED)
        sys.exit(1)
    except KeyboardInterrupt:
        print_colored(f"\n⚠️  Operation cancelled by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
