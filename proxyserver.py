from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

lock = threading.Lock()

PROXY_FILE = "proxy.txt"

@app.route("/delete_all_proxies", methods=["DELETE"])
def delete_all_proxies():
    """Apaga todos os proxies do arquivo de texto."""
    with lock:
        with open(PROXY_FILE, "w") as file:
            file.write("")
    return jsonify({"message": "All proxies deleted successfully"}), 200

def ler_proxies():
    """Lê todos os proxies do arquivo, mesmo que estejam em uma única linha."""
    with lock:
        with open(PROXY_FILE, "r") as file:
            data = file.read()
            proxies = data.replace("\n", " ").split()
            return proxies

def salvar_proxies(proxies):
    """Salva os proxies de volta ao arquivo em formato de uma única linha."""
    with lock:
        with open(PROXY_FILE, "w") as file:
            file.write(" ".join(proxies) + "\n")

@app.route("/get_proxy", methods=["GET"])
def get_proxy():
    proxies = ler_proxies()
    if not proxies:
        return jsonify({"error": "No proxies available"}), 404

    proxy = proxies.pop(0) 
    salvar_proxies(proxies)
    return jsonify({"proxy": proxy})

@app.route("/add_proxy", methods=["POST"])
def add_proxy():
    new_proxies = request.json.get("proxies", [])
    if not new_proxies:
        return jsonify({"error": "No proxies provided"}), 400

    proxies = ler_proxies()
    proxies_set = set(proxies)  # Converte a lista de proxies existentes para um conjunto
    new_proxies_set = set(new_proxies)  # Converte a lista de novos proxies para um conjunto

    unique_proxies = new_proxies_set - proxies_set
    proxies_set.update(unique_proxies)

    salvar_proxies(list(proxies_set))

    return jsonify({
        "message": "Proxies added successfully",
        "added_proxies": list(unique_proxies)
    })

@app.route("/check_duplicates", methods=["GET"])
def check_duplicates():
    proxies = ler_proxies()
    total_proxies = len(proxies)
    unique_proxies = len(set(proxies))
    duplicates = total_proxies - unique_proxies

    return jsonify({
        "total_proxies": total_proxies,
        "unique_proxies": unique_proxies,
        "duplicate_count": duplicates
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)