from main import roster_load, predict_custom_roster_wins
from visualization import visualize_roster_comparison, get_top_strengths
from model import load_model
from nba_api.stats.static import players
import pandas as pd

def load_roster_from_file(filename):
    """Helper to load roster from file"""
    roster = []
    try:
        with open(filename, "r") as f:
            roster = [
                {"position_num": str(i+1), "name": "X", "id": None}
                for i in range(5)
            ]
            for i, line in enumerate(f):
                player_name = line.strip().lower()
                name_matches = players.find_players_by_full_name(player_name)
                if name_matches:
                    roster[i]["name"] = name_matches[0]["full_name"]
                    roster[i]["id"] = name_matches[0]["id"]
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return roster

if __name__ == "__main__":
    print("Testing Roster Comparison Visualization\n")
    print("="*50)
    
    print("Loading roster.txt...")
    roster1 = load_roster_from_file("roster.txt")
    print("Loading roster2.txt...")
    roster2 = load_roster_from_file("roster2.txt")
    
    if not roster1 or not roster2:
        print("Error: Could not load rosters")
        exit(1)
    
    print("\nCalculating predictions...")
    wins1, model1, feature_cols1, X1 = predict_custom_roster_wins(roster1, return_details=True)
    wins2, model2, feature_cols2, X2 = predict_custom_roster_wins(roster2, return_details=True)
    
    print("Analyzing strengths...")
    strengths1 = get_top_strengths(model1, feature_cols1, X1, top_n=3)
    strengths2 = get_top_strengths(model2, feature_cols2, X2, top_n=3)
    
    print(f"\nRoster 1: {wins1:.1f} wins")
    print(f"Roster 2: {wins2:.1f} wins")
    
    print("\nGenerating visualization...")
    visualize_roster_comparison(
        roster1_name="Roster 1",
        roster1_wins=wins1,
        roster1_strengths=strengths1,
        roster2_name="Roster 2",
        roster2_wins=wins2,
        roster2_strengths=strengths2,
        save_path="roster_comparison.png"
    )
    
    print("\nDone! Check roster_comparison.png")
