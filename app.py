from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import secrets
import json
import urllib.request
import urllib.parse
import os
import ipaddress
from pathlib import Path
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'orbitra.db'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'orbitra-demo-local-secret-change-in-production')
TRADE_DURATION_SECONDS = 10
MARKET_CACHE = {}

COUNTRIES_ES = [
    'Afganistán','Albania','Alemania','Andorra','Angola','Antigua y Barbuda','Arabia Saudita','Argelia','Argentina','Armenia','Australia','Austria','Azerbaiyán',
    'Bahamas','Bangladés','Barbados','Baréin','Bélgica','Belice','Benín','Bielorrusia','Birmania (Myanmar)','Bolivia','Bosnia y Herzegovina','Botsuana','Brasil','Brunéi','Bulgaria','Burkina Faso','Burundi','Bután',
    'Cabo Verde','Camboya','Camerún','Canadá','Catar','Chad','Chile','China','Chipre','Ciudad del Vaticano','Colombia','Comoras','Corea del Norte','Corea del Sur','Costa de Marfil','Costa Rica','Croacia','Cuba',
    'Dinamarca','Dominica','Ecuador','Egipto','El Salvador','Emiratos Árabes Unidos','Eritrea','Eslovaquia','Eslovenia','España','Estados Unidos','Estonia','Esuatini','Etiopía',
    'Filipinas','Finlandia','Fiyi','Francia','Gabón','Gambia','Georgia','Ghana','Granada','Grecia','Guatemala','Guinea','Guinea-Bisáu','Guinea Ecuatorial','Guyana',
    'Haití','Honduras','Hungría','India','Indonesia','Irak','Irán','Irlanda','Islandia','Islas Marshall','Islas Salomón','Israel','Italia','Jamaica','Japón','Jordania',
    'Kazajistán','Kenia','Kirguistán','Kiribati','Kuwait','Laos','Lesoto','Letonia','Líbano','Liberia','Libia','Liechtenstein','Lituania','Luxemburgo',
    'Macedonia del Norte','Madagascar','Malasia','Malaui','Maldivas','Malí','Malta','Marruecos','Mauricio','Mauritania','México','Micronesia','Moldavia','Mónaco','Mongolia','Montenegro','Mozambique','Namibia','Nauru','Nepal','Nicaragua','Níger','Nigeria','Noruega','Nueva Zelanda',
    'Omán','Países Bajos','Pakistán','Palaos','Palestina','Panamá','Papúa Nueva Guinea','Paraguay','Perú','Polonia','Portugal','Puerto Rico','Reino Unido','República Centroafricana','República Checa','República del Congo','República Democrática del Congo','República Dominicana','Ruanda','Rumanía','Rusia',
    'Samoa','San Cristóbal y Nieves','San Marino','San Vicente y las Granadinas','Santa Lucía','Santo Tomé y Príncipe','Senegal','Serbia','Seychelles','Sierra Leona','Singapur','Siria','Somalia','Sri Lanka','Sudáfrica','Sudán','Sudán del Sur','Suecia','Suiza','Surinam',
    'Tailandia','Tanzania','Tayikistán','Timor Oriental','Togo','Tonga','Trinidad y Tobago','Túnez','Turkmenistán','Turquía','Tuvalu','Ucrania','Uganda','Uruguay','Uzbekistán','Vanuatu','Venezuela','Vietnam','Yemen','Yibuti','Zambia','Zimbabue'
]

MARKETS = {
    'BTCUSDT': {'name': 'Bitcoin', 'coinbase': 'BTC-USD'},
    'ETHUSDT': {'name': 'Ethereum', 'coinbase': 'ETH-USD'},
    'SOLUSDT': {'name': 'Solana', 'coinbase': 'SOL-USD'},
    'XRPUSDT': {'name': 'XRP', 'coinbase': 'XRP-USD'},
    'BNBUSDT': {'name': 'BNB', 'coinbase': None},
    'DOGEUSDT': {'name': 'Dogecoin', 'coinbase': 'DOGE-USD'},
    'ADAUSDT': {'name': 'Cardano', 'coinbase': 'ADA-USD'},
    'AVAXUSDT': {'name': 'Avalanche', 'coinbase': 'AVAX-USD'},
    'TRXUSDT': {'name': 'TRON', 'coinbase': None},
    'LINKUSDT': {'name': 'Chainlink', 'coinbase': 'LINK-USD'},
    'LTCUSDT': {'name': 'Litecoin', 'coinbase': 'LTC-USD'},
    'DOTUSDT': {'name': 'Polkadot', 'coinbase': None},
    'BCHUSDT': {'name': 'Bitcoin Cash', 'coinbase': 'BCH-USD'},
    'TONUSDT': {'name': 'Toncoin', 'coinbase': None},
}
ALLOWED_INTERVALS = {'1m':'1m','5m':'5m','15m':'15m','1h':'1h','4h':'4h','1d':'1d'}
COINBASE_GRANULARITY = {'1m':60,'5m':300,'15m':900,'1h':3600,'4h':21600,'1d':86400}


