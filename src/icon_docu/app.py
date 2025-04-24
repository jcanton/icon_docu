import os
from threading import Thread

import TexSoup
from flask import Flask, jsonify, send_from_directory

from icon_docu.watcher import watch_node_files

app = Flask(
    __name__, static_folder=os.path.join(os.path.dirname(__file__), "../../static")
)

BASE_DIR = os.path.dirname(__file__)
NODE_DIR = os.path.join(BASE_DIR, "nodes")
MACRO_FILE = os.path.join(BASE_DIR, "macros.tex")
CACHE_FILE = os.path.join(BASE_DIR, ".graph_cache.json")

_graph_data = None


def load_node_from_file(file_name):
    try:
        with open(os.path.join(NODE_DIR, f"{file_name}"), "r") as f:
            return f.read()
    except FileNotFoundError:
        return file_name  # fallback


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
    nodes = []
    for nodes_group in os.listdir(NODE_DIR):
        group_id = f"group_{nodes_group}"
        nodes.append({"data": {"id": group_id, "label": nodes_group}})
        if os.path.isdir(os.path.join(NODE_DIR, nodes_group)):
            group_nodes = [
                {
                    "data": {
                        "id": os.path.splitext(filename)[0],
                        "parent": group_id,
                        "label": load_node_from_file(os.path.join(nodes_group, filename)),
                        "nodeTitle": os.path.splitext(filename)[0],
                    }
                }
                for filename in os.listdir(os.path.join(NODE_DIR, nodes_group))
            ]
            nodes.extend(group_nodes)
    return {
        "nodes": nodes,
        "edges": [
            #
            # vn
            {"data": {"source": "compute_horizontal_gradient_of_exner_pressure_for_flat_coordinates", "target": "add_temporal_tendencies_to_vn"}},
            {"data": {"source": "predictor_stencils_2_3", "target": "compute_horizontal_gradient_of_exner_pressure_for_flat_coordinates"}},
            #
            {"data": {"source": "compute_horizontal_advection_of_rho_and_theta", "target": "add_temporal_tendencies_to_vn"}},
            #
            {"data": {"source": "compute_advective_normal_wind_tendency", "target": "add_temporal_tendencies_to_vn"}},
            {"data": {"source": "interpolate_to_cell_center", "target": "compute_advective_normal_wind_tendency"}},
            {"data": {"source": "interpolate_vn_to_ie_and_compute_ekin_on_edges", "target": "compute_advective_normal_wind_tendency"}},
            {"data": {"source": "compute_tangential_wind", "target": "compute_advective_normal_wind_tendency"}},
            {"data": {"source": "mo_math_divrot_rot_vertex_ri_dsl", "target": "compute_advective_normal_wind_tendency"}},
            {"data": {"source": "interpolate_contravariant_vertical_velocity_to_full_levels", "target": "compute_advective_normal_wind_tendency"}},
            #
            {"data": {"source": "compute_tangential_wind", "target": "interpolate_vn_to_ie_and_compute_ekin_on_edges"}},
            {"data": {"source": "interpolate_vn_to_ie_and_compute_ekin_on_edges", "target": "interpolate_to_cell_center"}},
            #
            # diffusion
            {"data": {"source": "calculate_nabla2_for_theta", "target": "update_theta_and_exner"}},
            {"data": {"source": "calculate_nabla2_and_smag_coefficients_for_vn", "target": "calculate_nabla2_for_theta"}},
            {"data": {"source": "calculate_nabla2_and_smag_coefficients_for_vn", "target": "apply_diffusion_to_vn"}},
            {"data": {"source": "calculate_nabla2_and_smag_coefficients_for_vn", "target": "calculate_nabla4"}},
            {"data": {"source": "mo_intp_rbf_rbf_vec_interpol_vertex", "target": "calculate_nabla2_and_smag_coefficients_for_vn"}},
            {"data": {"source": "mo_intp_rbf_rbf_vec_interpol_vertex", "target": "calculate_nabla4"}},
            {"data": {"source": "calculate_nabla4", "target": "apply_diffusion_to_vn"}},
        ]
    }


@app.route("/graph")
def get_graph():
    global _graph_data
    if _graph_data is None:
        _graph_data = load_graph()
    return jsonify(_graph_data)


@app.route("/macros")
def get_macros():
    macros = tex_macros_to_mathjax(MACRO_FILE)
    return jsonify(macros)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


def main():
    # Start file watcher in background
    def on_change():
        global _graph_data
        _graph_data = load_graph()

    Thread(target=watch_node_files, args=(NODE_DIR, on_change), daemon=True).start()
    app.run(debug=True)


if __name__ == "__main__":
    main()
