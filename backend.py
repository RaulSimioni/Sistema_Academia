import pandas as pd
import sqlite3

# 1) Conexão com o banco
conn = sqlite3.connect('academia_db.db')
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

conn.commit()

# 3) Carregando os CSVs
df_clientes         = pd.read_csv('clientes_academia.csv',    sep=',', encoding='utf-8')
df_instrutores      = pd.read_csv('instrutores.csv',         sep=',', encoding='utf-8')
df_exercicios       = pd.read_csv('exercicios.csv',          sep=',', encoding='utf-8')
df_planos           = pd.read_csv('planos.csv',              sep=',', encoding='utf-8')
df_treinos          = pd.read_csv('treinos.csv',             sep=',', encoding='utf-8')
df_treino_exercicios = pd.read_csv('treino_exercicios.csv', sep=',', encoding='utf-8')
df_pagamentos       = pd.read_csv('pagamento_clientes.csv',  sep=',', encoding='utf-8')

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

# pergunta 4 - Mostrar quantos clientes cada instrutor atende.  
def get_connection():
    return sqlite3.connect("academia_db.db", check_same_thread=False)

def clientes_instrutor(instrutor):
    conn = get_connection()
    df_filtro_instrutor = pd.read_sql_query('''
        SELECT i.nome AS Instrutor, COUNT(*) AS Quantidade_de_clientes
            FROM clientes c
            JOIN instrutores i ON c.instrutor_id = i.id
            WHERE i.nome = ?
            GROUP BY i.nome
    ''', conn, params=(instrutor,))
    return df_filtro_instrutor

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

    cliente_id = cursor.lastrowid

    duracao = int(planos[planos['id'] == plano_id]['duracao_meses'].values[0])
    from datetime import date
    from dateutil.relativedelta import relativedelta
    data_inicio = date.today()
    data_fim = data_inicio + relativedelta(months=duracao)

    cursor.execute(
        "INSERT INTO treinos (cliente_id, instrutor_id, data_inicio, data_fim, plano_id) VALUES (?, ?, ?, ?, ?)",
        (cliente_id, instrutor_id, data_inicio.isoformat(), data_fim.isoformat(), plano_id)
    )
    conn.commit()

    treino_id = cursor.lastrowid
    cursor.execute(
        "UPDATE clientes SET treino_id = ? WHERE id = ?",
        (treino_id, cliente_id)
    )
    conn.commit()

    conn.close()
    return f"Cliente {nome} inserido com sucesso!"

def get_conn():
    return sqlite3.connect('academia_db.db')

