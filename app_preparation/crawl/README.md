# Play Store Crawling

This directory contains code to crawl the Play Store.

## Run

- Run the following steps in the following order:
  - `npm run seed`: Retrieves the seed apps
  - `npm run related`: Recursively retrieves the related apps
  - `npm run info`: Retrieves the metadata for each app
  - `npm run db2csv`: Writes the package names to a CSV
- The outputs are the files `<current_date>.db` and `<current_date-free.csv>`