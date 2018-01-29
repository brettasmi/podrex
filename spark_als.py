# imports
# database
from podrex_db import connect_db

# python modeling
import pandas as pd

# pyspark sql
import pyspark as ps
import pyspark.sql.functions as F

# pyspark modeling
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.pipeline import Pipeline
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

# connect to db
conn, cursor = connect_db()

reviews = cursor.fetchall()
reviews_df = pd.DataFrame(reviews, columns=["podcast_id", "user_id", "rating",
                                            "date", "title_text", "review_text",
                                             "source_id"])

spark_reviews = spark.createDataFrame(reviews_df)
spark_reviews_clean = spark_reviews.drop("date", "title_text", "review_text",
                                         "source_id")

(reviews_training, reviews_test) = spark_reviews_clean.randomSplit([0.8, 0.2])
als_model = ALS(userCol="user_id", itemCol="podcast_id", ratingCol="rating",
                coldStartStrategy="drop")

podrex = als_model.fit(reviews_training)

predictions = podrex.transform(reviews_test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                predictionCol="prediction")
rmse = evaluator.evaluate(predictions)

print("Root-mean-square error = " + str(rmse))
