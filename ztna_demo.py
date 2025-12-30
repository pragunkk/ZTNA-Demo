from flask import Flask, request, render_template_string, session, redirect, url_for
import functools
import time

app = Flask(__name__)
app.secret_key = 'chainproof_demo_secret'

# --- 1. MOCK DATABASE (IDENTITY SOURCE) ---
# In ZTNA, Identity is just one pillar. We also need Context.
USERS = {
    'trader': {'role': 'broker', 'name': 'Rahul (Broker)'},
    'admin': {'role': 'admin', 'name': 'Priya (Exchange Admin)'},
    'guest': {'role': 'observer', 'name': 'Guest User'}
}

# --- 2. THE POLICY ENGINE (THE BRAIN OF ZTNA) ---
# This function represents the "Always Verify" principle. 
# It runs on EVERY request to sensitive segments.
def evaluate_policy(user_role, resource_sensitivity, device_trust, network_trust):
    """
    Returns True if access is allowed, False otherwise.
    
    Policies:
    1. 'Public' resources: Open to anyone logged in.
    2. 'Sensitive' (Trades): Requires BROKER or ADMIN role + TRUSTED DEVICE.
    3. 'Critical' (Admin Panel): Requires ADMIN role + CORPORATE VPN + TRUSTED DEVICE.
    """
    
    # Rule 1: Always deny if not logged in (handled by decorator below)
    
    # Rule 2: Micro-Segmentation Logic
    if resource_sensitivity == 'low':
        return True # Access granted to authenticated users
        
    if resource_sensitivity == 'medium': # e.g., Executing Trades
        if user_role in ['broker', 'admin'] and device_trust:
            return True
        return False
        
    if resource_sensitivity == 'high': # e.g., Updating Exchange Core
        if user_role == 'admin' and device_trust and network_trust:
            return True
        return False
        
    return False

# --- 3. THE PEP (POLICY ENFORCEMENT POINT) ---
# This decorator acts as the "Gateway" mentioned in your PDF.
def zero_trust_guard(sensitivity='low'):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # 1. Identity Check
            if 'user' not in session:
                return redirect(url_for('login'))
            
            user_role = USERS[session['user']]['role']
            
            # 2. Context Extraction (Simulated via Simulation Panel inputs)
            # In real life, these come from mTLS certs or device headers.
            device_trusted = session.get('sim_device_trusted', False)
            network_secure = session.get('sim_network_vpn', False)
            
            # 3. Policy Evaluation
            allowed = evaluate_policy(user_role, sensitivity, device_trusted, network_secure)
            
            if not allowed:
                return render_template_string(ACCESS_DENIED_TEMPLATE, 
                                            reason=f"Policy Violation for {sensitivity.upper()} Zone",
                                            user=user_role,
                                            device=device_trusted,
                                            network=network_secure)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# --- 4. ROUTES & ZONES ---

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username in USERS:
        session['user'] = username
        # Default simulation state
        session['sim_device_trusted'] = False 
        session['sim_network_vpn'] = False
        return redirect(url_for('dashboard'))
    return "Invalid user. Try 'trader', 'admin', or 'guest'."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/toggle_context')
def toggle_context():
    # Helper to flip simulation switches
    setting = request.args.get('setting')
    if setting == 'device':
        session['sim_device_trusted'] = not session.get('sim_device_trusted', False)
    elif setting == 'network':
        session['sim_network_vpn'] = not session.get('sim_network_vpn', False)
    return redirect(url_for('dashboard'))

# --- SEGMENT 1: GENERAL DASHBOARD (The Landing Zone) ---
@app.route('/dashboard')
@zero_trust_guard(sensitivity='low') # Least privilege: Basic access
def dashboard():
    user = USERS[session['user']]
    return render_template_string(DASHBOARD_TEMPLATE, 
                                  user=user, 
                                  device=session.get('sim_device_trusted'),
                                  network=session.get('sim_network_vpn'))

# --- SEGMENT 2: TRADING FLOOR (Micro-Segment: Medium Security) ---
@app.route('/trade')
@zero_trust_guard(sensitivity='medium') 
def trade_floor():
    return render_template_string(SUCCESS_TEMPLATE, zone="Active Trading Floor")

