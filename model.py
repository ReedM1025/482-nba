import pandas as pd
from sklearn.model_selection import KFold, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import joblib


model_path = "win_model.pkl"

#Player stat features (I took out games played because it seemed to create strange predictions)
FEATURE_STATS = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV"]


def compute_team_features(df):
    """
    Takes raw player stats and adds aggregated features:
    """
    for stat in FEATURE_STATS:
        player_cols = [f"P{i}_{stat}" for i in range(1, 6)]

        #Team averages and totals
        df[f"TEAM_AVG_{stat}"]   = df[player_cols].mean(axis=1)
        df[f"TEAM_TOTAL_{stat}"] = df[player_cols].sum(axis=1)

        #Top 2 for star power
        df[f"TEAM_TOP2_{stat}"] = df[player_cols].apply(
            lambda row: row.nlargest(2).sum(), axis=1
        )
        #Pet 36 minutes averages
        if stat != "MIN":
            total_stat = df[player_cols].sum(axis=1)
            total_min = df[[f"P{i}_MIN" for i in range(1, 6)]].sum(axis=1)
            df[f"TEAM_AVG_{stat}_P36"] = (total_stat / total_min.replace(0, pd.NA)) * 36

    return df


def train_model():
    df = pd.read_csv("data.csv")

    df = compute_team_features(df)

    y = df["Wins"].astype(float)
    feature_cols = [c for c in df.columns if c.startswith("TEAM_")]
    X = df[feature_cols].astype(float)

    param_dist = {
        "n_estimators": [200, 300, 500, 800],
        "learning_rate": [0.01, 0.02, 0.03, 0.05],
        "max_depth": [2, 3, 4],
        "min_samples_leaf": [1, 2, 3],
        "subsample": [0.8, 1.0],
    }

    gb = GradientBoostingRegressor(random_state=42)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    search = RandomizedSearchCV(
        gb,
        param_distributions=param_dist,
        n_iter=25,
        cv=kf,
        scoring="r2",
        random_state=42,
        n_jobs=-1,
    )

    search.fit(X, y)

    print("Best CV R-Squared:", search.best_score_)
    print("Best params:", search.best_params_)

    best_model = search.best_estimator_

    #Apply XGboost to all of the training data after grid search
    best_model.fit(X, y)

    raw_pred = best_model.predict(X).reshape(-1, 1)
    lr = LinearRegression()
    lr.fit(raw_pred, y)
    #bias term
    alpha = float(lr.intercept_)
    #scale term  
    beta = float(lr.coef_[0])       

    print(f"Calibration: Wins = {alpha:.3f} + {beta:.3f} * raw_pred")

    #Save model, features, and calibration params
    joblib.dump(
        {
            "model": best_model,
            "features": feature_cols,
            "alpha": alpha,
            "beta": beta,
        },
        model_path,
    )
    print(f"\nSaved tuned model + calibration to {model_path}")


def load_model(model_path: str = model_path):
    bundle = joblib.load(model_path)
    model = bundle["model"]
    features = bundle["features"]
    alpha = bundle.get("alpha", 0.0)
    beta = bundle.get("beta", 1.0)
    return model, features, alpha, beta


if __name__ == "__main__":
    train_model()
