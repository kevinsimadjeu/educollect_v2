from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)

import os
DB_CONFIG = {
    "host":     os.environ.get("MYSQLHOST", "localhost"),
    "user":     os.environ.get("MYSQLUSER", "root"),
    "password": os.environ.get("MYSQLPASSWORD", "Kev_in@stkf"),      
    "database": os.environ.get("MYSQLDATABASE", "educollect_v2"),
    "port" :    int(os.environ.get("MYSQLPORT", "3306"))
}


MATIERES = {
    "Informatique / Génie Logiciel": [
        "Algorithmique & Structures de données",
        "Programmation Java",
        "Programmation Python",
        "Programmation C/C++",
        "Base de données (SQL)",
        "Base de données (NoSQL)",
        "Réseaux informatiques",
        "Système d'exploitation",
        "Mathématiques discrètes",
        "Génie logiciel & UML",
        "Architecture des ordinateurs",
        "Intelligence artificielle",
        "Développement Web",
        "Sécurité informatique",
    ],
    "Réseaux & Télécoms": [
        "Protocoles réseau (TCP/IP)",
        "Sécurité & Cryptographie",
        "Administration système Linux",
        "Téléphonie IP (VoIP)",
        "Routage & Switching",
        "Programmation réseau",
        "Réseaux sans fil (WiFi/4G/5G)",
        "Supervision réseau",
        "Fibre optique & transmission",
        "Mathématiques des télécoms",
    ],
    "Mathématiques": [
        "Analyse (fonctions, limites, intégrales)",
        "Algèbre linéaire",
        "Probabilités & Statistiques",
        "Méthodes numériques",
        "Géométrie différentielle",
        "Topologie",
        "Équations différentielles",
        "Théorie des groupes",
        "Logique mathématique",
        "Optimisation",
    ],
    "Gestion / Économie": [
        "Comptabilité générale",
        "Comptabilité analytique",
        "Microéconomie",
        "Macroéconomie",
        "Statistiques & Probabilités",
        "Droit des affaires",
        "Marketing",
        "Gestion de projet",
        "Finance d'entreprise",
        "Fiscalité",
    ],
    "Autre": [
        "Anglais académique",
        "Méthodologie de recherche",
        "Expression écrite & orale",
        "Éthique professionnelle",
        "Culture générale",
    ],
}

NIVEAUX = ["L1", "L2", "L3", "Master 1", "Master 2"]
FILIERES = list(MATIERES.keys())


def get_db():
    
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"[ERREUR MySQL] {e}")
        return None



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/formulaire")
def formulaire():
    return render_template(
        "formulaire.html",
        niveaux=NIVEAUX,
        filieres=FILIERES,
        matieres=MATIERES
    )


#matières selon filière 
@app.route("/api/matieres/<filiere>")
def api_matieres(filiere):
    liste = MATIERES.get(filiere, [])
    return jsonify(liste)


#SOUMISSION
@app.route("/soumettre", methods=["POST"])
def soumettre():
    matricule  = request.form.get("matricule", "").strip().upper()
    niveau     = request.form.get("niveau", "").strip()
    filiere    = request.form.get("filiere", "").strip()
    difficiles = request.form.getlist("matieres_difficiles")
    pratiques  = request.form.getlist("matieres_pratique")

    #Validation 
    erreurs = []
    if not matricule:
        erreurs.append("Le matricule est obligatoire.")
    if niveau not in NIVEAUX:
        erreurs.append("Niveau académique invalide.")
    if filiere not in FILIERES:
        erreurs.append("Filière invalide.")
    if not difficiles:
        erreurs.append("Sélectionne au moins une matière difficile.")
    if not pratiques:
        erreurs.append("Sélectionne au moins une matière nécessitant plus de pratique.")

    if erreurs:
        return render_template(
            "formulaire.html",
            niveaux=NIVEAUX, filieres=FILIERES,
            matieres=MATIERES, erreurs=erreurs,
            form_data=request.form
        )

    conn = get_db()
    if not conn:
        return render_template(
            "formulaire.html",
            niveaux=NIVEAUX, filieres=FILIERES,
            matieres=MATIERES,
            erreurs=["Connexion base de données impossible. Réessaie."]
        )

    try:
        cursor = conn.cursor()

        # Vérifier doublon matricule
        cursor.execute("SELECT id FROM reponses WHERE matricule = %s", (matricule,))
        if cursor.fetchone():
            return render_template(
                "formulaire.html",
                niveaux=NIVEAUX, filieres=FILIERES,
                matieres=MATIERES,
                erreurs=[f"Le matricule {matricule} a déjà soumis une réponse."]
            )

        
        cursor.execute(
            "INSERT INTO reponses (matricule, niveau, filiere) VALUES (%s, %s, %s)",
            (matricule, niveau, filiere)
        )
        reponse_id = cursor.lastrowid

        
        for m in difficiles:
            cursor.execute(
                "INSERT INTO matieres_difficiles (reponse_id, matiere) VALUES (%s, %s)",
                (reponse_id, m)
            )

        
        for m in pratiques:
            cursor.execute(
                "INSERT INTO matieres_pratique (reponse_id, matiere) VALUES (%s, %s)",
                (reponse_id, m)
            )

        conn.commit()

    except Error as e:
        print(f"[ERREUR INSERT] {e}")
        return render_template(
            "formulaire.html",
            niveaux=NIVEAUX, filieres=FILIERES,
            matieres=MATIERES,
            erreurs=["Erreur lors de l'enregistrement. Réessaie."]
        )
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard", matricule=matricule))


