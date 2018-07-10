# Python functions for creating a d3 network graph

import numpy as np
import podrex_db_utils as db
from itertools import combinations, product

class d3Graph:
    def __init__(self, nodes, bonus_df, lookup_dict, graph=None):
        """Creates and updates json-like data object for use in a d3
        force directed graph

        Parameters:
        nodes (list): spark podcast ids corresponding to podcasts sent from
            webapp
        bonus_df (pd.DataFrame): dataframe containing "bonuses"
        lookup_dict (dict): spark_pid:itunes_id key:value lookup
        """
        self.bonus_df = bonus_df
        self.lookup_dict = lookup_dict
        self.new_nodes = []
        self.old_nodes = []
        if graph:
            self.graph = graph
            self.nodes = graph["nodes"].copy()
        else:
            five_pods.append((result[0], result[2]))
    cursor.close()
    return five_pods

def five_by_nlp(podcast, lookup_dict, dist_matrix):
    """Returns `podcast`'s five most closely related podcasts and their shared
    listener count
    """
    return [lookup_dict[i] for i in np.argsort(dist_matrix[podcast, :])[-5:]]

def get_listener_overlap(conn, podcast_1, podcast_2):
    """Returns the count of listeners shared by podcast_1 and podcast_2"""
    cursor = conn.cursor()
    cursor.execute("SELECT listeners FROM relationships "
                    "WHERE ((podcast_1 = (%s) AND podcast_2 = (%s)) "
                    "OR ((podcast_1 = (%s) AND podcast_2 = (%s))",
                    (podcast_1, podcast_2, podcast_2, podcast_1))
    result = cursor.fetchone()
    if result:
        cursor.close()
        return result[0]
    cursor.close()
