import tkinter as tk
from tkinter import ttk
import socket
import json
import threading

# --- CONFIGURATION ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
REFRESH_RATE = 2000  # Milliseconds (2 seconds)

class CryptoWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoSentinel")
        self.root.geometry("400x250")
        self.root.configure(bg="#1e1e1e")
        
        # --- UI ELEMENTS ---
        
        # Title
        self.lbl_title = tk.Label(root, text="BITCOIN TRACKER", font=("Helvetica", 12, "bold"), bg="#1e1e1e", fg="#888888")
        self.lbl_title.pack(pady=(20, 5))
        
        # Price Display
        self.lbl_price = tk.Label(root, text="$ ---,---", font=("Courier New", 36, "bold"), bg="#1e1e1e", fg="#ffffff")
        self.lbl_price.pack(pady=10)
        
        # Status / Timestamp
        self.lbl_status = tk.Label(root, text="Connecting...", font=("Helvetica", 10), bg="#1e1e1e", fg="#bbbbbb")
        self.lbl_status.pack(pady=5)
        
        # Recommendation
        self.lbl_rec = tk.Label(root, text="WAITING FOR DATA", font=("Helvetica", 10, "bold"), bg="#333333", fg="white", padx=10, pady=5)
        self.lbl_rec.pack(pady=20)

        self.update_data()

    def get_socket_data(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5) # Don't freeze GUI if server is slow
            sock.connect((SERVER_HOST, SERVER_PORT))
            data = sock.recv(1024)
            sock.close()
            return json.loads(data.decode('utf-8'))
        except:
            return None

    def update_data(self):
        data = self.get_socket_data()
        
        if data:
            price = data.get("bitcoin_price", 0)
            last_up = data.get("last_updated", "N/A")
            
            # Update Price
            self.lbl_price.config(text=f"${price:,}", fg="#00ff00")
            
            # Update Status
            self.lbl_status.config(text=f"Last Updated: {last_up}")
            
            if price > 0:
                self.lbl_rec.config(text="● SYSTEM LIVE", bg="#004d00", fg="#00ff00")
            
        else:
            self.lbl_price.config(text="OFFLINE", fg="#ff3333")
            self.lbl_status.config(text="Cannot connect to Core Server")
            self.lbl_rec.config(text="● DISCONNECTED", bg="#4d0000", fg="#ff3333")

        self.root.after(REFRESH_RATE, self.update_data)

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = CryptoWidget(root)
    root.mainloop()