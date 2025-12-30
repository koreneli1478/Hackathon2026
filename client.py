import socket
import protocol  
import consts

UDP_PORT = consts.UDP_PORT
BUFFER_SIZE = consts.BUFFER_SIZE

def get_user_action():
    while True:
        choice = input("Your action (h/s): ").lower()
        if choice in ['h', 'hit']:
            return "Hittt" 
        elif choice in ['s', 'stand']:
            return "Stand"
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
            
            my_turn = True
            round_over = False
            
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
                    suits = ['Heart', 'Diamond', 'Club', 'Spade']
                    rank_str = str(card_rank)
                    if card_rank == 1: rank_str = "Ace"
                    elif card_rank == 11: rank_str = "Jack"
                    elif card_rank == 12: rank_str = "Queen"
                    elif card_rank == 13: rank_str = "King"
                    
                    print(f"Server sent card: {rank_str} of {suits[card_suit]}")
                
                if result != 0:
                    round_over = True
                    if result == 3: 
                        print("You WON this round!")
                        wins += 1
                    elif result == 2: 
                        print("You LOST this round.")
                    elif result == 1: 
                        print("It's a TIE.")
                    continue 
                
                if my_turn:
                    action = get_user_action()
                    msg = protocol.pack_client_payload(action)
                    sock.sendall(msg)
                    
                    if action == "Stand":
                        my_turn = False
                        print("Waiting for dealer's moves...")
        
        win_rate = (wins / rounds) * 100
        print(f"Finished playing {rounds} rounds, win rate: {win_rate:.1f}%")
        
    except Exception as e:
        print(f"Game error: {e}")
    finally:
        if sock:
            sock.close()

def start_client():

    print("--- Welcome to Blackjack Client ---") 
    team_name = consts.TEAM_NAME
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
                
                play_session(server_ip, server_port, team_name, rounds)
                
                print("Client started, listening for offer requests...") 
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_client()