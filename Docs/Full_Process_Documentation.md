# Full Process Documentation: Restaurant Prioritization System

> End-to-end documentation covering every stage from raw data cleaning through interactive dashboarding. All formulas, parameters, design decisions, bug fixes, and validation methodologies are documented.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Stage 00: Exploratory Data Analysis](#2-stage-00-exploratory-data-analysis)
3. [Stage 01: Data Cleaning](#3-stage-01-data-cleaning)
4. [Stage 02: Web Scraping](#4-stage-02-web-scraping)
5. [Stage 03: NLP Sentiment Analysis](#5-stage-03-nlp-sentiment-analysis)
6. [Stage 04: Data Merging & Scoring](#6-stage-04-data-merging--scoring)
7. [Stage 05: Feature Engineering](#7-stage-05-feature-engineering)
8. [Stage 06: ML Classification](#8-stage-06-ml-classification)
9. [Stage 08: Dashboard Generation](#9-stage-08-dashboard-generation)
10. [Interactive Dashboard](#10-interactive-dashboard)
11. [Final Results Summary](#11-final-results-summary)
12. [Known Limitations & Design Decisions](#12-known-limitations--design-decisions)
13. [Bugs Fixed During Development](#13-bugs-fixed-during-development)

---

## 1. System Overview

This system addresses Hungry Hub's marketing resource allocation problem by building a **prioritized, ranked list of restaurant partners** using machine learning. Each restaurant is classified into one of four segments (Rising, Stable, Declining, Hidden Gem) and ranked by marketing opportunity.

### Architecture

```
Raw CSVs (dim_v2.csv, dim_tags.csv, KOL, Analytics)
  → 01. Data Cleaning (aggregation, outlier removal, GMV filters)
  → 02. Web Scraping (Google Maps ratings, reviews)
  → 03. NLP Sentiment Analysis (VADER on review text)
  → 04. Data Merging & Scoring (3 composite scores + sparse column removal)
  → 05. Feature Engineering (encoding, ratios, MECE labels, OOF stacking)
  → 06. ML Classification (LightGBM, Stratified 5-Fold CV, priority scoring)
  → 08. Dashboard Generation (ranked retention list + full portfolio)
  → Streamlit Dashboard (interactive filtering, charts, export)
```

### File Map

| Stage | Script | Notebook | Location |
|-------|--------|----------|----------|
| 00 | — | `00_EDA.ipynb` | `Data/EDA/` |
| 01 | — | `01_Data_Cleaning.ipynb` | `Data/` |
| 02 | — | `02_Web_Scraping.ipynb` | `Data/` |
| 03 | — | `03_NLP_Sentiment_Analysis.ipynb` | `Data/` |
| 04 | `run_04.py` | `04_Data_Merging_and_Scoring.ipynb` | `Data/` |
| 05 | `run_05.py` | `05_Feature_Engineering.ipynb` | `Data/` |
| 06 | `run_06.py` | `06_Restaurant_Classification.ipynb` | `Models/` |
| 08 | `run_08.py` | `08_Retention_Dashboard.ipynb` | `Models/` |
| UI | `app.py` | — | `Dashboard/` |

> **Note:** The `.py` scripts are the canonical source of truth. The `.ipynb` notebooks are auto-generated from them using `convert_to_notebooks.py`. When making changes, edit the `.py` scripts and re-run the converter.

### Data Flow

| File | Produced By | Rows | Columns | Description |
|------|-------------|------|---------|-------------|
| `master_cleaned_data.csv` | Stage 01 | 3,727 | ~20 | Cleaned transactional data |
| `master_web_scraping_data.csv` | Stage 02 | ~373 | ~8 | Google Maps scraped data |
| `master_nlp_data.csv` | Stage 03 | ~323 | ~5 | VADER sentiment results |
| `master_all_data.csv` | Stage 04 | 3,727 | 44 | Merged + scored dataset |
| `ML_Ready_Features.csv` | Stage 05 | 3,727 | 32 | Engineered features with labels |
| `Categorized_Restaurants.csv` | Stage 06 | 3,727 | 12 | ML predictions + probabilities |
| `Dashboard_List_1_Retention.csv` | Stage 08 | 103 | ~20 | Ranked marketing targets |
| `Dashboard_Predictions.csv` | Stage 08 | 3,727 | ~20 | Full portfolio rankings |

---

## 2. Stage 00: Exploratory Data Analysis

**Notebook:** `Data/EDA/00_EDA.ipynb`

### Purpose
Establish baseline understanding of the data and validate assumptions from the problem statement before any cleaning or engineering.

### Key Findings
- **Revenue Concentration:** Top 20% of partners generate **95.1%** of total revenue. This validates the core business problem from the problem statement (which estimated 98%).
- **KOL Data Coverage:** Only ~5% of restaurants (196/3,727) have KOL engagement data — these features are available but extremely sparse.
- **Web Traffic Anomaly:** Google Analytics `pagePaths` contain full URLs, not restaurant IDs — required slug-generation and mapping logic during the merge process.
- **Booking Volume Distribution:** Highly right-skewed — a few restaurants have 10,000+ bookings while the median is much lower.

---

## 3. Stage 01: Data Cleaning

**Notebook:** `Data/01_Data_Cleaning.ipynb`

### Inputs
| File | Description |
|------|-------------|
| `dim_v2.csv` | Raw transaction/booking data |
| `dim_tags.csv` | Restaurant metadata (cuisine, location, facilities) |
| KOL analytics CSV | Influencer engagement metrics (views, likes, comments) |
| Google Analytics CSV | Web traffic data (page views, sessions) |

### Processing Steps

#### 1. Transaction Aggregation
Per-restaurant metrics calculated from raw booking rows:
- `total_revenue` = sum of revenue for valid bookings (divided by 100, cents → THB)
- `total_bookings` = count of valid bookings
- `total_guests` = sum of party sizes
- `total_no_shows` = count of no-show events
- `no_show_rate` = `total_no_shows / total_bookings`
- `avg_revenue_per_booking` = `total_revenue / total_bookings`
- `total_temporary_bookings` = count where `is_temporary = TRUE`

#### 2. GMV Filters (per Client Rules)
Before any aggregation, raw bookings are filtered using **all 7 conditions** simultaneously:

| Filter | Value | Reason |
|--------|-------|--------|
| `active` | `TRUE` | Exclude inactive bookings |
| `no_show` | `0` | Exclude no-show events from revenue |
| `revenue` | `> 0` | Exclude zero-revenue placeholder rows |
| `is_temporary` | `0` | Exclude unpaid temporary holds |
| `for_locking_system` | `0` | Exclude seat-locking placeholders |
| `channel` | `≠ 5` | Exclude internal/test channel |
| `ack` | `TRUE` | Only acknowledged/confirmed bookings |

#### 3. Outlier Removal
Copper Beyond Buffet locations are hardcoded exclusions per client instruction:
```python
master = master[~master['restaurant_id'].isin([4503, 4502, 933, 837])]
```
These are extreme revenue outliers that skew all aggregate statistics and ML model training.

#### 4. Metadata Deduplication
`dim_tags.csv` deduplicated on `restaurant_id`. Merged with transactional data to add:
`primary_cuisine`, `secondary_cuisines`, `primary_dining_style`, `facilities`, `primary_place`, `places`, `hashtags`

#### 5. Web & KOL Analytics Parsing
- **KOL Data:** Engagement metrics (`kol_views`, `kol_likes`, `kol_comments`) parsed from raw CSV. Values with "k" and "m" suffixes converted to numbers via regex.
- **Web Traffic:** Google Analytics `pagePaths` mapped to `restaurant_id` via slug matching. Produces `web_views` and `web_revenue`.
- **`kol_engagement_rate`**: `(kol_likes + kol_comments) / kol_views`

### Output
`Data/Processed/master_cleaned_data.csv` — 3,727 restaurants, ~20 columns.

---

## 4. Stage 02: Web Scraping

**Notebook:** `Data/02_Web_Scraping.ipynb`

### Purpose
Extract Google Maps ratings and reviews to establish an external, public reputation signal independent of Hungry Hub's internal data.

### Method
- **Query format:** `"{restaurant_name_en} {extracted_location} Bangkok"`
- **Source:** Google Maps via Apify scraper actors
- **Data extracted per restaurant:**
  - `gmaps_rating` — Overall star rating (0–5 scale)
  - `gmaps_reviews` — Total review count (used as a reliability factor)
  - Review text snippets (fed to Stage 03 for NLP)

### Coverage
- **373 out of 3,727** restaurants matched (10.0%)
- The remaining 90% have `gmaps_rating = 0` and `gmaps_reviews = 0`
- This sparsity is a known limitation and is handled by dynamic weighting in the scoring functions

### Output
`Data/Processed/master_web_scraping_data.csv`

---

## 5. Stage 03: NLP Sentiment Analysis

**Notebook:** `Data/03_NLP_Sentiment_Analysis.ipynb`

### Purpose
Extract sentiment signals from Google Maps review text to add a qualitative dimension beyond star ratings.

### Method
- **Analyzer:** VADER (Valence Aware Dictionary and sEntiment Reasoner) — a rule-based sentiment engine optimized for social media text
- **Input:** Review text snippets from Stage 02's Google Maps extraction
- **Output per restaurant:**
  - `raw_average_sentiment` — Mean VADER compound score across all reviews (–1 to +1)
  - `sentiment_variance` — Variance of sentiment scores (measures review consistency)
  - `nlp_review_count` — Number of reviews analyzed
  - `sentiment_score` — Normalized composite sentiment (0–100 scale)

### Coverage
- **323 out of 3,727** restaurants have NLP data (8.7%)
- Slightly lower than GMaps coverage because some restaurants had ratings but no extractable review text

### Output
`Data/Processed/master_nlp_data.csv`

---

## 6. Stage 04: Data Merging & Scoring

**Script:** `Data/run_04.py` | **Notebook:** `Data/04_Data_Merging_and_Scoring.ipynb`

### Overview
Consolidates all data sources (cleaned transactional, scraping, NLP) into one unified dataset and calculates three composite scoring dimensions.

### Step 1: Universal Merge
```python
df_merged = df_master.copy()  # Start with cleaned transactional data (3,727 rows)
df_merged = pd.merge(df_merged, df_scrape, on='restaurant_id', how='left')   # Add scraping data
df_merged = pd.merge(df_merged, df_nlp, on='restaurant_id', how='left')       # Add NLP data
```
- **Join type:** `left` — all 3,727 restaurants are preserved; missing scrape/NLP data becomes NaN
- **Duplicate identity columns** (`restaurant_name_en`, `restaurant_name_th`, `extracted_location`) dropped from scrape data before merge to avoid `_x`/`_y` suffix conflicts

### Step 2: Sparse Column Removal
Columns with <10% coverage are dropped **twice** (belt and suspenders) to ensure they don't leak through from any source:
```python
sparse_cols = ['tiktok_views', 'tiktok_likes', 'tiktok_shares', 'facebook_likes',
               'wongnai_rating', 'wongnai_reviews']
# Dropped from scrape data BEFORE merge
# AND dropped from merged dataframe AFTER merge
```

### Step 3: Missing Value Handling
```python
fillna_cols = ['gmaps_rating', 'gmaps_reviews', 'sentiment_score', 'sentiment_variance']
# All filled with 0 — absence of data is distinct from negative data
```

### Step 4: Scoring Functions

#### Helper: Min-Max Scaling
All scores are normalized to 0–100 range:
```python
def min_max_scale(series):
    s_min, s_max = series.min(), series.max()
    if s_max - s_min == 0: return 0  # Prevent division by zero
    return ((series - s_min) / (s_max - s_min)) * 100
```

#### A. Momentum Score (KOL Activity)
Measures social media buzz from KOL (Key Opinion Leader) partnerships.
```python
raw_reach = kol_views.fillna(0).clip(lower=0)                              # Prevent negative values
raw_engagement = (kol_likes.fillna(0) + kol_comments.fillna(0)).clip(lower=0)  # Same
scaled_reach = min_max_scale(np.log1p(raw_reach))
scaled_engagement = min_max_scale(np.log1p(raw_engagement))
momentum_score = scaled_reach * 0.4 + scaled_engagement * 0.6   # Quality (engagement) weighted higher
```
- **Weight rationale:** 60% engagement (likes, comments indicate real interest) vs. 40% reach (views can be passive)
- **Log transform:** `np.log1p()` compresses extreme outliers (some KOL posts get millions of views)
- **Bug fix:** `.clip(lower=0)` prevents `np.log1p(-1) = -inf` which would poison the entire min-max scaling
- **Coverage:** 5.3% nonzero (196/3,727)

#### B. Internal Score (Business Performance)
Measures the restaurant's operational performance within Hungry Hub's platform.
```python
internal_raw = np.log1p(total_revenue.fillna(0)) * 0.7 + np.log1p(total_bookings.fillna(0)) * 0.3
internal_score = min_max_scale(internal_raw)
```
- **Weight rationale:** 70% revenue (direct business impact) vs. 30% bookings (volume signal)
- **Coverage:** 97.7% nonzero (near-universal)

#### C. External Quality Score (Public Reputation)
Measures external perception from Google Maps and review sentiment.
```python
# Scale VADER sentiment (0-100) to 0-5 range to match GMaps rating scale
sentiment_rating_scale = sentiment_score / 20.0

# Dynamic weighting: only use available signals
w_gmaps = 0.6 * has_gmaps    # 1 if gmaps_rating > 0, else 0
w_sens  = 0.4 * has_sens      # 1 if sentiment_rating_scale > 0, else 0
total_w = w_gmaps + w_sens     # Sum of available weights (prevent /0 with .replace(0, 1))

composite_external_rating = (gmaps_rating * w_gmaps + sentiment_rating_scale * w_sens) / total_w

# Scale by reliability (more reviews = more trustworthy)
reliability_factor = np.log1p(gmaps_reviews)
external_quality_score = min_max_scale(composite_external_rating * reliability_factor)
```
- **Dynamic weighting logic:** If a restaurant has only GMaps (no NLP), the 60% weight becomes 100% of the available signal. This prevents penalizing restaurants that lack one data source.
- **Reliability factor:** `log1p(review_count)` ensures restaurants with 500 reviews are weighted more than those with 5, but diminishing returns prevent runaway scaling.
- **Coverage:** 10.0% nonzero (373/3,727)

#### D. Combined Scores
```python
stability_score = internal_score * 0.5 + external_quality_score * 0.5
final_priority_score = momentum_score * 0.7 + stability_score * 0.3
```

### Step 5: Validation Status Tagging
Rule-based preliminary categorization (informational only, not used as ML labels):
| Status | Rule | Purpose |
|--------|------|---------|
| Verified | `gmaps_reviews > 0` | Has external data |
| Viral Hit | `momentum_score > 60` | High KOL activity |
| Hidden Gem | `external_quality_score > 60 AND internal_score < 30` | High quality, low business |
| Cash Cow | `internal_score > 80` | Top performer |
| Unknown | Everything else | Default |

### Output
`Data/Processed/master_all_data.csv` — 3,727 rows, 44 columns, sorted by `final_priority_score` descending.

---

## 7. Stage 05: Feature Engineering

**Script:** `Data/run_05.py` | **Notebook:** `Data/05_Feature_Engineering.ipynb`

### Overview
Creates ML-ready features, assigns ground-truth classification labels, and performs out-of-fold stacking. This is the most complex stage in the pipeline.

### Step 1: Categorical Encoding

#### A. Region Encoding (from `places` column)
The `places` column contains comma-separated geographic tags like `"popularzone:thonglor, btsroute:bts asok, shoppingmall:emquartier"`. The `assign_region()` function scans for keyword matches in priority order:

| Code | Region | Keywords Matched | Count |
|------|--------|-----------------|-------|
| 0 | Unknown | `nan`, `unknown`, empty | 1,957 |
| 7 | Provincial | `pattaya`, `phuket`, `hua hin`, `chiang mai`, `khao yai`, `koh samui`, `krabi`, `rayong`, `sriracha` | — |
| 1 | CBD | `siam`, `chidlom`, `ploenchit`, `ratchaprasong`, `rajdamri`, `pathum wan`, `lumpini`, `lang suan` | 133 |
| 2 | Sukhumvit | `thonglor`, `ekkamai`, `phrom phong`, `asok`, `nana`, `sukhumvit`, `phra khanong`, `on nut`, `bang na`, `udom suk`, `bearing` | 304 |
| 3 | Silom/Sathon | `silom`, `sathon`, `surasak`, `chong nonsi`, `sala daeng`, `sam yan`, `bang rak` | 102 |
| 4 | Riverside | `charoen krung`, `charoen nakorn`, `iconsiam`, `thonburi`, `river`, `riverside`, `khlong san` | 56 |
| 5 | North/Ari | `ari`, `phaya thai`, `victory monument`, `ratchathewi`, `chatuchak`, `saphan khwai`, `inthamara`, `lat phrao`, `ladprao` | 177 |
| 8 | Ratchada/Rama9 | `ratchada`, `rama 9`, `din daeng`, `huai khwang`, `bang kapi`, `ramkhamhaeng` | 116 |
| 9 | Outer Bangkok | `nonthaburi`, `samut prakan`, `bang sue`, `muangthong`, `ram intra`, `sai mai`, `rangsit`, `min buri`, `ratchaphruek`, `pinklao`, `banthat thong`, `rama 3`, `rama 4`, `rama 2` | 313 |
| 6 | Other | No keyword match (but has location data) | 569 |

> **Bug fix:** Original code used `extracted_location` which contained **cuisine data** (e.g., "Japanese", "Thai"), not geographic locations. This caused 99.4% of restaurants to be encoded as 6 ("Other"). Fixed to use the `places` column which has actual geographic tags.

#### B. Cuisine Encoding (from `primary_cuisine` + `secondary_cuisines`)
```python
def extract_cuisine(row):
    c = str(row['primary_cuisine']).lower() + " " + str(row['secondary_cuisines']).lower()
    # Priority-ordered keyword matching:
```
| Code | Cuisine | Keywords | Count |
|------|---------|----------|-------|
| 1 | Thai | `thai` | 1,110 |
| 2 | Japanese | `japanese`, `sushi`, `omakase` | 377 |
| 3 | Italian | `italian` | 170 |
| 4 | Chinese | `chinese` | 202 |
| 5 | Buffet | `buffet` | 0 |
| 6 | Seafood | `seafood` | 0 |
| 7 | Steak/Grill | `steak`, `grill` | 49 |
| 0 | Other | No match | 1,819 |

### Step 2: Efficiency Ratios
```python
revenue_per_guest = total_revenue / total_guests          # 0 if total_guests == 0
revenue_per_view  = total_revenue / web_views             # 0 if web_views == 0
booking_conversion_rate = total_bookings / web_views      # 0 if web_views == 0
```
All use `np.where` to safely handle division by zero.

### Step 3: NLP Intent Flag Extraction
Binary flags (0/1) extracted from Google Maps review text. Each flag indicates whether specific keywords appear in the restaurant's reviews:

| Feature | Keywords Scanned |
|---------|-----------------|
| `intent_birthday` | `birthday`, `bday` |
| `intent_anniversary` | `anniversary`, `anniv`, `romantic`, `date` |
| `intent_queue` | `queue`, `wait`, `line`, `packed`, `busy` |
| `intent_live_music` | `music`, `band`, `live`, `singer` |
| `intent_view` | `view`, `rooftop`, `sunset`, `scenery` |

- `has_reviews` flag (1/0) distinguishes "no reviews analyzed" from "all-zero keyword hits"
- NaN values filled with 0 for restaurants without GMaps review text
- **Error handling:** If `gmaps_reviews.csv` doesn't exist, the entire NLP block is skipped with a warning

### Step 4: Seasonality Velocity Ratio
```python
CURRENT_DATE = df_rev['review_date'].max()  # Anchored to latest review in dataset

reviews_l30d = count of reviews in [CURRENT_DATE - 30 days, CURRENT_DATE]
reviews_yoy_30d = count of reviews in [CURRENT_DATE - 395 days, CURRENT_DATE - 365 days]

velocity_ratio = (reviews_l30d + 5) / (reviews_yoy_30d + 5)    # Bayesian smoothed
```
- **Bayesian smoothing (+5 prior):** Prevents extreme ratios from small samples. Without it, a restaurant going from 0→1 reviews would get velocity_ratio = infinity.
- **Interpretation:** `> 1.0` = growing, `< 1.0` = declining, `= 1.0` = stable
- **Derived feature:** `internal_opportunity_gap` = reviews_l30d − (expected_bookings × 0.05)
- **Error handling:** If `gmaps_reviews.csv` doesn't exist, velocity features are skipped entirely

### Step 5: MECE Rule-Based Labeling

This is the **ground-truth label** that the ML model learns to predict. The labeling uses **percentile thresholds on internal KPIs** (97.7% data coverage) rather than external metrics (10% coverage) to ensure robust classification.

#### Threshold Computation
```python
med_int  = df['internal_score'].median()           # ~58.8
p25_int  = df['internal_score'].quantile(0.25)     # ~50.1
p40_int  = df['internal_score'].quantile(0.40)     # ~55.3
p60_int  = df['internal_score'].quantile(0.60)     # ~62.3
no_show_75 = df['no_show_rate'].quantile(0.75)     # ~0.0130
arb_25   = df['avg_revenue_per_booking'].quantile(0.25)  # ~10,680 THB

# External threshold: 75th pct among those WITH external data only
has_external = df['composite_external_rating'] > 0
ext_75pct = df.loc[has_external, 'composite_external_rating'].quantile(0.75)  # ~4.47
```

#### Label Assignment (Priority Order — MECE)
Labels are assigned in **strict priority order**. Once a restaurant matches a rule, it is classified and skipped by subsequent rules. This ensures Mutually Exclusive and Collectively Exhaustive (MECE) categories.

| Priority | Label | Rule | Business Meaning | Count |
|----------|-------|------|-----------------|-------|
| 1 | **Hidden Gem** | `composite_external_rating > 4.47` (75th pct among peers with data) AND `internal_score < 55.3` (40th pct) | High public quality but underperforming on Hungry Hub — needs marketing exposure | 23 (0.6%) |
| 2 | **Declining** | `internal_score > 62.3` (60th pct) AND (`no_show_rate > 0.013` OR `avg_revenue_per_booking < 10,680`) | Previously strong but showing operational problems — needs operational fixes, not marketing | 633 (17.0%) |
| 3 | **Rising** | `internal_score` between 50.1 (25th) and 58.8 (median) AND `booking_conversion_rate > 0` | Low-mid performance base but demonstrating digital conversion traction — invest marketing here | 89 (2.4%) |
| 4 | **Stable** | All remaining | Performing within expectations — maintain current support | 2,982 (80.0%) |

#### Design Rationale
- **Why percentile-based?** Absolute thresholds (e.g., "velocity > 1.25") fail when 90% of restaurants lack the required metric. Percentile thresholds adapt to the dataset and use universally-available internal KPIs.
- **Why this priority order?** Hidden Gems are rarest and most valuable, so they're checked first to prevent being swallowed by other categories. Declining is checked before Rising to ensure high-performers with problems aren't mislabeled as Rising.
- The **Rising** label specifically requires `booking_conversion_rate > 0`, which means the restaurant must have web views (`web_views > 0` for 23% of restaurants). This is intentional — Rising means "showing digital traction" which requires measurable web activity.

### Step 6: Pruning Text Columns
Non-numeric, non-feature columns dropped before ML:
```python
cols_to_drop = ['name', 'primary_cuisine', 'secondary_cuisines', 'primary_dining_style',
                'secondary_dining_styles', 'facilities', 'primary_place', 'places',
                'hashtags', 'restaurant_name_en', 'restaurant_name_th', 'extracted_location']
```

### Step 7: Out-of-Fold (OOF) Stacking

#### Purpose
Predict each restaurant's "expected" internal performance from external features alone. The residual (`actual - expected`) reveals which restaurants are over/under-performing vs. their characteristics.

#### Method
```python
# Target: internal_score
# Features: everything EXCEPT internal operational volumes and label-construction columns
# Model: LightGBM Regressor
# Validation: 5-fold KFold (shuffle=True, random_state=42)

for train_idx, val_idx in kf.split(X_reg):
    model = lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr, categorical_feature=['region_encoded', 'cuisine_encoded'])
    oof_preds[val_idx] = model.predict(X_va)

df['expected_kpi'] = oof_preds
df['residual_kpi'] = df['internal_score'] - df['expected_kpi']
```
- **Positive residual:** Restaurant is outperforming what its external features predict → internally strong
- **Negative residual:** Restaurant is underperforming → may benefit from marketing to close the gap
- **OOF guarantee:** Each prediction is made by a model that never saw that restaurant during training

#### Features Excluded from OOF Regression (to prevent leakage)
`restaurant_id`, `target_label`, `validation_status`, `no_show_rate`, `velocity_ratio`, `internal_score`, `total_revenue`, `total_bookings`, `total_guests`, `total_no_shows`, `avg_revenue_per_booking`, `total_temporary_bookings`, `target_encoded`, `proxy_yoy_growth`, `reviews_l30d`, `reviews_yoy_30d`

### Step 8: Final Column Pruning
All target-construction variables dropped from ML features to prevent leakage:
```python
cols_to_drop.extend([
    'proxy_yoy_growth', 'relative_cross_sectional_index',
    'total_revenue_clipped', 'web_views_clipped', 'total_bookings_clipped',
    'total_revenue', 'total_bookings', 'total_guests', 'total_no_shows',
    'avg_revenue_per_booking', 'total_temporary_bookings',
    'internal_score', 'velocity_ratio', 'no_show_rate', 'reviews_yoy_30d'
])
```

### File Lock Workaround
The script writes to a `.tmp` file and then renames it to the target file. If the target is locked (e.g., open in Excel), the `.tmp` file is preserved:
```python
shutil.move(TEMP_FILE, OUTPUT_FILE)
# except PermissionError → keeps .tmp
```

### Output
`Data/Processed/ML_Ready_Features.csv` — 3,727 rows, 32 columns.

---

## 8. Stage 06: ML Classification

**Script:** `Models/run_06.py` | **Notebook:** `Models/06_Restaurant_Classification.ipynb`

### Overview
Trains a LightGBM multiclass classifier to predict restaurant segments from external/observable features. Uses Stratified K-Fold cross-validation, exports class probabilities, and computes a marketing priority score.

### Why Stratified K-Fold (Not Walk-Forward)
- The dataset is **cross-sectional** — each restaurant is a single aggregated row, not a time series of observations
- There is no temporal ordering between restaurants (restaurant_id is not chronological)
- With only **23 Hidden Gems** and **89 Rising** samples, time-series splits would produce folds with zero minority class samples, making evaluation impossible
- **StratifiedKFold** ensures each fold contains proportional representation of all 4 classes
- Walk-forward testing would be appropriate if we had **monthly snapshot data** (e.g., "predict March segments from February features") but we have a single-point-in-time aggregation

### Target Encoding
```python
target_mapping = {'Declining': 0, 'Stable': 1, 'Rising': 2, 'Hidden Gem': 3}
inv_map = {0: 'Declining', 1: 'Stable', 2: 'Rising', 3: 'Hidden Gem'}
```
> **Bug fix:** The original `inv_map` was missing key `3: 'Hidden Gem'`, causing all Hidden Gem predictions to become NaN and disappear from downstream analysis.

### Feature Set (17 features)
After dropping all leakage, sparse, and non-numeric columns, 17 features remain:

| # | Feature | Coverage | Type | Description |
|---|---------|----------|------|-------------|
| 1 | `days_in_advance` | 66% | Continuous | Average booking lead time (days) |
| 2 | `weighted_rating_score` | 48% | Continuous | Hungry Hub's internal rating composite |
| 3 | `kol_views` | 5% | Continuous | KOL video views |
| 4 | `kol_likes` | 5% | Continuous | KOL content likes |
| 5 | `kol_comments` | 5% | Continuous | KOL content comments |
| 6 | `unique_kols_used` | 5% | Continuous | Number of unique KOL partnerships |
| 7 | `web_views` | 23% | Continuous | Website page views |
| 8 | `kol_engagement_rate` | 5% | Continuous | Engagement ratio (likes+comments)/views |
| 9 | `gmaps_rating` | 10% | Continuous | Google Maps star rating (0–5) |
| 10 | `gmaps_reviews` | 10% | Continuous | Google Maps total review count |
| 11 | `raw_average_sentiment` | 9% | Continuous | VADER mean compound score |
| 12 | `sentiment_variance` | 9% | Continuous | Sentiment consistency measure |
| 13 | `nlp_review_count` | 9% | Continuous | Reviews analyzed by NLP |
| 14 | `sentiment_score` | 9% | Continuous | Composite sentiment (0–100) |
| 15 | `sentiment_rating_scale` | 9% | Continuous | Sentiment mapped to 0–5 scale |
| 16 | `region_encoded` | 100% | Categorical | Bangkok zone code (0–9) |
| 17 | `cuisine_encoded` | 100% | Categorical | Cuisine category code (0–7) |

### Leakage Prevention (Columns Dropped Before Training)

Three categories of columns are dropped:

**1. Label-construction features (direct leakage):**
`composite_external_rating`, `external_quality_score`, `reliability_factor` — used in the Hidden Gem rule threshold. If left in, the model could trivially memorize `composite_external_rating > 4.47 → Hidden Gem`.

**2. Internal operational metrics (indirect leakage):**
`internal_score`, `no_show_rate`, `avg_revenue_per_booking`, `booking_conversion_rate`, `revenue_per_view`, `revenue_per_guest`, `web_revenue` — used in Declining and Rising rules.

**3. Derived/combined scores:**
`stability_score`, `final_priority_score`, `momentum_score`, `expected_kpi`, `residual_kpi`, `validation_status`, `internal_opportunity_gap`, `weighted_opportunity_gap`, `reviews_l30d`

**4. Sparse platform columns:**
`tiktok_views`, `tiktok_likes`, `tiktok_shares`, `facebook_likes`, `wongnai_rating`, `wongnai_reviews`

### LightGBM Hyperparameters
```python
lgb_params = {
    'objective': 'multiclass',
    'num_class': 4,
    'metric': 'multi_error',
    'boosting_type': 'gbdt',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'feature_fraction': 0.8,    # Use 80% of features per tree (regularization)
    'verbose': -1,
    'random_state': 42
}
```
- **CV: 100 boosting rounds** per fold
- **Production model: 150 boosting rounds** (more data = can train longer)

### Training-Time Winsorization
Volume features are clipped at the 95th percentile during each fold, fitted on training data only:
```python
for vol_feat in ['total_revenue', 'web_views', 'total_bookings']:
    upper = X_train[vol_feat].quantile(0.95)
    X_train[f'{vol_feat}_clipped'] = np.where(X_train[vol_feat] > upper, upper, X_train[vol_feat])
    X_test[f'{vol_feat}_clipped'] = np.where(X_test[vol_feat] > upper, upper, X_test[vol_feat])
```
> Note: These columns are not currently in the feature set (they're dropped as leakage), so this winsorization is a no-op in the current pipeline. It remains as defensive code.

### Cross-Validation Results
| Fold | Accuracy |
|------|----------|
| 1 | 77.9% |
| 2 | 78.4% |
| 3 | 79.6% |
| 4 | 77.9% |
| 5 | 79.9% |
| **Mean** | **78.7%** |

### Production Model Results (Trained on All Data)

| Segment | Precision | Recall | F1-Score | Support |
|---------|-----------|--------|----------|---------|
| Declining | 0.96 | 0.56 | 0.71 | 633 |
| Stable | 0.91 | 0.99 | 0.95 | 2,982 |
| Rising | 0.96 | 0.87 | 0.91 | 89 |
| Hidden Gem | 1.00 | 1.00 | 1.00 | 23 |
| **Overall** | **0.92** | **0.92** | **0.91** | **3,727** |

> **Important:** The production accuracy (92%) is measured on the training data — this is NOT an unbiased estimate. The **78.7% CV accuracy** is the honest, unbiased metric. The production model is expected to generalize at ~79% accuracy.

### Priority Score Computation
```python
df['prob_declining']  = final_predictions_probs[:, 0]
df['prob_stable']     = final_predictions_probs[:, 1]
df['prob_rising']     = final_predictions_probs[:, 2]
df['prob_hidden_gem'] = final_predictions_probs[:, 3]

ml_priority_score = (prob_rising × 0.6 + prob_hidden_gem × 0.4) × 100
```
- **Weight rationale:** Rising partners (60%) are weighted higher because they are actionable through marketing investment. Hidden Gems (40%) are also actionable but require different strategies (exposure campaigns vs. conversion campaigns).
- **Range:** 0–100. Top-ranked partners score ~58.

### Output
`Data/Processed/Categorized_Restaurants.csv` — 3,727 rows, 12 columns: `restaurant_id`, `target_label`, `ML_Predicted_Segment`, `prob_declining`, `prob_stable`, `prob_rising`, `prob_hidden_gem`, `ml_priority_score`, `expected_kpi`, `residual_kpi`, `momentum_score`, `external_quality_score`.

---

## 9. Stage 08: Dashboard Generation

**Script:** `Models/run_08.py` | **Notebook:** `Models/08_Retention_Dashboard.ipynb`

### Overview
Produces the final marketing deliverables: a ranked retention dashboard for immediate action, and full portfolio rankings for strategic planning.

### Step 1: Data Merge
```python
df_dash = pd.merge(
    df_cat,           # Categorized (predictions + probabilities)
    df_feat[cols],    # Selected feature columns for context
    on='restaurant_id', how='left'
)
```
Context columns merged: `booking_conversion_rate`, `web_views`, `gmaps_rating`, `gmaps_reviews`, `weighted_rating_score`, `region_encoded`, `cuisine_encoded`

### Step 2: Retention Dashboard (Actionable Partners)
```python
df_retention = df_dash[df_dash['ML_Predicted_Segment'].isin(['Rising', 'Hidden Gem'])]
df_retention = df_retention.sort_values('ml_priority_score', ascending=False)
df_retention['priority_rank'] = range(1, len(df_retention) + 1)
```
- **Filters:** Only Rising + Hidden Gem (the two actionable marketing segments)
- **Sorting:** Descending `ml_priority_score` — highest opportunity first
- **Ranking:** Explicit 1-based rank column for easy interpretation

### Step 3: Full Portfolio Rankings
```python
df_full = df_dash.sort_values('ml_priority_score', ascending=False)
df_full['overall_rank'] = range(1, len(df_full) + 1)
```
All 3,727 restaurants ranked, including Stable and Declining.

### Outputs
| File | Rows | Description |
|------|------|-------------|
| `Dashboard_List_1_Retention.csv` | **103** | 80 Rising + 23 Hidden Gem, sorted by priority |
| `Dashboard_Predictions.csv` | **3,727** | Full portfolio ranked |

---

## 10. Interactive Dashboard

**Application:** `Dashboard/app.py` (Streamlit)

### Launch Command
```bash
python -m streamlit run Dashboard/app.py
```

### Technology Stack
- **Framework:** Streamlit 1.54
- **Charts:** Plotly (interactive, dark theme)
- **Styling:** Custom CSS with Inter font, gradient KPI cards, glassmorphism

### Dashboard Sections

| Section | Description |
|---------|-------------|
| **Sidebar Filters** | Segment, Region, Cuisine multiselects + min priority score slider |
| **6 KPI Cards** | Total portfolio, revenue concentration, Rising count, Hidden Gem count, Declining count, total actionable |
| **Tab 1: Priority Marketing List** | Interactive sortable table of Rising + Hidden Gem partners with progress bars for probabilities. Toggle to show all segments. CSV download button. |
| **Tab 2: Portfolio Map** | Plotly scatter plot: `internal_score` (X) vs `weighted_rating_score` (Y), colored by segment, sized by priority score. Identifies quadrants: Cash Cows, Hidden Gems, At Risk. |
| **Tab 3: Segment Analysis** | Donut chart of segment distribution. Stacked bar charts: segments by cuisine and by region. |
| **Tab 4: Restaurant Explorer** | Dropdown search by name. Shows segment, probabilities, performance bar chart (5 dimensions), and business metrics table (revenue, bookings, no-show rate, web views, etc.) |

---

## 11. Final Results Summary

| Metric | Value |
|--------|-------|
| Total restaurants | 3,727 |
| Revenue concentration | 95.1% from top 20% |
| ML segments | 4 (Stable, Declining, Rising, Hidden Gem) |
| CV accuracy | 78.7% |
| Features used | 17 (leakage-free) |
| Dashboard targets | 103 (80 Rising + 23 Hidden Gem) |
| Top priority score | 58.5 |

### Segment Distribution

| Segment | Rule-Based | ML Predicted | Description |
|---------|------------|--------------|-------------|
| **Stable** | 2,982 (80.0%) | 3,256 (87.4%) | Performing within expectations |
| **Declining** | 633 (17.0%) | 368 (9.9%) | High revenue but deteriorating operational signals |
| **Rising** | 89 (2.4%) | 80 (2.1%) | Low base but showing digital conversion traction |
| **Hidden Gem** | 23 (0.6%) | 23 (0.6%) | High external quality, low internal performance |

---

## 12. Known Limitations & Design Decisions

### Feature Sparsity
14 of 17 features have less than 25% coverage. The model relies heavily on `region_encoded` and `cuisine_encoded` (100% coverage) and `weighted_rating_score` (48%) for most predictions. For the ~77% of restaurants with zero web/KOL/GMaps data, the model has very limited signal.

### Hidden Gem Detection
Hidden Gems require `composite_external_rating > 75th percentile` among peers. Since only 10% of restaurants have external data, Hidden Gem detection is limited to this subset. Restaurants without GMaps presence cannot currently be classified as Hidden Gems.

### Declining Recall
The ML model has only 56% recall for Declining restaurants — it misclassifies 44% as Stable. This is because the Declining rule uses `no_show_rate` and `avg_revenue_per_booking` which are dropped from training features (leakage prevention). The model must infer decline from external signals alone.

### Class Imbalance
The dataset is heavily imbalanced: 80% Stable, 17% Declining, 2.4% Rising, 0.6% Hidden Gem. LightGBM handles this implicitly through its leaf-level optimization, but extreme minority classes (23 Hidden Gems) can be unreliable.

### Single-Snapshot Data
The pipeline operates on a single aggregated snapshot. True "momentum" detection requires time-series data (monthly snapshots) for trend analysis. The current velocity_ratio from GMaps reviews is only available for 10% of restaurants.

---

## 13. Bugs Fixed During Development

| Bug | Root Cause | Impact | Fix |
|-----|-----------|--------|-----|
| **NaN momentum_score** | `np.log1p(-1) = -inf` when KOL likes + comments was negative | 100% of momentum scores were NaN | `.clip(lower=0)` before `np.log1p()` |
| **Sparse columns persisting** | Columns dropped from merge key but not from merged dataframe | Noise features in ML training | Drop from merged df after merge (belt and suspenders) |
| **`inv_map` missing Hidden Gem** | Key `3: 'Hidden Gem'` absent from integer→string mapping | All Hidden Gem predictions → NaN → filtered out of dashboard | Added missing key |
| **`region_encoded` = 99.4% constant** | `extracted_location` contained cuisine data ("Japanese") not geographic locations | Region feature was useless (all value 6) | Switched to `places` column with actual geographic tags |
| **`composite_external_rating` leakage** | Used directly in Hidden Gem labeling rule AND in training features | Model memorized threshold instead of learning patterns | Dropped from training features |
| **Syntax error in run_04.py** | Duplicate list lines in `fillna_cols` definition | Script crash on execution | Consolidated to single clean list |
| **Unicode encoding error** | Checkmark emoji (✅) in print statements on Windows cp1252 console | Script crash on print | Replaced with `[OK]` |
