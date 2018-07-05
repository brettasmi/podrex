# Python functions for creating a d3 network graph

import pickle

def five_by_listeners(conn, podcast):
    """Returns the five podcasts with the most shared listeners"""
    cursor = conn.cursor()
    five_pods = []
    cursor.execute("SELECT * FROM relationships "
                   "WHERE (podcast_1 = (%s)) "
                   "OR (podcast_2 = (%s)) "
                   "ORDER BY listeners desc "
                   "LIMIT 5", (podcast, podcast))
    results = cursor.fetchall()
    for result in results:
        if result[0] == podcast:
            five_pods.append((result[1], result[2]))
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
