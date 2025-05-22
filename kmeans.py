import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from wordcloud import WordCloud

# --- 1. 合併所有推文資料 ---
csv_files = sorted(glob.glob("data/tariff_data_en/*.csv"))
df_list = [pd.read_csv(f) for f in csv_files]
df = pd.concat(df_list, ignore_index=True)

# --- 2. 標準化欄位與時間處理 ---
df.columns = ['Timestamp', 'text', 'sentiment']
df.dropna(subset=['text'], inplace=True)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # 含 UTC 時區

# 修正：避免 tz-aware / naive 錯誤，明確指定事件日為 UTC 時間
event_date = pd.to_datetime("2025-04-02").tz_localize("UTC")
df['period'] = df['Timestamp'].apply(lambda x: 'before' if x < event_date else 'after')

# --- 3. 向量化推文（TF-IDF）---
custom_stopwords = set(['tariff', 'trump'])  # 你可以加入更多常見詞
all_stopwords = list(ENGLISH_STOP_WORDS.union(custom_stopwords))  # 修正錯誤：轉成 list 才能傳入
vectorizer = TfidfVectorizer(stop_words=all_stopwords, max_features=1000)
X = vectorizer.fit_transform(df['text'])

# --- 4. KMeans 聚類 ---
k = 6
kmeans = KMeans(n_clusters=k, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# --- 5. PCA 降維 + 畫群體分布圖 ---
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X.toarray())

os.makedirs("saved_imgs", exist_ok=True)

plt.figure(figsize=(10, 7))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df['cluster'], cmap='tab10', alpha=0.6)
plt.title("KMeans(PCA)")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.colorbar(scatter, label='Cluster')
plt.savefig("saved_imgs/kmeans_pca_clusters.png")
plt.close()

# --- 6. 產出每個群的 WordCloud ---
def plot_cluster_wordcloud(df, cluster_num):
    text = " ".join(df[df['cluster'] == cluster_num]['text'])
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=all_stopwords).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"Cluster {cluster_num} WordCloud")
    plt.savefig(f"saved_imgs/cluster_{cluster_num}_wordcloud.png")
    plt.close()

for cl in sorted(df['cluster'].unique()):
    plot_cluster_wordcloud(df, cl)

# --- 7. 額外分析輸出：事件前後各群數量與情緒分布 ---
print("\n📊 各群情緒比例（row-normalized）:")
print(df.groupby('cluster')['sentiment'].value_counts(normalize=True).unstack().fillna(0))

print("\n📆 各群在事件前/後的比例（row-normalized）:")
print(pd.crosstab(df['cluster'], df['period'], normalize='index'))