LANG_COUNTRY_GROUPS = {
    'es': {'ES','MX','AR','CO','CL','PE','VE','EC','GT','CU','BO','DO','HN','PY','SV','NI','CR','PA','UY','GQ','PR'},
    'pt': {'PT','BR','AO','MZ','CV','GW','ST','TL'},
    'fr': {'FR','BE','CH','CA','SN','CI','CM','ML','NE','BF','BJ','TG','GA','CG','CD','GN','MG','RW','BI','DJ','KM','CF','TD','MU','SC'},
    'ar': {'SA','AE','QA','KW','BH','OM','EG','MA','DZ','TN','LY','JO','LB','IQ','SY','YE','SD','PS'},
    'ru': {'RU','BY','KZ','KG'},
}

def language_for_country(code):
    code = (code or '').upper()
    for lang, codes in LANG_COUNTRY_GROUPS.items():
        if code in codes:
            return lang
    return 'en'

def request_client_ip():
    forwarded = request.headers.get('X-Forwarded-For','').split(',')[0].strip()
    candidate = forwarded or request.remote_addr or ''
    try:
        ip = ipaddress.ip_address(candidate)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return ''
        return candidate
    except ValueError:
        return ''

def browser_language():
    raw = (request.headers.get('Accept-Language') or '').lower()
    for lang in ('es','pt','fr','ar','ru','en'):
        if raw.startswith(lang) or f',{lang}' in raw or f';{lang}' in raw:
            return lang
    return 'en'


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_public_id(conn):
    while True:
        public_id = f"ORB-{secrets.randbelow(100_000_000):08d}"
        exists = conn.execute('SELECT 1 FROM users WHERE public_id=?', (public_id,)).fetchone()
        if not exists:
            return public_id


def init_db():
    conn = db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        public_id TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        country TEXT,
        demo_balance REAL NOT NULL DEFAULT 1000,
        password_hash TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS demo_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        entry_price REAL NOT NULL,
        exit_price REAL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    cols = {r['name'] for r in conn.execute('PRAGMA table_info(users)').fetchall()}
    for col, definition in [('public_id','TEXT'),('first_name','TEXT'),('last_name','TEXT'),('country','TEXT'),('demo_balance','REAL NOT NULL DEFAULT 1000'),('password_hash','TEXT')]:
        if col not in cols:
            conn.execute(f'ALTER TABLE users ADD COLUMN {col} {definition}')
    rows = conn.execute('SELECT id, public_id, first_name, last_name FROM users').fetchall()
    for row in rows:
        if not row['public_id']:
            conn.execute('UPDATE users SET public_id=? WHERE id=?', (generate_public_id(conn), row['id']))
        if not row['first_name']:
            conn.execute('UPDATE users SET first_name=? WHERE id=?', ('Usuario', row['id']))
        if not row['last_name']:
            conn.execute('UPDATE users SET last_name=? WHERE id=?', ('Orbitra', row['id']))
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_public_id ON users(public_id)')
    conn.commit(); conn.close()


def current_user():
    uid = session.get('user_id')
    if not uid: return None
    conn = db()
    user = conn.execute('SELECT id, public_id, first_name, last_name, country, demo_balance, password_hash FROM users WHERE id=?',(uid,)).fetchone()
    conn.close(); return user


