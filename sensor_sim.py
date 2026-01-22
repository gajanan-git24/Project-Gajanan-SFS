import socket
import time
import random

def start_sensor():
    # This simulates a Smart Irrigation Sensor sending data
    server_ip = "127.0.0.1"
    port = 9000
    
    print("[*] Smart Sensor Online. Sending data...")
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, port))
                # Simulate data: "Moisture: 45%"
                data = f"Moisture: {random.randint(10, 90)}%"
                s.sendall(data.encode())
            time.sleep(5)
        except:
            print("[!] Waiting for Security Gateway...")
            time.sleep(5)

if __name__ == "__main__":
    start_sensor()
