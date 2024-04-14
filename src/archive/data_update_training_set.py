import pandas as pd

from util__clean_text import clean_message_body


def update_training_data(df0, df1):
    """
    df1 is a subset of the data in df, and it contains the "expected" column, which is not contained in df.
    The only column we can use to match rows from df1 to df is the "body" column.
    If we assume that the "body" column is unique, we can use it to match rows.
    Create a new column in both DataFrames that contains the first 25 alphanumeric characters from the "body" column.
    Create an empty DataFrame with all the columns from df and the "expected" column from df1.
    For each row in df1, copy the matching row from df to the new DataFrame and add the "expected" value from df1.
    """

    # Clean the message body
    df0["body_clean"] = df0["body"].apply(clean_message_body).str.lower().str.strip()
    df1["body_clean"] = df1["body"].apply(clean_message_body).str.lower().str.strip()

    df0["body_match"] = df0["body_clean"].str.replace(r"\W", "", regex=True).str[:25]
    df1["body_match"] = df1["body_clean"].str.replace(r"\W", "", regex=True).str[:25]

    rows_to_append = []  # Collect rows here for efficient appending
    unmatched_rows = []  # Collect unmatched rows here for reporting

    for index, row in df1.iterrows():
        match = df0[df0["body_match"] == row["body_match"]]
        if len(match) == 1:
            # Create a dictionary with the correct structure, including the 'expected' value
            new_row_data = match.iloc[0].to_dict()
            new_row_data["expected"] = row[
                "expected"
            ]  # Add the 'expected' column value
            rows_to_append.append(new_row_data)  # Append the dictionary directly
        else:
            message_id = row["id"]
            unmatched_rows.append(message_id)

    # Now create df2 directly from the list of dictionaries
    df2 = pd.DataFrame(rows_to_append)

    # Get a list of ids that are in df2
    ids_in_df2 = df2["id"].unique()

    # Filter df for rows where 'id' is not in the list of ids_in_df2
    df0["expected"] = None
    df3 = df0[~df0["id"].isin(ids_in_df2)]
    df0.drop(columns=["expected"], inplace=True)

    # Remove the temporary columns
    df0.drop(columns=["body_clean", "body_match"], inplace=True)
    df1.drop(columns=["body_clean", "body_match"], inplace=True)
    df2.drop(columns=["body_clean", "body_match"], inplace=True)
    df3.drop(columns=["body_clean", "body_match"], inplace=True)

    return df2, df3, unmatched_rows


def main():
    """Update the training data."""

    uid = "zhpb4"

    df = pd.read_excel(f"{uid}_gmail_messages.xlsx")
    df1 = pd.read_excel("manual_review.xlsx")
    df2, df3, unmatched_rows = update_training_data(df, df1)

    # Save the updated DataFrames to Excel files
    df2.to_excel(f"{uid}_training_data.xlsx", index=False)
    df3.to_excel(f"{uid}_untrained_data.xlsx", index=False)

    # Report unmatched rows
    if len(unmatched_rows) > 0:
        print(f"Unmatched rows: {len(unmatched_rows)}")
        print(f"Matched rows: {len(df2)}")
        print(unmatched_rows)


if __name__ == "__main__":
    main()
