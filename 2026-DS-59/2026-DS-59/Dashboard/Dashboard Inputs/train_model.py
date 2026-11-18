"""Run once: trains the final Random Forest models and saves everything the dashboard needs."""
import pandas as pd, json, joblib
from sklearn.ensemble import RandomForestClassifier

train = pd.read_csv("train_final.csv"); test = pd.read_csv("test_final.csv")
train_o = pd.read_csv("train_final_odds.csv")
feats = json.load(open("final_feature_sets.json"))

def fit(df, cols):
    rf = RandomForestClassifier(n_estimators=200, max_depth=6, min_samples_leaf=30,
                                class_weight="balanced", random_state=42, n_jobs=-1)
    return rf.fit(df[cols], df["target"])          # settings found by the grid search in 02_random_forest.ipynb

joblib.dump(fit(train, feats["features_no_odds"]), "rf_no_odds.joblib")
joblib.dump(fit(train_o, feats["features_with_odds"]), "rf_with_odds.joblib")

# small tables for the charts
all_m = pd.concat([train, test], ignore_index=True)
pd.crosstab(all_m.season, all_m.match_outcome).to_csv("season_outcomes.csv")
res = pd.concat([pd.read_csv(f) for f in ["results_baseline.csv", "results_01_logistic_regression.csv",
      "results_02_random_forest.csv", "results_03_decision_tree.csv", "results_04_xgboost.csv"]])
res.to_csv("results_all.csv", index=False)
print("saved models and tables")
