# 🎬 Movie Trailer Finder

Automatically find and add YouTube trailer links to your movie CSV files. This CLI tool intelligently detects movie data columns and searches for trailers, adding them to your spreadsheet.

## ✨ Features

- **Smart Column Detection**: Automatically finds title, director, and year columns
- **YouTube Integration**: Finds official movie trailers automatically
- **TMDb Integration**: Discovers director's 3 most popular films
- **Flexible CSV Support**: Works with any delimiter (comma, semicolon, etc.)
- **Safe Processing**: Only adds data where none exists (won't overwrite)
- **Progress Tracking**: Beautiful progress bars and detailed logging
- **Dry Run Mode**: Preview changes before applying them
- **Rate Limiting**: Built-in delays to respect API limits

## 🚀 Quick Start

```bash
# Basic usage
python parser.py movies.csv

# Show detailed progress
python parser.py movies.csv --verbose

# Preview without making changes
python parser.py movies.csv --dry-run

# Faster processing (use with caution)
python parser.py movies.csv --delay 1.0
```

## 📋 Requirements

- Python 3.7+
- Required libraries: `requests`, `python-dotenv`, `tmdbv3api`
- TMDb API key (free from [themoviedb.org](https://www.themoviedb.org/settings/api))

Install dependencies:
```bash
pip install -r requirements.txt
# or individually:
pip install requests python-dotenv tmdbv3api
```

Create a `.env` file with your TMDb API key:
```
TMDB_API_KEY="your_api_key_here"
```

## 📊 CSV Format

Your CSV file should contain columns for:
- **Title** (movie, film, name)
- **Director** (director, filmmaker, directed)
- **Year** (year, date, released)

The tool will automatically detect these columns and optionally add:
- **Trailer** - YouTube trailer links
- **Related films** - Director's 3 most popular movies from TMDb

### Example CSV Structure

```csv
Section;Title;Director;Year
Panorama;13 Days Till Summer;Bartosz M. Kowalski;2025
Panorama;Abraham's Boys;Natasha Kermani;2025
```

After processing:
```csv
Section;Title;Director;Year;Trailer;Related films
Panorama;13 Days Till Summer;Bartosz M. Kowalski;2025;https://www.youtube.com/watch?v=abc123;Film A | Film B | Film C
Panorama;Abraham's Boys;Natasha Kermani;2025;https://www.youtube.com/watch?v=def456;Movie X | Movie Y | Movie Z
```

## 🛠 Usage

### Command Line Options

```
python parser.py <file> [options]

Arguments:
  file                    CSV file containing movie data

Options:
  -h, --help             Show help message
  -d, --delay SECONDS    Delay between searches (default: 2.0)
  -v, --verbose          Show detailed progress
  -n, --dry-run          Preview without making changes
  -f, --force            Skip confirmation prompts
  --no-related           Skip adding related films from TMDb
  --version              Show version information
```

### Examples

```bash
# Process a movie festival lineup
python parser.py festival_2025.csv

# Quick preview of what would be processed
python parser.py movies.csv --dry-run --verbose

# Batch processing with minimal delay
python parser.py large_dataset.csv --force --delay 0.5

# Detailed logging for troubleshooting
python parser.py problematic.csv --verbose

# Only add trailers, skip related films
python parser.py movies.csv --no-related
```

## 🏗 Project Structure

```
├── parser.py              # Main entry point
├── cli/
│   └── main.py           # Command-line interface
├── core/
│   └── processor.py      # Main processing logic
├── csv_handler/
│   └── parser.py         # CSV parsing utilities
├── search/
│   └── youtube.py        # YouTube search functionality
└── utils/
    └── colors.py         # Terminal formatting
```

## 🔍 How It Works

1. **File Validation**: Checks if the CSV file exists and is readable
2. **Column Detection**: Automatically identifies title, director, year columns
3. **Column Management**: Creates trailer and related films columns if needed
4. **Smart Processing**: Only processes movies without existing data
5. **YouTube Search**: Constructs optimized search queries for trailers
6. **TMDb Lookup**: Finds director's most popular films via API
7. **Safe Updates**: Writes results back to the original file

### Search Strategy

The tool creates intelligent YouTube search queries:
```
"{title} +movie +trailer {director} after:{year-1}-01-01"
```

This approach:
- Focuses on movie trailers specifically
- Includes director for better accuracy
- Uses date filtering to find relevant results
- Prioritizes official trailers over fan content

## ⚙️ Configuration

### Rate Limiting

Default delay is 2 seconds between requests to respect YouTube's rate limits. Adjust with `--delay`:

```bash
# Conservative (slower but safer)
python parser.py movies.csv --delay 3.0

# Aggressive (faster but may hit limits)
python parser.py movies.csv --delay 0.5
```

### Column Matching

The tool recognizes these column name patterns:

| Data Type | Recognized Names |
|-----------|------------------|
| Title     | title, movie, film, name |
| Director  | director, directed, filmmaker |
| Year      | year, date, released |
| Trailer   | trailer, link, url, video |
| Related   | related, films, movies, other, similar |

## 🚨 Error Handling

The tool gracefully handles:
- Missing or invalid files
- Network connectivity issues
- Rate limiting from YouTube
- Malformed CSV data
- Missing required columns
- Keyboard interruption (Ctrl+C)

## 📈 Output Examples

### Verbose Mode
```
🎬 Movie Trailer Finder
📁 Processing file: movies.csv
📊 Column mapping:
  Title: Title (column 2)
  Director: Director (column 3)
  Year: Year (column 4)
  Trailer: Trailer (column 5) - NEW

🔍 Processing 25 movies...
  🎯 Searching: Dune: Part Two (2024)
  ✅ Found: https://www.youtube.com/watch?v=Way9Dexny3w

📈 Summary:
  Total movies: 25
  Processed: 23
  Skipped: 2
  Trailers found: 21
✅ Processing complete! File updated: movies.csv
```

### Progress Bar Mode
```
🎬 Movie Trailer Finder
📁 Processing file: movies.csv
Progress: [████████████████████████████████████████████████████] 25/25 (100.0%)

📈 Summary:
  Total movies: 25
  Processed: 23
  Skipped: 2
  Trailers found: 21
✅ Processing complete! File updated: movies.csv
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source. Feel free to use, modify, and distribute.

## 🐛 Troubleshooting

### Common Issues

**"Could not find required columns"**
- Check your CSV headers contain words like "title", "director", "year"
- Use `--verbose` to see available columns

**"No video IDs found"**
- Movie might be too new or obscure
- Try adjusting the search delay
- Check your internet connection

**Rate limiting errors**
- Increase the delay: `--delay 3.0`
- Process smaller batches
- Try again later

**Permission denied**
- Ensure the CSV file isn't open in another program
- Check file permissions
- Run with appropriate user privileges

### Getting Help

Run with `--verbose` to see detailed processing information:
```bash
python parser.py movies.csv --verbose --dry-run
```

This will show exactly what the tool detects and plans to do without making changes.
