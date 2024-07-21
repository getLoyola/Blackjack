import random
import json

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
def insurance_bet(balance):
    while True:
        try:
            insurance = int(input("Place your insurance bet (half of your original bet): "))
            if 0 < insurance <= balance:
                return insurance
            elif insurance > balance:
                print("Insufficient balance.")
            else:
                print("Insurance bet must be greater than 0.")
        except ValueError:
            print("Invalid insurance bet amount. Please enter a number.")

# Player's turn
def player_turn(deck, player_hand):
    while True:
        action = input("Choose action: (H)it, (S)tand, (D)ouble Down, or (P) split: ").strip().upper()
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
                player_hand.append(deal_card(deck))
                display_hand(player_hand)
                if calculate_hand_value(player_hand) > 21:
                    print("Player busts! Dealer wins.")
                    return False
                return True
            else:
                print("Double Down can only be used with the initial hand.")
        elif action == 'P':
            if len(player_hand) == 2:
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
                print("Split can only be used with the initial hand.")
        else:
            print("Invalid action. Please choose 'H', 'S', 'D', or 'P'.")
    return True

# Dealer's turn
def dealer_turn(deck, dealer_hand):
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    return dealer_hand

# Initial game setup
def initial_game_setup():
    deck = create_deck(num_decks=6)  # Using multiple decks for more realism
    shuffle_deck(deck)
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    return deck, player_hand, dealer_hand

# Betting function
def place_bet(balance):
    while True:
        try:
            bet = int(input("Place your bet: "))
            if 0 < bet <= balance:
                return bet
            elif bet > balance:
                print("Insufficient balance.")
            else:
                print("Bet must be greater than 0.")
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
        insurance = insurance_bet(balance // 2)
        if calculate_hand_value(dealer_hand) == 21:
            print("Dealer has Blackjack.")
            if insurance > 0:
                print("Insurance bet won.")
                return insurance * 2
            else:
                print("Player loses.")
                return -bet

    if player_turn(deck, player_hand):
        dealer_hand = dealer_turn(deck, dealer_hand)
        display_hand(dealer_hand)
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)
        return evaluate_outcome(player_value, dealer_value, bet, balance, insurance)
    return -bet

# Play a round
def play_round(player):
    balance = player['balance']
    deck, player_hand, dealer_hand = initial_game_setup()
    print(f"Your balance: ${balance}")
    bet = place_bet(balance)
    
    display_hand(player_hand)
    display_hand(dealer_hand, hide_dealer_card=True)
    
    split_hands = []
    if len(player_hand) == 2 and player_hand[0]['value'] == player_hand[1]['value']:
        split_hands = player_turn(deck, player_hand)
        if split_hands:
            print("Playing split hands...")
            for hand in split_hands:
                print(f"Playing hand: {hand}")
                balance += play_hand(deck, hand, dealer_hand, bet / 2, balance)
    else:
        balance += play_hand(deck, player_hand, dealer_hand, bet, balance)

    player['balance'] = balance
    return player

# Save game state
def save_game_state(players, filename='game_state.json'):
    with open(filename, 'w') as f:
        json.dump(players, f)

# Load game state
def load_game_state(filename='game_state.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"name": "Player 1", "balance": 1000, "wins": 0, "losses": 0, "ties": 0}]

# Display player stats
def display_stats(players):
    for player in players:
        print(f"{player['name']}: Balance: ${player['balance']}, Wins: {player['wins']}, Losses: {player['losses']}, Ties: {player['ties']}")

# Display player rankings
def display_rankings(players):
    rankings = sorted(players, key=lambda x: x['wins'], reverse=True)
    print("\nPlayer Rankings:")
    for rank, player in enumerate(rankings, start=1):
        win_rate = (player['wins'] / (player['wins'] + player['losses'] + player['ties'])) * 100 if (player['wins'] + player['losses'] + player['ties']) > 0 else 0
        print(f"{rank}. {player['name']} - Wins: {player['wins']}, Win Rate: {win_rate:.2f}%")

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

# Main function
def main():
    players = load_game_state()
    while True:
        for player in players:
            if player['balance'] <= 0:
                player = handle_bankruptcy(player)
                if player is None:
                    players.remove(player)
                    continue

            print(f"\n{player['name']}'s turn:")
            player = play_round(player)
            save_game_state(players)

            if input("Play another round? (Y/N): ").strip().upper() != 'Y':
                display_stats(players)
                display_rankings(players)
                print("Saving game state...")
                save_game_state(players)
                print("Game state saved. Exiting...")
                return

if __name__ == '__main__':
    main()
