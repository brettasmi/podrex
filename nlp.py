# imports
# database
import podrex_db_utils as db
# pandas, other tools
import pandas as pd
# text cleaning tools
import string
import re

# nltk
from nltk import tokenize
from nltk.corpus import stopwords
# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

# some predefinded regexes
# punc_.. regex partially from https://stackoverflow.com/a/266162/
punc_newline_regex = re.compile('[%s\\n]' % re.escape(string.punctuation))

# links_regex from https://stackoverflow.com/a/11332543/
links_regex = re.compile('\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*')
non_alphanumeric = re.compile("[^a-zA-Z0-9\s]")

def clean_nlp_text(text, regex, replacement="", lower=True):
    """
    Returns a string of text appropriately cleaned for tokenizing

    Parameters
    text (string): string object to clean
    regex (list): list of re.compile regular expressions to replace
                  note: regex should be in order of cleaning!
    replacement (string): string to replace matched regex
    lower (bool): return lowercase if true, else as input

    Returns
    clean_text (string): cleaned text
    """
    clean_text = text
    for expression in regex:
        clean_text = expression.sub(replacement, clean_text)
    if lower:
        return clean_text.lower()
    else:
        return clean_text
