from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
import uvicorn

# Configuração do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./almoxarifado.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de dados
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, index=True)
    descricao = Column(String, index=True)
    codigo = Column(String, unique=True, index=True)
    disponibilidade = Column(Boolean, default=True)

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Instância do FastAPI
app = FastAPI()

# Dependência para conexão com o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para ler o arquivo Excel e carregar os dados no banco
def load_data_from_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        # Verifica se o código já existe
        existing_item = db.query(Item).filter(Item.codigo == row['codigo']).first()
        if existing_item is None:  # Se não existe, insere o novo item
            db_item = Item(
                categoria=row['categoria'],
                descricao=row['descricao'],
                codigo=row['codigo'],
                disponibilidade=True
            )
            db.add(db_item)
        else:
            print(f"Item com código {row['codigo']} já existe. Ignorando...")  # Mensagem de log para duplicatas
    db.commit()

# Carregar dados do arquivo Excel
with SessionLocal() as db:
    load_data_from_excel("almoxarifado.xlsx", db)

# Endpoint para listar itens
@app.get("/items/")
def read_items(categoria: str = None, descricao: str = None, codigo: str = None, db: Session = Depends(get_db)):
    query = db.query(Item)
    if categoria:
        query = query.filter(Item.categoria.ilike(f"%{categoria}%"))
    if descricao:
        query = query.filter(Item.descricao.ilike(f"%{descricao}%"))
    if codigo:
        query = query.filter(Item.codigo.ilike(f"%{codigo}%"))
    return query.all()

# Rodar o FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Código do Streamlit
import streamlit as st
import requests

st.title("Almoxarifado")

# Campos de filtro
categoria = st.text_input("Categoria")
descricao = st.text_input("Descrição")
codigo = st.text_input("Código")

# URL do FastAPI
fastapi_url = "http://127.0.0.1:8000/items/"

if st.button("Buscar Itens"):
    response = requests.get(fastapi_url, params={
        "categoria": categoria,
        "descricao": descricao,
        "codigo": codigo
    })
    if response.status_code == 200:
        items = response.json()
        st.write("Itens encontrados:")
        for item in items:
            st.write(f"{item['codigo']}: {item['descricao']} (Categoria: {item['categoria']})")
    else:
        st.write("Erro ao buscar itens.")

