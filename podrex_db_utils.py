import logging
import os
import psycopg2

db_name = os.environ["RDS_PODREX_DB"]
user = os.environ["RDS_USER"]
key = os.environ["RDS_SECRET_KEY"]
host = os.environ["RDS_HOST_NAME"]
port = os.environ["RDS_PORT"]

def connect_db():
    """
    Returns connection and cursor to AWS RDS set up for this purpose.

    Parameters
    None

    Returns
    conn: psycopg2 connection object
    cursor: psycopg2 cursor object
    """
    conn = psycopg2.connect("dbname={} user={} host={} port={} password={}"
                        .format(db_name, user, host, port, key))
    cursor = conn.cursor()
    return conn, cursor

def update_podcasts(pm, conn, cursor):
    """
    Updates podcast metadata table and returns bool of success or failure

    Parameters
    pm: result_dictionary with podcast metadata, from module
    scrape_itunes

    cursor: psycopg2 active cursor

    Returns
    True on success, False on failure
    """
    try:
        cursor.execute("UPDATE podcasts "
               "SET podcast_id = (%s), artist_id = (%s), artist_name = (%s), "
               "description = (%s), feed_url = (%s), mean_rating = (%s), "
               "rating_count = (%s), rating_distribution = (%s), "
               "review_count = (%s), genres = (%s), last_update = (%s), "
               "website_url = (%s), artwork = (%s), also_consumed = (%s), "
               "more_by_artist = (%s), top_in_genre = (%s) "
               "WHERE itunes_url = (%s) ",
              (pm["podcast_id"], pm["arist_id"], pm["artist_name"], pm["description"],
               pm["feed_url"], pm["mean_rating"], pm["rating_count"],
               pm["rating_distribution"], pm["review_count"], pm["genres"],
               pm["last_update"], pm["website_url"], pm["artwork"],
               pm["also_consumed"], pm["more_by_artist"], pm["top_in_genre"],
               pm["itunes_url"]))
        conn.commit()
        return True
    except:
        logging.exception("failed inside update_podcasts")
        conn.rollback() # fix cursor
        return False

def update_reviews(review, conn, cursor):
    """
    Updates the podcast reviews table and returns bool on success or failure

    Parameters
    review: a single dictionary of review metadata returned from parsing
    function in scrape_itunes module
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor

    Returns
    True on success, False on failure
    """

    try:
        cursor.execute("INSERT INTO reviews "
                       "(podcast_id, username, user_id, review_id, rating, "
                       "title, review_text, vote_count, vote_sum, "
                       "customer_type, date, data_source) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (review["podcast_id"], review["username"],
                        review["user_id"], review["review_id"],
                        review["rating"], review["title"], review["review_text"],
                        review["vote_count"], review["vote_sum"],
                        review["customer_type"], review["date"],
                        review["data_source"]))
        conn.commit()
        return True
    except:
        conn.rollback() # fix cursor
        logging.exception("failed inside update_reviews")
        return False

def update_episodes(episode, conn, cursor):
    """
    Updates the episodes table in the podcast db and returns bool on success

    Parameters
    episode (dict): a dictionary of a single episode metadata
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor

    Returns
    True on success, False on failure
    """
    try:
        cursor.execute("INSERT INTO episodes "
                       "(podcast_id, episode_id, description, name, "
                       "download_url, release_date, popularity) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (episode["podcast_id"], episode["episode_id"],
                        episode["description"], episode["name"],
                        episode["download_url"], episode["release_date"],
                        episode["popularity"]))
        conn.commit()
        return True
    except:
        conn.rollback() # fix cursor
        logging.exception("failed inside update_episodes")
        return False

def get_unprocessed_podcast(cursor, mark_in_progress=False):
    """
    Returns podcast name and url of a single unprocessed podcast
    based on column processed in table podcasts

    Parameters
    cursor: active psycopg2 cursor object

    Returns
    podcast_name (string) name of returned podcast
    itunes_url (string) url of returned podcast to scrape
    """
    cursor.execute("SELECT podcast_name, itunes_url "
                   "FROM podcasts WHERE processed = 'false' "
                   "LIMIT 1")
    result = cursor.fetchone()
    podcast_name, itunes_url = result[0], result[1]
    if mark_in_progress:
        cursor.execute("UPDATE podcasts "
                       "SET processed = 'in_progress' "
                       "WHERE itunes_url = %s ", [itunes_url])
    return podcast_name, itunes_url

def mark_as_itunes(conn, cursor, podcast_url):
    """
    Marks a podcast as processed through itunes in the database

    Parameters
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor
    podcast_url (str): podcast url to match for updating
    """
    cursor.execute("UPDATE podcasts "
                   "SET processed = 'itunes' "
                   "WHERE itunes_url = (%s)", [podcast_url])
    conn.commit()
