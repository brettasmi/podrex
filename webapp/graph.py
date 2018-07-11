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

    def five_by_listeners(self, conn, podcast, podcast_list):
        """Returns the five podcasts with the most shared listeners"""
        self.new_nodes = []
        podcast = self.lookup_dict[podcast]
        podcast_list = [self.lookup_dict[i] for i in podcast_list]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relationships "
                       "WHERE (podcast_1 = %(podcast)s "
                       "AND podcast_2 NOT IN %(podcasts)s) "
                       "OR (podcast_2 = %(podcast)s "
                       "AND podcast_1 NOT IN %(podcasts)s) "
                       "ORDER BY listeners DESC "
                       "LIMIT 5", {"podcast":podcast,
                            "podcasts":tuple(podcast_list)})
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

    def construct_graph(self, conn, id_dict):
        """Returns initial d3 graph"""
        if len(self.old_nodes) == 0:
            nodes_combos = [i for i in combinations(self.nodes, 2)]
        else:
            nodes_combos = [i for i in product(self.new_nodes, self.old_nodes)]
        for nodes in nodes_combos:
            link = self._get_listener_overlap(conn, nodes[0], nodes[1])
            if link:
                if link > 10:
                    self.graph["edges"].append({"source": str(nodes[0]),
                                            "target": str(nodes[1]),
                                            "value": int(np.log(link))-1})
        if len(self.old_nodes) == 0:
            nodes_data = db.get_podcast_info(conn, self.nodes)
        else:
            nodes_data = db.get_podcast_info(conn, self.new_nodes)
        for data_list in nodes_data:
            data_list.extend(list(self._get_bonus(data_list[2], self.bonus_df)))
            self.graph["nodes"].append(self._make_node_dict(data_list))
        self.graph["nodes"] = list({value["id"]:value for value in self.graph["nodes"]}.values())
        #print(id_dict)
        for node_data in self.graph["nodes"]:
            node_data["status"] = self._get_status(int(node_data["id"]), id_dict)
            #print(node_data["status"])
        return self.graph

    def _make_node_dict(self, data):
        """Returns a dictionary for json from data"""
        return {"podcast_id":data[0], "podcast_name":data[1],
            "id":str(data[2]), "description":data[3], "itunes_url":data[4],
            "stitcher_url":data[5], "website_url":data[6], "pop":data[7],
            "size":data[8]}
    def _get_status(self, spark_id, id_dict):
        """Returns status that corresponds to stroke-color in d3"""
        if spark_id in id_dict["liked"]:
            return "liked"
        elif spark_id in id_dict["recommended"]:
            return "recommended"
        elif spark_id in id_dict["new_nodes"]:
            return "newly_added"
        else:
            return "previously_added"

    def _get_bonus(self, spark_id, bonus_df):
        """Returns two values that correspond to size and color for the node
        depicting the podcast represented by `spark_id`"""
        if spark_id <= 3010:
            pop = float(bonus_df["bonus_one"].loc[bonus_df["spark_pid"] \
                == spark_id])
            size = int(np.log(bonus_df["rating_count"].loc[bonus_df["spark_pid"] \
                == spark_id])*1.5)
            return pop, size
        return (np.mean(bonus_df["bonus_one"]),
            int(np.mean(np.log(bonus_df["rating_count"]))))
