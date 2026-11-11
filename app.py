import sqlite3
from datetime import timedelta
from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_oficina_lgpd'
app.permanent_session_lifetime = timedelta(minutes=30)

DB_NAME = 'oficina.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def mascarar_cpf(cpf):
    limpo = ''.join(filter(str.isdigit, cpf))
    if len(limpo) == 11:
        return f"***.{limpo[3:6]}.{limpo[6:9]}-**"
    return "***.***.***-**"

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS veiculos (
            id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            placa TEXT NOT NULL UNIQUE,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            ano INTEGER NOT NULL,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        CREATE TABLE IF NOT EXISTS agendamentos (
            id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_veiculo INTEGER NOT NULL,
            data_agendamento TEXT NOT NULL,
            descricao_servico TEXT NOT NULL,
            status TEXT DEFAULT 'Agendado',
            FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
        );
    ''')

    if cursor.execute('SELECT COUNT(*) FROM usuarios').fetchone() == 0:
        senha_padrao = generate_password_hash('123456')
        cursor.executemany('INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)', [
            ('Eliel', 'eliel@oficina.com', senha_padrao),
            ('Valdenilson', 'valdenilson@oficina.com', senha_padrao),
            ('Mariana Costa', 'mariana@oficina.com', senha_padrao)
        ])

        cursor.executemany('INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)', [
            ('João Silva', '111.222.333-44', '(79) 99999-1010', 'joao@email.com'),
            ('Maria Santos', '222.333.444-55', '(79) 99999-2020', 'maria@email.com'),
            ('Pedro Oliveira', '333.444.555-66', '(79) 99999-3030', 'pedro@email.com')
        ])

        cursor.executemany('INSERT INTO veiculos (id_cliente, placa, marca, modelo, ano) VALUES (?, ?, ?, ?, ?)', [
            (1, 'ABC1D23', 'Fiat', 'Argo', 2021),
            (2, 'DEF4G56', 'Hyundai', 'HB20', 2022),
            (3, 'GHI7J89', 'Chevrolet', 'Tracker', 2023)
        ])

        cursor.executemany('INSERT INTO agendamentos (id_veiculo, data_agendamento, descricao_servico, status) VALUES (?, ?, ?, ?)', [
            (1, '2026-11-20T09:00', 'Troca de óleo e filtro de ar', 'Agendado'),
            (2, '2026-11-21T14:30', 'Revisão de pastilhas de freio', 'Agendado'),
            (3, '2026-11-22T10:00', 'Alinhamento e balanceamento', 'Agendado')
        ])

    conn.commit()
    conn.close()

BASE_STYLE = '''
<style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f4f6f9; color: #333; }
    .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    nav { background: #2c3e50; padding: 12px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; color: white; }
    nav a { color: white; text-decoration: none; margin-right: 15px; font-weight: bold; }
    nav a:hover { text-decoration: underline; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background: #34495e; color: white; }
    input, select, button { padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; }
    button { background: #2980b9; color: white; border: none; cursor: pointer; }
    button:hover { background: #1f6391; }
    .erro { color: #c0392b; background: #fadbd8; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['senha_hash'], senha):
            session.permanent = True
            session['usuario_id'] = user['id_usuario']
            session['usuario_nome'] = user['nome']
            return redirect(url_for('dashboard'))
        else:
            erro = 'Falha na autenticação: E-mail ou senha inválidos.'

    return render_template_string(BASE_STYLE + '''
    <div class="container" style="max-width: 400px; margin-top: 80px;">
        <h2>Login - Oficina Automotiva</h2>
        {% if erro %}<div class="erro">{{ erro }}</div>{% endif %}
        <form method="POST">
            <label>E-mail:</label><br>
            <input type="email" name="email" style="width: 95%;" required placeholder="eliel@oficina.com"><br>
            <label>Senha:</label><br>
            <input type="password" name="senha" style="width: 95%;" required placeholder="123456"><br><br>
            <button type="submit" style="width: 100%;">Entrar</button>
        </form>
    </div>
    ''', erro=erro)

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template_string(BASE_STYLE + '''
    <div class="container">
        <nav>
            <div>
                <a href="/dashboard">Início</a>
                <a href="/clientes">Clientes</a>
                <a href="/veiculos">Veículos</a>
                <a href="/agendamentos">Agendamentos</a>
            </div>
            <div>
                <span>Olá, <strong>{{ session['usuario_nome'] }}</strong> | </span>
                <a href="/logout" style="color: #e74c3c;">Sair</a>
            </div>
        </nav>
        <h2>Painel Principal</h2>
        <p>Bem-vindo ao Sistema de Gestão de Oficina Automotiva. Utilize o menu acima para gerenciar clientes, veículos e agendamentos.</p>
    </div>
    ''')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'cadastrar':
            conn.execute('INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)',
                         (request.form['nome'], request.form['cpf'], request.form['telefone'], request.form['email']))
            conn.commit()
        elif acao == 'editar':
            conn.execute('UPDATE clientes SET nome=?, telefone=?, email=? WHERE id_cliente=?',
                         (request.form['nome'], request.form['telefone'], request.form['email'], request.form['id_cliente']))
            conn.commit()

    termo = request.args.get('busca', '')
    if termo:
        lista = conn.execute('SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ?', (f'%{termo}%', f'%{termo}%')).fetchall()
    else:
        lista = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()

    clientes_formatados = []
    for c in lista:
        item = dict(c)
        item['cpf_mascarado'] = mascarar_cpf(c['cpf'])
        clientes_formatados.append(item)

    return render_template_string(BASE_STYLE + '''
    <div class="container">
        <nav>
            <div>
                <a href="/dashboard">Início</a>
                <a href="/clientes">Clientes</a>
                <a href="/veiculos">Veículos</a>
                <a href="/agendamentos">Agendamentos</a>
            </div>
            <div><span>{{ session['usuario_nome'] }} | </span><a href="/logout" style="color: #e74c3c;">Sair</a></div>
        </nav>
        <h2>Gerenciamento de Clientes (Proteção LGPD)</h2>
        
        <form method="POST">
            <input type="hidden" name="acao" value="cadastrar">
            <input type="text" name="nome" placeholder="Nome completo" required>
            <input type="text" name="cpf" placeholder="CPF (ex: 000.000.000-00)" required>
            <input type="text" name="telefone" placeholder="Telefone" required>
            <input type="email" name="email" placeholder="E-mail">
            <button type="submit">Cadastrar Cliente</button>
        </form>

        <hr>
        <form method="GET">
            <input type="text" name="busca" value="{{ termo }}" placeholder="Buscar por nome ou CPF...">
            <button type="submit">Pesquisar</button>
            <a href="/clientes"><button type="button" style="background:#7f8c8d;">Limpar</button></a>
        </form>

        <table>
            <tr><th>ID</th><th>Nome</th><th>CPF (LGPD)</th><th>Telefone</th><th>E-mail</th><th>Editar</th></tr>
            {% for c in clientes %}
            <tr>
                <form method="POST">
                    <input type="hidden" name="acao" value="editar">
                    <input type="hidden" name="id_cliente" value="{{ c.id_cliente }}">
                    <td>{{ c.id_cliente }}</td>
                    <td><input type="text" name="nome" value="{{ c.nome }}" required></td>
                    <td>{{ c.cpf_mascarado }}</td>
