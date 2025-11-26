import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats


#Function that Fetches all data for a given season
def get_team_season_stats(season: str, timeout: int = 60) -> pd.DataFrame:
    print(f"Fetching team stats for {season}")
    
    #Retrive stats
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        per_mode_detailed="PerGame",           
        season_type_all_star="Regular Season", 
        timeout=timeout,
    )

    #Create a Dataframe
    df = stats.get_data_frames()[0]

    #Return the dataframe
    return df


#Function for getting an individual player's stats
def get_player_season_stats(season: str, timeout: int = 60) -> pd.DataFrame:
    print(f"Fetching player stats for {season}")

    #Retrive stats
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame",   
        season_type_all_star="Regular Season", 
        timeout=timeout,
    )

    #Create Data frame
    df = stats.get_data_frames()[0]
    
    #Return data frame
    return df

#Helper Function to build a row of the CSV
def build_feature_row(season: str, team_row: pd.Series, starters_df: pd.DataFrame) -> dict:

    #Extract team name and wins
    team_name = team_row["TEAM_NAME"]
    wins = team_row["W"]

    #initailize row
    row = {
        "TeamName": team_name,
        "Season": season,
        "Wins": wins,
    }

    #stats we care about per player
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

    #Return the row
    return row


# Main Function Build the Dataset and save to the CSV provided
def build_dataset(filename: str, year_start: int, year_end: int, players_per_roster: int):
    """
    Build the full dataset for multiple seasons and save to CSV.
    """

    #Initialize list of seasons based on provided years
    seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(year_start, year_end)]

    all_rows = []

    #Iterate over each season
    for season in seasons:
        print(f"\nProcessing season: {season}")

        # 1) Team stats for this season (includes wins)
        team_df = get_team_season_stats(season)
        time.sleep(1.0)  #Rate Limiting Avoidence

        # 2) Player stats for this season
        player_df = get_player_season_stats(season)
        time.sleep(1.0)  #Rate Limiting Avoidence

        #iterate over each team in this season
        for _, team_row in team_df.iterrows():
            #Extract team name and ID
            team_id = team_row["TEAM_ID"]
            team_name = team_row["TEAM_NAME"]

            #Filter to players on this team
            team_players = player_df[player_df["TEAM_ID"] == team_id]

            #Edge case for empty data
            if team_players.empty:
                print(f"No player stats for {team_name} in {season}, skipping row")
                continue

            #Select the top X amount of players per roster to be included
            starters = team_players.sort_values("MIN", ascending=False).head(players_per_roster)

            #Call to helper and append
            feature_row = build_feature_row(season, team_row, starters)
            all_rows.append(feature_row)

    #Convert to DataFrame and save
    out_df = pd.DataFrame(all_rows)
    out_df.to_csv(filename, index=False)
    print(f"\nSaved {len(out_df)} rows to {filename}")


if __name__ == "__main__":
    build_dataset(filename="data.csv", year_start=2001, year_end=2025, players_per_roster=5)