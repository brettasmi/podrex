# podrex
#### Podcast recommendations based on what you already like

<img src="img/podrex_v3.png"  width=250>

Podrex uses a collaborative filtering approach and natural language processing (NLP) to return podcast recommendations based on user input. A user-friendly web interface asks users to input some of their favorite podcasts and to rate some other popular podcasts, the data is passed to the server where the model quickly approximates the user's rating vector for about two-thousand podcasts.

Podrex also generates podcast listener networks and dendrograms that advertisers can use to better understand the podcast advertising space and place more better targeted ads without the help of middle men.

#### The business problem
Finding a new podcast after listening to all the episodes of your favorite show is generally not a great experience. iTunes/Apple Podcasts don't offer user-tailored recommendations and many of the top podcasts are daily new podcasts, and other repositories aren't much better.

Further, for digital marketing specialists, finding podcasts on which to advertise isn't intuitive. Major podcast ad networks are tied to limited sets of podcasts which may or may not best suit an advertiser's marketing strategy. A direct approach to search on content and to understand how podcasts are related is needed.

#### The data
We scraped ratings data, review data, and podcast data  from multiple major podcast repositories. We identified and removed users and podcasts without enough ratings for meaningful modeling of relationships between podcasts. To prepare the podcast and description text data for NLP, we filtered urls and other unwanted text, removed common advertising words, and lemmatized the remaining tokens.

#### Modeling
For the collaborative filtering model, we used NMF to estimate the user and item matrices using an alternating least squares approach as implemented in Apache Spark via `pyspark` on AWS EMR instances. We analyzed the text data with the `NLTK`, `scikit-learn`, and `scipy` libraries in Python. We used the `networkx` library in Python to analyze podcast listener networks and `matplotlib` to make the resulting plots.

To estimate the user's approximate ratings vector, we use an ordinary least squares approach with a subset of the item features matrix based on user input. The model adds a language bonus to the resultant estimated rating vector to podcasts similar in show and episode descriptions. All podcasts receive a minor bonus based on popularity and overall rating. Using only simple linear algebra in `numpy`, the model rapidly returns recommendations to the user.

#### Evaluation
The matrix factorization model performs with ~1.00 star RMSE as determined through K-fold cross-validation. Highly rated user podcasts remain highly rated in the model, and many users have validated the results as meaningfully good.  

#### Deployment
[podrex.io](podrex.io) hosts a user-friendly, fast interface for rating podcasts and getting recommendations. We built the website with a `flask` and `postgresql` backend and and HTML, CSS, Javascript, and jQuery frontend. We built some of the visualizations using the javascript library `D3`.
