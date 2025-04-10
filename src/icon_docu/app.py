from flask import Flask, jsonify, send_from_directory
import os
import json
import TexSoup
from threading import Thread
from latex_graph_webapp.watcher import watch_node_files

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '../../static'))

BASE_DIR = os.path.dirname(__file__)
NODE_DIR = os.path.join(BASE_DIR, 'nodes')
MACRO_FILE = os.path.join(BASE_DIR, 'macros.tex')
CACHE_FILE = os.path.join(BASE_DIR, '.graph_cache.json')

_graph_data = None

def load_node_from_file(name):
    try:
        with open(os.path.join(NODE_DIR, f"{name}.tex"), "r") as f:
            return f.read()
    except FileNotFoundError:
        return name  # fallback

def tex_macros_to_mathjax(filename: str) -> dict:
    latex_macros = {}
    with open(filename, "r") as f:
        soup = TexSoup.TexSoup(f.read())
        for command in ["newcommand", "renewcommand"]:
            for macro in soup.find_all(command):
                name = macro.args[0].string.strip("\\")
                latex_macros[name] = f"{{{macro.args[-1].string}}}"
                if len(macro.args) == 3:
                    latex_macros[name] = [latex_macros[name], int(macro.args[1].string)]
    return latex_macros

def load_graph():
    return {
        "nodes": [
            {"data": {"id": "a", "label": load_node_from_file("a")}},
            {"data": {"id": "b", "label": load_node_from_file("b")}},
        ],
        "edges": [
            {"data": {"source": "a", "target": "b"}}
        ]
    }

@app.route('/graph')
def get_graph():
    global _graph_data
    if _graph_data is None:
        _graph_data = load_graph()
    return jsonify(_graph_data)

@app.route('/macros')
def get_macros():
    macros = tex_macros_to_mathjax(MACRO_FILE)
    return jsonify(macros)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

def main():
    # Start file watcher in background
    def on_change():
        global _graph_data
        _graph_data = load_graph()
    Thread(target=watch_node_files, args=(NODE_DIR, on_change), daemon=True).start()
    app.run(debug=True)

if __name__ == '__main__':
    main()

