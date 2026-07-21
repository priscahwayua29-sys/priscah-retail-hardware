import os, sqlite3
from datetime import datetime
from functools import wraps
from collections import defaultdict
from flask import Flask, request, redirect, url_for, flash, session, g, abort, Response, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hardware_store.db')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'priscah-hardware-multicart-2026')
DEPARTMENTS = ['Plumbing', 'Electrical', 'General Construction']
PAYMENT_METHODS = ['Cash', 'M-Pesa', 'Card']

CSS = '''
:root{--bg:#f4f7fb;--panel:#fff;--ink:#172033;--muted:#6d7890;--line:#e6ebf2;--blue:#123c69;--gold:#d6a23a;--green:#0f766e;--red:#b42318;--shadow:0 18px 45px rgba(23,32,51,.08)}*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Arial,sans-serif;background:var(--bg);color:var(--ink)}a{color:inherit}.shell{display:grid;grid-template-columns:280px 1fr;min-height:100vh}.sidebar{background:#0d1b2a;color:white;padding:26px;display:flex;flex-direction:column;gap:28px}.brand{display:flex;align-items:center;gap:12px}.brand-mark{width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,var(--gold),#fff0b3);display:grid;place-items:center;color:#0d1b2a;font-weight:900}.brand span,.userbox span,.topbar p,small{display:block;color:var(--muted);font-size:13px}.sidebar .brand span,.sidebar .userbox span{color:#a8b3c7}.sidebar nav{display:grid;gap:8px}.sidebar nav a{padding:12px 14px;border-radius:12px;text-decoration:none;color:#dfe8f4}.sidebar nav a:hover{background:#152a42}.sidebar strong{float:right;background:var(--gold);color:#111;padding:1px 8px;border-radius:999px}.userbox{margin-top:auto;border-top:1px solid #21344d;padding-top:18px}.userbox a{display:inline-block;margin-top:10px;color:#f5c451}.main{padding:30px}.topbar{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px}.topbar h1{margin:0;font-size:31px;letter-spacing:-.04em}.status-pill{background:#e8f7f4;color:var(--green);border:1px solid #b7e5dc;padding:10px 14px;border-radius:999px;font-weight:700;font-size:13px}.card,.kpi{background:var(--panel);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow);padding:22px}.grid{display:grid;gap:20px}.two{grid-template-columns:1fr 1fr}.cart-grid{grid-template-columns:1.45fr .9fr}.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:20px}.kpi span{text-transform:uppercase;font-size:12px;font-weight:800;color:var(--muted);letter-spacing:.08em}.kpi b{display:block;font-size:30px;margin:8px 0}.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:18px}.toolbar input,.toolbar select,label input,label select{height:44px;border:1px solid var(--line);border-radius:12px;padding:0 12px;background:white}label{display:grid;gap:7px;font-weight:700;margin-bottom:13px}.btn,button{border:0;border-radius:12px;background:#e9eef6;color:var(--ink);padding:11px 15px;font-weight:800;text-decoration:none;cursor:pointer}.primary{background:linear-gradient(135deg,var(--blue),#1c5d99)!important;color:white!important}.ghost{background:white!important;border:1px solid var(--line)}.small,.mini{padding:7px 10px;font-size:12px}.wide{display:block;text-align:center;width:100%;margin-top:12px}table{width:100%;border-collapse:collapse}th{text-align:left;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.06em}td,th{border-bottom:1px solid var(--line);padding:12px 8px;vertical-align:middle}.item-row{display:grid;grid-template-columns:1fr 110px 70px 70px;gap:10px;align-items:center;border-bottom:1px solid var(--line);padding:13px 0}.item-row span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.qty{width:70px;height:36px;border:1px solid var(--line);border-radius:10px;padding:0 8px}.total{display:flex;justify-content:space-between;align-items:center;margin-top:16px;padding-top:16px;border-top:2px solid var(--line)}.total b{font-size:24px}.big b{font-size:34px}.sticky{position:sticky;top:20px;align-self:start}.split{margin-top:18px;background:#f8fafc;border-radius:16px;padding:14px}.split p{display:flex;justify-content:space-between;margin:8px 0}.bars div{margin:14px 0}.bars em{display:block;height:10px;border-radius:999px;background:linear-gradient(90deg,var(--gold),var(--blue));margin-top:8px}.flash{padding:12px 14px;border-radius:13px;margin:8px 0;background:#eef4ff;border:1px solid #c7d7fe}.flash.success{background:#eafaf4;border-color:#b7e5dc}.flash.danger{background:#fff0ed;border-color:#f4b8ae}.danger-text{color:var(--red);font-weight:800}.login-bg{min-height:100vh;display:grid;place-items:center;background:linear-gradient(rgba(5,12,22,.56),rgba(5,12,22,.74)),url('/static/project_reference.jpg') center/cover no-repeat fixed}.login-card{width:min(440px,92vw);background:rgba(255,255,255,.94);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.45);border-radius:28px;padding:32px;box-shadow:0 30px 90px rgba(0,0,0,.28)}.login-card h1{margin:22px 0 6px;font-size:30px}.login-card input{width:100%;height:46px;border:1px solid var(--line);border-radius:12px;padding:0 12px}.audit p{border-bottom:1px solid var(--line);padding-bottom:10px}.inline{display:flex;gap:8px;align-items:center}.inline input:not(.qty){height:36px;border:1px solid var(--line);border-radius:10px;padding:0 8px}.system-photo{width:100%;height:220px;object-fit:cover;border-radius:18px;border:1px solid #e5e7eb;box-shadow:0 14px 34px rgba(23,32,51,.12);margin:0 0 18px}.login-photo{width:100%;height:190px;object-fit:cover;border-radius:20px;margin:0 0 18px;border:1px solid rgba(255,255,255,.35)}.hero-card{overflow:hidden}.hero-card p{margin-top:0}
@media(max-width:900px){.shell,.two,.cart-grid,.kpis{grid-template-columns:1fr}.item-row{grid-template-columns:1fr}.topbar{display:block}}
'''

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    conn = g.pop('db', None)
    if conn: conn.close()

