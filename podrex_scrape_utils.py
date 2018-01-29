
#scrape_utils
import json
import logging
import math
import os
import requests
import string
import time

import pandas as pd
import podrex_db_utils as db

from bs4 import BeautifulSoup
from collections import defaultdict
from scipy.stats import exponnorm

headers = {}
headers["User-Agent"] = os.environ["SCRAPE_HEADERS"]

def get_podcast_id(url):
    """
    Returns the podcast id from within the url

    Parameters
    url (str): url of podcast

    Returns
    id (str): itunes podcast id
    """
    return url.split("/")[-1].split("?")[0].strip(string.ascii_letters)

def request(url, podcast_name, headers, f):
    """
    Returns request object if a successful request is made

    Parameters
    url (string): url to request
    podcast_name (string): podcast name for writing errors
    headers (dict): headers to use to make the request
    f (file object): log file for writing errors

    Returns
    response (requests response object)
    success (bool): True if successful, else False
    """
    max_tries = 5
    tries = 0
    request = True
    while tries < max_tries:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response, True
        elif response.status_code == 403:
            time.sleep(exponnorm.rvs(20, loc=220, scale=1, size=1))
            tries += 1
        elif r.status_code == 400:
            page_index += 500
            print("Something went wrong with {}!! "
                  "(Error Code 400)".format(podcast_name))
            f.write("{}\n{}\n{}\n".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime()),
                                                      podcast_name, r.text))
            break
            return None, False
        else:
            print("Something went wrong with {}!!".format(podcast_name))
            f.write("{}\n{}\n{}\n{}\n".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime()),
                                        podcast_name, r.status_code,
                                        r.text))
            break
            return None, False
    return None, False

def process_podcast_request(response, mode, f, podcast_id=None):
    """
    Returns different dictionaries extracted from podcast page

    Parameters
    response (requests object)
    mode (int) = 0 for podcast data, 1 for reviews
    f (open file object in writeable mode): log object to write
    podcast_id (str): podcast id for podcast page requests

    Returns
    if mode 0
        podcast_data (dict): dictionary of some podcast information
        page_data (dict): dictionary of other podcast information
    elif mode 1
        reviews (list): list of reviews
    """
    if mode == 0:
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            scripts = soup.findAll('script')
            podcast_data = (json.loads(scripts[2].decode_contents()[15:])
                                       ["storePlatformData"]["product-dv-product"]
                                       ["results"][podcast_id])
            page_data = (json.loads(scripts[2].decode_contents()[15:])
                                    ["pageData"]["podcastPageData"])

            return podcast_data, page_data, True
        except:
            logging.exception("failed inside process_podcast_request, page 0")
            return None, None, False
    elif mode == 1:
        try:
            reviews = json.loads(response.text)["userReviewList"]
            return reviews, True
        except:
            logging.exception("failed inside process_podcast_request, reviews")
            return None, False

def parse_metadata(podcast_data, page_data, podcast_name, podcast_id,
                            podcast_url):
    """
    Returns dictionary of information about a podcast

    Parameters
    podcast_data (dict): data about a single podcast from itunes
    page_data (dict): other data from the podcast
    Returns:
    podcast_dict (dict): parsed data about a single podcast
    success (bool): True on success, False on failure
    """
    try:
        podcast_dict = {}
        podcast_dict["podcast_id"] = podcast_id # int
        podcast_dict["podcast_name"] = podcast_name
        podcast_dict["arist_id"] = podcast_data["artistId"] # int
        podcast_dict["artist_name"] = podcast_data["artistName"] # varchar
        podcast_dict["description"] = podcast_data["description"]["standard"] # text
        podcast_dict["feed_url"] = podcast_data["feedUrl"] # text
        podcast_dict["mean_rating"] = (podcast_data["userRating"]
                                       ["ariaLabelForRatings"].split()[0]) # float
        podcast_dict["rating_count"] = podcast_data["userRating"]["ratingCount"] # int
        podcast_dict["rating_distribution"] = (podcast_data["userRating"]
                                              ["ratingCountList"]) # array
        podcast_dict["review_count"] = page_data["totalNumberOfReviews"] # int
        podcast_dict["genres"] = podcast_data["genreNames"] # array
        podcast_dict["last_update"] = podcast_data["releaseDateTime"]
        podcast_dict["website_url"] = podcast_data["podcastWebsiteUrl"] # text
        podcast_dict["artwork"] = podcast_data["artwork"][0]["url"] # text
        podcast_dict["itunes_url"] = podcast_url
        also_consumed = [int(podcast) for podcast in page_data["listenersAlsoBought"]]
        podcast_dict["also_consumed"] = also_consumed #array
        more_by_artist = [int(artist_show) for artist_show in page_data["moreByArtist"]]
        podcast_dict["more_by_artist"] =  more_by_artist # array
        top_in_genre = [int(top_show) for top_show in page_data["topPodcastsInGenre"]]
        podcast_dict["top_in_genre"] =  top_in_genre # array
        return podcast_dict, True
    except:
        logging.exception("failed inside metadata parser")
        return None, False

