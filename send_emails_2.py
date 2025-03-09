import os
import uuid
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, render_template_string
from models import db, Student, Reponse  # Assurez-vous que models.py définit bien Student et Reponse

app = Flask(__name__)

# --- Configuration de la base de données ---
# Chemin absolu vers le fichier de base de données
db_file = "/Users/yaelfregier/Downloads/suivi etudiants/instance/students.db"
db_folder = os.path.dirname(db_file)
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Pour un chemin absolu sous Unix/Mac, on utilise 4 slash après sqlite:
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    print("Les tables ont été créées ou existent déjà.")

# --- Configuration SMTP ---
SMTP_SERVER = "smtprouter.test.fr"  # Remplacez par votre serveur SMTP réel
SMTP_PORT = 587
SMTP_USER = "super.dupont@test.fr"
SMTP_PASSWORD = "gotlieb4ever!"

def send_email(to_address, nom, token):
    # Le lien du formulaire, à adapter selon votre environnement (ici en local sur le port 8000)
    url_formulaire = f"http://localhost:8000/form?token={token}"
    subject = "Mise à jour de votre parcours post-licence"
    body = (
        f"Bonjour {nom},\n\n"
        f"Merci de bien vouloir compléter votre parcours en cliquant sur le lien suivant :\n"
        f"{url_formulaire}\n\n"
        "Cordialement."
    )
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_address

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email envoyé à {to_address}")
    except Exception as e:
        print(f"Erreur lors de l'envoi à {to_address} : {e}")

# --- Importation des étudiants et envoi des emails ---
# Création d'une session SQLAlchemy (pour la partie envoi d'emails)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

# Lecture du fichier Excel (vérifiez que "liste_etudiants.xlsx" est dans le dossier courant)
df = pd.read_excel("liste_etudiants.xlsx")
for index, row in df.iterrows():
    nom = row["nom"]
    email = row["email"]
    token = str(uuid.uuid4())
    # Vérifier si l'étudiant n'est pas déjà enregistré
    if session.query(Student).filter_by(email=email).first() is None:
        student = Student(nom=nom, email=email, token=token, date_envoi=datetime.utcnow())
        session.add(student)
        session.commit()
        send_email(email, nom, token)
    else:
        print(f"L'étudiant {email} est déjà enregistré.")
session.close()

# --- Définition de la route pour le formulaire ---
@app.route('/form', methods=['GET', 'POST'])
def form():
    token = request.args.get('token')
    if not token:
        return "Token manquant", 400
    # Recherche de l'étudiant par token via le query de Flask-SQLAlchemy
    student = Student.query.filter_by(token=token).first()
    if not student:
        return "Étudiant non trouvé", 404

    if request.method == "POST":
        formation = request.form.get('formation')
        etablissement = request.form.get('etablissement')
        parcours = request.form.get('parcours')
        # Enregistrer la réponse dans la table Reponse
        reponse = Reponse(
            student_id=student.id,
            formation=formation,
            etablissement=etablissement,
            parcours=parcours,
            date_reponse=datetime.utcnow()
        )
        db.session.add(reponse)
        db.session.commit()
        return "Merci pour votre réponse !"
    
    # Template HTML minimal pour le formulaire
    form_html = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <title>Mise à jour du parcours</title>
    </head>
    <body>
      <h1>Bonjour {{ student.nom }}</h1>
      <p>Email : {{ student.email }}</p>
      <form method="POST">
        <div>
          <label for="formation">Formation suivie :</label>
          <input type="text" name="formation" id="formation" required>
        </div>
        <div>
          <label for="etablissement">Établissement d'inscription :</label>
          <input type="text" name="etablissement" id="etablissement" required>
        </div>
        <div>
          <label for="parcours">Parcours professionnel :</label>
          <textarea name="parcours" id="parcours"></textarea>
        </div>
        <button type="submit">Envoyer</button>
      </form>
    </body>
    </html>
    '''
    return render_template_string(form_html, student=student)

# --- Lancement de l'application Flask ---
if __name__ == '__main__':
    # Le serveur s'exécutera sur le port 8000 pour être compatible avec l'URL utilisée dans l'email
    app.run(debug=True, port=8000)
