import os
import psycopg2
import podrex.scrape_itunes as psi

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

def update_metadata(result_dict, cursor):
    """
    Updates podcast metadata table and returns bool of success or failure

    Parameters
    result_dict: result_dictionary with podcast metadata, from module
    scrape_itunes

    cursor: psycopg2 active cursor

    Returns
    True on success, False on failure
    """
    try:
        cursor.execute("UPDATE podcasts "
               "SET podcast_id = (%s),"
               "last_update = (%s), "
               "title = (%s), "
               "category = (%s), "
               "description = (%s),"
               "image_url = (%s), "
               "publisher = (%s), "
               "processed = True "
               "WHERE itunes_url = (%s) ",
              (pm["podcast_id"], pm["last_update"], pm["title"], pm["category"],
              pm["description"], pm["image_url"], pm["publisher"], pm["iTunes_url"]))
        return True
    except:
        return False

def update_reviews(review, cursor):
    """
    Updates the podcast reviews table and returns bool on success or failure

    Parameters
    review: a single dictionary of review metadata returned from parsing
    function in scrape_itunes module
    cursor: active psycopg2 cursor

    Returns
    True on success, False on failure
    """
    try:
        cursor.execute("INSERT INTO reviews "
                       "(podcast_id, "
                       "user_id, "
                       "rating, "
                       "date, "
                       "title, "
                       "review_text, "
                       "source_id) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s) ",
                       (review["podcast_id"],
                        review["user_id"],
                        review["rating"],
                        review["date"],
                        review["title"],
                        review["review_text"],
                        review["source_id"]))
        return True
    except:
        print("problem with inserting {}".format(str(podcast_id)+str(user_id)))
        return False
