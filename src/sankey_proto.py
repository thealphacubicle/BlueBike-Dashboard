"""
File: sankey_proto.py
Description: A simple library containing the Sankey function
Name: Reema Sharma
Date: 3 Oct 2023
"""

import plotly.graph_objects as go
import pandas as pd

def _code_mapping(df, src, targ):
    """ Encodes source and target columns in a dataframe

    Args:
        df: DataFrame
        src: source column
        targ: target column
    Returns:
        a tuple of the encoded dataframe and a list of the unique labels
    """
    # Gets all unique labels in source and target columns
    labels = list(set(list(df[src]) + list(df[targ])))

    # Generates integer values that correspond to length of labels
    codes = list(range(len(labels)))

    # Maps the unique labels to the list of integer codes
    lc_map = dict(zip(labels, codes))

    # Replace the actual String names with the integer codes in the source and target columns
    df = df.replace({src: lc_map, targ: lc_map})

    # Return the encoded dataframe and the respective labels
    return df, labels


def _stacked_sankey(df, *columns):
    """
    Creates a stack of dataframes for a multi-sankey diagram.

    Args:
        df: DataFrame used to create the stacked DataFrame.
        columns: List of columns needed to build a stack.

    Returns:
        stacked: A stacked DataFrame.
    """
    # Create pairs of consecutive columns
    column_pairs = [(columns[i], columns[i + 1]) for i in range(len(columns) - 1)]

    # Initialize an empty list to hold the aggregated DataFrames
    aggregated_dfs = []

    for src, targ in column_pairs:
        # Group and count using the current pair of columns
        aggregated_df = df.groupby([src, targ]).size().reset_index(name='Count')

        # Filter out rows with '0' in the 'targ' column
        aggregated_df = aggregated_df[aggregated_df[targ] != '0']

        # Rename the columns
        aggregated_df.columns = ['src', 'targ', 'vals']

        # Append the aggregated DataFrame to the list
        aggregated_dfs.append(aggregated_df)

    # Concatenate all the aggregated DataFrames to create the stacked DataFrame
    stacked = pd.concat(aggregated_dfs, axis=0)
    print(stacked)

    return stacked


def make_sankey(df, *cols, vals=None, save=None, **kwargs):
    """ Create the Sankey diagram from a given dataframe

    Args:
        df (dataframe): dataframe used to create a sankey diagram
        *cols: variable length argument list
        vals (str): stores values; default as None
        **kwargs: keyword arguments for additional graph customization

    Returns:
        Shows the Sankey diagram
        """
    # Checks if values column is part of the dataframe -> else, just sets values = 1 for every relationship
    if vals is not None:
        values = df[vals]
    else:
        values = [1] * len(df)

    # Stack columns if there are more than two
    df = _stacked_sankey(df, *cols)

    # Assigning source, target, and values for code mapping
    src, targ, vals = 'src', 'targ', 'vals'

    # Convert the df labels to integer values
    df, labels = _code_mapping(df, src, targ)

    # Create the links for the Sankey diagram using encoded source and target values
    link = {'source': df[src], 'target': df[targ], 'value': values,
            'line': {'color': 'black', 'width': 2}}

    # If node thickness is defined in kwargs, then use it. Else, default to 50.
    node_thickness = kwargs.get("node_thickness", 50)

    # Create the source and target nodes with labels
    node = {'label': labels, 'pad': 50, 'thickness': node_thickness,
            'line': {'color': 'black', 'width': 1}}

    # Create the Sankey plot and display it
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.update_layout(title_text=kwargs.get("title_text", ""))
    fig.show()
