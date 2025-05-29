import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.MATERIA,
                    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css"],
                suppress_callback_exceptions=True
               )
app.title = "Dashboard de Estoque"
server = app.server