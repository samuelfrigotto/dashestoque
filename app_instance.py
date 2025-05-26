import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.MATERIA],
                suppress_callback_exceptions=True
               )
app.title = "Dashboard de Estoque"
server = app.server