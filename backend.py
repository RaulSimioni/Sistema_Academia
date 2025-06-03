import pandas as pd
import sqlite3
import hashlib
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import datetime
from sqlite3 import IntegrityError

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

def get_connection():
    return sqlite3.connect("academia_db.db", check_same_thread=False) 

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

def filter_novos(df, cols, tabela):
    df = df.drop_duplicates(subset=cols, keep='first')
    sel = ", ".join(cols)
    sql = f"SELECT {sel} FROM {tabela}"
    existentes = pd.read_sql_query(sql, conn)
    tuplas_exist = set(tuple(x) for x in existentes.values)
    mask = ~df[cols].apply(lambda row: tuple(row), axis=1).isin(tuplas_exist)
    return df[mask]

# 5) Inserção em cada tabela, só com novos
novos = filter_novos(df_clientes, ['email'], 'clientes')
if not novos.empty:
    novos.to_sql('clientes', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_instrutores, ['nome','especialidade'], 'instrutores')
if not novos.empty:
    novos.to_sql('instrutores', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_planos, ['nome','preco_mensal','duracao_meses'], 'planos')
if not novos.empty:
    novos.to_sql('planos', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_exercicios, ['nome','grupo_muscular'], 'exercicios')
if not novos.empty:
    novos.to_sql('exercicios', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_treinos,
                     ['cliente_id','instrutor_id','data_inicio','data_fim','plano_id'],
                     'treinos')
if not novos.empty:
    novos.to_sql('treinos', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_treino_exercicios,
                     ['treino_id','exercicio_id','series','repeticoes'],
                     'treino_exercicios')
if not novos.empty:
    novos.to_sql('treino_exercicios', conn, if_exists='append', index=False)
    conn.commit()

novos = filter_novos(df_pagamentos,
                     ['cliente_id','data_pagamento','valor_pago','plano_id'],
                     'pagamentos')
if not novos.empty:
    novos.to_sql('pagamentos', conn, if_exists='append', index=False)
    conn.commit()

#----------------------------------------pergunta 1 e 2---------------------------------------------------#
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
#----------------------------------------pergunta 3---------------------------------------------------#

def carregar_clientes():
    conn = get_connection()
    df_clientes = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    conn.close()
    return df_clientes

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

def carregar_pagamentos():
    """
    Agora carrega diretamente do banco SQLite, trazendo cliente_id, data_pagamento, valor_pago, plano_id.
    """
    conn = get_connection()
    query = """
        SELECT 
            cliente_id,
            date(data_pagamento) AS data_pagamento,
            valor_pago,
            plano_id
        FROM pagamentos
    """
    df = pd.read_sql_query(query, conn, parse_dates=["data_pagamento"])
    conn.close()
    return df


def calcular_resumo_pagamentos(df_pagamentos, df_clientes):
    """
    Retorna um DataFrame que inclui todos os clientes, com:
      - total_pago: soma dos valores (zero se não houver pagamento)
      - ultimo_pagamento: data do último pagamento (NaT se não houver)
    """
    resumo_pag = (
        df_pagamentos
        .groupby("cliente_id")
        .agg(
            total_pago=("valor_pago", "sum"),
            ultimo_pagamento=("data_pagamento", "max")
        )
        .reset_index()
    )

    df_clientes_renomeado = df_clientes.rename(
        columns={"id": "cliente_id", "nome": "cliente_nome"}
    )

    df_resumo = df_clientes_renomeado.merge(
        resumo_pag,
        on="cliente_id",
        how="left"
    )

    df_resumo["total_pago"] = df_resumo["total_pago"].fillna(0.0)
    return df_resumo

df_pagamentos = carregar_pagamentos()
df_clientes = carregar_clientes() 
df_resumo = calcular_resumo_pagamentos(df_pagamentos, df_clientes)

df_pagamentos = carregar_pagamentos()

