
"""
DS3500: Advanced Programming with Data
Homework 1
Rishita Shroff

sankey.py: A reusable library for sankey visualizations
"""

# importing required libraries
import pandas as pd
import plotly.graph_objects as go

def _code_mapping(df, src, targ):
    """
    helper for creating sankey diagram

    Args:
        df (dataframe): used to build sankey diagram
        src (list): list of values for nodes to connect
        targ (list): list of values for nodes to connect

    Returns:
        df (dataframe): mapped dataframe
        labels (list): list of distinct labels
    """

    # Get distinct labels
    labels = sorted(list(set(list(df[src]) + list(df[targ]))))

    # Get integer codes
    codes = list(range(len(labels)))

    # Create label to code mapping
    lc_map = dict(zip(labels, codes))

    # Substitute names for codes in dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels

def _stacked_sankey(df, columns):
    """
    helper for creating a stack of dataframes for a multi-sankey
    diagram

    Args:
        df (dataframe): dataframe used to create stacked dataframe
        columns (list): list of columns needed to build a stack

    Returns:
        stacked (dataframe): a stacked dataframe
    """

    # creating an empty dataframe
    stacked = pd.DataFrame()

    # looping through every item in the list except the last one to make
    # pairs of different columns.
    # for eg: 5 columns = 4 pairs
    for col in range(len(columns) - 1):

        # creating list of pairs
        col_list = [columns[col], columns[col + 1]]

        # creating an aggregated dataframe
        new_df = df[col_list].groupby(col_list).size().reset_index()

        # renaming the columns as source, target, and values
        new_df.columns = ['src', 'targ', 'vals']

        # removing null values
        new_df = new_df[new_df.targ != '0']

        # adding the aggregated dataframe to empty dataframe to make a stack
        stacked = pd.concat([stacked, new_df], axis=0)

    # printing stacked dataframe to see results
    print(stacked)

    return stacked

def make_sankey(df, *cols, vals=None, **kwargs):
    """
    Create a sankey diagram linking src values to
    target values with thickness vals

    Args:
        df (dataframe): dataframe used to create a sankey diagram
        *cols: variable length argument list
        vals (str): stores values; default as None
        **kwargs:
            threshold (int): minimum threshold
            pad (int): size of node

    Returns:
        None
    """

    # making the stacked dataframe by calling it
    df = _stacked_sankey(df, *cols)

    # getting source, target, and values for code mapping
    src, targ, vals = 'src', 'targ', 'vals'

    # getting a threshold
    threshold = kwargs.get("threshold", 0)
    if vals and threshold > 0:
        df = df[df[vals] > threshold]

    # making sankey diagram using code mapping
    df, labels = _code_mapping(df, src, targ)

    # getting values for the dataframe
    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)

    # linking dataframe to sankey
    link = {'source':df[src], 'target':df[targ], 'value':values}

    # making a default pad
    pad = kwargs.get('pad', 50)

    # adding labels and pad to nodes
    node = {'label': labels, 'pad': pad}

    # creating the sankey diagram
    sk = go.Sankey(link=link, node=node)

    # getting the sankey diagram
    fig = go.Figure(sk)
    fig.show()