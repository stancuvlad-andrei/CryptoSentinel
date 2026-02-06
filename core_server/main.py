import socket
import threading
import time
import requests
import json
import sys

# --- CONFIGURATION ---
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
CLOUD_AUDIT_URL = "https://crypto-sentinel-audit.onrender.com/audit"
HOST = '127.0.0.1' 
PORT = 5000         

latest_data = {
    "bitcoin_price": 0,
    "last_updated": "Never",
    "status": "Initializing"
}

# Control flag to stop threads safely
running = True

def fetch_crypto_price():
    global latest_data, running
    print(f"[API CLIENT] Started tracking Bitcoin price...")
    
    while running:
        try:
            response = requests.get(API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get('bitcoin', {}).get('usd', 0)
                
                # Update global state
                latest_data["bitcoin_price"] = price
                latest_data["last_updated"] = time.strftime("%H:%M:%S")
                latest_data["status"] = "Live"
                print(f"[API CLIENT] Fetched: ${price} at {latest_data['last_updated']}")
                
                def send_audit(p):
                    try:
                        requests.post(CLOUD_AUDIT_URL, json={"price": p}, timeout=3)
                        print(f"[CLOUD UPLOAD] Audit sent to {CLOUD_AUDIT_URL}")
                    except Exception as err:
                        print(f"[CLOUD UPLOAD] Warning - Failed: {err}")
                        
                audit_thread = threading.Thread(target=send_audit, args=(price,))
                audit_thread.start()
            else:
                print(f"[API CLIENT] Error: API returned {response.status_code}")
        except Exception as e:
            print(f"[API CLIENT] Connection Failed: {e}")
            latest_data["status"] = "Connection Error"

        # Sleep in small chunks to allow faster shutdown
        for _ in range(15):
            if not running: break
            time.sleep(1)

def handle_client(client_socket, address):
    print(f"[SOCKET SERVER] New connection from {address}")
    try:
        payload = json.dumps(latest_data)
        client_socket.send(payload.encode('utf-8'))
    except Exception as e:
        print(f"[SOCKET SERVER] Error handling client: {e}")
    finally:
        client_socket.close()

def start_socket_server():
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        server.settimeout(1.0) 
        
        print(f"[SOCKET SERVER] Listening on {HOST}:{PORT} (Press Ctrl+C to stop)")
        
        while running:
            try:
                # Waits 1 second for connection. If none, raises socket.timeout
                client_sock, addr = server.accept()
                
                # Handle client
                client_handler = threading.Thread(target=handle_client, args=(client_sock, addr))
                client_handler.start()
            
            except socket.timeout:
                continue
                
            except Exception as e:
                print(f"[SOCKET SERVER] Error: {e}")
                
    except Exception as e:
        print(f"[SOCKET SERVER] Critical Error: {e}")
    finally:
        server.close()
        print("[SOCKET SERVER] Socket closed.")

if __name__ == "__main__":
    print("--- STARTING CRYPTO SENTINEL CORE ---")
    
    api_thread = threading.Thread(target=fetch_crypto_price, daemon=True)
    api_thread.start()
    
    try:
        start_socket_server()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutdown signal received. Stopping threads...")
        running = False
        time.sleep(1) 
        print("[SYSTEM] System stopped cleanly.")
        sys.exit(0)