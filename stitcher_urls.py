import requests
import user_agent
import re
import string
import logging
import time

from webapp import podrex_db_utils as db

from bs4 import BeautifulSoup
from scipy.stats import exponnorm

punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
headers = {"User-Agent":user_agent.generate_user_agent(os=None,
           navigator=None, platform=None, device_type="desktop")}
def get_podcast_name(conn):
    """
    Gets the name of a podcast from the database

    Parameters
    conn: active psycopg2 connection

    Returns
    podcast_name (str): podcast name
    itunes_url (str): itunes_url for matching later
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT podcast_name, itunes_url "
                       "FROM stitcher "
                       "WHERE stitcher_url IS NULL "
                       "LIMIT 1")
        result = cursor.fetchone()
        podcast_name = punc_regex.sub("", result[0])
        itunes_url = result[1]
        cursor.close()
        return podcast_name, itunes_url

    except:
        logging.exception("failed to get name")
        conn.rollback()
        cursor.close()

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
    """
    google_result = requests.get(google_url, headers=headers)
    return google_result

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
        paragraphs = soup.findAll("p")
        if ("did not match any documents" in
            ''.join([p.decode_contents() for p in soup.findAll("p")])):
            return True, True, False
        else:
            logging.exception("failed to find top google result in parsing")
            return None, None, False
def update_db(conn, itunes_url, search_url, search_name):
    """
    Updates a row in the db with stitcher url and name

    Parameters
    conn: active psycopg2 connection
    itunes_url (str): itunes_url on which to match db row
    stitcher_url (str): parsed stitcher url
    stitcher_name (str): parsed stitcher name

    Returns
    True on success, False on failure
    """
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE stitcher SET search_name = (%s), "
                       "stitcher_url = (%s) "
                       "WHERE itunes_url = (%s)",
                       [search_name, search_url, itunes_url])
        conn.commit()
        cursor.close()
        return True
    except:
        conn.rollback()
        logging.exception("failed to update db on {}".format(itunes_url))
        cursor.close()
        return False

def process_podcast(conn, log_file):
    """
    Wrapper function to process a podcast

    Parameters
    conn: active psycopg2 connection
    log_file (writeable file object): log file to write errors
    Returns
    None
    """
    cursor = conn.cursor()
    podcast_name, itunes_url = get_podcast_name(conn)
    google_url = google_url_constructor(podcast_name)
    google_result = google_request(google_url, headers)
    if google_result.status_code == 503:
        print("YOU'VE BEEN DISCOVERED!!!!")
        cursor.close()
        time.sleep(3600)
        return None
    elif google_result.status_code != 200:
        print("failure on {}".format(podcast_name))
        log_file.write("failure on {}\n".format(podcast_name))
        cursor.execute("update stitcher set stitcher_url = 'problem' "
                       "where itunes_url = (%s)", [itunes_url])
        time.sleep(exponnorm.rvs(2, 45, 1, 1))
        cursor.close()
        return None
    search_url, search_name, parse_success = parse_google_result(google_result)
    if not parse_success:
        if search_url == True:
            print("no results for {}".format(podcast_name))
            log_file.write("no results for {}\n".format(podcast_name))
            cursor.execute("UPDATE stitcher SET search_name = 'no result', "
                           "stitcher_url = 'no result' "
                           "WHERE itunes_url = (%s)", [itunes_url])
            conn.commit()
            cursor.close()
            time.sleep(exponnorm.rvs(2, 45, 1, 1))
            return None
        else:
            print("failure on {}\n{}".format(podcast_name, google_result.text))
            log_file.write("failure on {}\n{}".format(podcast_name,
                                                      google_result.text))
            cursor.execute("update stitcher set stitcher_url = 'problem' "
                           "where itunes_url = (%s)", [itunes_url])
            conn.commit()
            cursor.close()
            time.sleep(exponnorm.rvs(2, 45, 1, 1))
            return None
    success = update_db(conn, itunes_url, search_url, search_name)
    if success:
        print("success on {}".format(podcast_name))
        log_file.write("success on {}".format(podcast_name))
        cursor.close()
        time.sleep(exponnorm.rvs(2, 45, 1, 1))
    else:
        print("failure on {}".format(podcast_name))
        log_file.write("failure on {}".format(podcast_name))
        cursor.close()
        time.sleep(exponnorm.rvs(2, 45, 1, 1))
if __name__ == "__main__":
    conn = db.connect_db()
    while True:
        with open ("stitcher_log.log", "a") as log_file:
            process_podcast(conn, log_file)