# Adiciona coluna de "Ano-Mês"
df_pagamentos["ano_mes"] = df_pagamentos["data_pagamento"].dt.to_period("M")

# Agrupa por "ano_mes" e soma os pagamentos
df_pagamentos_por_mes = (
    df_pagamentos.groupby("ano_mes")["valor_pago"]
    .sum()
    .reset_index()
)

# Converte a coluna "ano_mes" para string
df_pagamentos_por_mes["ano_mes"] = df_pagamentos_por_mes["ano_mes"].astype(str)

def grafico_pagamentos():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_pagamentos_por_mes["ano_mes"], df_pagamentos_por_mes["valor_pago"], color="skyblue")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total Pago (R$)")
    ax.set_title("Total de Pagamentos por Mês")
    plt.xticks(rotation=45)
    return fig

#----------------------------------------pergunta 4---------------------------------------------------#
def clientes_instrutor(instrutor):
    conn = get_connection()
    df_filtro_instrutor = pd.read_sql_query('''
        SELECT i.nome AS instrutor, COUNT(*) As Contagem
            FROM clientes c
            JOIN instrutores i ON c.instrutor_id = i.id
            WHERE i.nome = ?    
            GROUP BY i.nome
    ''', conn, params=(instrutor,))
    return df_filtro_instrutor

def clientes_por_instrutor_com_vazios():
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    query = '''
        SELECT i.nome AS instrutor, COUNT(*) AS quantidade
        FROM clientes c
        LEFT JOIN instrutores i ON c.instrutor_id = i.id
        GROUP BY i.nome
    '''
    df = pd.read_sql_query(query, conn)

    df["instrutor"] = df["instrutor"].fillna("Sem instrutor")
    return df

df_instrutores = clientes_por_instrutor_com_vazios()

def carregar_instrutores():
    conn = get_connection()
    query = "SELECT id, nome FROM instrutores"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
    
def grafico_instrutores():
    conn = get_connection()
    query = '''
        SELECT i.nome AS instrutor, COUNT(*) AS quantidade
        FROM clientes c
        LEFT JOIN instrutores i ON c.instrutor_id = i.id
        GROUP BY i.nome
    '''
    df_instrutores = pd.read_sql_query(query, conn)
    conn.close()

    if df_instrutores.empty:
        return "Sem dados para exibir."

    colors = ['#042940', '#005C53', '#9FC131']
    explode = [0.02] * len(df_instrutores)

   

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
    wedges, texts, autotexts = ax.pie(
        df_instrutores['quantidade'],
        labels=df_instrutores['instrutor'],
        autopct='%1.1f%%',
        startangle=140,
        colors=colors[:len(df_instrutores)],
        explode=explode,
        textprops=dict(color="white", fontsize=12, weight='bold'),
        pctdistance=0.50
    )
    ax.set_title("Distribuição de Clientes por Instrutor", color="white", fontsize=14, weight='bold')
    ax.axis('equal')
    fig.patch.set_facecolor('black')


    ax.legend(
        wedges,
        df_instrutores['instrutor'],
        title="Instrutores",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        facecolor='gray',
        labelcolor='black',
        fontsize=10,
        title_fontsize=12
    )

    return fig

#----------------------------------------pergunta 5---------------------------------------------------#
#Criação de uma função de registro de cliente
def novo_cliente(nome, idade, sexo, email, telefone, plano_nome, instrutor_nome):
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se já existe cliente com o mesmo nome ou e-mail
    query = """
        SELECT id, nome, email
        FROM clientes
        WHERE nome = ? OR email = ?
    """
    cursor.execute(query, (nome, email))
    resultado = cursor.fetchone()

    if resultado:
        cliente_existente_nome = resultado[1]
        cliente_existente_email = resultado[2]
        mensagem = "Erro: já existe um cliente com "

        if nome == cliente_existente_nome and email == cliente_existente_email:
            mensagem += f"o mesmo nome ('{nome}') e e-mail ('{email}')."
        elif nome == cliente_existente_nome:
            mensagem += f"o mesmo nome ('{nome}')."
        elif email == cliente_existente_email:
            mensagem += f"o mesmo e-mail ('{email}')."
        
        conn.close()
        return {
            "status": "erro",
            "mensagem": mensagem
        }
    else:
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
        return {
            "status": "sucesso",
            "mensagem": f"Cliente '{nome}' inserido com sucesso!"
        }


