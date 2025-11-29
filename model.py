import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib


model_path = "win_model.pkl"

#Player stat features (I took out games played because it seemed to create strange predictions)
FEATURE_STATS = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV"]

#Advanced shooting stats for efficiency metrics
SHOOTING_STATS = ["FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA"]

def compute_advanced_metrics(df):
    """
    Calculate advanced efficiency metrics: eFG% and TS%
    """
    for i in range(1, 6):
        fgm_col = f"P{i}_FGM"
        fga_col = f"P{i}_FGA"
        fg3m_col = f"P{i}_FG3M"
        ftm_col = f"P{i}_FTM"
        fta_col = f"P{i}_FTA"
        pts_col = f"P{i}_PTS"
        
        # Effective Field Goal Percentage: Formula Gemini threw - (FGM + 0.5 * FG3M) / FGA
        if fgm_col in df.columns and fga_col in df.columns and fg3m_col in df.columns:
            df[f"P{i}_EFG"] = np.where(
                df[fga_col] > 0,
                (df[fgm_col] + 0.5 * df[fg3m_col]) / df[fga_col],
                0.0
            )
        
        # True Shooting Percentage: Formula Gemini threw - PTS / (2 * (FGA + 0.44 * FTA))
        if pts_col in df.columns and fga_col in df.columns and fta_col in df.columns:
            df[f"P{i}_TS"] = np.where(
                (df[fga_col] + 0.44 * df[fta_col]) > 0,
                df[pts_col] / (2 * (df[fga_col] + 0.44 * df[fta_col])),
                0.0
            )
    
    return df

def compute_team_features(df):
    """
    Takes raw player stats and adds aggregated features:
    """
    if any(f"P1_{stat}" in df.columns for stat in SHOOTING_STATS):
        df = compute_advanced_metrics(df)
    
    for stat in FEATURE_STATS:
        player_cols = [f"P{i}_{stat}" for i in range(1, 6)]
        
        if not all(col in df.columns for col in player_cols):
            continue

        #Team averages and totals
        df[f"TEAM_AVG_{stat}"]   = df[player_cols].mean(axis=1)
        df[f"TEAM_TOTAL_{stat}"] = df[player_cols].sum(axis=1)

        #Top 2 for star power
        df[f"TEAM_TOP2_{stat}"] = df[player_cols].apply(
            lambda row: row.nlargest(2).sum(), axis=1
        )
        #Per 36 minutes averages
        if stat != "MIN":
            total_stat = df[player_cols].sum(axis=1)
            total_min = df[[f"P{i}_MIN" for i in range(1, 6)]].sum(axis=1)
            df[f"TEAM_AVG_{stat}_P36"] = (total_stat / total_min.replace(0, pd.NA)) * 36
    
    # Process advanced metrics if available
    for adv_stat in ["EFG", "TS"]:
        player_cols = [f"P{i}_{adv_stat}" for i in range(1, 6)]
        
        if all(col in df.columns for col in player_cols):
            #Team averages for efficiency metrics
            df[f"TEAM_AVG_{adv_stat}"] = df[player_cols].mean(axis=1)
            df[f"TEAM_TOTAL_{adv_stat}"] = df[player_cols].sum(axis=1)
            df[f"TEAM_TOP2_{adv_stat}"] = df[player_cols].apply(
                lambda row: row.nlargest(2).sum(), axis=1
            )

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

    #Apply GradientBoosting to all of the training data after grid search
    best_model.fit(X, y)

    # Predictions
    raw_pred = best_model.predict(X)
    
    # RMSE
    rmse_before = np.sqrt(mean_squared_error(y, raw_pred))
    r2_before = r2_score(y, raw_pred)
    
    print(f"\nModel Performance (Before Calibration):")
    print(f"  R² Score: {r2_before:.4f}")
    print(f"  RMSE: {rmse_before:.2f} wins")

    # Calibration
    raw_pred_reshaped = raw_pred.reshape(-1, 1)
    lr = LinearRegression()
    lr.fit(raw_pred_reshaped, y)
    #bias term
    alpha = float(lr.intercept_)
    #scale term  
    beta = float(lr.coef_[0])       

    calibrated_pred = alpha + beta * raw_pred
    
    # Calculate metrics after calibration
    rmse_after = np.sqrt(mean_squared_error(y, calibrated_pred))
    r2_after = r2_score(y, calibrated_pred)
    
    print(f"\nCalibration: Wins = {alpha:.3f} + {beta:.3f} * raw_pred")
    print(f"\nModel Performance (After Calibration):")
    print(f"  R² Score: {r2_after:.4f}")
    print(f"  RMSE: {rmse_after:.2f} wins")

    #Save model, features, and calibration params
    joblib.dump(
        {
            "model": best_model,
            "features": feature_cols,
            "alpha": alpha,
            "beta": beta,
            "rmse": rmse_after,
            "r2": r2_after,
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
