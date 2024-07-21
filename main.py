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

# Check for blackjack
def is_blackjack(hand):
    return len(hand) == 2 and calculate_hand_value(hand) == 21

# Player's turn
def player_turn(deck, player_hand):
    while True:
        action = input("Choose action: (H)it, (S)tand, (D)ouble Down, or (P) split: ").strip().upper()
        if action == 'H':
            player_hand.append(deal_card(deck))
            print(f"Player's hand: {player_hand}, Value: {calculate_hand_value(player_hand)}")
            if calculate_hand_value(player_hand) > 21:
                print("Player busts! Dealer wins.")
                return False
        elif action == 'S':
            break
        elif action == 'D':
            if len(player_hand) == 2:
                player_hand.append(deal_card(deck))
                print(f"Player's hand: {player_hand}, Value: {calculate_hand_value(player_hand)}")
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
                print(f"Hand 1: {split_hand1}, Value: {calculate_hand_value(split_hand1)}")
                print(f"Hand 2: {split_hand2}, Value: {calculate_hand_value(split_hand2)}")
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
    deck = create_deck()
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
def evaluate_outcome(player_value, dealer_value, bet, balance):
    if dealer_value > 21:
        print("Dealer busts! Player wins.")
        balance += bet
    elif dealer_value > player_value:
        print("Dealer wins.")
        balance -= bet
    elif dealer_value < player_value:
        print("Player wins.")
        balance += bet
    else:
        print("It's a tie.")
    return balance

# Play a hand
def play_hand(deck, player_hand, dealer_hand, bet):
    if is_blackjack(player_hand):
        print("Player has a Blackjack!")
        balance += bet * 1.5
        return balance

    if player_turn(deck, player_hand):
        dealer_hand = dealer_turn(deck, dealer_hand)
        print(f"Dealer's hand: {dealer_hand}, Value: {calculate_hand_value(dealer_hand)}")
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)
        balance = evaluate_outcome(player_value, dealer_value, bet, balance)
    return balance

# Play a round
def play_round(balance):
    deck, player_hand, dealer_hand = initial_game_setup()
    print(f"Your balance: ${balance}")
    bet = place_bet(balance)
    
    print(f"Player's hand: {player_hand}, Value: {calculate_hand_value(player_hand)}")
    print(f"Dealer's hand: {dealer_hand[0]} and [hidden]")
    
    split_hands = []
    if len(player_hand) == 2 and player_hand[0]['value'] == player_hand[1]['value']:
        split_hands = player_turn(deck, player_hand)
        if split_hands:
            print("Playing split hands...")
            for hand in split_hands:
                print(f"Playing hand: {hand}")
                balance = play_hand(deck, hand, dealer_hand, bet / 2)
    else:
        balance = play_hand(deck, player_hand, dealer_hand, bet)
    
    return balance

# Main function
def main():
    balance = 1000
    while True:
        balance = play_round(balance)
        if balance <= 0:
            print("You're out of money. Game over.")
            break
        if input("Play another round? (Y/N): ").strip().upper() != 'Y':
            print(f"Final balance: ${balance}")
            break

if __name__ == '__main__':
    main()
