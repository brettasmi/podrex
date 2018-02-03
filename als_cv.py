#!/usr/bin/env python

# imports
import pandas as pd
import numpy as np
import spark_helpers

# pyspark modeling
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.pipeline import Pipeline
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

def main():
    sc.setCheckpointDir('checkpoint/')
    ab3 = pd.read_pickle('data.pkl')
    spark_abpu_reviews = spark.createDataFrame(ab3)
    spark_abpu_reviews_clean = spark_abpu_reviews.drop(
        "date", "title", "review_text", "source_id", "username",
        "review_id", "vote_count", "vote_sum", "customer_type",
        "date", "data_source", "podcast_id", "user_id"
        )
    spark_abpu_training, spark_abpu_test = (
    spark_abpu_reviews_clean.randomSplit([0.8, 0.2])
        )
    tuningALS = ALS(userCol="spark_id", itemCol="spark_pid", ratingCol="rating",
                     coldStartStrategy="drop", nonnegative=True,
                     checkpointInterval=2, maxIter=40)
    #ranktuning = np.linspace(20,85,13, endpoint=False)
    #regtuning = np.linspace(0.22, 0.29, 15, endpoint = False)
    ranktuning = np.linspace(20,40,2, endpoint=False)
    regtuning = np.linspace(0.22, 0.29, 2, endpoint = False)
    paramGrid = ParamGridBuilder() \
        .addGrid(tuningALS.rank, ranktuning) \
        .addGrid(tuningALS.regParam, regtuning) \
        .build()
    crossval = CrossValidator(estimator=tuningALS,
        estimatorParamMaps=paramGrid,
        evaluator=RegressionEvaluator(metricName="rmse", labelCol="rating",
        predictionCol="prediction"), numFolds=5)
    cv_model = crossval.fit(spark_abpu_training)
    cv_info_dict = spark_helpers.get_CV_info(cv_model)
    spark_helpers.param_writer(cv_info_dict, "param_tuning_results.txt")
    spark_helpers.spark_model_saver(cv_model, "best_model.sparkmodel")

if __name__=="__main__":
    main()
