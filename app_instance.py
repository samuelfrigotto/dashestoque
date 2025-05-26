# app_instance.py
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True # Importante para callbacks com saídas em abas não ativas ou múltiplos callbacks
               )
app.title = "Dashboard de Estoque" # Definir o título do app aqui
server = app.server # Para compatibilidade com alguns servidores de deploy como Gunicorn