def parse_episode(episode, episode_id, podcast_id, popularity_map):
    """
    Returns a dictionary of parsed episode information.

    Parameters
    episode (dict): one dictionary podcast entry
    episode_id (int): unique episode_id for episode
    podcast_id (int): podcast id to use as foriegn key
    popularity_map (dict): dictionary of episode popularities as contained
    in page data

    Returns
    episode_info (dict): dictionary of an episode's metadata
    """
    episode_info = {}
    episode_info["podcast_id"] = episode["collectionId"] # probably just use the top one
    episode_info["episode_id"] = episode_id
    episode_info["description"] = episode["description"]["standard"]
    episode_info["name"] = episode["name"]
    episode_info["download_url"] = episode["offers"][0]["download"]["url"]
    episode_info["release_date"] = episode["releaseDateTime"]
    episode_info["popularity"] = popularity_map[str(episode_id)]
    return episode_info

def parse_review(review, podcast_id):
    """
    Return dictionary of data from a single review

    Parameters
    review (dict): single itunes podcast review

    Returns
    review_dict (dict): parsed information from itunes review
    """
    review_dict = {}
    review_dict["podcast_id"] = podcast_id # int
    review_dict["username"] = review["name"] # varchar
    review_dict["user_id"] = review["viewUsersUserReviewsUrl"].split("=")[1] # int
    review_dict["review_id"] = review["userReviewId"] # int
    review_dict["rating"] = review["rating"] # smallint
    review_dict["title"] = review["title"] # text
    review_dict["review_text"] = review["body"] # text
    review_dict["vote_count"] = review["voteCount"] # smallint
    review_dict["vote_sum"] = review["voteSum"] # smallint
    review_dict["customer_type"] = review["customerType"] # varchar
    review_dict["date"] = review["date"] # date
    review_dict["data_source"] = 1
    return review_dict

def process_podcast():
    """
    Gets and fully proccesses one podcast (in iTunes)

    Parameters
    None

    Returns
    None
    """
    conn, cursor = db.connect_db()
    podcast_name, podcast_url = db.get_unprocessed_podcast(cursor,
                                                           mark_in_progress=True)
    conn.commit() # commit set to in progress
    podcast_id = get_podcast_id(podcast_url)
    with open("scrape.log", "a") as log_file:
        podcast_dict, podcast_data, page_data = process_metadata(podcast_name,
                                                                 podcast_url,
                                                                 podcast_id,
                                                                 conn, cursor,
                                                                 log_file)
        total_reviews = podcast_dict["review_count"]
        time.sleep(exponnorm.rvs(2, loc=18, scale=1, size=1))
        process_reviews(podcast_id, podcast_name, total_reviews, conn, cursor, log_file)
        process_episodes(podcast_data, page_data, podcast_id, conn, cursor, log_file)
        log_file.write("{} | success on {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                  time.localtime()), podcast_name))
        print("{} | success on {}".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime()), podcast_name))
        time.sleep(exponnorm.rvs(2, loc=18, scale=1, size=1))
    db.mark_as_itunes(conn, cursor, podcast_url)

