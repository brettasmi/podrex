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
            self.graph = {"edges": [], "nodes": []}
            self.nodes = set(nodes)

    def five_by_listeners(self, conn, podcast):
        """Returns the five podcasts with the most shared listeners"""
        self.new_nodes = []
        podcast = self.lookup_dict[podcast]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relationships "
                       "WHERE (podcast_1 = (%s)) "
                       "OR (podcast_2 = (%s)) "
                       "ORDER BY listeners DESC "
                       "LIMIT 5", (podcast, podcast))
        results = cursor.fetchall()
        for result in results:
            if result[0] == podcast:
                self.nodes.append(self.lookup_dict[result[1]])
                self.new_nodes.append(self.lookup_dict[result[1]])
            else:
                self.nodes.append(self.lookup_dict[result[0]])
                self.new_nodes.append(self.lookup_dict[result[0]])
        cursor.close()

    def five_by_nlp(self, podcast, dist_matrix):
        """Returns `podcast`'s five most closely related podcasts and their shared
        listener count. Will not work for spark_pid > 3010.
        """
        self.new_nodes = []
        if podcast > 3010:
            return
        for pod in np.argsort(dist_matrix[podcast, :])[:5]:
            self.nodes.append(int(pod))
            self.new_nodes.append(int(pod))

    def _get_listener_overlap(self, conn, podcast_1, podcast_2):
        """Returns the count of listeners shared by podcast_1 and podcast_2"""
        podcasts = [self.lookup_dict[i] for i in
            [podcast_1, podcast_2, podcast_2, podcast_1]]
        cursor = conn.cursor()
        cursor.execute("SELECT listeners FROM relationships "
                        "WHERE (podcast_1 = (%s) AND podcast_2 = (%s)) "
                        "OR (podcast_1 = (%s) AND podcast_2 = (%s))",
                        podcasts)
        result = cursor.fetchone()
        if result:
            cursor.close()
            return (result[0])
        cursor.close()
        return result[0]
    cursor.close()
