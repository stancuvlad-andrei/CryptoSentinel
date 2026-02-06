import socket
import json
import time
import os
import sys

# --- CONFIGURATION ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_crypto_data():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        data = sock.recv(1024)
        sock.close()
        
        return json.loads(data.decode('utf-8'))
        
    except ConnectionRefusedError:
        return None
    except Exception as e:
        return {"error": str(e)}

def draw_dashboard(data):
    clear_screen()
    print("="*40)
    print("   CRYPTO SENTINEL - LIVE MONITORING")
    print("="*40)
    print(f" Connecting to: {SERVER_HOST}:{SERVER_PORT}")
    print("-" * 40)
    
    if data is None:
        print("\n [!] STATUS: OFFLINE")
        print("     Could not connect to Core Server.")
        print("     Is main.py running?")
        
    elif "error" in data:
        print(f"\n [!] ERROR: {data['error']}")
        
    else:
        price = data.get("bitcoin_price", 0)
        status = data.get("status", "Unknown")
        last_up = data.get("last_updated", "N/A")
        
        # Simulate simple analytics
        alert = "NORMAL"
        if price < 40000: alert = "LOW (Buy Opportunity)"
        if price > 90000: alert = "HIGH (Sell Opportunity)"
        
        print(f"\n  BTC PRICE (USD):  ${price:,}")
        print(f"  LAST UPDATE:      {last_up}")
        print(f"  SYSTEM STATUS:    {status}")
        print("-" * 40)
        print(f"  RECOMMENDATION:   {alert}")
        
    print("="*40)
    print(" Press Ctrl+C to exit")

if __name__ == "__main__":
    print("Starting Client Dashboard...")
    try:
        while True:
            data = get_crypto_data()
            draw_dashboard(data)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)