def q(sql, args=(), one=False):
    cur = db().execute(sql, args); rows = cur.fetchall(); cur.close()
    return (rows[0] if rows else None) if one else rows

def ex(sql, args=()):
    cur = db().execute(sql, args); db().commit(); return cur.lastrowid

def user():
    return q('SELECT * FROM users WHERE id=?', (session.get('user_id'),), one=True) if session.get('user_id') else None

def login_required(fn):
    @wraps(fn)
    def wrap(*a, **kw):
        if not user():
            flash('Please log in first.', 'warning'); return redirect(url_for('login'))
        return fn(*a, **kw)
    return wrap

def admin_required(fn):
    @wraps(fn)
    def wrap(*a, **kw):
        u=user()
        if not u: return redirect(url_for('login'))
        if u['role'] != 'Administrator': abort(403)
        return fn(*a, **kw)
    return wrap

def log(action):
    ex('INSERT INTO audit_logs(user_id,action,created_at) VALUES(?,?,?)', (session.get('user_id'), action, datetime.now().isoformat(timespec='seconds')))

def init_db():
    conn=sqlite3.connect(DB_PATH); c=conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password_hash TEXT,full_name TEXT,role TEXT,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,description TEXT);
    CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY AUTOINCREMENT,department_id INTEGER,sku TEXT UNIQUE,name TEXT,unit_price REAL,stock_qty INTEGER,reorder_level INTEGER DEFAULT 5,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,receipt_no TEXT UNIQUE,cashier_id INTEGER,customer_name TEXT,payment_method TEXT,mpesa_ref TEXT,subtotal REAL,amount_paid REAL,change_due REAL,created_at TEXT,status TEXT DEFAULT 'Completed');
    CREATE TABLE IF NOT EXISTS transaction_items(id INTEGER PRIMARY KEY AUTOINCREMENT,transaction_id INTEGER,item_id INTEGER,department_id INTEGER,quantity INTEGER,unit_price REAL,line_total REAL,returned_qty INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS returns(id INTEGER PRIMARY KEY AUTOINCREMENT,transaction_item_id INTEGER,quantity INTEGER,reason TEXT,processed_by INTEGER,created_at TEXT);
    CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,action TEXT,created_at TEXT);
    ''')
    if c.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        c.executemany('INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)', [('admin',generate_password_hash('Admin@2026'),'Store Administrator','Administrator'),('cashier',generate_password_hash('Cashier@2026'),'Main Counter Cashier','Cashier')])
    if c.execute('SELECT COUNT(*) FROM departments').fetchone()[0] == 0:
        c.executemany('INSERT INTO departments(name,description) VALUES(?,?)', [('Plumbing','Pipes, taps, valves, fittings and water accessories'),('Electrical','Bulbs, sockets, switches, cables and electrical fittings'),('General Construction','Cement, nails, tools, timber and site supplies')])
    if c.execute('SELECT COUNT(*) FROM items').fetchone()[0] == 0:
        dep={r[1]:r[0] for r in c.execute('SELECT id,name FROM departments')}
        items=[(dep['Plumbing'],'PL-TAP-001','Chrome Water Tap',850,38,8),(dep['Plumbing'],'PL-PVC-020','PVC Pipe 2 inch',620,72,15),(dep['Plumbing'],'PL-VAL-010','Gate Valve Brass',1450,24,5),(dep['Plumbing'],'PL-SNK-005','Kitchen Sink Trap',780,31,7),(dep['Electrical'],'EL-BULB-012','LED Bulb 12W',220,140,25),(dep['Electrical'],'EL-SWT-001','Single Switch',180,95,20),(dep['Electrical'],'EL-CBL-2.5','Copper Cable 2.5mm',120,300,50),(dep['Electrical'],'EL-SOC-013','Twin Socket Outlet',450,61,12),(dep['General Construction'],'GC-CEM-001','Cement 50kg Bag',880,110,20),(dep['General Construction'],'GC-NAIL-003','Steel Nails 1kg',260,76,15),(dep['General Construction'],'GC-HMR-002','Claw Hammer',950,18,5),(dep['General Construction'],'GC-WHB-001','Wheelbarrow Heavy Duty',7800,9,3)]
        c.executemany('INSERT INTO items(department_id,sku,name,unit_price,stock_qty,reorder_level) VALUES(?,?,?,?,?,?)', items)
    conn.commit(); conn.close()

def cart_rows():
    rows=[]; total=0
    for item_id, qty in session.get('cart', {}).items():
        item=q('SELECT items.*,departments.name department FROM items JOIN departments ON departments.id=items.department_id WHERE items.id=?', (int(item_id),), one=True)
        if item:
            line=item['unit_price']*int(qty); total+=line; rows.append({'item':item,'qty':int(qty),'line_total':line})
    return rows,total

def page(title, subtitle, content):
    u=user(); count=sum(session.get('cart',{}).values())
    nav=''
    if u:
        nav=f'''<nav><a href="{url_for('dashboard')}">Dashboard</a><a href="{url_for('cart')}">Multi-Cart <strong>{count}</strong></a><a href="{url_for('transactions')}">Transactions</a>'''
        if u['role']=='Administrator': nav += f'''<a href="{url_for('inventory')}">Inventory</a><a href="{url_for('reports')}">Reports</a>'''
        nav+='</nav>'
        userbox=f'''<div class="userbox"><b>{u['full_name']}</b><span>{u['role']}</span><a href="{url_for('logout')}">Logout</a></div>'''
    else: userbox=''
    flashes=''.join([f'<div class="flash {cat}">{msg}</div>' for cat,msg in get_flashed_messages(with_categories=True)])
    return render_template_string(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>{CSS}</style></head><body><div class="shell"><aside class="sidebar"><div class="brand"><div class="brand-mark">H</div><div><b>Bungoma Hardware</b><span>Unified Checkout</span></div></div>{nav}{userbox}</aside><main class="main"><header class="topbar"><div><h1>{title}</h1><p>{subtitle}</p></div><div class="status-pill">Silent department revenue attribution active</div></header>{flashes}{content}</main></div></body></html>''')

