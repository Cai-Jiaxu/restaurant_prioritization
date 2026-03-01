import pandas as pd
from sklearn.model_selection import StratifiedKFold
import numpy as np
import os
from sklearn.metrics import classification_report, accuracy_score
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

# Prefer .tmp file (new data) over potentially stale locked original
INPUT_FILE = "../Data/Processed/ML_Ready_Features.csv.tmp"
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = "../Data/Processed/ML_Ready_Features.csv"
OUTPUT_FILE = "../Data/Processed/Categorized_Restaurants.csv"

print("Loading ML Ready Dataset...")
df = pd.read_csv(INPUT_FILE)
print(f"Loaded from: {INPUT_FILE}")

# Map string targets to integers for LightGBM Objective
target_mapping = {'Declining': 0, 'Stable': 1, 'Rising': 2, 'Hidden Gem': 3}
df['target_encoded'] = df['target_label'].map(target_mapping)

print(f"Target distribution:\n{df['target_label'].value_counts()}")

# Drop Descriptive & Leakage Columns (Keeping ID for the final output)
# Also drop sparse platform columns if they survived
sparse_cols = ['tiktok_views', 'tiktok_likes', 'tiktok_shares', 'facebook_likes',
               'wongnai_rating', 'wongnai_reviews']
# LEAKAGE FIX: Also drop composite_external_rating, external_quality_score,
# and reliability_factor — these are used directly in the label rules for Hidden Gem
# and would allow the model to trivially memorize the threshold rather than learn patterns.
leakage_cols = ['composite_external_rating', 'external_quality_score', 'reliability_factor']
drop_cols = ['restaurant_id', 'target_label', 'target_encoded', 'validation_status',
             'relative_cross_sectional_index', 'no_show_rate', 'velocity_ratio',
             'internal_score', 'stability_score', 'final_priority_score',
             'web_revenue', 'booking_conversion_rate', 'revenue_per_view',
             'revenue_per_guest', 'expected_kpi', 'residual_kpi',
             'momentum_score', 'internal_opportunity_gap',
             'weighted_opportunity_gap', 'reviews_l30d'] + sparse_cols + leakage_cols

X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

# Ensure only numeric columns
non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
if non_numeric:
    print(f"Dropping non-numeric columns from features: {non_numeric}")
    X = X.drop(columns=non_numeric)

y = df['target_encoded']

print(f"Feature shape: {X.shape}")
print(f"Features: {list(X.columns)}")

# Explicitly define categorical structures for LightGBM
categorical_features = ['region_encoded', 'cuisine_encoded']
print("Initializing Stratified K-Fold Validation Framework...")

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

lgb_params = {
    'objective': 'multiclass',
    'num_class': 4,
    'metric': 'multi_error',
    'boosting_type': 'gbdt',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'feature_fraction': 0.8,
    'verbose': -1,
    'random_state': 42
}

fold_scores = []
for fold, (train_index, test_index) in enumerate(skf.split(X, y)):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    # Locally fit winsorization on training data only
    for vol_feat in ['total_revenue', 'web_views', 'total_bookings']:
        if vol_feat in X_train.columns:
            upper = X_train[vol_feat].quantile(0.95)
            X_train[f'{vol_feat}_clipped'] = np.where(X_train[vol_feat] > upper, upper, X_train[vol_feat])
            X_test[f'{vol_feat}_clipped'] = np.where(X_test[vol_feat] > upper, upper, X_test[vol_feat])

    train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=categorical_features)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data, categorical_feature=categorical_features)

    model = lgb.train(
        lgb_params,
        train_data,
        num_boost_round=100,
        valid_sets=[train_data, valid_data]
    )

    y_pred_probs = model.predict(X_test)
    y_pred = np.argmax(y_pred_probs, axis=1)

    acc = accuracy_score(y_test, y_pred)
    fold_scores.append(acc)
    print(f"Fold {fold + 1} Accuracy: {acc:.4f}")

print(f"\nAverage Validation Accuracy: {np.mean(fold_scores):.4f}")
print("Training Final Production Model on all data...")

train_data_full = lgb.Dataset(X, label=y, categorical_feature=categorical_features)
final_model = lgb.train(
    lgb_params,
    train_data_full,
    num_boost_round=150
)

# Predict classifications
final_predictions_probs = final_model.predict(X)
final_predictions = np.argmax(final_predictions_probs, axis=1)

# FIXED: inv_map now includes key 3 for 'Hidden Gem'
inv_map = {0: 'Declining', 1: 'Stable', 2: 'Rising', 3: 'Hidden Gem'}
df['ML_Predicted_Segment'] = pd.Series(final_predictions).map(inv_map)

print("\n--- Production Model Classification Matrix ---")
print(classification_report(y, final_predictions, labels=[0, 1, 2, 3],
                           target_names=['Declining', 'Stable', 'Rising', 'Hidden Gem'],
                           zero_division=0))

# Export class probabilities for priority ranking in run_08
df['prob_declining'] = final_predictions_probs[:, 0]
df['prob_stable'] = final_predictions_probs[:, 1]
df['prob_rising'] = final_predictions_probs[:, 2]
df['prob_hidden_gem'] = final_predictions_probs[:, 3]

# Priority score: higher = more marketing opportunity
# Combines probability of being Hidden Gem or Rising (actionable segments)
df['ml_priority_score'] = (df['prob_rising'] * 0.6 + df['prob_hidden_gem'] * 0.4) * 100

print(f"\nML Predicted Segment Distribution:")
print(df['ML_Predicted_Segment'].value_counts(dropna=False))

out_df_cols = [c for c in ['restaurant_id', 'target_label', 'ML_Predicted_Segment',
                           'prob_declining', 'prob_stable', 'prob_rising', 'prob_hidden_gem',
                           'ml_priority_score', 'expected_kpi', 'residual_kpi',
                           'momentum_score', 'external_quality_score'] if c in df.columns]
out_df = df[out_df_cols]

import shutil
TEMP_FILE = OUTPUT_FILE + ".tmp"
out_df.to_csv(TEMP_FILE, index=False)
try:
    shutil.move(TEMP_FILE, OUTPUT_FILE)
except PermissionError:
    print(f"WARNING: Could not overwrite {OUTPUT_FILE}. Output saved to {TEMP_FILE}")
    OUTPUT_FILE = TEMP_FILE

print(f"\n[OK] ML Categorization Complete! Exported to: {OUTPUT_FILE}")
print(f"Top 10 by ml_priority_score:")
print(out_df.nlargest(10, 'ml_priority_score')[['restaurant_id', 'ML_Predicted_Segment', 'ml_priority_score']].to_string(index=False))
out_df.head()