def process_metadata(podcast_name, podcast_url, podcast_id, conn, cursor,
                     log_file):
    """
    Wrapper function to process metadata of a podcast

    Parameters
    podcast_name (str): podcast name from database
    podcast_url (str): itunes url from database
    podcast_id (int): unique podcast identifier
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor
    log_file (file object in writeable mode): log file to write errors

    Returns
    podcast_dict (dict):
    podcast_data
    page_data
    """
    # request page
    response, success = request(podcast_url, podcast_name,
                                headers, log_file)
    if not success:
        fail_handler(podcast_name, "initial request", log_file)
        return None,
    # get podcast page data
    podcast_data, page_data, data_success = process_podcast_request(response, 0,
                                            log_file, podcast_id=podcast_id)
    if not data_success:
        fail_handler(podcast_name, "find first data", log_file)
        return None
    # parse podcast data
    podcast_dict, parse_success = parse_metadata(podcast_data, page_data,
                                                 podcast_name, podcast_id,
                                                 podcast_url)
    if not parse_success:
        fail_handler(podcast_name, "parse first page", log_file)

    # update podcast metadata database
    db_update_success = db.update_podcasts(podcast_dict, conn, cursor)
    if not db_update_success:
        fail_handler(podcast_name, "update podcast db", log_file)
        pass
    return podcast_dict, podcast_data, page_data

def process_reviews(podcast_id, podcast_name, total_reviews, conn, cursor, log_file):
    """
    Wrapper function to process reviews of a podcast

    Parameters
    podcast_id (int): unique podcast identifier
    total_reviews (int): total number of reviews
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor
    log_file (file object in writeable mode): log file to write errors
    max_episodes (int): max number episodes to add to the database

    Returns
    None
    """
    current_index = 0
    num_pages = math.ceil(total_reviews / 100)
    current_page = 1
    while current_index < total_reviews:
        review_url = review_url_constructor(podcast_id, current_index,
                                            total_reviews)
        response, revreq_success = request(review_url, podcast_name,
                                           headers, log_file)
        if not revreq_success:
            fail_handler(podcast_name, "review request", log_file)
            break
        current_index += 100
        reviews, review_success = process_podcast_request(response,
                                                         1, log_file)
        if not review_success:
            fail_hander(podcast_name, "review page data", log_file)

        for review in reviews:
            review_dict = parse_review(review, podcast_id)
            db.update_reviews(review_dict, conn, cursor)
        print("Success on page {} of {} on {}".format(current_page, num_pages,
                                                      podcast_name))
        current_page += 1
        if current_index < total_reviews:
            time.sleep(exponnorm.rvs(2, loc=19, scale=1, size=1))

def process_episodes(podcast_data, page_data, podcast_id, conn, cursor,
                     log_file, max_episodes=50):
    """
    Wrapper function to process episodes of a podcast

    Parameters
    podcast_data (dict): dictionary of podcast data from itunes
    page_data (dict): dictionary of more podcast data from itunes
    podcast_id (int): unique podcast identifier
    conn: active psycopg2 connection
    cursor: active psycopg2 cursor
    log_file (file object in writeable mode): log file to write errors
    max_episodes (int): max number episodes to add to the database

    Returns
    None
    """
    episode_data = podcast_data["children"]
    popularity_map = page_data["popularityMap"]["podcastEpisode"]
    episode_list = list(episode_data.keys())
    if len(episode_list) > max_episodes: #get most recent episode
        df = pd.read_json(json.dumps(episode_data), convert_dates=False,
                          convert_axes=False, orient="index")
        df = df.sort_values(by="releaseDate").iloc[-50:]
        episode_data = df.to_dict(orient="index")
        episode_list = list(episode_data.keys())
    for episode in episode_list:
        parsed_episode = parse_episode(episode_data[episode], episode,
                                       podcast_id, popularity_map)
        db.update_episodes(parsed_episode, conn, cursor)

def review_url_constructor(podcast_id, current_index, total_reviews):
    """
    Contructs a url that can be requested to get podcast reviews

    Parameters
    podcast_id (string): unique podcast id
    current_index (int): index of last review received
    total_reviews (int): total number of reviews for a given podcast

    Returns
    url (str): formatted url
    """
    if total_reviews - current_index >= 100:
        end_index = current_index + 100
    else:
        end_index = total_reviews
    url = ("https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?"
           "id={}&displayable-kind=4&startIndex={}&endIndex={}&sort=1".format(
            podcast_id, current_index, end_index))

    return url
def fail_handler(podcast_name, event, log_file):
    """
    Handles writing failures to log

    Parameters
    podcast name (str): podcast name
    event (str): what was happening upon failure
    log_file (file object in writeable mode): log file to write

    Returns
    None
    """
    log_file.write("{} | failure on {} for {}".format(
                   time.strftime("%Y-%m-%d %H:%M:%S",
                   time.localtime()), event, podcast_name))
    print("Failed on {}, continuing...".format(podcast_name))

if __name__ == "__main__":
    while True:
        process_podcast()
