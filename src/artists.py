"""
File: artists.py
Description: Constructs Sankey diagrams based of the artist data
Name: Reema Sharma
Date: 3 Oct 2023
"""

import pandas as pd
import sankey_proto as sk


def group_by(df, grouping_cols, threshold=20):
    """ Returns a dataframe counts the number of groups based on the grouping_cols given
    Args:
        df: a pandas.DataFrame
        grouping_cols: a list of column names to group by
        threshold: the minimum count for a row; anything under the threshold will be filtered out

    Returns: df: a filtered dataframe
    """
    df = df.groupby(grouping_cols).size().reset_index(name='Count')
    
    if 'Decade' in grouping_cols:
        df = df.dropna(subset=['Decade']).query('Decade != 0')
    
    df = df[df['Count'] >= threshold]
    return df


def main():
    # Read the JSON file into a dataframe
    art = pd.read_json("Artists.json", orient="records")

    # Cleaning data
    art = art[art.Nationality != "Nationality unknown"]

    # Create the 'Decade' column
    art['Decade'] = (art['BeginDate'] // 10) * 10
    
    # Create three different grouped dataframes and then 2-layered Sankey diagrams
    nat_dec_df = group_by(art, ['Nationality', 'Decade'], threshold=50)
    sk.make_sankey(nat_dec_df, 'Nationality', 'Decade', vals='Count', title_text='Nationality vs Decade')

    nat_gen_df = group_by(art, ['Nationality', 'Gender'], threshold=60)
    sk.make_sankey(nat_gen_df, 'Nationality', 'Gender', vals='Count', title_text='Nationality vs Gender')

    gen_dec_df = group_by(art, ['Gender', 'Decade'], threshold=50)
    sk.make_sankey(gen_dec_df, 'Gender', 'Decade', vals='Count', title_text='Gender vs Decade')

    sk.make_sankey(art, ['Nationality', 'Gender', 'Decade'], vals='Count', threshold=50)


if __name__ == '__main__':
    main()
