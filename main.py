from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from typing import List, Dict
import pandas as pd

#=========================
#   Global Vars
#=========================





#Function to Display the main Menu
def display_menu():
    """This Function prints out the Menu for the teminal control of the program. Returns the str of the selection"""
    #Title
    print("==="*10)
    print("Welcome to NBA Simulator!\n\n")
    print("Project made by:")

    #Print Names
    names = ["Reed", "Ryan", "Pratham"]
    for name in names:
        print(f'- {name}')

    #Print Options
    print("\n\nSelect one of the Following options:\n")
    print("A) - Create a Custom NBA Roster\n")
    print("B) - Load in Custom NBA Roster\n")
    print("C) - Display Roster Stats\n")
    print("D) - Predict Custom NBA Roster\n")
    print("Q) - Exit\n")
    print("==="*10)

    raw_input = str(input("\nEnter Selection: "))
    user_selection = raw_input.lower().strip()

    return user_selection


def display_roster(user_roster, isComplete = False):
    """Helper Function to Display the Current Roster"""
    print("==="*10)
    if isComplete:
        print("Completed Roster:")
    else:
        print("Current Roster:")

    #Iterate over the user's Roster
    for player in user_roster:
        print(f"{player["position_num"]}) Position: {player["position"]} -- Name: {player["name"]}")
        
    print("==="*10)

#Function to get player roster
def get_player_list():
    """Function to retrieve the 5 player roster from the user"""

    #Helper Function for Checking if the roster is full
    def isRosterComplete(user_roster) -> bool:
        """""Iterates over each player in the current roster, making sure that each name has been set."""
        flag = True

        #Iterate over each player
        for player in user_roster:
            #Check if the name has been filled in
            if player["name"] == "X":
                flag = False    #Set Flag

        #Return Result
        return flag
        
    #Reset user's Roster
    user_roster = [
    {   #1 - Guard
        "position": "G", 
        "position_num": "1",
        "name": "X"
    }, 
    {   #2 - Shooting Guard
        "position": "SG", 
        "position_num": "2",
        "name": "X"
    }, 
    {   #3 - Small Forward
        "position": "SF", 
        "position_num": "3",
        "name": "X"
    }, 
    {   #4 - Power Forward
        "position": "PF", 
        "position_num": "4",
        "name": "X"
    }, 
    {   #5 - Center
        "position": "C", 
        "position_num": "5",
        "name": "X"
    }
    ]

    #Continue to Iterate until the user completes their roster
    while not isRosterComplete(user_roster=user_roster):
        #Display current Roster
        display_roster(user_roster)

        #Get User Input
        player_index = int(input("\nEnter index for player position (1-5): "))
        
        #Get Player Name
        player_name = str(input("\nEnter the Player Name: ")).lower()

        #Call to NBA API to retrieve the player name/info
        name_matches = players.find_players_by_full_name(player_name)

        #Player Not Found
        if len(name_matches) == 0:
            print("/nERROR - Name not Found Try Again\n")

        #Invalid Position entered
        elif ((player_index < 1) or (player_index > 5)):
            print("\nERROR - Invalid Player Index Provided, Try Again\n")

        #Player Found, add to the desired position
        else:
            #Add Player Name
            player_index -= 1   #Adjust for 0 index
            user_roster[player_index]["name"] = name_matches[0]["full_name"]

            #Add Player ID
            user_roster[player_index]["id"] = name_matches[0]["id"]

    #Return the User's Roster
    return user_roster

def roster_load(user_roster):
    """A Function that Will load a roster given a filename"""
    #Get Filename
    filename = str(input("Enter Exact Filename: ")).strip()

    #Reset User Roster
    user_roster = [
    {   #1 - Guard
        "position": "G", 
        "position_num": "1",
        "name": "X"
    }, 
    {   #2 - Shooting Guard
        "position": "SG", 
        "position_num": "2",
        "name": "X"
    }, 
    {   #3 - Small Forward
        "position": "SF", 
        "position_num": "3",
        "name": "X"
    }, 
    {   #4 - Power Forward
        "position": "PF", 
        "position_num": "4",
        "name": "X"
    }, 
    {   #5 - Center
        "position": "C", 
        "position_num": "5",
        "name": "X"
    }
    ]

    try:
        #Open File
        with open(filename, "r") as f:
            #Iterate over each line
            for i, line in enumerate(f):
                #Clean
                player_name = line.strip().lower()

                #Get Player Info   
                name_matches = players.find_players_by_full_name(player_name)

                #Extract ID
                user_roster[i]["name"] = name_matches[0]["full_name"]

                #Add Player ID
                user_roster[i]["id"] = name_matches[0]["id"]

            #Return the Roster
            return user_roster

    except:
        print("ERROR - File Read Error")

#Function to get a players most recent stat line
def get_last_season_stats(player_id):
    #Call to API to retrieve the players per gane stats
    career = playercareerstats.PlayerCareerStats(
        player_id=player_id,
        per_mode36="PerGame" 
    )

    #Retreive Most Recent Season
    df = career.get_data_frames()[0]
    last = df.iloc[-1]     

    #Return last season    
    return last 

def print_roster_stats_table(user_roster):
    """
    Iterates over each player in user_roster, collects their last-season stats,
    and prints a nice table.
    """
    rows = []

    for player in user_roster:
        #Retrieve Player Info
        name = player["name"]
        player_id = player["id"]

        #Get the stats from last season
        stats = get_last_season_stats(player_id)

        #Build a row with the desired stats
        row = {
            "Name":  name,
            "PPG":  round(float(stats["PTS"]), 1),
            "RPG":  round(float(stats["REB"]), 1),
            "APG":  round(float(stats["AST"]), 1),
            "SPG":  round(float(stats["STL"]), 1),
            "BPG":  round(float(stats["BLK"]), 1),
            "TOPG": round(float(stats["TOV"]), 1),
        }
        #Append row 
        rows.append(row)

    #Turn into DataFrame and print as a table
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))


def main():
    """Main Entry point of the program"""
    #Iterate until exit
    flag = True

    #Initialize user's Roster
    user_roster = []

    while flag:
        #Print out the Menu
        user_input = display_menu()

        #OPTION A - Create A Roster
        if user_input == "a":
            #First Get Player Roster
            user_roster = get_player_list()

            #Display Roster
            display_roster(user_roster=user_roster, isComplete=True)

        #OPTION B - Load in a roster from a file
        elif user_input == "b":
            user_roster = roster_load(user_roster=user_roster)

        #OPTION C - Display Custom Team Stats
        elif user_input == "c":
            #Display Roster
            display_roster(user_roster=user_roster, isComplete=True)

            #Iterate over each player and extract their stats
            print_roster_stats_table(user_roster=user_roster)

        #OPTION D - Predict Win Total
        elif user_input == "d":
            pass

        #EXIT
        elif user_input == "q":
            flag = False    #Set flag to false to exit loop

        #Error
        else:
            print("ERROR - Invalid Input - Try again")


if __name__ == "__main__":
    main()