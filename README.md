
# Web Crawler Project

## Overview

This project implements a web crawler that traverses websites within the `.nz` domain, starting from a list of seed URLs and following sub-links while respecting `robots.txt` restrictions. It uses a breadth-first search (BFS) approach with priority given to new domains, extracts links, and logs details about each crawl. Additionally, the crawler tracks specific file types (`.css`, `.js`, `.png`, `.svg`) encountered on each page and logs relevant statistics.

## Features

1. **Seed Queue Initialization**: Reads a list of seed URLs from `nz_domain_seeds_list.txt`, which are added to a priority queue based on domain and URL length.
2. **BFS with Domain Priority**: The crawler prioritizes new domains to ensure diverse link traversal within the `.nz` domain.
3. **URL Validation and Robots.txt Compliance**: The crawler validates URLs, checks `robots.txt` to ensure compliance, and ignores disallowed paths.
4. **Link Extraction**: Uses BeautifulSoup to parse HTML and extract sub-links, which are added to the crawl queue if they haven't been visited.
5. **File Type Tracking**: Counts specific file types (.css, .js, .png, .svg) found on each page.
6. **Logging**: Logs crawled URLs, depth, page size, and HTTP status code to provide an overview of the crawl’s progress.
7. **Termination Condition**: Runs for a predefined duration (e.g., 5 hours or 18,000 seconds), after which it automatically stops.

## Project Structure

- **`Web Crawling.py`**: Python script implementing the web crawler.
- **`nz_domain_seeds_list.txt`**: Text file containing initial seed URLs.
- **`first_logs.txt`** & **`second_logs.txt`**: Log files recording the details of each crawl.
- **`first_logs.txt-seed-list.txt`** & **`second_logs.txt-seed-list.txt`**: Files containing the seed lists used for specific crawling sessions.
- **`explain.txt`**: Detailed explanation of the project and how it operates.

## Installation

Ensure the following packages are installed:
```bash
pip install bs4 html5lib
```

## Usage

1. **Prepare the Seed List**: Create a file named `nz_domain_seeds_list.txt` with URLs to be used as the starting points for the crawl.
2. **Run the Crawler**:
   - Open the Python script `Web Crawling.py`.
   - Use the function `start_the_crawler` with appropriate parameters:
     ```python
     start_the_crawler(seedlist, logFileName, durationOfCrawl)
     ```
   - Example:
     ```python
     start_the_crawler(lines[60:80], "second_logs.txt", 18000)
     ```
   - Parameters:
     - `seedlist`: List of initial seed URLs.
     - `logFileName`: Name of the log file for recording crawl details.
     - `durationOfCrawl`: Duration in seconds for which the crawler will run (e.g., 18000 seconds for 5 hours).

## How It Works

1. **Seed Queue Initialization**: Reads URLs from `nz_domain_seeds_list.txt` and adds them to a priority queue for efficient management.
2. **URL Priority Queue**: The crawler prioritizes URLs based on domain, enhancing diversity across `.nz` domains.
3. **Link Extraction and Absolute URL Conversion**: Converts relative links to absolute URLs and validates them before adding to the queue.
4. **Logging**: Logs details such as URL, crawl depth, page size, and status code into the specified log file.
5. **File Type Counting**: Tracks occurrences of `.css`, `.js`, `.png`, and `.svg` file types.

## Limitations

- **Time-Limited Execution**: Crawler stops after a specified duration, configurable with `durationOfCrawl`.
- **Tracked File Types**: Only tracks specific file types (`.css`, `.js`, `.png`, `.svg`) along with the total count of crawled pages.

## Known Issues

No known bugs, but further optimizations could include multi-threading for faster crawling.

## Example Execution

After setting up, you can run the following command to start the crawler:
```python
start_the_crawler(lines[60:80], "second_logs.txt", 18000)
```
Expected Output:
- A log file (`second_logs.txt`) with details on crawled URLs, depth, page size, and status code.
- A count of encountered file types: `.css`, `.js`, `.png`, `.svg`.

## Additional Resources

- **BeautifulSoup**: Used for HTML parsing.
- **urllib**: Handles HTTP requests for crawling.
