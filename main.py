import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect('academia.db')
cursor = conn.cursor()







st.set_page_config(page_title="Sistema de Academia Senai", layout="wide")
st.title("🌍 Academia Senai")
st.divider()