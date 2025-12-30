import random

# הגדרת קבועים לערכי קלפים וצורות (חשוב שיתאים לפרוטוקול הרשת אחר כך)
# Rank: 1-13, Suit: 0-3 [cite: 103]
SUITS = ['Heart', 'Diamond', 'Club', 'Spade'] 
RANKS = {
    1: 11,   # Ace [cite: 29]
    2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
    11: 10,  # Jack [cite: 27]
    12: 10,  # Queen [cite: 27]
    13: 10   # King [cite: 27]
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank  # 1-13
        self.suit = suit  # 0-3

    def get_value(self):
        return RANKS[self.rank]

    def __str__(self):
        NamedCards = {1: 'Ace', 11: 'Jack', 12: 'Queen', 13: 'King'}
        if self.rank in NamedCards:
            rank_str = NamedCards[self.rank]
            return f"{rank_str} of {SUITS[self.suit]}"
        else:
            return f"{self.rank} of {SUITS[self.suit]}"

class Deck:
    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1, 14):
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None

class Hand:

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total_value = 0
        for card in self.cards:
            total_value += card.get_value()
        return total_value

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

class BlackjackGame:

    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()

    def start_round(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        
        self.player_hand.add_card(self.deck.draw_card())
        self.player_hand.add_card(self.deck.draw_card())
        self.dealer_hand.add_card(self.deck.draw_card())
        self.dealer_hand.add_card(self.deck.draw_card())
        return {
            'player_cards': [str(card) for card in self.player_hand.cards],
            'dealer_cards': [str(self.dealer_hand.cards[0]), 'Hidden']
        }
    def player_hit(self):
        new_card = self.deck.draw_card()
        self.player_hand.add_card(new_card)
        is_bust = self.player_hand.get_value() > 21
        return {
            'new_card': str(new_card),
            'is_bust': is_bust
        }

    def dealer_turn(self):
        dealer_cards = [str(card) for card in self.dealer_hand.cards]
        while self.dealer_hand.get_value() < 17:
            new_card = self.deck.draw_card()
            self.dealer_hand.add_card(new_card)
            dealer_cards.append(str(new_card))
        return dealer_cards



    def check_winner(self):
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()

        if player_value > 21:
            return 'Loss' 
        elif dealer_value > 21:
            return 'Win'  
        elif player_value > dealer_value:
            return 'Win'
        elif player_value < dealer_value:
            return 'Loss'
        else:
            return 'Tie'