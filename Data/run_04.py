import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

CLEAN_FILE = "Processed/master_cleaned_data.csv"
SCRAPE_FILE = "Processed/master_web_scraping_data.csv"
NLP_FILE = "Processed/master_nlp_data.csv"
OUTPUT_FILE = "Processed/master_all_data.csv"

print("Loading Data...")
df_master = pd.read_csv(CLEAN_FILE)
print(f"Master Cleaned Records: {len(df_master)}")

try:
    df_scrape = pd.read_csv(SCRAPE_FILE)
    print(f"Web Scraping Records: {len(df_scrape)}")
except:
    df_scrape = pd.DataFrame()

try:
    df_nlp = pd.read_csv(NLP_FILE)
    print(f"NLP Sentiment Records: {len(df_nlp)}")
except:
    df_nlp = pd.DataFrame()

# ── 2. Universal Merge ──
df_merged = df_master.copy()

if not df_scrape.empty:
    # Drop duplicate identity columns AND sparse platform columns from scrape data before merge
    scrape_drop_cols = ['restaurant_name_en', 'restaurant_name_th', 'extracted_location',
                        'tiktok_views', 'tiktok_likes', 'tiktok_shares', 'facebook_likes',
                        'wongnai_rating', 'wongnai_reviews']
    df_merged = pd.merge(df_merged, df_scrape.drop(columns=scrape_drop_cols, errors='ignore'), on='restaurant_id', how='left')

if not df_nlp.empty:
    df_merged = pd.merge(df_merged, df_nlp, on='restaurant_id', how='left')

print(f"Merged Dataset Shape: {df_merged.shape}")

# Also remove sparse columns if they leaked from master_cleaned_data
sparse_cols = ['tiktok_views', 'tiktok_likes', 'tiktok_shares', 'facebook_likes',
               'wongnai_rating', 'wongnai_reviews']
df_merged = df_merged.drop(columns=[c for c in sparse_cols if c in df_merged.columns], errors='ignore')

# Ensure numeric fill logic for newly generated metrics (FIXED: removed duplicate lines)
fillna_cols = [
    'gmaps_rating', 'gmaps_reviews',
    'sentiment_score', 'sentiment_variance'
]
for c in fillna_cols:
    if c in df_merged.columns:
        df_merged[c] = df_merged[c].fillna(0)
    else:
        df_merged[c] = 0

# ── 3. Prioritization Scoring Logic ──
def min_max_scale(series):
    s_min = series.min()
    s_max = series.max()
    if s_max - s_min == 0: return pd.Series(0, index=series.index)
    return ((series - s_min) / (s_max - s_min)) * 100

### A. Momentum Score ###
# FIXED: fillna(0) AND clip(lower=0) BEFORE log1p to prevent -inf and NaN
# np.log1p(-1) = -inf which poisons the entire min_max_scale output
raw_reach = df_merged['kol_views'].fillna(0).clip(lower=0)
raw_engagement = (df_merged['kol_likes'].fillna(0) + df_merged['kol_comments'].fillna(0)).clip(lower=0)

scaled_reach = min_max_scale(np.log1p(raw_reach))
scaled_engagement = min_max_scale(np.log1p(raw_engagement))

# 40% Reach and 60% Engagement (Quality over Quantity)
df_merged['momentum_score'] = (scaled_reach * 0.4) + (scaled_engagement * 0.6)
print(f"Momentum Score: {df_merged['momentum_score'].isna().sum()} NaN, mean={df_merged['momentum_score'].mean():.2f}")


### B. Internal Stability Score ###
internal_raw = np.log1p(df_merged['total_revenue'].fillna(0)) * 0.7 + np.log1p(df_merged['total_bookings'].fillna(0)) * 0.3
df_merged['internal_score'] = min_max_scale(internal_raw)


### C. External Quality Score (SOLVING MISSING DATA PENALTY) ###
# VADER mapped 0 to 100. Move it to 0-5 to be proportional with GMaps
df_merged['sentiment_rating_scale'] = df_merged['sentiment_score'] / 20.0

# Identify existing components
has_gmaps = (df_merged['gmaps_rating'] > 0).astype(int)
has_sens = (df_merged['sentiment_rating_scale'] > 0).astype(int)

# Base conceptual weights
w_gmaps = 0.6 * has_gmaps
w_sens = 0.4 * has_sens

# Total viable weight
total_w = w_gmaps + w_sens
total_w = total_w.replace(0, 1) # Fallback to prevent divide by zero

df_merged['composite_external_rating'] = (
    (df_merged['gmaps_rating'] * w_gmaps) +
    (df_merged['sentiment_rating_scale'] * w_sens)
) / total_w

# Multiply by reliability count
df_merged['reliability_factor'] = np.log1p(df_merged['gmaps_reviews'])
df_merged['external_quality_score'] = min_max_scale(df_merged['composite_external_rating'] * df_merged['reliability_factor'])


### D. Final Calculation ###
df_merged['stability_score'] = (df_merged['internal_score'] * 0.5) + (df_merged['external_quality_score'] * 0.5)
df_merged['final_priority_score'] = (df_merged['momentum_score'] * 0.7) + (df_merged['stability_score'] * 0.3)

# ── 4. Final Categorization ──
df_merged['validation_status'] = 'Unknown'

# Validated if there is scraping data (FIXED: removed references to deleted sparse columns)
scraped_mask = (df_merged['gmaps_reviews'] > 0)
df_merged.loc[scraped_mask, 'validation_status'] = 'Verified'

# Viral Hit: High Momentum
df_merged.loc[(df_merged['momentum_score'] > 60), 'validation_status'] = 'Viral Hit'

# Hidden Gem: High External Quality BUT Low Internal Performance
df_merged.loc[
    (df_merged['external_quality_score'] > 60) &
    (df_merged['internal_score'] < 30),
    'validation_status'
] = 'Hidden Gem'

# Cash Cow: High Internal Performance and Stable External Quality
df_merged.loc[(df_merged['internal_score'] > 80), 'validation_status'] = 'Cash Cow'

# Output
df_final = df_merged.sort_values('final_priority_score', ascending=False)
df_final.to_csv(OUTPUT_FILE, index=False)

print(f"\n[OK] Fully Integrated! Saved {len(df_final)} records to {OUTPUT_FILE}")
print(f"Momentum NaN check: {df_final['momentum_score'].isna().sum()}")
print(f"Sparse cols remaining: {[c for c in sparse_cols if c in df_final.columns]}")
print(df_final[['final_priority_score', 'momentum_score', 'external_quality_score', 'validation_status']].head(10))