def novo_pagamento(cliente_nome, plano_nome, data):
    conn = get_connection()
    cursor = conn.cursor()

    # Obter IDs
    clientes = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    planos = pd.read_sql_query("SELECT id, nome, preco_mensal FROM planos", conn)

    cliente_id = int(clientes[clientes['nome'] == cliente_nome]['id'].values[0])
    plano_id = int(planos[planos['nome'] == plano_nome]['id'].values[0])
    valor_plano = float(planos[planos['nome'] == plano_nome]['preco_mensal'].values[0])
    data_pagamento = str(data)

    # Verificar se já existe um pagamento para esse cliente na mesma data
    cursor.execute("""
        SELECT id FROM pagamentos
        WHERE cliente_id = ? AND data_pagamento = ?
    """, (cliente_id, data_pagamento))
    pagamento_existente = cursor.fetchone()

    if pagamento_existente:
        conn.close()
        return {
            "status": "erro",
            "mensagem": f"Já existe um pagamento registrado para o cliente '{cliente_nome}' na data {data_pagamento}."
        }

    # Inserir novo pagamento
    cursor.execute(
        "INSERT INTO pagamentos (cliente_id, plano_id, valor_pago, data_pagamento) VALUES (?, ?, ?, ?)",
        (cliente_id, plano_id, valor_plano, data_pagamento)
    )
    conn.commit()
    conn.close()

    return {
        "status": "sucesso",
        "mensagem": f"Pagamento do cliente {cliente_nome} inserido com sucesso! Valor: {valor_plano} | Data: {data_pagamento}"
    }

def novo_treino(cliente_nome, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obter dados dos clientes e planos
        clientes = pd.read_sql_query("SELECT id, nome, instrutor_id, plano_id FROM clientes", conn)
        planos = pd.read_sql_query("SELECT id, nome, duracao_meses FROM planos", conn)

        # Verifica se cliente existe
        cliente_row = clientes[clientes['nome'] == cliente_nome]
        if cliente_row.empty:
            return f"Erro: Cliente '{cliente_nome}' não encontrado."

        cliente_id = int(cliente_row['id'].values[0])
        instrutor_id = int(cliente_row['instrutor_id'].values[0])
        plano_id = int(cliente_row['plano_id'].values[0])

        # Verifica se plano é válido
        plano_row = planos[planos['id'] == plano_id]
        if plano_row.empty:
            return f"Erro: Plano associado ao cliente não encontrado."

        duracao = int(plano_row['duracao_meses'].values[0])

        data_inicial = data
        data_final = data + relativedelta(months=duracao)

        # Verifica se já existe treino com mesmo cliente e mesmas datas
        cursor.execute(
            """
            SELECT COUNT(*) FROM treinos 
            WHERE cliente_id = ? AND data_inicio = ? AND data_fim = ?
            """,
            (cliente_id, data_inicial, data_final)
        )
        treino_existente = cursor.fetchone()[0] > 0

        if treino_existente:
            return {"status": "error",
            "message": "Erro: Um treino com a mesma data já existe para esse cliente."}

        # Inserção segura
        cursor.execute(
            "INSERT INTO treinos (cliente_id, instrutor_id, data_inicio, data_fim, plano_id) VALUES (?, ?, ?, ?, ?)",
            (cliente_id, instrutor_id, data_inicial, data_final, plano_id)
        )
        conn.commit()

        return {
            "status": "success",
            "message": f"Treino do cliente {cliente_nome} inserido com sucesso! Data inicial: {data_inicial} | Data final: {data_final}"
        }

    except Exception as e:
        return {"status": "error",
            "message": f"Erro durante inserção do treino: {str(e)}"}

    finally:
        if 'conn' in locals():
            conn.close()

def novo_exercicio(nome_exercicio, grupo_muscular):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO exercicios (nome, grupo_muscular) VALUES (?, ?)",
            (nome_exercicio, grupo_muscular)
        )
        conn.commit()  # Salva a transação no banco
        message = f"Exercício '{nome_exercicio}' inserido com sucesso!"
    except sqlite3.IntegrityError:  # Caso o exercício já exista ou erro de integridade
        message = "Exercício já existe ou ocorreu um erro ao inserir."
    conn.close()
    return message


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

