# Grant Scraper Data Files

This project uses the following key files for grant data processing:

## Files

- **`csv_worker.py`**  
  Script or module for processing and converting grant data to and from CSV format.  
  Use this to manipulate or analyze grant data in tabular form.

- **`grants_20250812T014733Z.json`**  
  The raw export of grant opportunities in JSON format.  
  This file contains unprocessed grant data as fetched from the source.

- **`grants_20250812T014733Z_cleaned.json`**  
  The cleaned and processed version of the raw JSON export.  
  Use this file for downstream analysis, as it has improved formatting and possibly filtered or standardized fields.

## Typical Workflow

1. **Fetch and Export**  
   Obtain the raw grant data and save it as  
   `grants_20250812T014733Z.json`.

2. **Clean Data**  
   Process the raw JSON to remove inconsistencies or unwanted fields,  
   saving the result as `grants_20250812T014733Z_cleaned.json`.

3. **CSV Processing**  
   Use `csv_worker.py` to convert between JSON and CSV,  
   or to perform further data analysis.

---

For more details, see the code in **`csv_worker.py`**  
and the data files in the **`grants_exports/`** directory.
