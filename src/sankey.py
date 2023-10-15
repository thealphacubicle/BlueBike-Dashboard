import plotly.graph_objects as go
import pandas as pd


def _code_mapping(df, src, targ, add_cols=None):
    """Encodes source and target columns in a dataframe

    :param df: Dataframe
    :param src: Source column
    :param targ: Target column
    :return: Tuple of encoded dataframe and list of constructed labels
    """
    x = list(df[src]) + list(df[targ])

    if add_cols is not None:
        for col in add_cols:
            x = x+list(df[col])

    # Gets all unique labels in source and target columns
    labels = list(set(x))

    # Generates integer values that correspond to length of labels
    codes = list(range(len(labels)))

    # Maps the unique labels to the list of integer codes
    lc_map = dict(zip(labels, codes))

    # Replace the actual String names with the integer codes in the source and target columns
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels


def df_stacking(df, cols, vals):
    """
    Stacks the dataframe into source and target columns
    :param df: Dataframe
    :param cols: Column #1 as source column
    :param vals: Column #2 as value column
    :return: Stacked dataframe
    """
    stacked_df = pd.DataFrame()

    # Checks if values column is part of the dataframe -> else, just sets values = 1 for every relationship
    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)

    # Stack the columns in the dataframe
    for i in range(0, len(cols) - 1):
        d1 = df[[cols[i], cols[i + 1]]]
        d1.columns = ['src', 'targ']

        # Concatenate inner pairing df with resultant df
        stacked_df = pd.concat([stacked_df, d1])

        # Aggregate same links together, carrying over the values column
        stacked_df = create_value_column(stacked_df, val_column_name='Count',
                                         group_by_cols=['src', 'targ'])
    return stacked_df


def create_value_column(df, group_by_cols, val_column_name):
    """Creates the value column via aggregation given a data frame

    :param df: Dataframe
    :param group_by_cols: Columns to group by
    :param val_column_name: Name of the value column
    :return: Aggregated dataframe with values column
    """
    # Aggregate by nationality and decade
    df_grouped = df.groupby(group_by_cols)
    counts_df = df_grouped.size().reset_index(name=val_column_name)

    return counts_df


def make_sankey(df, col1, col2, add_cols=None, vals=None, return_fig=False, **kwargs):
    """Creates a Sankey plot

    :param df: Dataframe
    :param col1: Source column
    :param col2: Target column
    :param vals: (OPTIONAL) Name of values column
    :param add_cols: Additional columns to include in Sankey plot
    :param kwargs: Keyword arguments of graph properties
    :return: Sankey diagram
    """

    # Stack dataframe if add_cols is not empty
    if add_cols is not None:
        df = df_stacking(df, [col1] + list(add_cols) + [col2], vals)
        col1, col2 = 'src', 'targ'

    # Encode the dataframe and get the labels using the utility method defined above
    df, labels = _code_mapping(df, col1, col2, add_cols)
    df = df.reset_index()
    vals = df.columns[-1]

    # Create the links for the Sankey diagram using encoded source and target values
    link = {'source': df[col1], 'target': df[col2], 'value': df[vals],
            'line': {'color': 'black', 'width': 1}}

    # If node thickness is defined in kwargs, then use it. Else, default to 50.
    node_thickness = kwargs.get("node_thickness", 50)

    # Create the source and target nodes with labels
    node = {'label': labels, 'pad': 75, 'thickness': node_thickness,
            'line': {'color': 'black', 'width': 4}}

    # Create the Sankey plot and display it
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.update_layout(title_text=kwargs.get("title_text", ""))

    if return_fig:
        return fig

    else:
        fig.show()

    ####################################TESTING############################################################
# df = pd.DataFrame({'nationality': ['A', 'B', 'C', 'D'],
#                        "gender": ['M', 'M', 'F', 'M'],
#                        "decade": ['1930', '1940', '1930', '1940']})
#
# make_sankey(df, 'nationality', 'decade', 'gender')