#DASHBOARD
@app.route("/dashboard")
def dashboard():
    matricule = request.args.get("matricule", "")
    conn = get_db()

    stats = {
        "total_reponses": 0,
        "top_difficiles": [],       
        "top_pratique": [],         
        "par_niveau_diff": {},      
        "par_niveau_prat": {},      
        "ma_reponse": None,         
        "mes_difficiles": [],
        "mes_pratiques": [],
        "niveaux": NIVEAUX,
    }

    if not conn:
        return render_template("dashboard.html", stats=stats)

    try:
        cursor = conn.cursor(dictionary=True)

        # Total réponses
        cursor.execute("SELECT COUNT(*) AS total FROM reponses")
        stats["total_reponses"] = cursor.fetchone()["total"]

        # Top 10 matières difficiles globales
        cursor.execute("""
            SELECT matiere, COUNT(*) AS nb
            FROM matieres_difficiles
            GROUP BY matiere
            ORDER BY nb DESC
            LIMIT 10
        """)
        stats["top_difficiles"] = cursor.fetchall()

        # Top 10 matières nécessitant pratique globales
        cursor.execute("""
            SELECT matiere, COUNT(*) AS nb
            FROM matieres_pratique
            GROUP BY matiere
            ORDER BY nb DESC
            LIMIT 10
        """)
        stats["top_pratique"] = cursor.fetchall()

        # Top 5 difficiles par niveau
        for niv in NIVEAUX:
            cursor.execute("""
                SELECT md.matiere, COUNT(*) AS nb
                FROM matieres_difficiles md
                JOIN reponses r ON r.id = md.reponse_id
                WHERE r.niveau = %s
                GROUP BY md.matiere
                ORDER BY nb DESC
                LIMIT 5
            """, (niv,))
            stats["par_niveau_diff"][niv] = cursor.fetchall()

        # Top 5 pratique par niveau
        for niv in NIVEAUX:
            cursor.execute("""
                SELECT mp.matiere, COUNT(*) AS nb
                FROM matieres_pratique mp
                JOIN reponses r ON r.id = mp.reponse_id
                WHERE r.niveau = %s
                GROUP BY mp.matiere
                ORDER BY nb DESC
                LIMIT 5
            """, (niv,))
            stats["par_niveau_prat"][niv] = cursor.fetchall()

        # Réponse de l'étudiant actuel
        if matricule:
            cursor.execute(
                "SELECT * FROM reponses WHERE matricule = %s", (matricule,)
            )
            stats["ma_reponse"] = cursor.fetchone()

            if stats["ma_reponse"]:
                rid = stats["ma_reponse"]["id"]
                cursor.execute(
                    "SELECT matiere FROM matieres_difficiles WHERE reponse_id = %s", (rid,)
                )
                stats["mes_difficiles"] = [r["matiere"] for r in cursor.fetchall()]

                cursor.execute(
                    "SELECT matiere FROM matieres_pratique WHERE reponse_id = %s", (rid,)
                )
                stats["mes_pratiques"] = [r["matiere"] for r in cursor.fetchall()]

    except Error as e:
        print(f"[ERREUR SELECT] {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard.html", stats=stats, matricule=matricule)



if __name__ == "__main__":
    
   import os
   
   port = int(os.environ.get("PORT", 5000))
   app.run(debug=False, host="0.0.0.0", port=port)
