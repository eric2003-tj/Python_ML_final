# Python_ML_Final

# 📊 關稅主題推文分群分析專案說明

本專案整合了兩大部分：
1. 使用 **Selenium** 自動化爬蟲從 Twitter 抓取推文
2. 使用 **Sentence-BERT + KMeans** 進行語意向量化與分群分析

---

## 📁 專案結構

```
project_root/
│
├── data/
│   └── tariff_data_en/           # 儲存 Twitter 抓下來的 .csv 推文資料
│
├── tariff-crawl.py               # 用 Selenium 爬 Twitter 推文
├── kmeans.py                     # 執行語意向量轉換 + 分群分析
```

---

## 🐦 Part 1: 使用 Selenium 爬取 Twitter 推文（tariff-crawl.py）

### Step 1: 設定 WebDriver

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

webdriver_path = "/opt/homebrew/bin/chromedriver"
options = Options()
options.add_argument("--start-maximized")
# ... 其他設定 ...
driver = webdriver.Chrome(service=Service(webdriver_path), options=options)
```

### Step 2: 自動登入與存取

- 可選擇使用 cookies 快速登入
- 自動捲動頁面直到載入所有目標推文
- 擷取推文時間與文字內容，儲存為 `data/tariff_data_en/*.csv`

---

## 🤖 Part 2: 推文分析與分群（kmeans.py）

### Step 1: 合併資料檔

```python
import glob, pandas as pd
df_list = [pd.read_csv(f) for f in glob.glob("data/tariff_data_en/*.csv")]
df = pd.concat(df_list, ignore_index=True)
```

### Step 2: 預處理時間欄位與事件標記

```python
df.columns = ['Timestamp', 'text', 'sentiment']
event_date = pd.to_datetime("2025-04-02").tz_localize("UTC")
df["period"] = df["Timestamp"].apply(lambda x: "before" if x < event_date else "after")
```

### Step 3: 使用 Sentence-BERT 編碼文本

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
X = model.encode(df['text'].tolist(), show_progress_bar=True)
```

### Step 4: 使用 KMeans 分群

```python
from sklearn.cluster import KMeans
k = 6
kmeans = KMeans(n_clusters=k)
df["cluster"] = kmeans.fit_predict(X)
```

---

## 📈 可選擴充分析

- 每群的 **詞雲** 分析
- 群內 **情緒比例統計**
- **PCA 降維** 將向量映射成 2D 可視化分群

---

## ✅ 結語

此專案展示了如何整合：
- Twitter 社群資料爬取
- 語意向量表示技術（BERT）
- 無監督學習（KMeans）

應用於事件導向的輿情與情緒變化分析。
