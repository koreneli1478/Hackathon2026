import struct
import consts

MAGIC_COOKIE = consts.MAGIC_COOKIE  
MSG_TYPE_OFFER = consts.MSG_TYPE_OFFER      
MSG_TYPE_REQUEST = consts.MSG_TYPE_REQUEST     
MSG_TYPE_PAYLOAD = consts.MSG_TYPE_PAYLOAD     

OFFER_FORMAT = consts.OFFER_FORMAT
REQUEST_FORMAT = consts.REQUEST_FORMAT
CLIENT_PAYLOAD_FORMAT = consts.CLIENT_PAYLOAD_FORMAT
SERVER_PAYLOAD_FORMAT = consts.SERVER_PAYLOAD_FORMAT  

def pack_offer(server_port, server_name):
    server_name_bytes = server_name.encode('utf-8')
    if len(server_name_bytes) > 32:
        server_name_bytes = server_name_bytes[:32]  
    return struct.pack(OFFER_FORMAT, MAGIC_COOKIE, MSG_TYPE_OFFER, server_port, server_name_bytes)

def unpack_offer(data):
    try:
        cookie, msg_type, port, name = struct.unpack(OFFER_FORMAT, data)
        if cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_OFFER:
            return None
        return port, name.decode('utf-8').rstrip('\x00')
    except:
        return None

def pack_request(rounds, team_name):
    team_name_bytes = team_name.encode('utf-8')
    if len(team_name_bytes) > 32:
        team_name_bytes = team_name_bytes[:32]  
    return struct.pack(REQUEST_FORMAT, MAGIC_COOKIE, MSG_TYPE_REQUEST, rounds, team_name_bytes)

def unpack_request(data):
    try:
        if len(data) < 38: return None
        cookie, msg_type, rounds, name = struct.unpack(REQUEST_FORMAT, data)
        if cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_REQUEST:
            return None
        return rounds, name.decode('utf-8').rstrip('\x00')
    except:
        return None
    
def pack_client_payload(decision):
    decision_bytes = decision.encode('utf-8')
    return struct.pack(CLIENT_PAYLOAD_FORMAT, MAGIC_COOKIE, MSG_TYPE_PAYLOAD, decision_bytes)

def unpack_client_payload(data):
    try:
        cookie, msg_type, decision = struct.unpack(CLIENT_PAYLOAD_FORMAT, data)
        if cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_PAYLOAD:
            return None
        return decision.decode('utf-8').rstrip('\x00')
    except:
        return None
    
def pack_server_payload(result_code, card_rank, card_suit):
    return struct.pack(SERVER_PAYLOAD_FORMAT, MAGIC_COOKIE, MSG_TYPE_PAYLOAD, result_code, card_rank, card_suit)

def unpack_server_payload(data):
    try:
        cookie, msg_type, result, rank, suit = struct.unpack(SERVER_PAYLOAD_FORMAT, data)
        if cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_PAYLOAD:
            return None
        return result, rank, suit
    except:
        return None