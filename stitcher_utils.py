#imports
import json
import logging
import math
import psycopg2
import requests
import time
import user_agent

import podrex_db_utils as db

from bs4 import BeautifulSoup
from scipy.stats import exponnorm


# functions

def get_stitcher_url(conn, cursor):
    """
    Returns a stitcher url to scrape

    Parameters
    conn, cursor: active psycopg2 connection and cursor objects

    Returns
    stitcher_url
    """

    cursor.execute("SELECT stitcher_url, podcast_id FROM podcasts "
                   "WHERE stitcher_url IS NOT NULL AND "
                   "stitcher_id IS NULL AND "
                   "processed <> 'stitcher' AND "
                   "processed <> 'in_stitcher' AND "
                   "podcast_id IS NOT NULL "
                   "LIMIT 1")
    result = cursor.fetchone()
    stitcher_url = result[0]
    podcast_id = result[1]
    cursor.execute("UPDATE podcasts "
                   "SET processed = 'in_stitcher' "
                   "WHERE podcast_id = (%s)", [podcast_id])
    conn.commit()
    return stitcher_url, podcast_id

def request_stitcher_page(stitcher_url, headers, log_file):
    """
    Returns requests object on successful get request

    Parameters
    stitcher_url (str): url to request
    headers (dict): headers to use for http request
    log_file (file object in writeable mode): log file to write errors

    Returns
    stitcher_page (requests object)
    True on success, False on failure
    """
    stitcher_page = requests.get(stitcher_url, headers=headers)
    if stitcher_page.status_code == 200:
        log_file.write("Successfully got {}\n".format(stitcher_url))
        return stitcher_page, True
    else:
        log_file.write("Failed to get {}, status_code: {}\n".format(
                       stitcher_url, stitcher_page.status_code))
        return stitcher_page, False

def parse_stitcher_page(stitcher_page, log_file):
    """
    Returns stitcher podcast id

    Parameters
    stitcher_page(requests object): requests request object with status_code 200
    log_file(file object in writeable mode): log file to write errors

    Returns
    stitcher_id(int): unique stitcher id associated with podcast
    True on success, False on failure
    """
    try:
        soup = BeautifulSoup(stitcher_page.text, 'html.parser')
        res = soup.find("meta", property="og:url")
        stitcher_id = res.attrs["content"].split("=")[1]
        return stitcher_id, True
    except:
        log_file.write("".format(logging.exception("failed inside parse_stitcher_page")))
        return None, False