# --- SEGMENT 3: EXCHANGE CORE (Micro-Segment: High Security) ---
@app.route('/admin')
@zero_trust_guard(sensitivity='high')
def admin_panel():
    return render_template_string(SUCCESS_TEMPLATE, zone="Exchange Admin Core")

# --- 5. HTML TEMPLATES (Embedded for simplicity) ---

CSS = """
<style>
    body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; text-align: center; padding: 50px; }
    .card { background: #1e293b; max-width: 600px; margin: auto; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
    .btn { padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }
    .btn-green { background: #10b981; color: white; }
    .btn-red { background: #ef4444; color: white; }
    .btn-blue { background: #3b82f6; color: white; }
    .status-box { border: 1px dashed #64748b; padding: 15px; margin: 20px 0; border-radius: 5px; }
    .denied { color: #ef4444; font-size: 1.5em; font-weight: bold; }
    .granted { color: #10b981; font-size: 1.5em; font-weight: bold; }
    table { margin: auto; text-align: left; }
    td { padding: 5px 10px; }
</style>
"""

LOGIN_TEMPLATE = CSS + """
<div class="card">
    <h2>ChainProof Portal Login</h2>
    <form action="/login" method="post">
        <input type="text" name="username" placeholder="Enter user (trader/admin/guest)" style="padding: 10px; width: 60%;">
        <button type="submit" class="btn btn-blue">Login</button>
    </form>
    <p><small>Hint: Try 'trader', 'admin', or 'guest'</small></p>
</div>
"""

DASHBOARD_TEMPLATE = CSS + """
<div class="card">
    <h2>User Dashboard: {{ user.name }}</h2>
    <p>Welcome to the secure gateway. Select a resource to access.</p>
    
    <div class="status-box">
        <h3>🛡️ ZTNA Context Simulator</h3>
        <p>Zero Trust verifies CONTEXT, not just passwords. Toggle your status below:</p>
        <table>
            <tr>
                <td>Device Status:</td>
                <td>
                    {% if device %} <span style="color:#10b981">✅ Verified Corp Laptop</span> 
                    {% else %} <span style="color:#ef4444">❌ Unknown Personal Device</span> {% endif %}
                </td>
                <td><a href="/toggle_context?setting=device" class="btn btn-blue">Toggle</a></td>
            </tr>
            <tr>
                <td>Network:</td>
                <td>
                    {% if network %} <span style="color:#10b981">✅ Secure VPN Tunnel</span> 
                    {% else %} <span style="color:#ef4444">❌ Public WiFi</span> {% endif %}
                </td>
                <td><a href="/toggle_context?setting=network" class="btn btn-blue">Toggle</a></td>
            </tr>
        </table>
    </div>

    <h3>Available Segments (Micro-Segmentation)</h3>
    <a href="/trade" class="btn btn-green">💰 Access Trading Floor</a>
    <a href="/admin" class="btn btn-red">⚡ Access Admin Core</a>
    <br><br>
    <a href="/logout" style="color: #94a3b8;">Logout</a>
</div>
"""

ACCESS_DENIED_TEMPLATE = CSS + """
<div class="card" style="border-color: #ef4444;">
    <div class="denied">⛔ ACCESS DENIED</div>
    <h3>Zero Trust Policy Violation</h3>
    <p>{{ reason }}</p>
    <div style="text-align:left; background: #000; padding: 15px; border-radius: 5px; font-family: monospace;">
        > Evaluating Policy...<br>
        > User Role: {{ user }}<br>
        > Device Verified: {{ device }} <br>
        > Network Secure: {{ network }} <br>
        > <b>DECISION: BLOCK</b>
    </div>
    <br>
    <a href="/dashboard" class="btn btn-blue">Back to Dashboard</a>
</div>
"""

SUCCESS_TEMPLATE = CSS + """
<div class="card" style="border-color: #10b981;">
    <div class="granted">🔓 ACCESS GRANTED</div>
    <h3>Welcome to the {{ zone }}</h3>
    <p>Your identity and context have been verified.</p>
    <br>
    <a href="/dashboard" class="btn btn-blue">Back to Dashboard</a>
</div>
"""

if __name__ == '__main__':
    print("ChainProof ZTNA Demo running on http://127.0.0.1:5000")
    app.run(debug=True)