def http_json(url, timeout=7):
    req = urllib.request.Request(url, headers={'User-Agent':'OrbitraDemo/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def binance_candles(symbol, interval, limit=120):
    q = urllib.parse.urlencode({'symbol':symbol,'interval':interval,'limit':limit})
    data = http_json('https://api.binance.com/api/v3/klines?' + q)
    candles = []
    for x in data:
        candles.append({'t':int(x[0]),'o':float(x[1]),'h':float(x[2]),'l':float(x[3]),'c':float(x[4]),'v':float(x[5])})
    return candles, 'Binance'


def coinbase_candles(symbol, interval):
    product = MARKETS[symbol].get('coinbase')
    if not product: raise RuntimeError('No fallback provider')
    gran = COINBASE_GRANULARITY[interval]
    data = http_json(f'https://api.exchange.coinbase.com/products/{product}/candles?granularity={gran}')
    # Coinbase: [time, low, high, open, close, volume]
    data = sorted(data, key=lambda x: x[0])[-120:]
    candles = [{'t':int(x[0])*1000,'o':float(x[3]),'h':float(x[2]),'l':float(x[1]),'c':float(x[4]),'v':float(x[5])} for x in data]
    return candles, 'Coinbase (USD)'


def fetch_candles(symbol, interval):
    try: return binance_candles(symbol, interval)
    except Exception:
        return coinbase_candles(symbol, interval)


def coinbase_ticker(symbol):
    product = MARKETS[symbol].get('coinbase')
    if not product:
        raise RuntimeError('No fallback provider')
    ticker = http_json(f'https://api.exchange.coinbase.com/products/{product}/ticker', timeout=4)
    stats = http_json(f'https://api.exchange.coinbase.com/products/{product}/stats', timeout=4)
    price = float(ticker.get('price') or stats.get('last') or 0)
    high = float(stats.get('high') or price)
    low = float(stats.get('low') or price)
    opened = float(stats.get('open') or price)
    change = ((price - opened) / opened * 100) if opened else 0.0
    return {
        'price': price,
        'high': high,
        'low': low,
        'change': change,
        'source': 'Coinbase (USD)'
    }


def fetch_ticker(symbol):
    now = datetime.now(timezone.utc).timestamp()
    cached = MARKET_CACHE.get(symbol)
    if cached and now - cached['ts'] < 0.8:
        return cached['data']
    try:
        q = urllib.parse.urlencode({'symbol':symbol})
        d = http_json('https://api.binance.com/api/v3/ticker/24hr?' + q, timeout=4)
        data = {'price':float(d['lastPrice']),'high':float(d['highPrice']),'low':float(d['lowPrice']),'change':float(d['priceChangePercent']),'source':'Binance'}
    except Exception:
        data = coinbase_ticker(symbol)
    MARKET_CACHE[symbol] = {'ts': now, 'data': data}
    return data

def parse_utc(value):
    if not value:
        return datetime.now(timezone.utc)
    text = str(value).replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            dt = datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def seconds_left(opened_at):
    elapsed = (datetime.now(timezone.utc) - parse_utc(opened_at)).total_seconds()
    return max(0.0, TRADE_DURATION_SECONDS - elapsed)

DEMO_PAYOUT_RATE = 1.0

def training_result(trade, exit_price):
    """Settle a 10-second demo position from entry/exit direction.

    Stake is reserved when the trade opens. If the selected direction is
    correct, the stake is returned plus a 100% demo profit. If it is wrong,
    the reserved stake is lost. A flat quote returns the stake.
    """
    entry = float(trade['entry_price'])
    exit_price = float(exit_price)
    stake = entry * float(trade['quantity'])
    if exit_price > entry:
        market_direction = 'UP'
    elif exit_price < entry:
        market_direction = 'DOWN'
    else:
        market_direction = 'FLAT'
    side = str(trade['side']).upper()
    if market_direction == 'FLAT':
        result = 'PUSH'
        profit = 0.0
        settlement = stake
    else:
        won = (side == 'BUY' and market_direction == 'UP') or (side == 'SELL' and market_direction == 'DOWN')
        if won:
            result = 'WIN'
            profit = stake * DEMO_PAYOUT_RATE
            settlement = stake + profit
        else:
            result = 'LOSS'
            profit = -stake
            settlement = 0.0
    return {
        'result': result,
        'market_direction': market_direction,
        'profit': profit,
        'stake': stake,
        'settlement': settlement,
    }


def guest_demo_state():
    # v2 resets older guest sessions to the new $1,000 training balance once.
    if session.get('guest_demo_version') != 3:
        session['guest_demo_version'] = 3
        session['guest_demo_balance'] = 1000.0
        session['guest_demo_trades'] = []
        session.modified = True
    if 'guest_demo_balance' not in session:
        session['guest_demo_balance'] = 1000.0
    if 'guest_demo_trades' not in session:
        session['guest_demo_trades'] = []
    return float(session['guest_demo_balance']), list(session['guest_demo_trades'])


def save_guest_demo(balance, trades):
    session['guest_demo_balance'] = round(float(balance), 8)
    session['guest_demo_trades'] = trades[-40:]
    session.modified = True


@app.context_processor
def inject_user():
    return {'user':current_user(),'countries_es':COUNTRIES_ES}

@app.route('/')
def index():
    guest_demo_state()
    just_registered_id = session.pop('just_registered_id','')
    return render_template('index.html', just_registered_id=just_registered_id)

@app.post('/register')
def register():
    first_name=request.form.get('first_name','').strip(); last_name=request.form.get('last_name','').strip(); country=request.form.get('country','').strip()
    if len(first_name)<2 or len(last_name)<2:
        flash('Introduce tu nombre y apellido.','error'); return redirect(url_for('index')+'#register')
    if country not in COUNTRIES_ES:
        flash('Selecciona tu país de la lista.','error'); return redirect(url_for('index')+'#register')
    conn=db(); public_id=generate_public_id(conn)
    cur=conn.execute('INSERT INTO users(public_id,first_name,last_name,country,demo_balance) VALUES(?,?,?,?,1000)',(public_id,first_name,last_name,country)); user_id=cur.lastrowid
    conn.commit(); conn.close()
    # Guest training positions/history intentionally do not migrate into a real profile.
    session.pop('guest_demo_balance',None); session.pop('guest_demo_trades',None)
    session['guest_demo_version']=3
    session['user_id']=user_id; session['just_registered_id']=public_id
    return redirect(url_for('index')+'#registered')

@app.post('/login')
def login():
    public_id=request.form.get('public_id','').strip().upper(); first_name=request.form.get('first_name','').strip(); last_name=request.form.get('last_name','').strip(); password=request.form.get('password','')
    conn=db(); user=conn.execute('''SELECT * FROM users WHERE UPPER(public_id)=UPPER(?) AND LOWER(first_name)=LOWER(?) AND LOWER(last_name)=LOWER(?)''',(public_id,first_name,last_name)).fetchone(); conn.close()
    if not user or (user['password_hash'] and not check_password_hash(user['password_hash'], password)):
        flash('Datos de acceso incorrectos.','error'); return redirect(url_for('index')+'#login')
    session['user_id']=user['id']; flash('Sesión iniciada.','success'); return redirect(url_for('index')+'#profile')

@app.post('/set-password')
def set_password():
    user=current_user()
    if not user:
        flash('Primero inicia sesión.','error'); return redirect(url_for('index')+'#login')
    password=request.form.get('password','')
    confirm=request.form.get('confirm_password','')
    if len(password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.','error'); return redirect(url_for('index')+'#profile')
    if password != confirm:
        flash('Las contraseñas no coinciden.','error'); return redirect(url_for('index')+'#profile')
    conn=db(); conn.execute('UPDATE users SET password_hash=? WHERE id=?',(generate_password_hash(password),user['id'])); conn.commit(); conn.close()
    flash('Contraseña guardada.','success'); return redirect(url_for('index')+'#profile')

@app.post('/logout')
def logout():
    session.clear(); flash('Sesión cerrada.','success'); return redirect(url_for('index'))



@app.get('/api/locale')
def locale_api():
    # Geo lookup is used only to choose a default UI language. The IP is not stored.
    ip = request_client_ip()
    country = ''
    lang = ''
    if ip:
        try:
            geo = http_json(f'https://ipwho.is/{urllib.parse.quote(ip)}', timeout=2.5)
            if geo.get('success', True):
                country = str(geo.get('country_code') or '').upper()
                lang = language_for_country(country)
        except Exception:
            pass
    if not lang:
        lang = browser_language()
    return jsonify({'language': lang, 'country_code': country, 'source': 'geo' if country else 'browser'})


@app.get('/api/account')
def account_api():
    user=current_user()
    if not user: return jsonify({'authenticated':False}),401
    return jsonify({'authenticated':True,'id':user['public_id'],'first_name':user['first_name'],'last_name':user['last_name'],'country':user['country'],'demo_balance':round(user['demo_balance'],2),'has_password':bool(user['password_hash'])})

@app.get('/api/market/<symbol>/candles')
def candles_api(symbol):
    symbol=symbol.upper(); interval=request.args.get('interval','1m')
    if symbol not in MARKETS or interval not in ALLOWED_INTERVALS: return jsonify({'error':'unsupported market'}),400
    try:
        candles, source=fetch_candles(symbol,interval)
        return jsonify({'symbol':symbol,'interval':interval,'source':source,'candles':candles})
    except Exception as e:
        return jsonify({'error':'market data unavailable','detail':str(e)}),503

@app.get('/api/market/<symbol>/ticker')
def ticker_api(symbol):
    symbol=symbol.upper()
    if symbol not in MARKETS: return jsonify({'error':'unsupported market'}),400
    try: return jsonify({'symbol':symbol,**fetch_ticker(symbol)})
    except Exception as e: return jsonify({'error':'market data unavailable','detail':str(e)}),503

@app.get('/api/demo/trades')
def list_trades():
    user=current_user(); prices={}; auto_closed=[]
    if user:
        conn=db(); rows=conn.execute('SELECT * FROM demo_trades WHERE user_id=? ORDER BY id DESC',(user['id'],)).fetchall(); raw=[dict(r) for r in rows]
        # Automatically settle every 10-second trade once its timer expires.
        for r in raw:
            if r['status']=='OPEN' and seconds_left(r.get('opened_at')) <= 0:
                try: price=fetch_ticker(r['symbol'])['price']
                except Exception: price=float(r['entry_price'])
                result=training_result(r,price)
                stake=result['stake']
                settlement=result['settlement']
                conn.execute("UPDATE demo_trades SET status='CLOSED',exit_price=?,closed_at=CURRENT_TIMESTAMP WHERE id=?",(price,r['id']))
                conn.execute('UPDATE users SET demo_balance=demo_balance+? WHERE id=?',(settlement,user['id']))
                auto_closed.append({'id':r['id'],'exit_price':price,**result})
        if auto_closed: conn.commit()
        balance=float(conn.execute('SELECT demo_balance FROM users WHERE id=?',(user['id'],)).fetchone()['demo_balance'])
        rows=conn.execute('SELECT * FROM demo_trades WHERE user_id=? ORDER BY id DESC',(user['id'],)).fetchall(); raw=[dict(r) for r in rows]; conn.close()
    else:
        balance, raw = guest_demo_state()
        changed=False
        for r in raw:
            if r['status']=='OPEN' and seconds_left(r.get('opened_at')) <= 0:
                try: price=fetch_ticker(r['symbol'])['price']
                except Exception: price=float(r['entry_price'])
                result=training_result(r,price)
                stake=result['stake']
                settlement=result['settlement']
                r['status']='CLOSED'; r['exit_price']=price; r['closed_at']=datetime.now(timezone.utc).isoformat(); balance+=settlement; changed=True
                auto_closed.append({'id':r['id'],'exit_price':price,**result})
        if changed: save_guest_demo(balance,raw)
        raw=list(reversed(raw))
    out=[]
    for r in raw:
        current=r.get('exit_price') if r.get('status')=='CLOSED' else None
        if current is None:
            try:
                if r['symbol'] not in prices: prices[r['symbol']]=fetch_ticker(r['symbol'])['price']
                current=prices[r['symbol']]
            except Exception: current=r['entry_price']
        live_result=training_result(r,current)
        out.append({'id':r['id'],'symbol':r['symbol'],'side':r['side'],'quantity':r['quantity'],'stake':live_result['stake'],'entry_price':r['entry_price'],'current_price':current,'market_direction':live_result['market_direction'],'projected_result':live_result['result'],'projected_profit':live_result['profit'],'status':r['status'],'opened_at':r.get('opened_at'),'closed_at':r.get('closed_at'),'seconds_left':seconds_left(r.get('opened_at')) if r['status']=='OPEN' else 0})
    return jsonify({'balance':balance,'trades':out,'authenticated':bool(user),'auto_closed':auto_closed,'duration_seconds':TRADE_DURATION_SECONDS})

@app.post('/api/demo/trades')
def open_trade():
    user=current_user()
    data=request.get_json(silent=True) or {}; symbol=str(data.get('symbol','')).upper(); side=str(data.get('side','')).upper()
    try: amount=float(data.get('amount',0))
    except Exception: amount=0
    if symbol not in MARKETS or side not in {'BUY','SELL'} or amount<=0: return jsonify({'error':'invalid order'}),400
    try: price=fetch_ticker(symbol)['price']
    except Exception: return jsonify({'error':'market price unavailable'}),503
    balance=float(user['demo_balance']) if user else guest_demo_state()[0]
    if amount>balance: return jsonify({'error':'insufficient demo balance','max_notional':balance}),400
    quantity=amount/price
    opened=datetime.now(timezone.utc)
    new_balance=balance-amount
    if user:
        conn=db(); cur=conn.execute('INSERT INTO demo_trades(user_id,symbol,side,quantity,entry_price,opened_at) VALUES(?,?,?,?,?,?)',(user['id'],symbol,side,quantity,price,opened.isoformat())); conn.execute('UPDATE users SET demo_balance=? WHERE id=?',(new_balance,user['id'])); conn.commit(); conn.close(); trade_id=cur.lastrowid
    else:
        balance, trades=guest_demo_state(); trade_id=(max([int(t['id']) for t in trades], default=0)+1)
        trades.append({'id':trade_id,'symbol':symbol,'side':side,'quantity':quantity,'entry_price':price,'exit_price':None,'status':'OPEN','opened_at':opened.isoformat(),'closed_at':None})
        save_guest_demo(new_balance,trades)
    return jsonify({'ok':True,'trade_id':trade_id,'entry_price':price,'quantity':quantity,'stake':amount,'balance':new_balance,'authenticated':bool(user),'duration_seconds':TRADE_DURATION_SECONDS,'expires_at':(opened+timedelta(seconds=TRADE_DURATION_SECONDS)).isoformat()})


@app.post('/api/demo/refill')
def refill_demo_balance():
    refill_amount = 1000.0
    user = current_user()
    if user:
        conn = db()
        conn.execute('UPDATE users SET demo_balance=? WHERE id=?', (refill_amount, user['id']))
        conn.commit()
        conn.close()
        balance = refill_amount
    else:
        _, trades = guest_demo_state()
        balance = refill_amount
        save_guest_demo(balance, trades)
    return jsonify({'ok': True, 'balance': balance})

@app.post('/api/demo/trades/<int:trade_id>/close')
def close_trade(trade_id):
    # Kept for compatibility; 10-second positions normally close automatically.
    user=current_user()
    if user:
        conn=db(); tr=conn.execute('SELECT * FROM demo_trades WHERE id=? AND user_id=?',(trade_id,user['id'])).fetchone()
        if not tr or tr['status']!='OPEN': conn.close(); return jsonify({'error':'trade not found'}),404
        tr=dict(tr)
    else:
        balance,trades=guest_demo_state(); tr=next((t for t in trades if int(t['id'])==trade_id and t['status']=='OPEN'),None)
        if not tr: return jsonify({'error':'trade not found'}),404
    try: price=fetch_ticker(tr['symbol'])['price']
    except Exception:
        if user: conn.close()
        return jsonify({'error':'market price unavailable'}),503
    result=training_result(tr,price)
    stake=result['stake']
    settlement=result['settlement']
    if user:
        conn.execute("UPDATE demo_trades SET status='CLOSED',exit_price=?,closed_at=CURRENT_TIMESTAMP WHERE id=?",(price,trade_id))
        conn.execute('UPDATE users SET demo_balance=demo_balance+? WHERE id=?',(settlement,user['id']))
        conn.commit(); balance=conn.execute('SELECT demo_balance FROM users WHERE id=?',(user['id'],)).fetchone()['demo_balance']; conn.close()
    else:
        for t in trades:
            if int(t['id'])==trade_id:
                t['status']='CLOSED'; t['exit_price']=price; t['closed_at']=datetime.now(timezone.utc).isoformat(); break
        balance=float(balance)+settlement; save_guest_demo(balance,trades)
    return jsonify({'ok':True,'exit_price':price,**result,'balance':balance,'authenticated':bool(user)})

init_db()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