def get_stitcher_reviews(stitcher_id, headers, log_file, page_index=0):
    """
    Returns dict(json) of stitcher reviews and review count

    Parameters
    stitcher_id: unique stitcher id associated with podcast
    page_index: review page to get
    headers: headers to use to request page
    Returns
    stitcher_reviews (list of dict): reviews to parse
    review_count(int): total review count
    """
    review_offset = page_index * 100
    review_limit = 100
    reviews_url = "https://api.bazaarvoice.com/data/batch.json"
    params = {
        'apiversion': '5.5',
        'callback': 'BV._internal.dataHandler0',
        'displaycode': '17163-en_us',
        'filter.q0': f'id:eq:{stitcher_id}',
        'filter.q1': [
            'isratingsonly:eq:false',
            f'productid:eq:{stitcher_id}',
            'contentlocale:eq:en_US'
            ],
        'filter.q2': [f'productid:eq:{stitcher_id}', 'contentlocale:eq:en_US'],
        'filter.q3': [
            f'productid:eq:{stitcher_id}',
            'isratingsonly:eq:false',
            'issyndicated:eq:false',
            'rating:gt:3',
            'totalpositivefeedbackcount:gte:3',
            'contentlocale:eq:en_US'
            ],
        'filter.q4': [f'productid:eq:{stitcher_id}',
        'isratingsonly:eq:false',
        'issyndicated:eq:false',
        'rating:lte:3',
        'totalpositivefeedbackcount:gte:3',
        'contentlocale:eq:en_US'],
        'filter_comments.q1': 'contentlocale:eq:en_US',
        'filter_reviewcomments.q0': 'contentlocale:eq:en_US',
        'filter_reviewcomments.q1': 'contentlocale:eq:en_US',
        'filter_reviews.q0': 'contentlocale:eq:en_US',
        'filter_reviews.q1': 'contentlocale:eq:en_US',
        'filter_reviews.q3': 'contentlocale:eq:en_US',
        'filter_reviews.q4': 'contentlocale:eq:en_US',
        'filteredstats.q0': 'reviews',
        'filteredstats.q1': 'reviews',
        'include.q1': 'authors,products,comments',
        'include.q3': 'authors,reviews,products',
        'include.q4': 'authors,reviews,products',
        'limit.q1': f'{review_limit}',
        'limit.q2': '1',
        'limit.q3': '1',
        'limit.q4': '1',
        'limit_comments.q1': '3',
        'offset.q1': f'{review_offset}',
        'passkey': 'dtc34lzs6wi8u90qiq8g4m62f',
        'resource.q0': 'products',
        'resource.q1': 'reviews',
        'resource.q2': 'reviews',
        'resource.q3': 'reviews',
        'resource.q4': 'reviews',
        'sort.q1': 'relevancy:a1',
        'sort.q3': 'totalpositivefeedbackcount:desc',
        'sort.q4': 'totalpositivefeedbackcount:desc',
        'stats.q0': 'reviews',
        'stats.q1': 'reviews'}
    reviews_page = requests.get(reviews_url, params=params, headers=headers)
    #reviews_page = requests.get(reviews_url, headers=headers)
    if reviews_page.status_code == 200:
        reviews_soup = BeautifulSoup(reviews_page.text,"lxml")
        try:
            page_data = json.loads(reviews_soup.find("p").decode_contents()[26:-1])
            reviews = page_data["BatchedResults"]["q1"]["Results"]
            if len(reviews) == 0:
                log_file.write("No reviews for {}\n".format(stitcher_id))
                return "no_reviews", None, None, False
            total_reviews = (page_data["BatchedResults"]["q1"]["Includes"]["Products"]
                             [stitcher_id]["TotalReviewCount"])
            log_file.write("Successfully got {}\n".format(reviews_url))
            page_index += 1
            return reviews, page_index, total_reviews, True
        except:
            logging.exception("failed after getting successful reviews page "
                               "for {}".format(stitcher_id))
            return None, None, None, False
    else:
        log_file.write("Failed to get {}, status_code: {}\n".format(
                       reviews_url, reviews_page.status_code))
        return reviews_page, current_index, total_reviews, False

def parse_stitcher_review(podcast_id, review):
    """
    Returns a dictionary of user review data from stitcher

    Parameters
    podcast_id(int): unique podcast id from database
    review (dict): dictionary of stitcher reviews as returned by
                    parse_stitcher_page

    Returns
    stitcher_review (dict): dictionary of parsed data from a stitcher review
    """
    stitcher_review = {}
    stitcher_review["podcast_id"] = podcast_id
    stitcher_review["username"] = review["UserNickname"]
    stitcher_review["user_id"] = review["AuthorId"]
    stitcher_review["review_id"] = review["Id"]
    stitcher_review["rating"] = review["Rating"]
    stitcher_review["title"] = review["Title"]
    stitcher_review["review_text"] = review["ReviewText"]
    stitcher_review["vote_count"] = review["TotalFeedbackCount"]
    stitcher_review["vote_sum"] = (review["TotalPositiveFeedbackCount"] -
                                   review["TotalNegativeFeedbackCount"])

    stitcher_review["date"] = review["SubmissionTime"]
    stitcher_review["data_source"] = 2

    return stitcher_review

