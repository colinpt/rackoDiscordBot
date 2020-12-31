import random

# Returns an array of 60 cards numbered 1-60. 
def init_deck():
    deck = []
    for i in range(1,61):
        deck.append(i)
    return deck

# Accepts a array and shuffles the contents.
def shuffle_cards(deck):
    for i in range(0,len(deck)):
        rand = random.randint(0,len(deck) - 1)
        temp = deck[i]
        deck[i] = deck[rand]
        deck[rand] = temp

# Checks an array to see if contents are in ascending order.
def check_racko(rack):
    for i in range(0,len(rack)-1):
        if rack[i+1] < rack[i]:
            return False
    return True

# Returns a card out of a given deck, and removes it from said deck.
def deal_card(deck):
    card = deck[len(deck)-1]
    deck.pop(len(deck)-1)
    return card

# Deals two 10 card hands in the typical alternating fashion.
def deal_hands(deck):
    hand1 = []
    hand2 = []
    for i in range(0,20):
        if i % 2 == 1:
            hand1.insert(0,deck[len(deck)-1])
        else:
            hand2.insert(0,deck[len(deck)-1])

        deck.pop(len(deck)-1)
    return [hand1,hand2]

# Returns a given hand as a string.
def getGameBoard(userRack, compRack, discard):
    output = "\n----USER RACK----      ----COMP RACK----"
    i = len(userRack) -1
    output = output + "\n---SLOT---CARD---      ---SLOT---CARD---"
    while i >= 0:
        output = output + "\n    {0}  -  {1}".format(i, userRack[i])
        if len(str(userRack[i])) == 1:
            output = output + " " 
        output = output + "              {0}  -  {1}   ".format(i, compRack[i])
        i -= 1
    output = output + "\n-----------------      -----------------"
    output = output + "\nTOP OF DECK: ?\nTOP OF DISCARD: "
    if discard:
        output = output + str(discard[len(discard) - 1])
    else:
        output = output + "N/A"
    return output

# Accepts a card and a discard array, and adds the card to the discard.
def discard_card(card,discard):
    discard.append(card)

# Accepts a new card, the card that is to be replaced, a hand, and the discard array.
# Checks position of the card that is to be replaced, discards it, and replaces it with the new card.
def find_and_replace(new_card, slot, hand, discard, player):
    output = player + " replaced {0} with {1} in slot {2}".format(hand[slot], new_card, slot)
    discard_card(hand[slot], discard)
    hand[slot] = new_card
    return output

# Runs the computers turn. 
def computer_turn(hand, deck, discard):
    # Calls check_spots and stores the data for the hand
    spots = check_spots(hand)
    output = ""
    # If the discard pile is not empty.
    if discard:
        # Sets current card to top of discard
        card = discard[len(discard)-1]
        # Removes top card of discard from the pile.
        discard.pop(len(discard) - 1)

        # If there is only one slot that is not complete.
        if spots[10] == 1:
            # Stores a copy of the hand.
            test_hand = hand
            # Set index to the index of the incomplete spot
            index = spots[11]
            # Add card to the test hand in the incomplete index.
            test_hand[index] = card
            # Check if adding the top discard to the index completes the test-hand
            if check_racko(test_hand) == True:
                # Replace the card in the real hand.
                output = output + "The Computer drew a {0} from the discard pile.\n".format(card)
                output = output + find_and_replace(card, index, hand, discard, "The Computer")
                return output
            # Otherwise draw from the deck and replace the incomplete index
            else:
                card = deal_card(deck)
                output = output + "The Computer drew a {0} from the deck.\n".format(card)
                output = output + find_and_replace(card, index, hand, discard, "The Computer")
                return output
        
        logic = comp_logic(card,hand,discard)
        if  len(logic) > 0:
            output = output + "The Computer drew a {0} from the discard pile.\n".format(card)
            output = output + logic
            logic = True
        else:
            logic = False

        if  logic == False:
            discard.append(card)
            card = deal_card(deck)
            output = output + "The Computer drew a {0} from the deck.\n".format(card)
            logic = comp_logic(card,hand,discard)
            if  len(logic) > 0:
                output = output + logic
                logic = True
            else:
                logic = False
            if  logic == False:
                output = output + find_and_replace(card, 9, hand, discard, "The Computer")
                return output
            else:
                return output
        else:
            return output
            
    else:
        card = deal_card(deck)
        output = output + "The Computer drew a {0} from the deck.\n".format(card)
        logic = comp_logic(card, hand, discard)
        if  len(logic) > 0:
            output = output + logic
            logic = True
        else:
            logic = False
        if logic == False:
            output = output + find_and_replace(card, 9, hand, discard, "The Computer")
            return output
        else:
            return output

# Checks a card against a given hand to find ideal position
def comp_logic(card,hand,discard):
    output = ""
    for i in range (0,10):
        if i < 9:
            next_i = hand[i+1]
        else:
            next_i = 61
        # If card is greater than the card in index i, and card is <= 10 + 5 * the index of the hand. (Slot 5 = 30, Slot 8 = 45, etc. ) and that slot is not already completed
        # OR the card is greater than the index, and card is less than the following
        if not(i == 0 and card > hand[i]) and card <= (10 + (i*5)) and check_comp_hand(hand,i) == 0 or (card > hand[i] and card < next_i and card < i + 1 * 6):
            # If the card is less than 50 and didn't fit in the first 9 slots, return False.
            if i == 9 and card < 50:
                return output
            # Replace card in appropriate slot, and display computers action.
            else:
                output = output + find_and_replace(card, i, hand, discard, "The Computer")
                return output
    # If no ideal position is found, return False.
    return output

# Checks a given index in hand to see if it is in an appropriate slot.
def check_comp_hand(hand, num):
        if hand[num] < ((num + 1) * 6) and hand[num] > ((num + 1) * 5):
            return 1
        else:
            return 0

# Accepts a hand and returns an array of related data.
# For indexes 0-9, a 0 represents an incorrect position, a 1 represents a correct position.
# Index 10 represents the number of incorrect positions in the hand
# Index 11 represents the index of the remaining incorrect position. (Only relevant if only one inccorect position remains.)  
def check_spots(hand):
    spots = []
    spots_count = 10
    spots_index = 0
    for i in range(0,len(hand) - 1):
        if hand[i] < hand[i+1]:
            spots.append(1)
            spots_count -= 1
            spots_index = i
        else:
            spots.append(0)
    spots.append(spots_count)
    spots.append(spots_index)
    return spots


