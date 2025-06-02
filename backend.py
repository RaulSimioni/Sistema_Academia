import pandas as pd
import sqlite3
import hashlib

# 1) Conexão com o banco
conn = sqlite3.connect('academia_db.db', check_same_thread=False)
cursor = conn.cursor()

# 2) Criação das tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER NOT NULL,
    sexo TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telefone TEXT NOT NULL,
    plano_id INTEGER NOT NULL,
    instrutor_id INTEGER NOT NULL,
    treino_id INTEGER,
    FOREIGN KEY(instrutor_id) REFERENCES instrutores(id),
    FOREIGN KEY(treino_id)    REFERENCES treinos(id),
    FOREIGN KEY(plano_id)     REFERENCES planos(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS instrutores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especialidade TEXT,
    UNIQUE (nome, especialidade)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS planos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco_mensal REAL NOT NULL,
    duracao_meses INTEGER NOT NULL,
    UNIQUE (nome, preco_mensal, duracao_meses)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    grupo_muscular TEXT NOT NULL,
    UNIQUE (nome, grupo_muscular)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS treinos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    instrutor_id INTEGER NOT NULL,
    data_inicio TEXT,
    data_fim TEXT,
    plano_id INTEGER,
    FOREIGN KEY(cliente_id)   REFERENCES clientes(id),
    FOREIGN KEY(instrutor_id) REFERENCES instrutores(id),
    FOREIGN KEY(plano_id)     REFERENCES planos(id),
    UNIQUE (cliente_id, instrutor_id, data_inicio, data_fim, plano_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS treino_exercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    treino_id INTEGER NOT NULL,
    treino TEXT,
    exercicio_id INTEGER NOT NULL,
    exercicio TEXT,
    series INTEGER NOT NULL,
    repeticoes INTEGER NOT NULL,
    FOREIGN KEY(treino_id)    REFERENCES treinos(id),
    FOREIGN KEY(exercicio_id) REFERENCES exercicios(id),
    UNIQUE (treino_id, exercicio_id, series, repeticoes)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data_pagamento TEXT NOT NULL,
    valor_pago REAL NOT NULL,
    plano_id INTEGER NOT NULL,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(plano_id)   REFERENCES planos(id),
    UNIQUE (cliente_id, data_pagamento, valor_pago, plano_id)
);
""")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
''')

conn.commit()

# 3) Carregando os CSVs
df_clientes         = pd.read_csv('clientes_academia.csv',    sep=',', encoding='utf-8')
df_instrutores      = pd.read_csv('instrutores.csv',         sep=',', encoding='utf-8')
df_exercicios       = pd.read_csv('exercicios.csv',          sep=',', encoding='utf-8')
df_planos           = pd.read_csv('planos.csv',              sep=',', encoding='utf-8')
df_treinos          = pd.read_csv('treinos.csv',             sep=',', encoding='utf-8')
df_treino_exercicios = pd.read_csv('treino_exercicios.csv', sep=',', encoding='utf-8')
df_pagamentos       = pd.read_csv('pagamento_clientes.csv',  sep=',', encoding='utf-8')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(username, password):
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0] == hash_password(password)
    return False

def registrar_usuario(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# 4) Função auxiliar para filtrar registros novos
def filter_novos(df, cols, tabela):
    """
    Retorna apenas as linhas de df cujas colunas em `cols`
    não estejam já presentes na tabela SQLite `tabela`.
    """
    # remove duplicados internos
    df = df.drop_duplicates(subset=cols, keep='first')
    # lê valores existentes
    sel = ", ".join(cols)
    sql = f"SELECT {sel} FROM {tabela}"
    existentes = pd.read_sql_query(sql, conn)
    # monta conjunto de tuplas existentes
    tuplas_exist = set(tuple(x) for x in existentes.values)
    # filtra linhas cujo tuple(cols) NÃO está em existentes
    mask = ~df[cols].apply(lambda row: tuple(row), axis=1).isin(tuplas_exist)
    return df[mask]

# 5) Inserção em cada tabela, só com novos

# 5.1 clientes (chave natural = email)
novos = filter_novos(df_clientes, ['email'], 'clientes')
if not novos.empty:
    novos.to_sql('clientes', conn, if_exists='append', index=False)
    conn.commit()

# 5.2 instrutores (nome + especialidade)
novos = filter_novos(df_instrutores, ['nome','especialidade'], 'instrutores')
if not novos.empty:
    novos.to_sql('instrutores', conn, if_exists='append', index=False)
    conn.commit()

# 5.3 planos (nome + preco_mensal + duracao_meses)
novos = filter_novos(df_planos, ['nome','preco_mensal','duracao_meses'], 'planos')
if not novos.empty:
    novos.to_sql('planos', conn, if_exists='append', index=False)
    conn.commit()

# 5.4 exercicios (nome + grupo_muscular)
novos = filter_novos(df_exercicios, ['nome','grupo_muscular'], 'exercicios')
if not novos.empty:
    novos.to_sql('exercicios', conn, if_exists='append', index=False)
    conn.commit()

# 5.5 treinos (cliente_id, instrutor_id, data_inicio, data_fim, plano_id)
novos = filter_novos(df_treinos,
                     ['cliente_id','instrutor_id','data_inicio','data_fim','plano_id'],
                     'treinos')
if not novos.empty:
    novos.to_sql('treinos', conn, if_exists='append', index=False)
    conn.commit()

# 5.6 treino_exercicios (treino_id, exercicio_id, series, repeticoes)
novos = filter_novos(df_treino_exercicios,
                     ['treino_id','exercicio_id','series','repeticoes'],
                     'treino_exercicios')
if not novos.empty:
    novos.to_sql('treino_exercicios', conn, if_exists='append', index=False)
    conn.commit()

# 5.7 pagamentos (cliente_id, data_pagamento, valor_pago, plano_id)
novos = filter_novos(df_pagamentos,
                     ['cliente_id','data_pagamento','valor_pago','plano_id'],
                     'pagamentos')
if not novos.empty:
    novos.to_sql('pagamentos', conn, if_exists='append', index=False)
    conn.commit()

#pegunta 1
def clientes_planos(nome_plano):
    conn = sqlite3.connect('academia_db.db')
    query = '''
        SELECT c.nome AS Cliente, p.nome AS Plano
        FROM clientes c
        JOIN planos p ON c.plano_id = p.id
        WHERE p.nome = ?
        ORDER BY c.nome
    '''
    df = pd.read_sql_query(query, conn, params=(nome_plano,))
    conn.close()
    return df

# Pregunta 2 - Filtrar e mostrar treinos e seus exercícios.

def clientes_planos(nome_cliente):
    conn = sqlite3.connect('academia_db.db')
    query = '''
        SELECT c.nome AS Cliente, p.nome AS Plano
        FROM clientes c
        JOIN planos p ON c.plano_id = p.id
        WHERE p.nome = ?
        ORDER BY c.nome
    '''
    df = pd.read_sql_query(query, conn, params=(nome_cliente,))
    conn.close()
    return df
# pergunta 3 - Mostra total de pagamentos e o ultimo pagamento do cliente

def listar_treinos_com_exercicios():
    conn = get_connection()
    query = """
        SELECT 
            t.id AS Treino_ID,
            c.nome AS Cliente,
            i.nome AS Instrutor,
            t.data_inicio,
            t.data_fim,
            e.nome AS Exercicio,
            te.series,
            te.repeticoes
        FROM treinos t
        JOIN clientes c ON c.id = t.cliente_id
        JOIN instrutores i ON i.id = t.instrutor_id
        JOIN treino_exercicios te ON te.treino_id = t.id
        JOIN exercicios e ON e.id = te.exercicio_id
        ORDER BY c.nome, t.data_inicio
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def carregar_pagamentos(caminho_csv="pagamento_clientes.csv"):
    return pd.read_csv(caminho_csv, parse_dates=["data_pagamento"])

def calcular_resumo_pagamentos(df):
    resumo = df.groupby("cliente_id").agg(
        total_pago=("valor_pago", "sum"),
        ultimo_pagamento=("data_pagamento", "max")
    ).reset_index()
    return resumo

# pergunta 4 - Mostrar quantos clientes cada instrutor atende.  
def get_connection():
    return sqlite3.connect("academia_db.db", check_same_thread=False)

def clientes_instrutor(instrutor):
    conn = get_connection()
    df_filtro_instrutor = pd.read_sql_query('''
        SELECT i.nome AS Instrutor, COUNT(*) AS Quantidade_de_clientes
        FROM treino_exercicios te
        JOIN treinos t ON te.treino_id = t.id
        JOIN instrutores i ON t.instrutor_id = i.id
        WHERE i.nome = ?
        GROUP BY i.nome
    ''', conn, params=(instrutor,))
    return df_filtro_instrutor

# pergunta 4 COMPLEMENTO
def clientes_por_instrutor_com_vazios():
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    query = '''
        SELECT i.nome AS instrutor, COUNT(c.id) AS quantidade
        FROM clientes c
        LEFT JOIN instrutores i ON c.instrutor_id = i.id
        GROUP BY i.nome
    '''
    df = pd.read_sql_query(query, conn)

    # Preenche valores nulos (clientes sem instrutor) com texto
    df["instrutor"] = df["instrutor"].fillna("Sem instrutor")
    return df

# pergunta 5 - Formulario Novo Cliente
def novo_cliente(nome, idade, sexo, email, telefone, plano_nome, instrutor_nome):
    conn = get_connection()
    cursor = conn.cursor()

    planos = pd.read_sql_query("SELECT id, nome, duracao_meses FROM planos", conn)
    instrutores = pd.read_sql_query("SELECT id, nome FROM instrutores", conn)

    plano_id = int(planos[planos['nome'] == plano_nome]['id'].values[0])
    instrutor_id = int(instrutores[instrutores['nome'] == instrutor_nome]['id'].values[0])
    
    cursor.execute(
        "INSERT INTO clientes (nome, idade, sexo, email, telefone, plano_id, instrutor_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nome, idade, sexo, email, telefone, plano_id, instrutor_id)
    )
    conn.commit()

    conn.close()
    return f"Cliente {nome} inserido com sucesso!"

def get_conn():
    return sqlite3.connect('academia_db.db')

# pergunta 5 - Formulario Novo Pagamento
def novo_pagamento(cliente_nome, plano_nome, data):
    conn = get_connection()
    cursor = conn.cursor()

    clientes = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    planos = pd.read_sql_query("SELECT id, nome, preco_mensal FROM planos", conn)

    cliente_id = int(clientes[clientes['nome'] == cliente_nome]['id'].values[0])
    plano_id = int(planos[planos['nome'] == plano_nome]['id'].values[0])
    valor_plano = float(planos[planos['nome'] == plano_nome]['preco_mensal'].values[0])
    data_pagamento = str(data)

    cursor.execute(
        "INSERT INTO pagamentos (cliente_id,plano_id,valor_pago,data_pagamento) VALUES (?, ?, ?, ?)",
        (cliente_id, plano_id, valor_plano, data_pagamento)
    )
    conn.commit()
    conn.close()

    return f"Pagamento do cliente {cliente_nome} inserido com sucesso! Valor: {valor_plano} | Data:{data_pagamento}"

# pergunta 5 - Formulario Novo Treino
def novo_treino(cliente_nome, data):
    conn = get_connection()
    cursor = conn.cursor()

    clientes = pd.read_sql_query("SELECT id, nome, instrutor_id, plano_id FROM clientes", conn)
    planos = pd.read_sql_query("SELECT id, nome, duracao_meses FROM planos", conn)

    cliente_id = int(clientes[clientes['nome'] == cliente_nome]['id'].values[0])
    instrutor_id = int(clientes[clientes['nome'] == cliente_nome]['instrutor_id'].values[0])
    plano_id = int(clientes[clientes['nome'] == cliente_nome]['plano_id'].values[0])
    
    duracao = int(planos[planos['id'] == plano_id]['duracao_meses'].values[0])
    from datetime import date
    from dateutil.relativedelta import relativedelta
    data_inicial = data
    data_final = data + relativedelta(months=duracao)
    cursor.execute(
        "INSERT INTO treinos (cliente_id,instrutor_id,data_inicio,data_fim,plano_id) VALUES (?, ?, ?, ?, ?)",
        (cliente_id, instrutor_id, data_inicial, data_final, plano_id)
    )
    conn.commit()
    conn.close()

    return f"Treino do cliente {cliente_nome} inserido com sucesso! Data inicial: {data_inicial} | Data final:{data_final}"

# pergunta 5 - Formulario Novo Exercício
def novo_exercicio(nome_exercicio, grupo_muscular):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO exercicios (nome, grupo_muscular) VALUES (?, ?)",
            (nome_exercicio, grupo_muscular)
        )
        conn.commit()
        message = f"Exercício '{nome_exercicio}' inserido com sucesso!"
    except sqlite3.IntegrityError:
        message = "Exercício já existe ou ocorreu um erro ao inserir."
    conn.close()
    return message

# pergunta 5 - Formulario Novo Treino Exercício
def novo_treino_exercicio(treino_data, tipo_treino, exercicio_nome, series, repeticoes):
    conn = get_connection()
    cursor = conn.cursor()

    treinos = pd.read_sql_query ("SELECT id, data_inicio FROM treinos", conn)
    exercicios = pd.read_sql_query ("SELECT id, nome FROM exercicios", conn)

    treino_id = int(treinos[treinos['data_inicio'] == treino_data]['id'].values[0])
    exercicio_id = int(exercicios[exercicios['nome'] == exercicio_nome]['id'].values[0])

    cursor.execute(
        "INSERT INTO treino_exercicios (treino_id,treino,exercicio_id,exercicio,series,repeticoes) VALUES (?, ?, ?, ?, ?, ?)",
        (treino_id, tipo_treino, exercicio_id, exercicio_nome, series, repeticoes)
    )
    conn.commit()
    conn.close()

    return f"Treino Exercícios inserido com sucesso!"

def get_clientes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, nome FROM clientes ORDER BY nome", conn)
    conn.close()
    return df