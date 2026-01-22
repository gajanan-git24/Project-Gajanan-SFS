from flask import Flask, render_template, request, redirect, url_for
import socket
import threading
import subprocess

app = Flask(__name__)

# Data storage
iot_logs = []
blacklist = set()

def iot_security_listener():
    """Background listener for Smart Farm Sensors on Port 9000"""
    server_ip = "127.0.0.1"
    port = 9000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((server_ip, port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    if addr[0] in blacklist:
                        conn.close()
                        continue
                    data = conn.recv(1024).decode()
                    if data:
                        status = "SECURE"
                        try:
                            val = int(data.split(":")[1].replace("%", ""))
                            if val > 95: status = "⚠️ ATTACK (Tampering)"
                        except:
                            status = "INVALID DATA"
                        iot_logs.append({"ip": addr[0], "data": data, "status": status})
                        if len(iot_logs) > 15: iot_logs.pop(0)
        except Exception as e:
            print(f"Socket Error: {e}")

# Start IoT Listener Thread
threading.Thread(target=iot_security_listener, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def home():
    scan_results = None
    target_ip = None
    
    if request.method == 'POST':
        # Handle the Nmap Scan Form
        target_ip = request.form.get('target_ip')
        if target_ip:
            process = subprocess.run(["nmap", "--top-ports", "10", target_ip], capture_output=True, text=True)
            scan_results = [line for line in process.stdout.split('\n') if "open" in line]

    return render_template('index.html', 
                           iot_logs=reversed(iot_logs), 
                           blacklist=list(blacklist), 
                           scan_results=scan_results, 
                           target=target_ip)

@app.route('/block/<ip>')
def block_ip(ip):
    blacklist.add(ip)
    return redirect(url_for('home'))

if __name__ == '__main__':
    # use_reloader=False prevents the 'Address already in use' error
    app.run(debug=True, port=5000, use_reloader=False)
