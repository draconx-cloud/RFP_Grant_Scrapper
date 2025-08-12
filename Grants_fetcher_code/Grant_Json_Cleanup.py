from pathlib import Path
import pandas as pd

def clean_grants_json(input_json_path: str, output_json_path: str) -> None:
    """
    Cleans the grants JSON export by:
      - Dropping rows with missing required fields
      - Removing unneeded columns
      - Filling missing values in selected columns with 'Not Provided'
      - Marking estimated post date as redundant if posted date exists
      - Saving cleaned data to a pretty JSON file

    Args:
        input_json_path (str): Path to the input JSON file.
        output_json_path (str): Path to save the cleaned JSON file.
    """
    input_path = Path(input_json_path)
    output_path = Path(output_json_path)

    # ---- Load ----
    with input_path.open("r", encoding="utf-8") as f:
        grant_df = pd.read_json(f)

    # ---- Drop rows if any required column is missing/empty ----
    required_cols = [
        "OPPORTUNITY_NUMBER",
        "OPPORTUNITY_ID",
        "OPPORTUNITY_NUMBER_LINK",
        "OPPORTUNITY_TITLE",
    ]
    grant_df[required_cols] = grant_df[required_cols].replace("", pd.NA)
    grant_df = grant_df.dropna(subset=required_cols)

    # ---- Drop unneeded columns ----
    drop_cols = [
        "SYNOPSIS_ARCHIVED",
        "VERSION",
        "LAST_UPDATED_DATETIME",
        "OPPORTUNITY_PACKAGE",
    ]
    grant_df = grant_df.drop(columns=drop_cols, errors="ignore")

    # ---- Fill blanks/NA in specific columns ----
    fill_cols = [
        "GRANTOR_CONTACT",
        "GRANTOR_CONTACT_PHONE",
        "GRANTOR_CONTACT_EMAIL",
        "LINK_TO_ADDITIONAL_INFORMATION",
        "CATEGORY_OF_FUNDING_ACTIVITY",
        "FUNDING_CATEGORY_EXPLANATION",
        "FUNDING_INSTRUMENT_TYPE",
        "ASSISTANCE_LISTINGS",
        "ESTIMATED_TOTAL_FUNDING",
        "EXPECTED_NUMBER_OF_AWARDS",
        "AWARD_CEILING",
        "AWARD_FLOOR",
    ]
    grant_df[fill_cols] = (
        grant_df[fill_cols]
        .replace(["", "N/A", "n/a", "NA"], pd.NA)
        .fillna("Not Provided")
    )

    # ---- If posted date exists and estimated post date exists, mark estimated as redundant ----
    date_cols = ["POSTED_DATE", "ESTIMATED_POST_DATE"]
    grant_df[date_cols] = grant_df[date_cols].replace("", pd.NA)
    mask = grant_df["POSTED_DATE"].notna() & grant_df["ESTIMATED_POST_DATE"].notna()
    grant_df.loc[mask, "ESTIMATED_POST_DATE"] = "Opportunity already posted"

    # ---- Save pretty JSON ----
    grant_df.to_json(output_path, orient="records", indent=4, force_ascii=False)
