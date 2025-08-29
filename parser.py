import csv
import requests
from time import sleep
import sys
import re

TITLE_COLUMN = 1  # 0 is the first column
DIRECTOR_COLUMN = 2  # 0 is the first column
YEAR_COLUMN = 3  # 0 is the first column


def search_youtube(query):
    try:
        search_url = f"https://www.youtube.com/results?search_query={query}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Use regex to find video IDs
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)

        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        else:
            print(f"No video IDs found for query: {query}")
            return None
    except requests.RequestException as e:
        print(f"Error searching for '{query}': {e}", file=sys.stderr)
    return None


def update_csv_with_trailers(input_file, output_file):
    try:
        with open(input_file, "r", newline="", encoding="utf-8") as infile, open(
            output_file, "w", newline="", encoding="utf-8"
        ) as outfile:

            reader = csv.reader(infile, delimiter=";")
            writer = csv.writer(outfile, delimiter=";")

            header = next(reader)
            header.append("Trailer")
            writer.writerow(header)

            total_rows = sum(1 for _ in reader)
            infile.seek(0)
            next(reader)

            for i, row in enumerate(reader, 1):
                movie_title = row[TITLE_COLUMN]
                movie_director = row[DIRECTOR_COLUMN]
                movie_year = row[YEAR_COLUMN]
                print(f"Processing {i}/{total_rows}: {movie_title}")

                trailer_link = search_youtube(
                    f"{movie_title} +movie +trailer {movie_director} after:{int(movie_year) - 1}-01-01 "
                )
                if trailer_link:
                    print(f"Found trailer: {trailer_link}")
                row.append(trailer_link if trailer_link else "")
                writer.writerow(row)

                sleep(2)  # Increased delay to avoid rate limiting

                print(f"Progress: {i}/{total_rows} ({i / total_rows * 100:.2f}%)")

        print(f"Processing complete. Output saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
    except PermissionError:
        print(
            f"Error: Permission denied when trying to write to '{output_file}'.",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    input_file = "input.csv"
    output_file = "output.csv"
    update_csv_with_trailers(input_file, output_file)