def grafico_treinos_por_cliente():
    conn = get_connection()
    query = '''
        SELECT c.nome AS Cliente, te.treino AS Tipo
        FROM clientes c
        JOIN treino_exercicios te ON c.treino_id = te.treino_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    contagens = df['Tipo'].value_counts()
    tipo_order = ['a', 'b', 'c', 'd']
    labels = tipo_order
    sizes = [contagens.get(t, 0) for t in tipo_order]

    default_color_list = ['#042940', '#005C53', '#9FC131', '#D6D58E']
    colors = default_color_list[:len(sizes)]
    explode = [0.02] * len(sizes)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        explode=explode,
        textprops=dict(color="white", fontsize=12, weight='bold'),
        pctdistance=0.50
    )

    ax.axis('equal')
    fig.patch.set_facecolor('black')

    ax.legend(
        wedges,
        labels,
        title="Tipo Treino",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        facecolor='gray',
        labelcolor='black',
        fontsize=10,
        title_fontsize=12
    )

    return fig



def grafico_clientes_por_plano():
    conn = get_connection()
    query = '''
        SELECT p.nome AS plano, COUNT(*) AS total
        FROM clientes c
        JOIN planos p ON c.plano_id = p.id
        GROUP BY p.nome
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return "Sem dados para exibir."

    colors = ['#042940', '#005C53', '#9FC131', '#D6D58E']
    explode = [0.02] * len(df)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
    wedges, texts, autotexts = ax.pie(
        df['total'],
        labels=df['plano'],
        autopct='%1.1f%%',
        startangle=140,
        colors=colors[:len(df)],
        explode=explode,
        textprops=dict(color="white", fontsize=12, weight='bold'),
        pctdistance=0.50
    )

    ax.axis('equal')
    fig.patch.set_facecolor('black')

    ax.legend(
        wedges,
        df['plano'],
        title="Planos",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        facecolor='gray',
        labelcolor='black',
        fontsize=10,
        title_fontsize=12
    )

    return fig

def get_treinos_por_cliente(nome_cliente):
    """
    Retorna um DataFrame com as colunas [id, data_inicio] 
    de todos os treinos existentes para o cliente cujo nome é nome_cliente.
    """
    conn = get_connection()
    query = """
        SELECT
            t.id,
            date(t.data_inicio) AS data_inicio
        FROM treinos t
        JOIN clientes c ON c.id = t.cliente_id
        WHERE c.nome = ?
        ORDER BY t.data_inicio DESC
    """
    # parse_dates para garantir que data_inicio seja uma datetime
    df = pd.read_sql_query(query, conn, params=(nome_cliente,), parse_dates=["data_inicio"])
    conn.close()
    return df

