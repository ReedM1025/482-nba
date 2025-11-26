import time
import pandas as pd

from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats


def get_team_season_stats(season: str, timeout: int = 60) -> pd.DataFrame:
    print(f"  Fetching team stats for {season}...")
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        per_mode_detailed="PerGame",           # keep this
        season_type_all_star="Regular Season", # keep this
        timeout=timeout,
    )
    df = stats.get_data_frames()[0]
    # For sanity, you can inspect columns once:
    # print(df.columns)
    return df


def get_player_season_stats(season: str, timeout: int = 60) -> pd.DataFrame:
    print(f"  Fetching player stats for {season}...")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame",           # keep
        season_type_all_star="Regular Season", # keep
        timeout=timeout,
    )
    df = stats.get_data_frames()[0]
    # print(df.columns)
    return df


def build_feature_row(season: str,
                      team_row: pd.Series,
                      starters_df: pd.DataFrame) -> dict:
    """
    Build a single row for the output dataset:
    TeamName, Season, Wins, and 5 players' stats.
    """
    team_name = team_row["TEAM_NAME"]
    wins = team_row["W"]

    row = {
        "TeamName": team_name,
        "Season": season,
        "Wins": wins,
    }

    # Stats we care about per player
    stat_cols = {
        "GP": "GP",
        "MIN": "MIN",
        "PTS": "PTS",
        "AST": "AST",
        "REB": "REB",
        "STL": "STL",
        "BLK": "BLK",
        "TOV": "TOV",
    }

    # Ensure we always have exactly 5 slots: if fewer than 5 players, pad with NaN
    starters_df = starters_df.copy()
    if len(starters_df) < 5:
        # pad with empty rows
        for _ in range(5 - len(starters_df)):
            starters_df = pd.concat(
                [starters_df, pd.Series(dtype=object).to_frame().T],
                ignore_index=True,
            )

    # Fill P1_*, P2_*, ..., P5_* columns
    for i, (_, p) in enumerate(starters_df.iterrows(), start=1):
        prefix = f"P{i}_"
        row[prefix + "NAME"] = p.get("PLAYER_NAME", None)

        for stat_key, col in stat_cols.items():
            row[prefix + stat_key] = p.get(col, None)

        if i == 5:
            break

    return row


def build_dataset(output_csv: str):
    """
    Build the full dataset for multiple seasons and save to CSV.
    """

    # Last ~11 seasons, adjust if you want more/less
    seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2013, 2024)]

    all_rows = []

    for season in seasons:
        print(f"\nProcessing season {season}...")

        # 1) Team stats for this season (includes wins)
        team_df = get_team_season_stats(season)
        time.sleep(1.0)  # gentle on the API

        # 2) Player stats for this season
        player_df = get_player_season_stats(season)
        time.sleep(1.0)  # gentle on the API

        # For each team in this season
        for _, team_row in team_df.iterrows():
            team_id = team_row["TEAM_ID"]
            team_name = team_row["TEAM_NAME"]

            # Filter to players on this team
            team_players = player_df[player_df["TEAM_ID"] == team_id]

            if team_players.empty:
                print(f"  [WARN] No player stats for {team_name} in {season}, skipping.")
                continue

            # Choose "starting 5" as top 5 by minutes per game
            starters = team_players.sort_values("MIN", ascending=False).head(5)

            feature_row = build_feature_row(season, team_row, starters)
            all_rows.append(feature_row)

    # Convert to DataFrame and save
    out_df = pd.DataFrame(all_rows)
    out_df.to_csv(output_csv, index=False)
    print(f"\nSaved {len(out_df)} rows to {output_csv}")


if __name__ == "__main__":
    build_dataset("data.csv")