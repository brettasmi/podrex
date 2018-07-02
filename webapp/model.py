# imports
import nlp
import pickle

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import pairwise_distances as skl_pdist

# load pickles
bonuses = pd.read_pickle("bonuses.pickle")
bonus_array = bonuses[["bonus_one", "bonus_two", "bonus_three",
                       "bonus_four", "bonus_five", "bonus_six",
                       "bonus_seven"]].values

with open("V.pickle", "rb") as in_pickle:
    V = pickle.load(in_pickle)
with open("pairwise_dist_nlp", "rb") as in_pickle:
    pairwise_dist_2d = pickle.load(in_pickle)
with open("tfidf_model.pickle", "rb") as in_pickle:
    tfidf_model = pickle.load(in_pickle)
with open("word_matrix.pickle", "rb") as in_pickle:
    word_matrix = pickle.load(in_pickle)

regexes = [nlp.links_regex, nlp.punc_newline_regex, nlp.non_alphanumeric]

class PodcastRecommender:
    def __init__(self):
        """
        Instantiate a PodcastRecommender object.

        Takes no arguments.

        Returns None.
        """
    def _get_recommendations(self, bonus=True, n_items=16):
        """
        Returns indices of the top n_items in approx_d
        Helper function for np.argsort

        Parameters
        ----------
        approx_d (numpy array): approximated ratings for m items
        n_items (int): number of recommendation indices to return
        bonus (bool): True to use self.bonused_d

        Returns
        -------
        indices (numpy array): indices of the most highly scoring
                               items in approx_d
        """
        if bonus:
            self.recommendation_indices = np.argsort(self.bonused_d)[-n_items:]
        else:
            self.recommendation_indices = np.argsort(self.approx_d)[-n_items:]
        return self.recommendation_indices

    def _add_bonus(self, bonus_array, bonus_level):
        """
        Returns modified d vector with a bonus to popular and
        highly-rated items

        Parameters
        ----------
        approx_d (numpy array): length m array of approximated user
                                ratings on m items
        bonus_array (numpy_array): m x n array of bonus scores for
                                   m items at n levels
        bonus_level (int): level of bonus in range[0,n). Corresponds
                           to columns of bonus_array.

        Returns
        -------
        bonused_d (numpy array): approx_d array with added bonus
        """
        bonus = bonus_array.T[bonus_level]
        self.bonused_d = self.approx_d + bonus


    def _calculate_d(self, ratings, indices, V, dismissed=None, penalize=True):
        """
        Returns approximate d vector from a set of ratings on popular items

        Parameters
        ----------
        ratings (list): input user ratings
        indices (list): indices for spark_pid corresponding to ratings
        V (numpy array): m (items) x n (rank) matrix of latent features
                         from NMF or SVD
        penalize (bool): subtract ratings from approx_d before returning
        Returns
        -------
        approx_d (numpy array): approximated d vector of length m representing
                                predicted user ratings
        """
        ratings_array = np.array(ratings)
        ratings_indices = np.array(indices)
        if dismissed:
            dismissed_indices = np.array(dismissed)
            dismissed_array = np.empty(dismissed_indices.shape, dtype=int)
            dismissed_array.fill(5)
        V_sub = V.T[:,ratings_indices]
        self.approx_u = np.linalg.lstsq(V_sub.T, ratings_array)
        self.approx_d = np.dot(self.approx_u[0], V.T)
        if penalize == True:
            penalty = np.zeros(V.shape[0])
            penalty[ratings_indices] = ratings_array
            if dismissed:
                penalty[dismissed_indices] = dismissed_array
            self.approx_d -= penalty

    def _add_nlp(self, ratings, indices, pairwise_dist_2d, bonus_level):
        for couplet in zip(ratings, indices):
            if couplet[0]==5:
                bonus_nlp = 1-(pairwise_dist_2d[couplet[1],:]) * (1/bonus_level)
                self.bonused_d += bonus_nlp

    def fit_predict(self, ratings, indices, dismissed=None, n_items=16):
        """
        Wrapper function to analyze and give predictions based on a user's
        input ratings.

        Parameters
        ----------
        ratings (list): input user ratings
        indices (list): indices for spark_pid corresponding to ratings
        dismissed (set): indices for spark_pid to
        n_items (int): number of recommendations to return

        Returns
        -------
        final_recommendations (list): indices for spark_pid related
                                     corresponding items
        """
        self._calculate_d(ratings, indices, V, dismissed)
        self._add_bonus(bonus_array, 6)
        self._add_nlp(ratings, indices, pairwise_dist_2d, 1)
        raw_recommendations = self._get_recommendations(bonus=True,
                                                     n_items=n_items)
        final_recommendations = [int(i) for i in raw_recommendations]
        return final_recommendations

    def nlp_search(self, search_terms, nlp_model=tfidf_model,
                   nlp_matrix=word_matrix, results=12):
        """
        Returns the top n results most closely related to search_terms

        Parameters
        ----------
        nlp_model: natural language processing model with a transform method
        nlp_matrix (numpy array): tokenized matrix of processed text to
                                  search against
        search_terms (str): space-separated search terms
        results (int): number of recommendations to return

        Returns
        -------
        recommendations (numpy array): array of indices of podcasts to recommend
        """
        clean_search = nlp.clean_nlp_text(search_terms, regexes)
        search_vector = nlp_model.transform([clean_search])
        search_distances = skl_pdist(nlp_matrix, search_vector,
                                     metric="cosine").reshape(-1)
        raw_nlp_recommendations = np.argsort(search_distances)[:results]
        nlp_recommendations = [int(i) for i in raw_nlp_recommendations]
        return nlp_recommendations