def get_flashed_messages(with_categories=True):
    from flask import get_flashed_messages as gfm
    return gfm(with_categories=with_categories)

@app.route('/')
def index(): return redirect(url_for('dashboard') if user() else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=q('SELECT * FROM users WHERE username=? AND active=1', (request.form.get('username','').strip(),), one=True)
        if u and check_password_hash(u['password_hash'], request.form.get('password','')):
            session.clear(); session['user_id']=u['id']; session['cart']={}; log(f'{u["username"]} logged in'); return redirect(url_for('dashboard'))
        flash('Invalid username or password.','danger')
    flashes=''.join([f'<div class="flash {cat}">{msg}</div>' for cat,msg in get_flashed_messages(with_categories=True)])
    return render_template_string(f'''<!doctype html><html><head><meta charset="utf-8"><title>Login</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"><style>{CSS}</style></head><body class="login-bg"><div class="login-card"><div class="brand"><div class="brand-mark">H</div><div><b>Bungoma Hardware</b><span>Multi-Cart Sales System</span></div></div><h1>Secure Staff Login</h1><p>One customer payment. Silent department-level accounting.</p>{flashes}<form method="post"><label>Username<input name="username" required autofocus></label><label>Password<input type="password" name="password" required></label><button class="btn primary" type="submit">Login</button></form><small><b>Demo:</b> admin / Admin@2026 · cashier / Cashier@2026</small></div></body></html>''')

@app.route('/logout')
@login_required
def logout(): log('User logged out'); session.clear(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    totals=q('SELECT d.name,COALESCE(SUM(ti.line_total),0) revenue,COALESCE(SUM(ti.quantity),0) units FROM departments d LEFT JOIN transaction_items ti ON ti.department_id=d.id GROUP BY d.id ORDER BY d.name')
    today=datetime.now().date().isoformat(); ts=q('SELECT COALESCE(SUM(subtotal),0) total, COUNT(*) count FROM transactions WHERE substr(created_at,1,10)=?', (today,), one=True)
    low=q('SELECT items.*,departments.name department FROM items JOIN departments ON departments.id=items.department_id WHERE stock_qty<=reorder_level ORDER BY stock_qty')
    recent=q('SELECT t.*,u.full_name cashier FROM transactions t JOIN users u ON u.id=t.cashier_id ORDER BY t.id DESC LIMIT 6')
    bars=''.join([f'<div><span><b>{r["name"]}</b></span><strong style="float:right">KES {r["revenue"]:,.2f}</strong><em style="width:{min(100,r["revenue"]/50000*100)}%"></em></div>' for r in totals])
    recent_rows=''.join([f'<tr><td><a href="{url_for("receipt",tx_id=t["id"])}">{t["receipt_no"]}</a></td><td>{t["cashier"]}</td><td>KES {t["subtotal"]:,.2f}</td></tr>' for t in recent]) or '<tr><td colspan=3>No transactions yet.</td></tr>'
    low_rows=''.join([f'<tr><td>{i["sku"]}</td><td>{i["name"]}</td><td>{i["department"]}</td><td><span class="danger-text">{i["stock_qty"]}</span></td></tr>' for i in low]) or '<tr><td colspan=4>No low stock items.</td></tr>'
    html=f'''<section class="kpis"><div class="kpi"><span>Today Sales</span><b>KES {ts['total']:,.2f}</b><small>{ts['count']} transaction(s)</small></div><div class="kpi"><span>Departments</span><b>{len(totals)}</b><small>Plumbing · Electrical · Construction</small></div><div class="kpi"><span>Low Stock Alerts</span><b>{len(low)}</b><small>Items at reorder level</small></div></section><section class="grid two"><div class="card hero-card"><img class="system-photo" src="/static/project_reference.jpg" alt="Professional hardware store reference"><h2>Professional hardware store reference</h2><p class="sub">Visual reference for Plumbing, Electrical and General Construction retail operations.</p></div><div class="card"><h2>Department Revenue Split</h2><div class="bars">{bars}</div></div><div class="card"><h2>Recent Transactions</h2><table><tr><th>Receipt</th><th>Cashier</th><th>Total</th></tr>{recent_rows}</table></div></section><div class="card"><h2>Stock Reorder Watch</h2><table><tr><th>SKU</th><th>Item</th><th>Department</th><th>Stock</th></tr>{low_rows}</table></div>'''
    return page('Operations Dashboard','Real-time checkout, inventory and departmental performance overview',html)

@app.route('/cart')
@login_required
def cart():
    department=request.args.get('department',''); search=request.args.get('search','').strip(); sql='SELECT items.*,departments.name department FROM items JOIN departments ON departments.id=items.department_id WHERE items.active=1'; args=[]
    if department: sql+=' AND departments.name=?'; args.append(department)
    if search: sql+=' AND (items.name LIKE ? OR items.sku LIKE ?)'; args += [f'%{search}%', f'%{search}%']
    items=q(sql+' ORDER BY departments.name,items.name', args); rows,total=cart_rows()
    opts='<option value="">All Departments</option>'+''.join([f'<option value="{d}" {"selected" if department==d else ""}>{d}</option>' for d in DEPARTMENTS])
    item_html=''.join([f'''<form class="item-row" method="post" action="{url_for('cart_add',item_id=i['id'])}"><div><b>{i['name']}</b><span>{i['sku']} · {i['department']} · Stock {i['stock_qty']}</span></div><strong>KES {i['unit_price']:,.2f}</strong><input type="number" name="qty" min="1" max="{i['stock_qty']}" value="1"><button class="btn small primary">Add</button></form>''' for i in items])
    cart_html=''.join([f'''<tr><td><b>{r['item']['name']}</b><br><small>{r['item']['department']}</small></td><td><form method="post" action="{url_for('cart_update',item_id=r['item']['id'])}"><input class="qty" type="number" name="qty" min="0" value="{r['qty']}"><button class="mini">Update</button></form></td><td>KES {r['line_total']:,.2f}</td></tr>''' for r in rows]) or '<tr><td>Cart is empty.</td></tr>'
    html=f'''<form class="toolbar" method="get"><select name="department">{opts}</select><input name="search" placeholder="Search item or SKU" value="{search}"><button class="btn">Filter</button><a class="btn ghost" href="{url_for('cart')}">Reset</a></form><section class="grid cart-grid"><div class="card"><h2>Available Items</h2>{item_html}</div><div class="card sticky"><h2>Unified Cart</h2><table>{cart_html}</table><div class="total"><span>Total</span><b>KES {total:,.2f}</b></div><a class="btn primary wide" href="{url_for('checkout')}">Proceed to Unified Checkout</a></div></section>'''
    return page('Department & Multi-Cart Dashboard','Add items from Plumbing, Electrical and General Construction into one shared basket',html)

@app.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def cart_add(item_id):
    qty=max(1,int(request.form.get('qty',1))); item=q('SELECT * FROM items WHERE id=?', (item_id,), one=True); cart=dict(session.get('cart',{})); current=int(cart.get(str(item_id),0))
    if current+qty > item['stock_qty']: flash(f'Only {item["stock_qty"]} available for {item["name"]}.','danger')
    else: cart[str(item_id)]=current+qty; session['cart']=cart; flash(f'Added {qty} × {item["name"]} to unified cart.','success')
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def cart_update(item_id):
    qty=int(request.form.get('qty',0)); cart=dict(session.get('cart',{}))
    if qty<=0: cart.pop(str(item_id),None)
    else: cart[str(item_id)]=qty
    session['cart']=cart; return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    rows,total=cart_rows()
    if not rows: flash('The cart is empty.','warning'); return redirect(url_for('cart'))
    split=defaultdict(float)
    for r in rows: split[r['item']['department']] += r['line_total']
    if request.method=='POST':
        paid=float(request.form.get('amount_paid') or 0)
        if paid < total: flash('Amount paid is less than the cart total.','danger')
        else:
            receipt='RCPT-'+datetime.now().strftime('%Y%m%d%H%M%S')
            tx=ex('INSERT INTO transactions(receipt_no,cashier_id,customer_name,payment_method,mpesa_ref,subtotal,amount_paid,change_due,created_at) VALUES(?,?,?,?,?,?,?,?,?)', (receipt,session['user_id'],request.form.get('customer_name','Walk-in Customer') or 'Walk-in Customer',request.form.get('payment_method','Cash'),request.form.get('mpesa_ref') or None,total,paid,paid-total,datetime.now().isoformat(timespec='seconds')))
            for r in rows:
                ex('INSERT INTO transaction_items(transaction_id,item_id,department_id,quantity,unit_price,line_total) VALUES(?,?,?,?,?,?)', (tx,r['item']['id'],r['item']['department_id'],r['qty'],r['item']['unit_price'],r['line_total']))
                ex('UPDATE items SET stock_qty=stock_qty-? WHERE id=?', (r['qty'],r['item']['id']))
            session['cart']={}; log(f'Processed unified checkout {receipt} worth KES {total:,.2f}; revenue silently attributed by department'); flash('Unified checkout completed. One receipt generated and departmental revenue split silently.','success'); return redirect(url_for('receipt',tx_id=tx))
    item_rows=''.join([f'<tr><td>{r["item"]["name"]}</td><td>{r["item"]["department"]}</td><td>{r["qty"]}</td><td>KES {r["line_total"]:,.2f}</td></tr>' for r in rows])
    split_html=''.join([f'<p><span>{k}</span><b>KES {v:,.2f}</b></p>' for k,v in split.items()])
    pay_opts=''.join([f'<option>{p}</option>' for p in PAYMENT_METHODS])
    html=f'''<section class="grid two"><div class="card"><h2>Customer Bill</h2><table><tr><th>Item</th><th>Dept</th><th>Qty</th><th>Total</th></tr>{item_rows}</table><div class="total big"><span>Amount Due</span><b>KES {total:,.2f}</b></div></div><div class="card"><h2>Payment</h2><form method="post"><label>Customer Name<input name="customer_name" placeholder="Walk-in Customer"></label><label>Payment Method<select name="payment_method">{pay_opts}</select></label><label>M-Pesa / Reference<input name="mpesa_ref"></label><label>Amount Paid<input type="number" step="0.01" name="amount_paid" value="{total:.2f}" required></label><button class="btn primary wide">Complete Unified Checkout</button></form><div class="split"><h3>Internal Revenue Split</h3>{split_html}</div></div></section>'''
    return page('Unified Checkout','Collect one payment while the backend attributes revenue to each department',html)

@app.route('/receipt/<int:tx_id>')
@login_required
def receipt(tx_id):
    tx=q('SELECT t.*,u.full_name cashier FROM transactions t JOIN users u ON u.id=t.cashier_id WHERE t.id=?',(tx_id,),one=True); items=q('SELECT ti.*,items.name,items.sku,departments.name department FROM transaction_items ti JOIN items ON items.id=ti.item_id JOIN departments ON departments.id=ti.department_id WHERE ti.transaction_id=?',(tx_id,))
    rows=''.join([f'<tr><td>{i["name"]}<br><small>{i["sku"]}</small></td><td>{i["quantity"]}</td><td>KES {i["unit_price"]:,.2f}</td><td>KES {i["line_total"]:,.2f}</td></tr>' for i in items])
    html=f'''<div class="receipt card"><h2>Bungoma Hardware Store</h2><b>{tx['receipt_no']}</b><p>{tx['created_at']} · Cashier: {tx['cashier']}</p><table><tr><th>Item</th><th>Qty</th><th>Unit</th><th>Total</th></tr>{rows}</table><div class="total big"><span>Total Paid</span><b>KES {tx['subtotal']:,.2f}</b></div><p>Payment: {tx['payment_method']}</p><a class="btn" href="{url_for('returns',tx_id=tx_id)}">Process Return Verification</a> <a class="btn primary" href="{url_for('cart')}">New Sale</a></div>'''
    return page('Single Customer Receipt','One receipt for the customer; departmental split remains internal',html)

@app.route('/transactions')
@login_required
def transactions():
    txs=q('SELECT t.*,u.full_name cashier FROM transactions t JOIN users u ON u.id=t.cashier_id ORDER BY t.id DESC')
    rows=''.join([f'<tr><td>{t["receipt_no"]}</td><td>{t["created_at"]}</td><td>{t["customer_name"]}</td><td>{t["cashier"]}</td><td>KES {t["subtotal"]:,.2f}</td><td><a class="btn small" href="{url_for("receipt",tx_id=t["id"])}">Receipt</a> <a class="btn small ghost" href="{url_for("returns",tx_id=t["id"])}">Return</a></td></tr>' for t in txs]) or '<tr><td colspan=6>No transactions yet.</td></tr>'
    return page('Transactions','Unified receipts with original details for return verification',f'<div class="card"><table><tr><th>Receipt</th><th>Date</th><th>Customer</th><th>Cashier</th><th>Total</th><th></th></tr>{rows}</table></div>')

@app.route('/returns/<int:tx_id>', methods=['GET','POST'])
@login_required
def returns(tx_id):
    tx=q('SELECT * FROM transactions WHERE id=?',(tx_id,),one=True)
    if request.method=='POST':
        ti_id=int(request.form['transaction_item_id']); qty=int(request.form['quantity']); row=q('SELECT * FROM transaction_items WHERE id=?',(ti_id,),one=True)
        if qty<1 or qty>row['quantity']-row['returned_qty']: flash('Invalid return quantity.','danger')
        else:
            ex('INSERT INTO returns(transaction_item_id,quantity,reason,processed_by,created_at) VALUES(?,?,?,?,?)',(ti_id,qty,request.form.get('reason',''),session['user_id'],datetime.now().isoformat(timespec='seconds'))); ex('UPDATE transaction_items SET returned_qty=returned_qty+? WHERE id=?',(qty,ti_id)); ex('UPDATE items SET stock_qty=stock_qty+? WHERE id=?',(qty,row['item_id'])); log(f'Processed return of {qty} item(s) on receipt {tx["receipt_no"]}'); flash('Return verified against original transaction and stock adjusted.','success'); return redirect(url_for('returns',tx_id=tx_id))
    items=q('SELECT ti.*,items.name,items.sku,departments.name department FROM transaction_items ti JOIN items ON items.id=ti.item_id JOIN departments ON departments.id=ti.department_id WHERE ti.transaction_id=?',(tx_id,))
    rows=''.join([f'''<tr><td>{i['name']}</td><td>{i['department']}</td><td>{i['quantity']}</td><td>{i['returned_qty']}</td><td>{f'<form class="inline" method="post"><input type="hidden" name="transaction_item_id" value="{i["id"]}"><input class="qty" type="number" name="quantity" min="1" max="{i["quantity"]-i["returned_qty"]}" value="1"><input name="reason" placeholder="Reason"><button class="btn small">Verify Return</button></form>' if i['quantity']>i['returned_qty'] else 'Fully returned'}</td></tr>''' for i in items])
    return page('Return Verification','Verify original receipt details before stock adjustment',f'<div class="card"><h2>{tx["receipt_no"]}</h2><table><tr><th>Item</th><th>Department</th><th>Sold</th><th>Returned</th><th>Action</th></tr>{rows}</table></div>')

@app.route('/inventory')
@login_required
@admin_required
def inventory():
    items=q('SELECT items.*,departments.name department FROM items JOIN departments ON departments.id=items.department_id WHERE items.active=1 ORDER BY departments.name,items.name')
    dep_opts=''.join([f'<option value="{d}">{d}</option>' for d in DEPARTMENTS])
    rows=''.join([f'''<tr><td>{i["sku"]}</td><td>{i["name"]}</td><td>{i["department"]}</td><td>
<form class="inline" method="post" action="{url_for('inventory_update',item_id=i["id"])}">
<input class="qty" style="width:90px" type="number" step="0.01" name="unit_price" value="{i["unit_price"]:.2f}">
<input class="qty" type="number" name="add_stock" placeholder="+stock" value="0" title="Add to current stock">
<input class="qty" type="number" name="reorder_level" value="{i["reorder_level"]}" title="Reorder level">
<button class="btn small">Save</button>
</form></td><td>{i["stock_qty"]}</td><td>{i["reorder_level"]}</td><td>
<form method="post" action="{url_for('inventory_deactivate',item_id=i["id"])}" onsubmit="return confirm('Remove {i["name"]} from inventory?')"><button class="btn small ghost danger-text">Remove</button></form>
</td></tr>''' for i in items])
    add_form=f'''<div class="card"><h2>Add New Item</h2><form class="grid two" method="post" action="{url_for('inventory_add')}">
<label>SKU<input name="sku" required></label>
<label>Item Name<input name="name" required></label>
<label>Department<select name="department">{dep_opts}</select></label>
<label>Unit Price (KES)<input type="number" step="0.01" name="unit_price" required></label>
<label>Opening Stock<input type="number" name="stock_qty" value="0" required></label>
<label>Reorder Level<input type="number" name="reorder_level" value="5" required></label>
<button class="btn primary wide" type="submit">Add Item</button>
</form></div>'''
    table=f'<div class="card"><table><tr><th>SKU</th><th>Item</th><th>Department</th><th>Price / Restock / Reorder</th><th>Stock</th><th>Reorder</th><th></th></tr>{rows}</table></div>'
    return page('Department Inventory','Administrator can add items, restock, edit prices and remove items',add_form+table)

@app.route('/inventory/add', methods=['POST'])
@login_required
@admin_required
def inventory_add():
    dep=q('SELECT id FROM departments WHERE name=?', (request.form.get('department',''),), one=True)
    if not dep: flash('Choose a valid department.','danger'); return redirect(url_for('inventory'))
    try:
        ex('INSERT INTO items(department_id,sku,name,unit_price,stock_qty,reorder_level) VALUES(?,?,?,?,?,?)',
           (dep['id'], request.form.get('sku','').strip(), request.form.get('name','').strip(),
            float(request.form.get('unit_price') or 0), int(request.form.get('stock_qty') or 0), int(request.form.get('reorder_level') or 5)))
        log(f'Added new item {request.form.get("name","")} ({request.form.get("sku","")})')
        flash('New item added to inventory.','success')
    except sqlite3.IntegrityError:
        flash('That SKU already exists.','danger')
    return redirect(url_for('inventory'))

@app.route('/inventory/update/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def inventory_update(item_id):
    item=q('SELECT * FROM items WHERE id=?', (item_id,), one=True)
    if not item: abort(404)
    price=float(request.form.get('unit_price') or item['unit_price'])
    reorder=int(request.form.get('reorder_level') or item['reorder_level'])
    add_stock=int(request.form.get('add_stock') or 0)
    ex('UPDATE items SET unit_price=?, reorder_level=?, stock_qty=stock_qty+? WHERE id=?', (price, reorder, add_stock, item_id))
    log(f'Updated item {item["name"]}: price KES {price:,.2f}, reorder {reorder}, +{add_stock} stock')
    flash(f'{item["name"]} updated.','success')
    return redirect(url_for('inventory'))

@app.route('/inventory/deactivate/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def inventory_deactivate(item_id):
    item=q('SELECT * FROM items WHERE id=?', (item_id,), one=True)
    if not item: abort(404)
    ex('UPDATE items SET active=0 WHERE id=?', (item_id,))
    log(f'Removed item {item["name"]} from active inventory')
    flash(f'{item["name"]} removed from inventory.','warning')
    return redirect(url_for('inventory'))

@app.route('/reports')
@login_required
@admin_required
def reports():
    dept=q('SELECT d.name,COALESCE(SUM(ti.line_total),0) revenue,COALESCE(SUM(ti.quantity),0) units FROM departments d LEFT JOIN transaction_items ti ON ti.department_id=d.id GROUP BY d.id ORDER BY revenue DESC'); total=sum(r['revenue'] for r in dept); audit=q('SELECT a.*,u.username FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 30')
    rows=''.join([f'<tr><td>{r["name"]}</td><td>{r["units"]}</td><td>KES {r["revenue"]:,.2f}</td></tr>' for r in dept]); logs=''.join([f'<p><b>{a["created_at"]}</b><br><span>{a["username"] or "System"} · {a["action"]}</span></p>' for a in audit])
    html=f'<p><a class="btn ghost" href="{url_for("export_report")}">Export CSV</a></p><section class="grid two"><div class="card"><h2>Department Revenue</h2><table><tr><th>Department</th><th>Units</th><th>Revenue</th></tr>{rows}</table><div class="total"><span>Total Revenue</span><b>KES {total:,.2f}</b></div></div><div class="card"><h2>Audit Log</h2><div class="audit">{logs}</div></div></section>'
    return page('Department Sales Reports','Administrator-only profit and loss tracking from silent backend attribution',html)

@app.route('/reports/export.csv')
@login_required
@admin_required
def export_report():
    dept=q('SELECT d.name,COALESCE(SUM(ti.line_total),0) revenue,COALESCE(SUM(ti.quantity),0) units FROM departments d LEFT JOIN transaction_items ti ON ti.department_id=d.id GROUP BY d.id ORDER BY d.name')
    lines=['Department,Units Sold,Revenue']+[f'{r["name"]},{r["units"]},{r["revenue"]:.2f}' for r in dept]
    return Response('\n'.join(lines), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=department_sales_report.csv'})

# Initialize SQLite when imported by Gunicorn/Render.
init_db()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5051)))
