# controle_financeiro_simples.py
# Requisitos: pip install pandas matplotlib openpyxl

import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ------------------------------
# CONFIGURAÇÃO DO BANCO LOCAL
# ------------------------------
DB_NAME = "empresa_financeiro.db"

def criar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,          -- "receita" ou "despesa"
            categoria TEXT,
            valor REAL,
            descricao TEXT,
            conta TEXT          -- "caixa", "banco1", "cartao", etc
        )
    ''')
    
    conn.commit()
    conn.close()

# ------------------------------
# FUNÇÕES BÁSICAS
# ------------------------------
def adicionar_lancamento(tipo, categoria, valor, descricao="", conta="Caixa"):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lancamentos (data, tipo, categoria, valor, descricao, conta)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data, tipo, categoria, valor, descricao, conta))
    
    conn.commit()
    conn.close()
    print(f"Lançamento {tipo} de R$ {valor:.2f} adicionado com sucesso!")

def ver_fluxo_caixa():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM lancamentos ORDER BY data", conn)
    conn.close()
    
    if df.empty:
        print("Ainda não existem lançamentos.")
        return
    
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = df.apply(lambda x: x['valor'] if x['tipo'] == 'receita' else -x['valor'], axis=1)
    
    df['saldo_acumulado'] = df['valor'].cumsum()
    
    print("\nFluxo de Caixa:")
    print(df[['data', 'tipo', 'categoria', 'valor', 'descricao', 'saldo_acumulado']].to_string(index=False))
    
    # Gráfico simples
    plt.figure(figsize=(10,5))
    plt.plot(df['data'], df['saldo_acumulado'], marker='o')
    plt.title("Evolução do Saldo")
    plt.xlabel("Data")
    plt.ylabel("Saldo Acumulado (R$)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ------------------------------
# MENU SIMPLES
# ------------------------------
def menu():
    criar_banco()
    while True:
        print("\n" + "="*40)
        print(" CONTROLE FINANCEIRO SIMPLES - OFFLINE")
        print("="*40)
        print("1. Adicionar Receita")
        print("2. Adicionar Despesa")
        print("3. Ver Fluxo de Caixa")
        print("4. Sair")
        
        op = input("\nEscolha: ")
        
        if op == "1":
            valor = float(input("Valor da receita: R$ "))
            cat = input("Categoria (ex: Vendas, Recebimento cliente): ")
            desc = input("Descrição (opcional): ")
            adicionar_lancamento("receita", cat, valor, desc)
            
        elif op == "2":
            valor = float(input("Valor da despesa: R$ "))
            cat = input("Categoria (ex: Aluguel, Fornecedor, Energia): ")
            desc = input("Descrição (opcional): ")
            adicionar_lancamento("despesa", cat, valor, desc)
            
        elif op == "3":
            ver_fluxo_caixa()
            
        elif op == "4":
            print("Até mais! Dados salvos localmente.")
            break
            
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()