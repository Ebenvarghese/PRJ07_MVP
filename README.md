# PRJ-07: Multi-Database Entity Resolution & Unified Data Repository

## Overview

This project is a Flask-based data integration platform that combines records from multiple datasets into a unified repository. It performs rule-based field mapping, data cleaning, and progressive entity enrichment to identify the same person across different data sources.

## Features

- Import data from 4 different CSV datasets
- Rule-based field mapping
- Data cleaning and normalization
- SQLite unified repository
- Progressive enrichment:
  - Email → Phone → Username → Member ID
- Source traceability
- Unified search
- Processing statistics dashboard

## Technologies Used

- Python
- Flask
- Pandas
- SQLite
- HTML
- CSS

## Project Structure

PRJ07_MVP/
├── app.py
├── requirements.txt
├── entity_repo.db
├── README.md
├── data/
│   ├── hr.csv
│   ├── business.csv
│   ├── startup.csv
│   └── contact.csv
├── templates/
│   └── index.html
└── static/
    └── style.css

## How It Works

1. Import demo datasets.
2. Normalize different column names.
3. Store records in SQLite.
4. Search using Email, Phone, Username, or Member ID.
5. Progressively enrich records across all datasets.
6. Display one unified master entity with source traceability.

## Example

Searching:

john@example.com

returns:

- Name: John Doe
- Phone: 9876543210
- Username: johndoe
- Member ID: M001
- Company: TechNova
- Address: Mumbai

## Future Improvements

- SQL dump support
- Fuzzy matching
- Background processing
- Interactive graph visualization
- Bulk uploads