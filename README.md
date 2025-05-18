# Python_ML_Final

This project aims to apply traditional machine learning methods to estimate the **daily average sentiment** on X (formerly Twitter) during the period following President Trump's announcement of reciprocal tariffs. We further compare our model’s predictions with the actual average sentiment scores derived from the collected data.

## Step 1: Web Scraping

We scraped tweets from X (Twitter) that were related to the topic of tariffs. The data collection covers the period from **2025/03/01 to 2025/05/16**, using keyword-based filtering (e.g., “tariff”) to ensure relevance.

## Step 2: Prediction Target

Our goal is to forecast the **daily average sentiment score** throughout the target period, using features extracted from the social media activity on each day.

## Step 3: Data Labeling

Since we aim to predict sentiment numerically, we first needed to label each tweet with a sentiment score. To do this, we applied the **VADER sentiment analyzer**, which assigns a compound score to each tweet ranging from -1 (negative) to +1 (positive).

## Step 4: Data Preprocessing

1. Filter out non-English tweets.
2. Handle missing values and malformed entries.
3. Aggregate tweets on a daily basis to form a new DataFrame (one row per day).
4. Define and extract meaningful features per day (e.g., sentiment ratios, tweet volume, lexical statistics).

## Step 5: Model Construction

1. Due to the limited dataset (≈60 days), we first experimented with simple, interpretable models such as **Linear Regression**, **Ridge Regression**, and **Random Forest**.
2. We split our dataset into three subsets:
   - 65% for training
   - 15% for validation (parameter tuning)
   - 20% for testing (final evaluation)
