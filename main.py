from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from typing import List, Dict

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
    print("A) - Predict Current NBA Team Win Totals\n")
    print("B) - Predict Custom NBA Roster\n")
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
        
    #Initialize user's Roster
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


def main():
    """Main Entry point of the program"""
    #Iterate until exit
    flag = True

    while flag:
        #Print out the Menu
        user_input = display_menu()

        #OPTION A - Team Stats
        if user_input == "a":
            pass

        #OPTION B - Custom Team Stats
        elif user_input == "b":
            #First Get Player Names
            user_roster = get_player_list()

            #Display Roster
            display_roster(user_roster=user_roster, isComplete=True)

        #EXIT
        elif user_input == "q":
            flag = False    #Set flag to false to exit loop

        #Error
        else:
            print("ERROR - Invalid Input - Try again")


if __name__ == "__main__":
    main()