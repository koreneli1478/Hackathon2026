import socket
import threading
import time
import game_logic 
import consts
import protocol 

UDP_DEST_PORT = consts.UDP_PORT  
BUFFER_SIZE = consts.BUFFER_SIZE

def send_broadcast_offers(server_port):

    server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #for hotspot
    #server_udp.bind((get_local_ip(), 0))

    print(f"UDP Broadcast started. Announcing TCP Port: {server_port}")

    try:
        while True:
            message = protocol.pack_offer(server_port, "Blackjack Server")
            
            server_udp.sendto(message, ('<broadcast>', UDP_DEST_PORT))
            
            time.sleep(1)
    except Exception as e:
        print(f"Error in UDP broadcast: {e}")
    finally:
        server_udp.close()

def handle_client(client_socket, client_address):

    print(f"Client connected from {client_address}")
    
    try:
        data = client_socket.recv(BUFFER_SIZE)
        result = protocol.unpack_request(data)
        if not result:
            print("Invalid request from client")
            return
        
        total_rounds, player_name = result
        print(f"Player '{player_name}' requested {total_rounds} rounds")
        
        game = game_logic.BlackjackGame()
        
        for round_num in range(1, total_rounds + 1):
            print(f"Starting round {round_num} for {player_name}")
            
            initial_cards = game.start_round()
            
            for card in game.player_hand.cards:
                msg = protocol.pack_server_payload(0, card.rank, card.suit)
                client_socket.send(msg)
            
            dealer_visible = game.dealer_hand.cards[0]
            msg = protocol.pack_server_payload(0, dealer_visible.rank, dealer_visible.suit)
            client_socket.send(msg)
            
            player_busted = False
            while True:
                action_data = client_socket.recv(BUFFER_SIZE)
                action = protocol.unpack_client_payload(action_data)
                
                if not action:
                    print("Invalid action or disconnect")
                    break
                
                if action.lower() == "stand":
                    print(f"{player_name} chose to stand")
                    break
                elif action.lower() == "hit":
                    print(f"{player_name} chose to hit")
                    hit_result = game.player_hit()
                    new_card = game.player_hand.cards[-1]
                    
                    if hit_result['is_bust']:
                        msg = protocol.pack_server_payload(10, new_card.rank, new_card.suit)
                        client_socket.send(msg)
                        print(f"{player_name} busted!")
                        player_busted = True
                        break
                    else:
                        msg = protocol.pack_server_payload(0, new_card.rank, new_card.suit)
                        client_socket.send(msg)

            if not player_busted:
                print("Dealer's turn...")
                dealer_hidden = game.dealer_hand.cards[1]
                msg = protocol.pack_server_payload(0, dealer_hidden.rank, dealer_hidden.suit)
                client_socket.send(msg)
                
                initial_count = len(game.dealer_hand.cards)
                game.dealer_turn()
                for i in range(initial_count, len(game.dealer_hand.cards)):
                    card = game.dealer_hand.cards[i]
                    msg = protocol.pack_server_payload(0, card.rank, card.suit)
                    client_socket.send(msg)
            
            result = game.check_winner() 
            print(f"Round {round_num} result: {result}")
            
            if result == 'Win': 
                result_code = 3
            elif result == 'Loss': 
                result_code = 2
            else: 
                result_code = 1 
            
            msg = protocol.pack_server_payload(result_code, 0, 0)
            client_socket.send(msg)
            
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        print(f"Closing connection with {client_address}")
        client_socket.close()

def get_local_ip():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
       return "127.0.0.1"
       #for hotspot:
 #       return "172.20.231.13"

def start_server():

    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp.bind(("", 0)) 
    assigned_port = server_tcp.getsockname()[1]
    
    server_tcp.listen()
    print(f"Server started on IP address {get_local_ip()}")


    udp_thread = threading.Thread(target=send_broadcast_offers, args=(assigned_port,))
    udp_thread.daemon = True 
    udp_thread.start()

    while True:
        try:
            client_sock, client_addr = server_tcp.accept()
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_sock, client_addr)
            )
            client_thread.start()
        except KeyboardInterrupt:
            print("\nServer stopping...")
            break
        except Exception as e:
            print(f"Error accepting client: {e}")

if __name__ == "__main__":
    start_server()