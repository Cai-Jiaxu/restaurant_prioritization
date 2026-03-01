import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

INPUT_FILE = "Processed/master_all_data.csv"
REVIEWS_FILE = "../gmaps_reviews.csv"
OUTPUT_FILE = "Processed/ML_Ready_Features.csv"

print("Loading Scaled Dataset...")
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} restaurants.")

# ── 2. Categorical Encoding ──
print("Encoding Categoricals...")

# A. Location Binning
# BUG FIX: `extracted_location` contains CUISINE data (not location).
# Using `places` column instead — it contains actual geographic data like
# "popularzone:thonglor, btsroute:bts asok, shoppingmall:emquartier"
def assign_region(places_str):
    loc = str(places_str).lower()
    if loc == 'nan' or loc == 'unknown' or loc == '': return 0  # Unknown
    # Non-Bangkok locations
    if any(x in loc for x in ['pattaya', 'phuket', 'hua hin', 'chiang mai', 'khao yai',
                               'koh samui', 'krabi', 'rayong', 'sriracha']): return 7  # Provincial
    # Bangkok CBD
    if any(x in loc for x in ['siam', 'chidlom', 'ploenchit', 'ratchaprasong', 'rajdamri',
                               'pathum wan', 'lumpini', 'lang suan']): return 1  # CBD
    # Sukhumvit corridor
    if any(x in loc for x in ['thonglor', 'ekkamai', 'phrom phong', 'asok', 'nana',
                               'sukhumvit', 'phra khanong', 'on nut', 'bang na',
                               'udom suk', 'bearing']): return 2  # Sukhumvit
    # Silom / Sathon business district
    if any(x in loc for x in ['silom', 'sathon', 'surasak', 'chong nonsi', 'sala daeng',
                               'sam yan', 'bang rak']): return 3  # Silom/Sathon
    # Riverside / Charoen Krung
    if any(x in loc for x in ['charoen krung', 'charoen nakorn', 'iconsiam', 'thonburi',
                               'river', 'riverside', 'khlong san']): return 4  # Riverside
    # North Bangkok / Ari / Chatuchak
    if any(x in loc for x in ['ari', 'phaya thai', 'victory monument', 'ratchathewi',
                               'chatuchak', 'saphan khwai', 'inthamara',
                               'lat phrao', 'ladprao']): return 5  # North/Ari
    # Ratchada / Rama 9 / East Bangkok
    if any(x in loc for x in ['ratchada', 'rama 9', 'din daeng', 'huai khwang',
                               'bang kapi', 'ramkhamhaeng']): return 8  # Ratchada/Rama9
    # Outer Bangkok suburbs
    if any(x in loc for x in ['nonthaburi', 'samut prakan', 'bang sue', 'muangthong',
                               'ram intra', 'sai mai', 'rangsit', 'min buri',
                               'ratchaphruek', 'pinklao', 'banthat thong',
                               'rama 3', 'rama 4', 'rama 2']): return 9  # Outer Bangkok
    return 6  # Other/Unclassified

df['region_encoded'] = df['places'].apply(assign_region)
print(f"Region distribution: {df['region_encoded'].value_counts().sort_index().to_dict()}")

# B. Cuisine Binning
def extract_cuisine(row):
    c = str(row['primary_cuisine']).lower() + " " + str(row['secondary_cuisines']).lower()
    if 'thai' in c: return 1
    if 'japanese' in c or 'sushi' in c or 'omakase' in c: return 2
    if 'italian' in c: return 3
    if 'chinese' in c: return 4
    if 'buffet' in c: return 5
    if 'seafood' in c: return 6
    if 'steak' in c or 'grill' in c: return 7
    return 0 # Other

df['cuisine_encoded'] = df.apply(extract_cuisine, axis=1)

# ── 3. Efficiency Ratios ──
print("Preserving Original Outliers (Winsorization moved to Model Cross-Validation)...")
print("Calculating Efficiency Ratios...")
df['revenue_per_guest'] = np.where(df['total_guests'] > 0, df['total_revenue'] / df['total_guests'], 0)
df['revenue_per_view'] = np.where(df['web_views'] > 0, df['total_revenue'] / df['web_views'], 0)
df['booking_conversion_rate'] = np.where(df['web_views'] > 0, df['total_bookings'] / df['web_views'], 0)

