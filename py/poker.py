import random
from itertools import combinations

# --- Card and Deck Setup ---
RANKS = '23456789TJQKA'
SUITS = 'hdcs'  # heart, diamond, club, spade

DECK = {r + s for r in RANKS for s in SUITS}

# --- Hand Evaluation ---
def get_hand_rank(hand):
    all_cards = sorted(hand, key=lambda c: RANKS.index(c[0]), reverse=True)

    # Helper to get card ranks (as numbers) and suits
    card_ranks = [RANKS.index(c[0]) for c in all_cards]
    card_suits = [c[1] for c in all_cards]

    # --- Check for flush and straight flush ---
    is_flush = None
    flush_suit = None
    for suit in SUITS:
        if card_suits.count(suit) >= 5:
            is_flush = True
            flush_suit = suit
            break

    # --- Check for straight and straight flush ---
    is_straight = False
    straight_high_card = -1
    
    # Check for Ace-low straight (A-2-3-4-5)
    unique_ranks = sorted(list(set(card_ranks)), reverse=True)
    if all(r in unique_ranks for r in [12, 3, 2, 1, 0]): # A, 5, 4, 3, 2
        unique_ranks.append(-1) # Add a "low ace" for calculation

    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i+4] == 4:
            is_straight = True
            straight_high_card = unique_ranks[i]
            break

    # Straight flush
    if is_flush and is_straight:
        flush_cards = sorted([c for c in all_cards if c[1] == flush_suit], key=lambda c: RANKS.index(c[0]), reverse=True)
        flush_ranks = sorted(list(set([RANKS.index(c[0]) for c in flush_cards])), reverse=True)
        if all(r in flush_ranks for r in [12, 3, 2, 1, 0]):
             flush_ranks.append(-1)
        for i in range(len(flush_ranks) - 4):
            if flush_ranks[i] - flush_ranks[i+4] == 4:
                return (8, flush_ranks[i]) # Straight flush

    # --- Check for other hand types ---
    rank_counts = {r: card_ranks.count(r) for r in unique_ranks}
    counts = sorted(rank_counts.values(), reverse=True)
    
    # Four of a kind
    if counts[0] == 4:
        four_rank = [r for r, c in rank_counts.items() if c == 4][0]
        kickers = [r for r in unique_ranks if r != four_rank]
        return (7, four_rank, kickers[0])

    # Full House
    if counts[0] == 3 and counts[1] >= 2:
        three_rank = [r for r, c in rank_counts.items() if c == 3][0]
        two_rank = [r for r, c in rank_counts.items() if c >= 2 and r != three_rank][0]
        return (6, three_rank, two_rank)

    # Flush
    if is_flush:
        flush_ranks = sorted([RANKS.index(c[0]) for c in all_cards if c[1] == flush_suit], reverse=True)
        return (5, tuple(flush_ranks[:5]))

    # Straight
    if is_straight:
        return (4, straight_high_card)

    # Three of a kind
    if counts[0] == 3:
        three_rank = [r for r, c in rank_counts.items() if c == 3][0]
        kickers = [r for r in unique_ranks if r != three_rank]
        return (3, three_rank, tuple(kickers[:2]))

    # Two Pair
    if counts[0] == 2 and counts[1] == 2:
        pair_ranks = [r for r, c in rank_counts.items() if c == 2]
        high_pair = max(pair_ranks)
        low_pair = min(pair_ranks)
        kickers = [r for r in unique_ranks if r not in pair_ranks]
        return (2, high_pair, low_pair, kickers[0])

    # One Pair
    if counts[0] == 2:
        pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
        kickers = [r for r in unique_ranks if r != pair_rank]
        return (1, pair_rank, tuple(kickers[:3]))

    # High Card
    return (0, tuple(unique_ranks[:5]))

def get_best_hand(seven_cards):
    """Finds the best 5-card hand from a 7-card hand."""
    best_rank = (-1,)
    for hand_combination in combinations(seven_cards, 5):
        rank = get_hand_rank(list(hand_combination))
        if rank > best_rank:
            best_rank = rank
    return best_rank

# --- Main Logic ---
def calculate_win_probability(player_cards, community_cards):
    """
    Calculates the win probability for the player against one random opponent.
    """
    # Create a deck without the player's and community cards
    remaining_deck = DECK - set(player_cards) - set(community_cards)
    
    wins = 0
    ties = 0
    losses = 0
    
    player_best_hand = get_best_hand(player_cards + community_cards)
    
    # Generate all possible 2-card hands for the opponent
    opponent_hands = list(combinations(remaining_deck, 2))
    total_opp_hands = len(opponent_hands)
    
    for opp_cards in opponent_hands:
        opp_best_hand = get_best_hand(list(opp_cards) + community_cards)
        
        if player_best_hand > opp_best_hand:
            wins += 1
        elif player_best_hand == opp_best_hand:
            ties += 1
        else:
            losses += 1
            
    # Win probability = (wins + ties/2) / total
    win_prob = (wins + ties / 2) / total_opp_hands
    return win_prob

def get_suggestion(win_probability):
    """
    Returns a suggested action based on the win probability.
    """
    if win_probability > 0.7:
        return "Raise (Рейз)"
    elif win_probability > 0.4:
        return "Call (Колл)"
    else:
        return "Fold (Пас)"

def parse_cards(card_string):
    """Parses a string of cards into a list."""
    return card_string.strip().split()

# --- Main Execution ---
if __name__ == "__main__":
    print("Ace-Oracle Poker Assistant")
    print("Введите карты в формате: Th 9s (T - десятка, h - червы, s - пики)")
    print("Ранги: 2-9, T, J, Q, K, A")
    print("Масти: h (hearts/червы), d (diamond/бубны), c (club/трефы), s (spade/пики)")
    
    try:
        player_cards_str = input("Введите ваши 2 карты: ")
        player_cards = parse_cards(player_cards_str)

        community_cards_str = input("Введите 5 карт на столе (ривер): ")
        community_cards = parse_cards(community_cards_str)
        
        if len(player_cards) != 2 or len(community_cards) != 5:
            print("Ошибка: Неверное количество карт. У вас должно быть 2 карты, а на столе 5.")
        else:
            all_entered_cards = player_cards + community_cards
            if len(set(all_entered_cards)) != 7:
                print("Ошибка: Среди введенных карт есть дубликаты.")
            else:
                print("\nРассчитываю шансы...")
                
                win_prob = calculate_win_probability(player_cards, community_cards)
                suggestion = get_suggestion(win_prob)
                
                print(f"\nВаши карты: {', '.join(player_cards)}")
                print(f"Карты на столе: {', '.join(community_cards)}")
                print(f"Шанс на победу: {win_prob:.2%}")
                print(f"Рекомендуемое действие: {suggestion}")

    except Exception as e:
        print(f"\nПроизошла ошибка. Убедитесь, что вы ввели карты правильно. Ошибка: {e}")