def get_exercicios():
    """
    Retorna um DataFrame com as colunas [id, nome] de todos os exercícios cadastrados,
    ordenados por nome.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, nome FROM exercicios ORDER BY nome", conn)
    conn.close()
    return df

def adicionar_exercicio_treino(treino_id, nome_exercicio, series, repeticoes):
    """
    Insere um registro em treino_exercicios relacionando um exercício já cadastrado
    a um treino existente. 
    Retorna um dict com status e mensagem.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1) Busca o ID do exercício pelo nome
    cursor.execute("SELECT id FROM exercicios WHERE nome = ?", (nome_exercicio,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return {"status": "erro", "mensagem": f"Exercício '{nome_exercicio}' não encontrado."}
    exercicio_id = result[0]

    # 2) Tenta inserir em treino_exercicios
    try:
        cursor.execute(
            """
            INSERT INTO treino_exercicios 
                (treino_id, treino, exercicio_id, exercicio, series, repeticoes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                treino_id,
                "",  # campo 'treino' (texto) ficará vazio; você pode alterar conforme quiser
                exercicio_id,
                nome_exercicio,
                series,
                repeticoes
            )
        )
        conn.commit()
        return {"status": "sucesso", "mensagem": "Exercício atribuído ao treino com sucesso!"}
    except sqlite3.IntegrityError:
        return {"status": "erro", "mensagem": "Este exercício já está atribuído a este treino."}
    finally:
        conn.close()

# ----------------------------------------KPI EXISTENTES---------------------------------------------------
def get_total_clientes():
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_total_planos():
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM planos")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_total_pagamentos_mes():
    df_pag = carregar_pagamentos()
    if df_pag.empty:
        return 0
    hoje = pd.to_datetime(datetime.datetime.now())
    filt = (
        (df_pag["data_pagamento"].dt.month == hoje.month) &
        (df_pag["data_pagamento"].dt.year  == hoje.year)
    )
    return int(df_pag.loc[filt].shape[0])

def get_media_idade_clientes():
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    df_idade = pd.read_sql_query("SELECT idade FROM clientes", conn)
    conn.close()
    if df_idade.empty:
        return 0.0
    return float(df_idade["idade"].mean())

def get_clientes_ativos():
    """
    Conta quantos clientes têm pelo menos um treino cujo data_fim >= hoje.
    """
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT cliente_id)
        FROM treinos
        WHERE date(data_fim) >= date('now');
    """)
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def get_receita_mes_atual():
    """
    Soma todos os valores_pago de pagamentos cujo data_pagamento está no mês/ano atuais.
    """
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    query = """
        SELECT IFNULL(SUM(valor_pago), 0)
        FROM pagamentos
        WHERE strftime('%Y', data_pagamento) = strftime('%Y', 'now')
          AND strftime('%m', data_pagamento) = strftime('%m', 'now');
    """
    cursor = conn.cursor()
    cursor.execute(query)
    total = cursor.fetchone()[0] or 0.0
    conn.close()
    return float(total)

def get_novos_clientes_30dias():
    """
    Conta quantos clientes iniciaram treino nos últimos 30 dias
    (considera-se que cada cliente tem pelo menos um registro em treinos).
    """
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT cliente_id)
        FROM treinos
        WHERE date(data_inicio) >= date('now', '-30 day');
    """)
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def get_top1_plano():
    """
    Retorna uma lista contendo exatamente um tupla: (nome_do_plano, qtd_clientes).
    """
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    query = """
        SELECT p.nome AS plano, COUNT(*) AS total_clientes
        FROM clientes c
        JOIN planos p ON c.plano_id = p.id
        GROUP BY p.nome
        ORDER BY total_clientes DESC
        LIMIT 1;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Exemplo de retorno: [("Premium", 132)]
    return list(df.itertuples(index=False, name=None))

def get_receita_por_mes():
    """
    Retorna um DataFrame com duas colunas:
      - mes (string no formato 'YYYY-MM')
      - total (soma de valor_pago)
    agrupado por mês, ordenado de forma crescente.
    """
    conn = sqlite3.connect("academia_db.db", check_same_thread=False)
    query = """
        SELECT 
            strftime('%Y-%m', data_pagamento) AS mes,
            IFNULL(SUM(valor_pago), 0)       AS total
        FROM pagamentos
        GROUP BY mes
        ORDER BY mes;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df