# ── 4. NLP Keyword Trigger Extraction ──
print("Extracting NLP Keywords...")
try:
    df_rev = pd.read_csv(REVIEWS_FILE)

    # Aggregate all text snippets per restaurant
    rev_text = df_rev.groupby('restaurant_id')['text_snippet'].apply(lambda x: ' '.join(x.dropna().astype(str).tolist())).reset_index()

    def flag_keyword(text, keywords):
        t = str(text).lower()
        return int(any(k in t for k in keywords))

    rev_text['intent_birthday'] = rev_text['text_snippet'].apply(lambda x: flag_keyword(x, ['birthday', 'bday']))
    rev_text['intent_anniversary'] = rev_text['text_snippet'].apply(lambda x: flag_keyword(x, ['anniversary', 'anniv', 'romantic', 'date']))
    rev_text['intent_queue'] = rev_text['text_snippet'].apply(lambda x: flag_keyword(x, ['queue', 'wait', 'line', 'packed', 'busy']))
    rev_text['intent_live_music'] = rev_text['text_snippet'].apply(lambda x: flag_keyword(x, ['music', 'band', 'live', 'singer']))
    rev_text['intent_view'] = rev_text['text_snippet'].apply(lambda x: flag_keyword(x, ['view', 'rooftop', 'sunset', 'scenery']))

    rev_text.drop(columns=['text_snippet'], inplace=True)
    df = pd.merge(df, rev_text, on='restaurant_id', how='left')

    df['has_reviews'] = df['intent_birthday'].notna().astype(int)
    for col in ['intent_birthday', 'intent_anniversary', 'intent_queue', 'intent_live_music', 'intent_view']:
        df[col] = df[col].fillna(0).astype(int)
except Exception as e:
    print(f"Warning: Could not process NLP triggers from reviews file. {e}")

# ── 5. Seasonality Velocity Ratio (Optional — from gmaps_reviews.csv) ──
print("Calculating Seasonality Velocity Ratio...")
try:
    # Convert review_date to datetime
    df_rev['review_date'] = pd.to_datetime(df_rev['review_date'], errors='coerce')
    df_rev = df_rev.dropna(subset=['review_date'])

    # Anchor "current date" to the max scraped timestamp
    CURRENT_DATE = df_rev['review_date'].max()

    # L30 Days
    l30_start = CURRENT_DATE - timedelta(days=30)
    l30_revs = df_rev[(df_rev['review_date'] >= l30_start) & (df_rev['review_date'] <= CURRENT_DATE)]
    l30_counts = l30_revs.groupby('restaurant_id').size().reset_index(name='reviews_l30d')

    # L30 Days Last Year (Seasonality Baseline)
    yoy_end = CURRENT_DATE - timedelta(days=365)
    yoy_start = yoy_end - timedelta(days=30)
    yoy_revs = df_rev[(df_rev['review_date'] >= yoy_start) & (df_rev['review_date'] <= yoy_end)]
    yoy_counts = yoy_revs.groupby('restaurant_id').size().reset_index(name='reviews_yoy_30d')

    # Merge
    df = pd.merge(df, l30_counts, on='restaurant_id', how='left')
    df = pd.merge(df, yoy_counts, on='restaurant_id', how='left')
    df['reviews_l30d'] = df['reviews_l30d'].fillna(0)
    df['reviews_yoy_30d'] = df['reviews_yoy_30d'].fillna(0)

    # Velocity Formula (Bayesian smoothed)
    df['velocity_ratio'] = (df['reviews_l30d'] + 5) / (df['reviews_yoy_30d'] + 5)

    # Conversion Gap
    df['internal_opportunity_gap'] = df['reviews_l30d'] - ((df['total_bookings'] / df.get('days_in_advance', 365).replace(0, 1)) * 30 * 0.05)
    df['weighted_opportunity_gap'] = df['internal_opportunity_gap'] * df['avg_revenue_per_booking']
except Exception as e:
    print(f"Warning: Could not process Velocity Ratio from review file. {e}")

# ── 6. REDESIGNED MECE Labeling (Percentile-Based, Internal KPIs) ──
print("Generating MECE Ground-Truth Labels for Classification...")

# Compute percentile thresholds from internal KPIs (97.7% coverage)
med_int = df['internal_score'].median()
p25_int = df['internal_score'].quantile(0.25)
p40_int = df['internal_score'].quantile(0.40)
p60_int = df['internal_score'].quantile(0.60)
no_show_75 = df['no_show_rate'].quantile(0.75)
arb_25 = df['avg_revenue_per_booking'].quantile(0.25)

# External quality threshold: 75th percentile among those WITH external data
has_external = df['composite_external_rating'] > 0
ext_75pct = df.loc[has_external, 'composite_external_rating'].quantile(0.75) if has_external.any() else 999

print(f"  Thresholds: med_int={med_int:.1f}, p25_int={p25_int:.1f}, p40_int={p40_int:.1f}, p60_int={p60_int:.1f}")
print(f"  no_show_75={no_show_75:.4f}, arb_25={arb_25:.0f}, ext_75pct={ext_75pct:.2f}")

