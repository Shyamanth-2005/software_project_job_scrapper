# Software Project Submission (Shyamanth Reddy M 23BAI1285)

## JobFunnel Setup Guide

This guide will help you set up and run JobFunnel to search for job listings across multiple platforms.

## Quick Start

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd job_scraper
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 4. Install JobFunnel

```bash
pip install git+https://github.com/PaulMcInnis/JobFunnel.git
```

### 5. Download Configuration

```bash
python -c "import urllib.request; urllib.request.urlretrieve('https://git.io/JUWeP', 'my_settings.yaml')"
```

### 6. Run JobFunnel

```bash
funnel load -s my_settings.yaml
```

## What is JobFunnel?

JobFunnel is a tool that aggregates job listings from multiple job search platforms into a single, manageable interface. It helps you:

- Search across multiple job boards simultaneously (Indeed, Monster, Glassdoor, etc.)
- Filter and organize job listings
- Avoid duplicate applications
- Track your job search progress
- Export results to CSV format

## Configuration

The `my_settings.yaml` file contains all the configuration settings for your job search. You can customize:

- **Search queries**: Job titles, keywords, locations
- **Platforms**: Which job sites to search (Indeed, Monster, etc.)
- **Filters**: Salary range, experience level, date posted, remoteness
- **Output format**: How results are saved and organized

### Example Settings

After downloading the configuration file, edit `my_settings.yaml` to match your preferences:

```yaml
search:
  province: "CA" # or your state/province code
  city: "San Francisco"
  keywords:
    - "software engineer"
    - "python developer"
  providers:
    - Indeed
    - Glassdoor
  max_listing_days: 30
  remoteness: "Any" # Any, Remote, OnSite

output:
  master_csv: "master_list.csv"
  block_list: "block_list.json"
  duplicates_list: "duplicates_list.json"

filters:
  blocked_company_names:
    - "Company to avoid"
```

## Usage

### Basic Search

```bash
funnel load -s my_settings.yaml
```

### Without Scraping (Use Cache)

```bash
funnel load -s my_settings.yaml --no-scrape
```

### Recover from Cache

```bash
funnel load -s my_settings.yaml --recover
```

## Output

JobFunnel generates:

- **master_list.csv**: Main file containing all job listings with columns:
  - Job title, company, location
  - Description, salary (if available)
  - Post date, scrape date
  - Status (NEW, APPLIED, INTERVIEW, REJECTED, etc.)
  - Provider, remoteness, tags
- **Cache files**: Pickled job data for offline access
- **block_list.json**: Jobs you've blocked/rejected
- **duplicates_list.json**: Detected duplicate listings
- **Logs**: Detailed scraping and filtering information

## Features

- **Multi-platform scraping**: Search Indeed, Monster, Glassdoor simultaneously
- **Duplicate detection**: Automatically identifies similar job postings
- **Status tracking**: Mark jobs as applied, interviewed, rejected, etc.
- **Date filtering**: Accept multiple date formats in CSV
- **Flexible filtering**: Block companies, filter by remoteness, location, and more
- **Proxy support**: Configure proxy for scraping if needed

## Troubleshooting

- **ModuleNotFoundError**: Ensure virtual environment is activated and dependencies are installed
- **Connection errors**: Check internet connection and verify job platforms are accessible
- **Configuration errors**: Validate your `my_settings.yaml` syntax and paths
- **Date parsing issues**: The tool now supports multiple date formats (%Y-%m-%d, %d-%m-%Y, %m/%d/%Y, etc.)
- **Rate limiting**: Some platforms may have rate limits; the tool includes delays between requests

## Project Structure

```
job_scraper/
├── .venv/                  # Virtual environment (ignored by git)
├── .gitignore             # Git ignore file
├── my_settings.yaml       # Configuration file
├── master_list.csv        # Output CSV with job listings
├── block_list.json        # Blocked jobs list
├── duplicates_list.json   # Duplicate jobs list
└── README.md              # This file
```

---