def update_reviews_stitcher(review, conn, cursor):
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
        cursor.execute("INSERT INTO stitcher_reviews2 "
                       "(podcast_id, username, user_id, review_id, rating, "
                       "title, review_text, vote_count, vote_sum, "
                       "date, data_source) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (review["podcast_id"], review["username"],
                        review["user_id"], review["review_id"],
                        review["rating"], review["title"], review["review_text"],
                        review["vote_count"], review["vote_sum"],
                        review["date"], review["data_source"]))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback() # fix cursor
        logging.exception("failed inside update_reviews_stitcher")
        return True
    except:
        logging.exception("failed inside update_reviews_stitcher")
        return False
def process_stitcher_podcast(conn, cursor, log_file):
    """
    Completely processes one podcast from stitcher

    Parameters
    conn, cursor: active psycopg2 objects
    log_file (writeable file object): file object to write errors
    headers (dict): headers to use for http requests

    Returns
    None
    """
    headers = {"User-Agent":user_agent.generate_user_agent(os=None,
            navigator=None, platform=None, device_type="desktop")}
    stitcher_url, podcast_id = get_stitcher_url(conn, cursor)
    stitcher_page, request_success = request_stitcher_page(stitcher_url,
                                                   headers, log_file)
    if not request_success:
            stitcher_fail_handler(conn, cursor, stitcher_url, "requesting page", log_file)
            return None
    stitcher_id, parse_success = parse_stitcher_page(stitcher_page, log_file)
    if not parse_success:
            stitcher_fail_handler(conn, cursor, stitcher_url, "parsing page", log_file)
            return None
    total_reviews = 100
    page_index = 0
    while page_index * 100 < total_reviews:
        reviews, page_index, total_reviews, review_success = get_stitcher_reviews(
                                                                  stitcher_id,
                                                                  headers,
                                                                  log_file,
                                                                  page_index=page_index)
        if not review_success:
            if reviews == "no_reviews":
                mark_as_stitcher(conn, cursor, podcast_id)
                return None
            else:
                stitcher_fail_handler(conn, cursor, stitcher_url,
                                      "parsing reviews", log_file)
                return None
        for review in reviews:
            review_dict = parse_stitcher_review(podcast_id, review)
            review_update_success = update_reviews_stitcher(review_dict, conn, cursor)
            if not review_update_success:
                stitcher_fail_handler(conn, cursor, stitcher_url, "updating reviews", log_file)
        total_pages = math.ceil(total_reviews / 99)
        print("Success on page {} of {} for {}".format(page_index, total_pages,
                                                        podcast_id))
        time.sleep(exponnorm.rvs(3, 20, 1, 1,))

    if review_update_success:
        mark_as_stitcher(conn, cursor, podcast_id)

def stitcher_fail_handler(conn, cursor, stitcher_url, event, log_file):
    """
    Handles log-writing for errors

    Parameters
    stitcher_url (str): url on which function failed
    event (str): event on which function failed
    logfile (writeable file object): log file to write errors

    Returns
    None
    """
    cursor.execute("UPDATE podcasts "
                   "SET processed = 'stitcher_problem' "
                   "WHERE stitcher_url = (%s)", [stitcher_url])
    conn.commit()
    log_file.write("{} | failed on {} {}\n".format(
                            time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime()), event, stitcher_url))

    print("failure on {} in {}".format(stitcher_url, event))

def mark_as_stitcher(conn, cursor, podcast_id):
    """
    Marks a podcast as processed through itunes in the database

    Parameters
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor
    podcast_url (str): podcast url to match for updating
    """
    cursor.execute("UPDATE podcasts "
                   "SET processed = 'stitcher' "
                   "WHERE podcast_id = (%s)", [podcast_id])
    conn.commit()

if __name__ == "__main__":
    conn, cursor = db.connect_db()
    while True:
        with open("stitcher_scrape_log.log", "a") as log_file:
            process_stitcher_podcast(conn, cursor, log_file)
