import requests
import time
import string
import math
import user_agent

import pandas as pd

from bs4 import BeautifulSoup
from collections import defaultdict
from scipy.stats import exponnorm

def get_subgenres(super_genre, page):
    """
    Return dictionary of subgenres and their urls for every page

    Parameters
    super_genre: string indicating the top-level genre
    page: bs4.BeautifulSoup object

    Output:
    subgenres: dictionary of dictionariess. First key is the top-level
    genre and its value is a dictionary of dictionaries of subgenre
    names and their urls
    """
    subgenre_tags = (page.find("ul", {"class":"list top-level-subgenres"}).
                     find_all("a"))
    subgenres = {}
    subgenres[super_genre] = {}
    for tag in subgenre_tags:
        curr_subgenre = tag.decode_contents()
        curr_url = tag.attrs["href"]
        subgenres[super_genre][curr_subgenre] = curr_url

    return subgenres

def get_podcasts(genre, page):
    """
    Return a dictionary of subgenres and their urls

    Parameters
    genre: name of current genre (string)
    page: bs4.BeautifulSoup object

    Output
    podcasts: dictionary of podcast title (string) keys and
              url (string) values
    """
    podcasts = {}
    podcasts[genre] = {}
    pod_tags = page.find("div", {"id":"selectedcontent"}).find_all("a")
    for pod_tag in pod_tags:
        curr_pod_name = pod_tag.decode_contents()
        curr_pod_url = pod_tag.attrs["href"]
        podcasts[genre][curr_pod_name] = curr_pod_url

    return podcasts

def pod_metadata_parser(xml, podcast_id, podcast_url):
    """
    Returns a dictionary with key:value pairs for things of interest
    in iTunes reviews

    Parameters
    xml: first entry in xml returned by request made to iTunes review
    pages
    podcast_id: unique iTunes podcast id derived from url

    Returns
    pod_dict: dictionary with keys [title, last_update, iTunes_url
    name, category, publisher, image_url] and their corresponding values
    """
    pod_dict = {}
    pod_dict["title"] = xml.find("title").decode_contents()
    pod_dict["last_update"] = xml.find("updated").decode_contents()
    pod_dict["iTunes_url"] = podcast_url
    pod_dict["name"] = xml.find("im:name").decode_contents()
    pod_dict["category"] = xml.find("category").attrs["label"]
    pod_dict["publisher"] = xml.find("im:artist").decode_contents()
    pod_dict["image_url"] = xml.find_all("im:image")[-1].decode_contents()
    pod_dict["description"] = xml.find("summary").decode_contents()
    pod_dict["podcast_id"] = podcast_id
    return pod_dict

def review_parser(podcast_name, podcast_id, review):
    """
    Returns a dictionary with a key:value pairs for
    things of interest in iTunes reviews

    Parameters
    review: single bs4.element.Tag object for a review that
    has been decoded with "xml" parser from BeautifulSoup

    Output
    review_dict: dictionary with keys [podcast_name, podcast_id, date,
    title, user_id, review_text, rating]
    """
    try:
        review_dict = {}
        review_dict["podcast_name"] = podcast_name
        review_dict["podcast_id"] = podcast_id
        review_dict["date"] = review.find("updated").decode_contents()
        review_dict["title"] = review.find("title").decode_contents()
        review_dict["user_id"] = (review.find("uri").decode_contents()
                                  .split("/")[-1].strip(string.ascii_letters))
        review_dict["review_text"] = review.find("content").decode_contents()
        review_dict["rating"] = (int(review.find("im:rating")
                                     .decode_contents()))
        review_dict["source_id"] = 1
        return review_dict, True
    except:
        return None, False

def get_review_count(url):
    """
    Returns count of reviews from parsed iTunes page

    Parameters
    url: url for the podcast of interest

    Output
    count: number of reviews
    """
    headers = {"User-Agent":user_agent.generate_user_agent(os=None,
                navigator=None, platform=None, device_type="desktop")}
    r = requests.get(url, headers=headers)
    request = True
    while request:
        if r.status_code == 200:
            try:
                count = int(BeautifulSoup(r.text, "html.parser")
                         .find("span", {"class":"rating-count"})
                         .decode_contents().split()[0])
            except:
                count = 1
            time.sleep(10)
            return count
        elif r.status_code == 403:
            time.sleep(60)
            print("retrying...")
        else:
            print("Something went wrong!!")
            break

def get_podcast_reviews(podcast_name, podcast_url):
    """
    Returns dictionaries of metadata and reviews for an
    individual podcast

    Parameters
    podcast: podcast title (string)
    podcast_url: iTunes url for podcast page

    Output:
    podcast_metadata: dictionary of metadata
    podcast_reviews: list of dictionaries of reviews
    """
    podcast_reviews = []
    page_index = 1
    podcast_id = (podcast_url.split("/")[-1].split("?")[0]
                  .strip(string.ascii_letters))
    headers = {"User-Agent":user_agent.generate_user_agent(os=None,
                navigator=None, platform=None, device_type="desktop")}
    review_count = get_review_count(podcast_url)
    num_pages = math.ceil(review_count / 50) + 1
    if num_pages > 11:
        num_pages = 11
    while page_index < num_pages:
        url = ("https://itunes.apple.com/us/rss/customerreviews/"
               "id={}/sortby=mostHelpful/page={}/xml".format(podcast_id,
                                                            page_index))
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            reviews = BeautifulSoup(r.text, "xml").find_all("entry")
            if page_index == 1:
                try:
                    podcast_metadata = pod_metadata_parser(reviews[0], podcast_id, podcast_url)
                except:
                    print("Something went wrong!!")
                    print("{}\n{}\n{}\n{}".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                              time.localtime()),
                                                podcast_name, r.status_code,
                                                r.text))
                    return None, None, False
            for review in reviews[1:]:
                curr_review, review_parse_success = review_parser(podcast_name,
                                                    podcast_id, review)
                if review_parse_success:
                    podcast_reviews.append(curr_review)
                else:
                    pass
            print("Success on page {} of {} for {}".format(page_index,
                                                           num_pages - 1,
                                                           podcast_name))
            page_index += 1
            if num_pages == 2 or page_index == 10:
                pass
            else:
                time.sleep(exponnorm.rvs(3, loc=20, scale=1, size=1))
        elif r.status_code == 403:
            time.sleep(exponnorm.rvs(20, loc=240, scale=1, size=1))
        elif r.status_code == 400:
            page_index += 500
            print("Something went wrong!! (Error Code 400)")
            print("{}\n{}\n{}".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime()),
                                                      podcast_name, r.text))
            break
        else:
            print("Something went wrong!!")
            print("{}\n{}\n{}\n{}".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime()),
                                        podcast_name, r.status_code,
                                        r.text))
            break
    return podcast_metadata, podcast_reviews, True
