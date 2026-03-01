import pandas as pd
import numpy as np
import os
import shutil
import warnings
warnings.filterwarnings('ignore')

# 1. Load Data
CATEGORIZED_FILE = "../Data/Processed/Categorized_Restaurants.csv"
FEATURES_FILE = "../Data/Processed/ML_Ready_Features.csv.tmp"
if not os.path.exists(FEATURES_FILE):
    FEATURES_FILE = "../Data/Processed/ML_Ready_Features.csv"
DASH_OUTPUT = "../Data/Processed/Dashboard_List_1_Retention.csv"
FULL_RANKINGS = "../Data/Processed/Dashboard_Predictions.csv"

print("Loading datasets...")
df_cat = pd.read_csv(CATEGORIZED_FILE)
df_feat = pd.read_csv(FEATURES_FILE)
print(f"Categorized: {df_cat.shape}, Features: {df_feat.shape}")

# 2. Pipeline A: The Retention Dashboard (Prioritized Ranked List)
print("--- Generating Pipeline A: Prioritized Retention Dashboard ---")

# Merge categorization with feature data for a richer dashboard
df_dash = pd.merge(df_cat, df_feat[['restaurant_id', 'booking_conversion_rate', 'web_views',
                                     'gmaps_rating', 'gmaps_reviews', 'weighted_rating_score',
                                     'region_encoded', 'cuisine_encoded']],
                   on='restaurant_id', how='left')

# Filter for actionable segments: Rising + Hidden Gem
df_retention = df_dash[df_dash['ML_Predicted_Segment'].isin(['Rising', 'Hidden Gem'])].copy()

print(f"Found {len(df_retention)} partners in actionable segments (Rising + Hidden Gem).")

if not df_retention.empty:
    # Sort by ml_priority_score (highest marketing opportunity first)
    df_retention = df_retention.sort_values('ml_priority_score', ascending=False)

    # Add rank column
    df_retention['priority_rank'] = range(1, len(df_retention) + 1)

    # Print summary
    print(f"\nSegment breakdown:")
    print(df_retention['ML_Predicted_Segment'].value_counts())
    print(f"\nTop 15 Priority Partners:")
    top_cols = ['priority_rank', 'restaurant_id', 'ML_Predicted_Segment', 'ml_priority_score']
    if 'prob_rising' in df_retention.columns:
        top_cols.extend(['prob_rising', 'prob_hidden_gem'])
    print(df_retention[top_cols].head(15).to_string(index=False))
else:
    print('No Retention Targets Found. Dashboard exported empty.\n')

# Export ranked retention dashboard
TEMP_FILE = DASH_OUTPUT + ".tmp"
if not df_retention.empty:
    df_retention.to_csv(TEMP_FILE, index=False)
else:
    pd.DataFrame(columns=['restaurant_id']).to_csv(TEMP_FILE, index=False)

try:
    shutil.move(TEMP_FILE, DASH_OUTPUT)
except PermissionError:
    print(f"WARNING: Output saved to {TEMP_FILE}")
    DASH_OUTPUT = TEMP_FILE

print(f"\nExported ranked retention dashboard: {DASH_OUTPUT}")

# 3. Also export full portfolio rankings (all restaurants, sorted by priority)
print("\n--- Generating Full Portfolio Rankings ---")
df_full = df_dash.sort_values('ml_priority_score', ascending=False).copy()
df_full['overall_rank'] = range(1, len(df_full) + 1)

TEMP_FULL = FULL_RANKINGS + ".tmp"
df_full.to_csv(TEMP_FULL, index=False)
try:
    shutil.move(TEMP_FULL, FULL_RANKINGS)
except PermissionError:
    print(f"WARNING: Output saved to {TEMP_FULL}")
    FULL_RANKINGS = TEMP_FULL

print(f"Exported full portfolio rankings: {FULL_RANKINGS}")
print(f"Total: {len(df_full)} restaurants ranked by ml_priority_score")
