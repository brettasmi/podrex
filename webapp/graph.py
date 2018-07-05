# Python functions for creating a d3 network graph

import pickle

def five_by_listeners(conn, podcast):
    """Returns the five podcasts with the most shared
    listeners
    """
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
