import random

# Define card values and suits
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# Create a deck of cards
def create_deck():
    return [{'suit': suit, 'value': value} for suit in suits for value in values]

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

# Player's turn
def player_turn(deck, player_hand):
    while True:
        action = input("Choose action: (H)it or (S)tand: ").strip().upper()
        if action == 'H':
            player_hand.append(deal_card(deck))
            print(f"Player's hand: {player_hand}, Value: {calculate_hand_value(player_hand)}")
            if calculate_hand_value(player_hand) > 21:
                print("Player busts! Dealer wins.")
                return False
        elif action == 'S':
            break
        else:
            print("Invalid action. Please choose 'H' or 'S'.")
    return True

# Dealer's turn
def dealer_turn(deck, dealer_hand):
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    return dealer_hand

# Initial game setup
def initial_game_setup():
    deck = create_deck()
    shuffle_deck(deck)
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    return deck, player_hand, dealer_hand

# Betting function
def place_bet():
    while True:
        try:
            bet = int(input("Place your bet: "))
            if bet > 0:
                return bet
            else:
                print("Bet must be greater than 0.")
        except ValueError:
            print("Invalid bet amount. Please enter a number.")

# Main function
def main():
    deck, player_hand, dealer_hand = initial_game_setup()
    player_balance = 1000
    print(f"Your balance: ${player_balance}")
    bet = place_bet()
    if bet > player_balance:
        print("Insufficient balance.")
        return

    print(f"Player's hand: {player_hand}, Value: {calculate_hand_value(player_hand)}")
    print(f"Dealer's hand: {dealer_hand[0]} and [hidden]")
    
    if player_turn(deck, player_hand):
        dealer_hand = dealer_turn(deck, dealer_hand)
        print(f"Dealer's hand: {dealer_hand}, Value: {calculate_hand_value(dealer_hand)}")
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)
        
        if dealer_value > 21:
            print("Dealer busts! Player wins.")
            player_balance += bet
        elif dealer_value >= player_value:
            print("Dealer wins.")
            player_balance -= bet
        else:
            print("Player wins.")
            player_balance += bet
    
    print(f"Your balance: ${player_balance}")

if __name__ == '__main__':
    main()