def assign_label(row):
    # Hidden Gem: Has external data, high external quality among peers, low internal
    if (row['composite_external_rating'] > ext_75pct and 
        row['internal_score'] < p40_int):
        return 'Hidden Gem'

    # Declining: High internal but deteriorating operational signals
    if (row['internal_score'] > p60_int and 
        (row['no_show_rate'] > no_show_75 or 
         row['avg_revenue_per_booking'] < arb_25)):
        return 'Declining'

    # Rising: Low-mid internal base but showing digital conversion traction
    bcr = row['total_bookings'] / row['web_views'] if row.get('web_views', 0) > 0 else 0
    if (row['internal_score'] < med_int and 
        row['internal_score'] > p25_int and
        bcr > 0):
        return 'Rising'

    return 'Stable'

df['target_label'] = df.apply(assign_label, axis=1)
print(f"Target Label Distribution:\n{df['target_label'].value_counts()}")

# ── 7. Pruning & OOF Stacking ──
print("Pruning unneeded text columns...")

cols_to_drop = [
    'name', 'primary_cuisine', 'secondary_cuisines',
    'primary_dining_style', 'secondary_dining_styles',
    'facilities', 'primary_place', 'places',
    'hashtags', 'restaurant_name_en', 'restaurant_name_th', 'extracted_location'
]
df_ml = df.drop(columns=[c for c in cols_to_drop if c in df.columns])


print("Generating Out-of-Fold Expected KPI Stacking Features...")
import lightgbm as lgb
from sklearn.model_selection import KFold

# Prepare features for regression — drop internal operational volumes and target-related cols
reg_drop_cols = ['restaurant_id', 'target_label', 'validation_status', 'relative_cross_sectional_index',
                 'no_show_rate', 'velocity_ratio', 'internal_score', 'total_revenue',
                 'total_bookings', 'total_guests', 'total_no_shows', 'avg_revenue_per_booking',
                 'total_temporary_bookings', 'target_encoded', 'proxy_yoy_growth',
                 'reviews_l30d', 'reviews_yoy_30d'] + cols_to_drop

X_reg = df.drop(columns=[c for c in reg_drop_cols if c in df.columns], errors='ignore')

# Ensure only numeric columns remain for regression
non_numeric = X_reg.select_dtypes(exclude=[np.number]).columns.tolist()
if non_numeric:
    print(f"  Dropping non-numeric columns from regression features: {non_numeric}")
    X_reg = X_reg.drop(columns=non_numeric)

# Categorical features for LGBM
cat_cols = ['region_encoded', 'cuisine_encoded']
for c in cat_cols:
    if c in X_reg.columns:
        X_reg[c] = X_reg[c].astype(int)

y_reg = df['internal_score']  # Predict internal performance baseline

kf = KFold(n_splits=5, shuffle=True, random_state=42)
oof_preds = np.zeros(len(df))

for train_idx, val_idx in kf.split(X_reg):
    X_tr, y_tr = X_reg.iloc[train_idx], y_reg.iloc[train_idx]
    X_va, y_va = X_reg.iloc[val_idx], y_reg.iloc[val_idx]

    model = lgb.LGBMRegressor(random_state=42, n_estimators=100, verbose=-1)
    model.fit(X_tr, y_tr, categorical_feature=[c for c in cat_cols if c in X_tr.columns])

    oof_preds[val_idx] = model.predict(X_va)

df['expected_kpi'] = oof_preds
df['residual_kpi'] = df['internal_score'] - df['expected_kpi']
print("OOF Stacking Regression Complete. Added expected_kpi and residual_kpi.")

# Final column pruning — remove leakage/target-construction columns
cols_to_drop.extend([
    'proxy_yoy_growth', 'relative_cross_sectional_index',
    'total_revenue_clipped', 'web_views_clipped', 'total_bookings_clipped',
    'total_revenue', 'total_bookings', 'total_guests', 'total_no_shows',
    'avg_revenue_per_booking', 'total_temporary_bookings',
    'internal_score', 'velocity_ratio', 'no_show_rate', 'reviews_yoy_30d'
])
df_ml = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
import shutil
TEMP_FILE = OUTPUT_FILE + ".tmp"
df_ml.to_csv(TEMP_FILE, index=False)
try:
    shutil.move(TEMP_FILE, OUTPUT_FILE)
except PermissionError:
    print(f"WARNING: Could not overwrite {OUTPUT_FILE} (file locked). Output saved to {TEMP_FILE}")
    OUTPUT_FILE = TEMP_FILE
print(f"\n[OK] Highly-Engineered Feature Dataset created! Saved {len(df_ml)} rows to {OUTPUT_FILE}")
print(f"Columns: {list(df_ml.columns)}")
df_ml.head()
