import socket
import protocol  
import consts
import game_logic

UDP_PORT = consts.UDP_PORT
BUFFER_SIZE = consts.BUFFER_SIZE

def get_user_action():
    while True:
        choice = input("Your action (h/s): ").lower()
        if choice in ['h', 'hit']:
            return "hit"
        elif choice in ['s', 'stand']:
            return "stand"
        print("Invalid input. Please enter 'h' or 's'.")

def play_session(server_ip, server_port, team_name, rounds):

    print(f"Connecting to {server_ip}:{server_port}...")
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))

        req_msg = protocol.pack_request(rounds, team_name)
        sock.sendall(req_msg)
        
        wins = 0
        for i in range(1, rounds + 1):
            print(f"\n--- Round {i} of {rounds} ---")
            
            player_hand = game_logic.Hand()
            dealer_hand = game_logic.Hand()
            my_turn = True
            round_over = False
            card_count = 0
            dealer_turn_started = False
            player_busted = False
            
            while not round_over:
                header_data = sock.recv(9)
                if not header_data:
                    raise Exception("Server disconnected unexpectedly")
                
                parsed = protocol.unpack_server_payload(header_data)
                if not parsed:
                    print("Error: Invalid message format.")
                    break
                    
                result, card_rank, card_suit = parsed
                
                if card_rank > 0:
                    card = game_logic.Card(card_rank, card_suit)
                    
                    if card_count < 2:
                        player_hand.add_card(card)
                        print(f"You received: {card}")
                        if card_count == 1:
                            total = player_hand.get_value()
                            if total == 21:
                                print(f"Your hand: {player_hand} (Total: 21 BLACKJACK!)")
                            else:
                                print(f"Your hand: {player_hand} (Total: {total})")
                    elif card_count == 2:
                        dealer_hand.add_card(card)
                        print(f"Dealer's visible card: {card}")
                    else:
                        if my_turn:
                            player_hand.add_card(card)
                            print(f"You received: {card}")
                            total = player_hand.get_value()
                            if total == 21:
                                print(f"Your hand: {player_hand} (Total: 21 BLACKJACK!)")
                            else:
                                print(f"Your hand: {player_hand} (Total: {total})")
                            if total > 21:
                                print("You BUSTED!")
                                player_busted = True
                        else:
                            dealer_hand.add_card(card)
                            if not dealer_turn_started:
                                print(f"Dealer's hidden card was: {card}")
                                dealer_turn_started = True
                            else:
                                print(f"Dealer received: {card}")
                            dealer_total = dealer_hand.get_value()
                            if dealer_total == 21:
                                print(f"Dealer's hand: {dealer_hand} (Total: 21 BLACKJACK!)")
                            else:
                                print(f"Dealer's hand: {dealer_hand} (Total: {dealer_total})")
                            if dealer_total > 21:
                                print("Dealer BUSTED!")
                    
                    card_count += 1
                
                # Handle final results (1=Tie, 2=Loss, 3=Win)
                if result >= 1 and result <= 3:
                    round_over = True
                    if result == 3: 
                        print("You WON this round!")
                        wins += 1
                    elif result == 2: 
                        print("You LOST this round.")
                    elif result == 1: 
                        print("It's a TIE.")
                    continue
                
                if result == 10:
                    my_turn = False
                    continue 
                
                if my_turn and card_count >= 3 and not player_busted:
                    if player_hand.get_value() == 21:
                        print("Standing with 21!")
                        msg = protocol.pack_client_payload("stand")
                        sock.sendall(msg)
                        my_turn = False
                        print("Waiting for dealer's moves...")
                    else:
                        action = get_user_action()
                        msg = protocol.pack_client_payload(action)
                        sock.sendall(msg)
                        
                        if action.lower() == "stand":
                            my_turn = False
                            print("Waiting for dealer's moves...")
        
        win_rate = (wins / rounds) * 100
        print(f"Finished playing {rounds} rounds, win rate: {win_rate:.1f}%")
        return True  

    except Exception as e:
        print(f"Game error: {e}")
        return False  
    finally:
        if sock:
            sock.close()

def start_client():

    print("--- Welcome to Blackjack Client ---") 
    team_name = input("Enter your team name: ")[:31]
    print(f"Team Name: {team_name}")
    while True:
        try:
            rounds_input = input("How many rounds to play? ")
            rounds = int(rounds_input)
            if rounds > 0: break
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid number.")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    udp_sock.bind(("", UDP_PORT))
    
    print("Client started, listening for offer requests...") 

    while True:
        try:
            data, addr = udp_sock.recvfrom(BUFFER_SIZE)
            offer = protocol.unpack_offer(data)
            
            if offer:
                server_port, server_name = offer
                server_ip = addr[0]
                
                print(f"Received offer from {server_ip} ('{server_name}')") 
                
                while True:
                    play_session(server_ip, server_port, team_name, rounds)
                    
                    play_again = input("\nDo you want to play again? (y/n): ").lower()
                    if play_again != 'y':
                        print("Thanks for playing!")
                        udp_sock.close()
                        return                      
                    while True:
                        try:
                            rounds_input = input("How many rounds to play? ")
                            rounds = int(rounds_input)
                            if rounds > 0: break
                            print("Please enter a positive number.")
                        except ValueError:
                            print("Invalid number.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_client()