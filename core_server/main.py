import socket
import threading
import time
import requests
import json

# --- CONFIGURATION ---
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
HOST = '127.0.0.1'  # Localhost
PORT = 5000         # Port to listen on

# --- GLOBAL STATE ---
# We use a dictionary as a shared state between threads.
# Ideally, we would use a Lock(), but for this demo, Python's GIL handles this simple dict assignment safely enough.
latest_data = {
    "bitcoin_price": 0,
    "last_updated": "Never",
    "status": "Initializing"
}

def fetch_crypto_price():
    """
    COMPONENT 1: PUBLIC WEB SERVICE CLIENT
    Runs in a background thread. Polls CoinGecko API every 10 seconds.
    """
    global latest_data
    print(f"[API CLIENT] Started tracking Bitcoin price...")
    
    while True:
        try:
            # REST API Call
            response = requests.get(API_URL, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = data.get('bitcoin', {}).get('usd', 0)
                
                # Update global state
                latest_data["bitcoin_price"] = price
                latest_data["last_updated"] = time.strftime("%H:%M:%S")
                latest_data["status"] = "Live"
                
                print(f"[API CLIENT] Fetched: ${price} at {latest_data['last_updated']}")
            else:
                print(f"[API CLIENT] Error: API returned {response.status_code}")
                
        except Exception as e:
            print(f"[API CLIENT] Connection Failed: {e}")
            latest_data["status"] = "Connection Error"

        # Pause to respect API rate limits (CoinGecko allows ~10-30 calls/min free)
        time.sleep(15)

def handle_client(client_socket, address):
    """
    Handles a single connected client. 
    Sends the latest data immediately, then closes connection (Request-Response pattern).
    Alternatively, we could keep it open for streaming.
    """
    print(f"[SOCKET SERVER] New connection from {address}")
    
    try:
        # Prepare JSON payload
        payload = json.dumps(latest_data)
        
        # Send data (encode to bytes)
        client_socket.send(payload.encode('utf-8'))
        
    except Exception as e:
        print(f"[SOCKET SERVER] Error handling client: {e}")
    finally:
        # Clean up connection
        client_socket.close()

def start_socket_server():
    """
    COMPONENT 2: SOCKET SERVER
    Binds to a port and listens for incoming TCP connections.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow port reuse (prevents "Address already in use" errors on restart)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5) # Backlog of 5 connections
        print(f"[SOCKET SERVER] Listening on {HOST}:{PORT}")
        
        while True:
            # Blocking call - waits for a connection
            client_sock, addr = server.accept()
            
            # Handle client in a new thread so the server doesn't freeze
            client_handler = threading.Thread(target=handle_client, args=(client_sock, addr))
            client_handler.start()
            
    except Exception as e:
        print(f"[SOCKET SERVER] Critical Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    print("--- STARTING CRYPTO SENTINEL CORE ---")
    
    # 1. Start the API Fetcher in a separate thread
    api_thread = threading.Thread(target=fetch_crypto_price, daemon=True)
    api_thread.start()
    
    # 2. Start the Socket Server in the main thread
    start_socket_server()