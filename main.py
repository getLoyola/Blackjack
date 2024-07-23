import random
import json
import os

# Define card values and suits
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# Create a deck of cards
def create_deck(num_decks=1):
    return [{'suit': suit, 'value': value} for suit in suits for value in values] * num_decks

# Shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)

# Deal a card from the deck
def deal_card(deck):
    return deck.pop()

# Calculate the hand value
def calculate_hand_value(hand):
    value = sum(values_dict[card['value']] for card in hand)
    num_aces = sum(1 for card in hand if card['value'] == 'A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

# Check for blackjack
def is_blackjack(hand):
    return len(hand) == 2 and calculate_hand_value(hand) == 21

# Display hand
def display_hand(hand, hide_dealer_card=False):
    if hide_dealer_card and len(hand) == 2:
        print(f"Dealer's hand: [{hand[0]['value']} of {hand[0]['suit']}] and [hidden]")
    else:
        hand_str = ', '.join(f"{card['value']} of {card['suit']}" for card in hand)
        print(f"Hand: {hand_str}, Value: {calculate_hand_value(hand)}")

# Insurance bet
def insurance_bet(balance, bet):
    while True:
        try:
            insurance = int(input(f"Place your insurance bet (up to {bet // 2}): "))
            if 0 <= insurance <= bet // 2:
                return insurance
            else:
                print(f"Insurance bet must be between 0 and {bet // 2}.")
        except ValueError:
            print("Invalid insurance bet amount. Please enter a number.")

# Player's turn
def player_turn(deck, player_hand, bet):
    while True:
        action = input("Choose action: (H)it, (S)tand, (D)ouble Down, or (P) Split: ").strip().upper()
        if action == 'H':
            player_hand.append(deal_card(deck))
            display_hand(player_hand)
            if calculate_hand_value(player_hand) > 21:
                print("Player busts! Dealer wins.")
                return False
        elif action == 'S':
            break
        elif action == 'D':
            if len(player_hand) == 2:
                bet *= 2
                player_hand.append(deal_card(deck))
                display_hand(player_hand)
                if calculate_hand_value(player_hand) > 21:
                    print("Player busts! Dealer wins.")
                    return False
                return True
            else:
                print("Double Down can only be used with the initial hand.")
        elif action == 'P':
            if len(player_hand) == 2 and player_hand[0]['value'] == player_hand[1]['value']:
                split_hand1 = [player_hand.pop()]
                split_hand2 = [player_hand.pop()]
                split_hand1.append(deal_card(deck))
                split_hand2.append(deal_card(deck))
                print("Hand 1:")
                display_hand(split_hand1)
                print("Hand 2:")
                display_hand(split_hand2)
                return split_hand1, split_hand2
            else:
                print("Split can only be used with the initial hand and matching cards.")
        else:
            print("Invalid action. Please choose 'H', 'S', 'D', or 'P'.")
    return True

# Dealer's turn
def dealer_turn(deck, dealer_hand):
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    return dealer_hand

# Initial game setup
def initial_game_setup(num_decks=6):
    deck = create_deck(num_decks=num_decks)  # Using multiple decks for more realism
    shuffle_deck(deck)
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    return deck, player_hand, dealer_hand

# Betting function
def place_bet(balance, min_bet, max_bet):
    while True:
        try:
            bet = int(input(f"Place your bet (minimum ${min_bet}, maximum ${max_bet}): "))
            if min_bet <= bet <= max_bet and bet <= balance:
                return bet
            elif bet > balance:
                print("Insufficient balance.")
            elif bet < min_bet:
                print(f"Bet must be at least ${min_bet}.")
            elif bet > max_bet:
                print(f"Bet cannot exceed ${max_bet}.")
        except ValueError:
            print("Invalid bet amount. Please enter a number.")

# Evaluate the outcome
def evaluate_outcome(player_value, dealer_value, bet, balance, insurance_bet=0):
    if dealer_value > 21:
        print("Dealer busts! Player wins.")
        balance += bet + insurance_bet
    elif dealer_value > player_value:
        print("Dealer wins.")
        balance -= bet
        if insurance_bet > 0:
            print("Insurance bet lost.")
    elif dealer_value < player_value:
        print("Player wins.")
        balance += bet
        if insurance_bet > 0:
            print("Insurance bet won.")
            balance += insurance_bet * 2
    else:
        print("It's a tie.")
        if insurance_bet > 0:
            print("Insurance bet won.")
            balance += insurance_bet
    return balance

# Play a hand
def play_hand(deck, player_hand, dealer_hand, bet, balance):
    dealer_blackjack = is_blackjack(dealer_hand)
    player_blackjack = is_blackjack(player_hand)

    if dealer_blackjack:
        display_hand(dealer_hand)
        if player_blackjack:
            print("Both player and dealer have Blackjack. It's a tie.")
            return bet  # Push
        else:
            print("Dealer has a Blackjack! Player loses.")
            return -bet

    if player_blackjack:
        print("Player has a Blackjack! Player wins.")
        return bet * 1.5

    insurance = 0
    if dealer_hand[0]['value'] == 'A':
        insurance = insurance_bet(balance, bet)
        if calculate_hand_value(dealer_hand) == 21:
            print("Dealer has Blackjack.")
            if insurance > 0:
                print("Insurance bet won.")
                return insurance * 2
            else:
                print("Player loses.")
                return -bet

    if player_turn(deck, player_hand, bet):
        dealer_hand = dealer_turn(deck, dealer_hand)
        display_hand(dealer_hand)
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)
        return evaluate_outcome(player_value, dealer_value, bet, balance, insurance)
    return -bet

