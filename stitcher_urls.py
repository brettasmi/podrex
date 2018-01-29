import requests
import user_agent
import re
import string
import logging
import time

import podrex_db_utils as db

from bs4 import BeautifulSoup
from scipy.stats import exponnorm

punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36)"}
def get_podcast_name(conn, cursor):
    """
    Gets the name of a podcast from the database

    Parameters
    conn, cursor: active psycopg2 connection and cursor objects

    Returns
    podcast_name (str): podcast name
    itunes_url (str): itunes_url for matching later
    """
    try:
        cursor.execute("SELECT podcast_name, itunes_url "
                       "FROM stitcher "
                       "WHERE stitcher_url IS NULL "
                       "LIMIT 1")
        result = cursor.fetchone()
        podcast_name = punc_regex.sub("", result[0])
        itunes_url = result[1]
        return podcast_name, itunes_url

    except:
        logging.exception("failed to get name")
        conn.rollback()

def google_url_constructor(podcast_name):
    """
    Constructs a google search url from a podcast name

    Parameters
    podcast_name (str): podcast name to search

    Returns
    google_url (str): google url to search
    """
    google_url = "https://www.google.com/search?q=site%3Astitcher.com"
    google_url = google_url + "+" + "+".join(podcast_name.split())
    return google_url

def google_request(google_url, headers):
    """
    Returns google result from a request to google_url

    Parameters
    google_url (str): google search url
    headers (dict): headers to use for consistent search

    Returns
    google_result (requests object)
    True on success, False on failure
    """
    google_result = requests.get(google_url, headers=headers)
    if google_result.status_code == 200:
        return google_result, True
    else:
        print("failed to get {}".format(google_url))
        return google_result, False

def parse_google_result(google_result):
    """
    Returns the first title and url from a google search result

    Parameters
    google_result (requests object)

    Returns
    search_name, search_url
    """

    soup = BeautifulSoup(google_result.text, "html.parser")
    try:
        top_result = soup.find("h3",{"class":"r"}).find("a")
        search_url = top_result.attrs["href"]
        search_name = top_result.decode_contents().split("|")[0]
        return search_url, search_name, True
    except:
        logging.exception("failed to find top google result in parsing")
        return None, None, False
def update_db(conn, cursor, itunes_url, search_url, search_name):
    """
    Updates a row in the db with stitcher url and name

    Parameters
    conn, cursor: active psycopg2 objects
    itunes_url (str): itunes_url on which to match db row
    stitcher_url (str): parsed stitcher url
    stitcher_name (str): parsed stitcher name

    Returns
    True on success, False on failure
    """
    try:
        cursor.execute("UPDATE stitcher SET search_name = (%s), "
                       "stitcher_url = (%s) "
                       "WHERE itunes_url = (%s)",
                       [search_name, search_url, itunes_url])
        conn.commit()
        return True
    except:
        conn.rollback()
        logging.exception("failed to update db on {}".format(itunes_url))
        return False

def process_podcast(conn, cursor, log_file):
    """
    Wrapper function to process a podcast

    Parameters
    conn, cursor: active psycopg2 objects
    log_file (writeable file object): log file to write errors
    Returns
    None
    """
    podcast_name, itunes_url = get_podcast_name(conn, cursor)
    google_url = google_url_constructor(podcast_name)
    google_result, search_success = google_request(google_url, headers)
    if not search_success:
        print("failure on {}".format(podcast_name))
        log_file.write("failure on {}\n".format(podcast_name))
        cursor.execute("update stitcher set stitcher_url = 'problem' "
                       "where itunes_url = (%s)", [itunes_url])
        time.sleep(exponnorm.rvs(2, 27, 1, 1))
        return None
    search_url, search_name, parse_success = parse_google_result(google_result)
    if not parse_success:
        print("failure on {}\n{}".format(podcast_name, google_result.text))
        log_file.write("failure on {}\n{}".format(podcast_name,
                                                  google_result.text))
        cursor.execute("update stitcher set stitcher_url = 'problem' "
                       "where itunes_url = (%s)", [itunes_url])
        conn.commit()
        time.sleep(exponnorm.rvs(2, 27, 1, 1))
        return None
    success = update_db(conn, cursor, itunes_url, search_url, search_name)
    if success:
        print("success on {}".format(podcast_name))
        log_file.write("success on {}".format(podcast_name))
        time.sleep(exponnorm.rvs(2, 27, 1, 1))
    else:
        print("failure on {}".format(podcast_name))
        log_file.write("failure on {}".format(podcast_name))
        time.sleep(exponnorm.rvs(2, 27, 1, 1))
if __name__ == "__main__":
    conn, cursor = db.connect_db()
    while True:
        with open ("stitcher_log.log", "a") as log_file:
            process_podcast(conn, cursor, log_file)
