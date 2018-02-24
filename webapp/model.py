import numpy as np
import pandas as pd
import pickle
bonuses = pd.read_pickle("bonuses.pickle")
bonus_array = bonuses[["bonus_one", "bonus_two", "bonus_three",
                       "bonus_four", "bonus_five"]].values
with open("V.pickle", "rb") as in_pickle:
    V = pickle.load(in_pickle)
with open("pairwise_dist_nlp", "rb") as infile:
    pairwise_dist_2d = pickle.load(infile)

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


    def _calculate_d(self, ratings, indices, V, penalize=True):
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
        #print(indices, ratings)
        self.ratings_array = np.array(ratings)
        self.ratings_indices = np.array(indices)
        self.V = V
        #print(self.V.shape)
        self.V_sub = self.V.T[:,self.ratings_indices]
        self.approx_u = np.linalg.lstsq(self.V_sub.T, self.ratings_array)
        self.approx_d = np.dot(self.approx_u[0], self.V.T)
        if penalize == True:
            penalty = np.zeros(self.V.shape[0])
            penalty[self.ratings_indices] = self.ratings_array
            self.approx_d -= penalty

    def _add_nlp(self, ratings, indices, pairwise_dist_2d, bonus_level):
        for couplet in zip(ratings, indices):
            if couplet[0]==5:
                bonus_nlp = 1-(pairwise_dist_2d[couplet[1],:]) * (1/bonus_level)
                #print(bonus_nlp)
                self.bonused_d += bonus_nlp

    def fit_predict(self, ratings, indices, n_items=16):
        """
        Wrapper function to analyze and give predictions based on a user's
        input ratings.

        Parameters
        ----------
        ratings (list): input user ratings
        indices (list): indices for spark_pid corresponding to ratings
        n_items (int): number of recommendations to return

        Returns
        -------
        final_recommendations (list): indices for spark_pid related
                                     corresponding items
        """
        self._calculate_d(ratings, indices, V)
        self._add_bonus(bonus_array, 4)
        self._add_nlp(ratings, indices, pairwise_dist_2d, 1)
        raw_recommendations = self._get_recommendations(bonus=True,
                                                     n_items=n_items)
        final_recommendations = [int(i) for i in raw_recommendations]
        return final_recommendations
