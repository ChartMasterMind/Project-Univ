# pyspark apache est une api de apache spark ==> apach spark est un service comme pandas qui permet d'utiliser des fonction et des methode apach spark sur notre code.

#pour l'utiliser dans python, il faut utiliser pyspark

# pyspark permet des traitement de base de donnée de big data ( cad avec des million de ligne) tres rapidement la où pandas serait bcp plus lent.

# sa permet aussi donc de faire du machine learning dans des termps plus rapide ( car il faut eneormement de donn&ée pour faire des papprentissage)

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pandas as pd
import logging

app = Flask(__name__)

# Configure the secret key for session management
app.secret_key = 'your_secret_key_here'

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def afficher_page_principale():
    return render_template("cocoi.html")

@app.route("/admin", methods=["POST"])
def verification_utilisateur_mdp():
    try:
        data = request.get_json()
        logging.debug(f"Data received: {data}")

        utilisateur = data.get("utilisateur_name")
        mot_de_passe = data.get("mot_de_pass")

        if not utilisateur or not mot_de_passe:
            logging.error("Données manquantes")
            return jsonify({"success": False, "error": "Données manquantes"}), 400

        base = {
            "base_id": ["patrick_cheminou65", "julie78", "marie_lafofolle", "mama2001"],
            "mdp": ["123456789", "machoupinette2000@", "laprincesse908", "Massyle2001"]
        }

        bs = pd.DataFrame(base)
        logging.debug(f"DataFrame actuel: {bs}")

        dictionnaire_utilisateurs_mdp = dict(zip(bs["base_id"], bs["mdp"]))
        logging.debug(f"Dictionary actuel des user associé au mdp: {dictionnaire_utilisateurs_mdp}")

        if utilisateur in dictionnaire_utilisateurs_mdp:
            if dictionnaire_utilisateurs_mdp[utilisateur] == mot_de_passe:
                session['utilisateur_name'] = utilisateur  # Store username in session
                logging.info("Utilisateur authentifié avec succès")
                return jsonify({"success": True}), 200
            else:
                logging.warning("Nom d'utilisateur ou mot de passe incorrect")
                return jsonify({"success": False, "error": "Nom d'utilisateur ou mot de passe incorrect"}), 401
        else:
            logging.warning("Nom d'utilisateur ou mot de passe incorrect")
            return jsonify({"success": False, "error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return jsonify({"success": False, "error": "Une erreur s'est produite sur le serveur"}), 500

@app.route("/admin", methods=["GET"])
def admin_page():
    if 'utilisateur_name' in session:
        username = session['utilisateur_name']
        return render_template("admin.html", username=username)
    else:
        logging.info("Utilisateur non authentifié, redirection vers la page principale")
        return redirect(url_for("/"))
    
@app.route("/admin/message", methods = ["GET"])

def message_page():
    username = session['utilisateur_name']
    return render_template("message.html" , username = username)

    

if __name__ == "__main__":
    app.run(debug=True)