# Play a round
def play_round(player, num_decks, min_bet, max_bet):
    balance = player['balance']
    deck, player_hand, dealer_hand = initial_game_setup(num_decks)
    print(f"Your balance: ${balance}")
    bet = place_bet(balance, min_bet, max_bet)

    # Track bet history
    if 'bet_history' not in player:
        player['bet_history'] = []
    player['bet_history'].append(bet)
    
    display_hand(player_hand)
    display_hand(dealer_hand, hide_dealer_card=True)

    split_hands = []
    if len(player_hand) == 2 and player_hand[0]['value'] == player_hand[1]['value']:
        split_hands = player_turn(deck, player_hand, bet)
        if split_hands:
            print("Playing split hands...")
            for hand in split_hands:
                print(f"Playing hand: {hand}")
                balance += play_hand(deck, hand, dealer_hand, bet / 2, balance)
    else:
        balance += play_hand(deck, player_hand, dealer_hand, bet, balance)

    player['balance'] = balance
    update_player_stats(player, balance - player['balance'], bet)
    return player

# Save game state
def save_game_state(players, num_decks, filename='game_state.json'):
    with open(filename, 'w') as f:
        json.dump({'players': players, 'num_decks': num_decks}, f)

# Load game state
def load_game_state(filename='game_state.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            return data['players'], data['num_decks']
    else:
        return [{"name": "Player 1", "balance": 1000, "wins": 0, "losses": 0, "ties": 0, "games_played": 0, "total_winnings": 0, "longest_win_streak": 0, "bet_history": []}], 6

# Display player stats
def display_stats(players):
    for player in players:
        print(f"{player['name']}: Balance: ${player['balance']}, Wins: {player['wins']}, Losses: {player['losses']}, Ties: {player['ties']}, Games Played: {player['games_played']}, Total Winnings: ${player['total_winnings']}, Longest Winning Streak: {player['longest_win_streak']}")
        print(f"Bet History: {player['bet_history']}")

# Display player rankings
def display_rankings(players):
    sorted_players = sorted(players, key=lambda x: (x['wins'], x['balance']), reverse=True)
    print("\nPlayer Rankings:")
    for rank, player in enumerate(sorted_players, 1):
        win_rate = (player['wins'] / (player['wins'] + player['losses'] + player['ties'])) * 100 if (player['wins'] + player['losses'] + player['ties']) > 0 else 0
        avg_bet = sum(player['bet_history']) / len(player['bet_history']) if player['bet_history'] else 0
        print(f"{rank}. {player['name']} - Wins: {player['wins']}, Win Rate: {win_rate:.2f}%, Average Bet: ${avg_bet:.2f}")

# Handle player bankruptcy
def handle_bankruptcy(player):
    while True:
        action = input(f"{player['name']}, you are out of money. Would you like to reset your balance to $1000 or leave the game? (R)eset / (L)eave: ").strip().upper()
        if action == 'R':
            player['balance'] = 1000
            print(f"{player['name']}'s balance has been reset to $1000.")
            return player
        elif action == 'L':
            print(f"{player['name']} has left the game.")
            return None
        else:
            print("Invalid action. Please choose 'R' to reset or 'L' to leave.")

# Add new player
def add_new_player(players):
    name = input("Enter new player's name: ").strip()
    if name:
        players.append({"name": name, "balance": 1000, "wins": 0, "losses": 0, "ties": 0, "games_played": 0, "total_winnings": 0, "longest_win_streak": 0, "bet_history": []})
        print(f"Player {name} added.")
    else:
        print("Invalid name.")

# Remove player
def remove_player(players):
    name = input("Enter the name of the player to remove: ").strip()
    players = [player for player in players if player['name'] != name]
    print(f"Player {name} removed.")
    return players

# Update player stats
def update_player_stats(player, result, bet):
    player['games_played'] += 1
    if result > 0:
        player['wins'] += 1
        player['total_winnings'] += result
        player['longest_win_streak'] = max(player['longest_win_streak'], player['wins'] - player['losses'])
    elif result < 0:
        player['losses'] += 1
        player['longest_win_streak'] = 0
    else:
        player['ties'] += 1

# Display game instructions
def display_instructions():
    print("\nGame Instructions:")
    print("1. Place your bet.")
    print("2. You will be dealt two cards, and the dealer will have two cards (one hidden).")
    print("3. Choose your action: Hit (H), Stand (S), Double Down (D), or Split (P).")
    print("4. If you choose to Double Down, your bet will be doubled.")
    print("5. If you choose to Split, you will play two separate hands.")
    print("6. The dealer will reveal their hidden card and draw until they reach at least 17.")
    print("7. If your hand value is higher than the dealer's without busting, you win. If it's lower, you lose. If it's the same, it's a tie.")
    print("8. Insurance bet is available if the dealer's face-up card is an Ace.")
    print("9. You can reset your balance or leave the game if you run out of money.")
    print("10. You can view player stats and rankings from the main menu.")
    print("11. Each action can be chosen during your turn: (H)it, (S)tand, (D)ouble Down, or (P) Split.")
    print("12. Check the bet history and statistics for better strategies.")
    print("13. At the end of each game, a summary of bets and outcomes will be provided.\n")

# Game Summary
def display_game_summary(players):
    print("\nGame Summary:")
    for player in players:
        print(f"{player['name']}:")
        print(f"  Total Bets: ${sum(player['bet_history'])}")
        print(f"  Total Wins: ${player['total_winnings']}")
        print(f"  Win-Loss Ratio: {player['wins'] / (player['losses'] + 1):.2f}")
        print(f"  Average Hand Value: {sum(calculate_hand_value(hand) for hand in player['hand_history']) / len(player['hand_history']) if player['hand_history'] else 0:.2f}")
        print()

# Function to calculate the dealer's blackjack bonus
def calculate_blackjack_bonus(balance, bet):
    blackjack_bonus = bet * 0.5  # 50% bonus for blackjack
    return balance + blackjack_bonus

# Function to add a new card type
def add_custom_card_type(deck, suit, value, card_value):
    deck.append({'suit': suit, 'value': value, 'card_value': card_value})

# Function to handle player interactions
def handle_player_interactions(players):
    while True:
        interaction = input("Choose interaction: (V)iew player stats, (R)eset stats, (D)etailed player view, or (E)xit: ").strip().upper()
        if interaction == 'V':
            display_stats(players)
        elif interaction == 'R':
            for player in players:
                player['wins'] = 0
                player['losses'] = 0
                player['ties'] = 0
                player['total_winnings'] = 0
                player['longest_win_streak'] = 0
            print("Player stats have been reset.")
        elif interaction == 'D':
            player_name = input("Enter player's name for detailed view: ").strip()
            player = next((p for p in players if p['name'] == player_name), None)
            if player:
                print(f"Detailed view for {player_name}:")
                print(f"Balance: ${player['balance']}")
                print(f"Bet History: {player['bet_history']}")
                print(f"Games Played: {player['games_played']}")
                print(f"Longest Winning Streak: {player['longest_win_streak']}")
            else:
                print("Player not found.")
        elif interaction == 'E':
            break
        else:
            print("Invalid interaction. Please choose a valid option.")

# Function to display customized messages based on player's current balance
def display_balance_message(player):
    balance = player['balance']
    if balance <= 50:
        print(f"{player['name']}, you have a very low balance! Consider depositing more funds.")
    elif balance <= 200:
        print(f"{player['name']}, your balance is getting low. Manage your bets carefully.")
    elif balance > 2000:
        print(f"{player['name']}, you have a high balance! Great job managing your funds.")

# Function to simulate a tournament mode
def play_tournament(players, num_decks, min_bet, max_bet, rounds=5):
    tournament_results = {player['name']: {'wins': 0, 'losses': 0, 'ties': 0} for player in players}
    for round_num in range(rounds):
        print(f"\nTournament Round {round_num + 1}")
        for player in players:
            if player['balance'] <= 0:
                player = handle_bankruptcy(player)
                if player is None:
                    players.remove(player)
                    continue
            print(f"\n{player['name']}'s turn:")
            player = play_round(player, num_decks, min_bet, max_bet)
            result = player['balance'] - 1000  # Example result calculation
            if result > 0:
                tournament_results[player['name']]['wins'] += 1
            elif result < 0:
                tournament_results[player['name']]['losses'] += 1
            else:
                tournament_results[player['name']]['ties'] += 1
            save_game_state(players, num_decks)
    print("\nTournament Results:")
    for player_name, result in tournament_results.items():
        print(f"{player_name} - Wins: {result['wins']}, Losses: {result['losses']}, Ties: {result['ties']}")

# Bank Deposit
def deposit_money(player):
    while True:
        try:
            amount = int(input(f"Enter amount to deposit (current balance: ${player['balance']}): "))
            if amount > 0:
                player['balance'] += amount
                print(f"${amount} deposited. New balance: ${player['balance']}")
                return player
            else:
                print("Deposit amount must be greater than 0.")
        except ValueError:
            print("Invalid amount. Please enter a number.")

# Bank Withdrawal
def withdraw_money(player):
    while True:
        try:
            amount = int(input(f"Enter amount to withdraw (current balance: ${player['balance']}): "))
            if 0 < amount <= player['balance']:
                player['balance'] -= amount
                print(f"${amount} withdrawn. New balance: ${player['balance']}")
                return player
            elif amount > player['balance']:
                print("Insufficient balance.")
            else:
                print("Withdrawal amount must be greater than 0.")
        except ValueError:
            print("Invalid amount. Please enter a number.")

# Customize Game Settings
def customize_game_settings():
    while True:
        try:
            min_bet = int(input("Enter minimum bet amount: "))
            max_bet = int(input("Enter maximum bet amount: "))
            if min_bet > 0 and max_bet >= min_bet:
                return min_bet, max_bet
            else:
                print("Invalid bet amounts. Minimum bet must be greater than 0 and maximum bet must be at least equal to minimum bet.")
        except ValueError:
            print("Invalid amount. Please enter a number.")

# Main function
def main():
    players, num_decks = load_game_state()
    min_bet = 10
    max_bet = 1000
    while True:
        action = input("Choose action: (P)lay, (A)dd player, (R)emove player, (C)hange deck count, (H)elp, (S)ummary, (B)ank, (G)ame settings, or (Q)uit: ").strip().upper()
        if action == 'P':
            for player in players:
                if player['balance'] <= 0:
                    player = handle_bankruptcy(player)
                    if player is None:
                        players.remove(player)
                        continue
                print(f"\n{player['name']}'s turn:")
                player = play_round(player, num_decks, min_bet, max_bet)
                update_player_stats(player, player['balance'] - 1000, 0)  # Example update
                save_game_state(players, num_decks)

                if input("Play another round? (Y/N): ").strip().upper() != 'Y':
                    display_stats(players)
                    display_rankings(players)
                    print("Saving game state...")
                    save_game_state(players, num_decks)
                    print("Game state saved. Exiting...")
                    return
        elif action == 'A':
            add_new_player(players)
        elif action == 'R':
            players = remove_player(players)
        elif action == 'C':
            while True:
                try:
                    num_decks = int(input("Enter the number of decks to use: "))
                    if num_decks > 0:
                        break
                    else:
                        print("Number of decks must be greater than 0.")
                except ValueError:
                    print("Invalid number. Please enter a valid number.")
        elif action == 'H':
            display_instructions()
        elif action == 'S':
            display_game_summary(players)
        elif action == 'B':
            while True:
                bank_action = input("(D)eposit, (W)ithdraw, or (E)xit: ").strip().upper()
                if bank_action == 'D':
                    for player in players:
                        player = deposit_money(player)
                elif bank_action == 'W':
                    for player in players:
                        player = withdraw_money(player)
                elif bank_action == 'E':
                    break
                else:
                    print("Invalid action.")
        elif action == 'G':
            min_bet, max_bet = customize_game_settings()
        elif action == 'Q':
            print("Saving game state...")
            save_game_state(players, num_decks)
            print("Game state saved. Exiting...")
            break
        else:
            print("Invalid action. Please choose a valid option.")

if __name__ == '__main__':
    main()
