import pandas as pd

# Définir les données des étudiants
data = {
    'nom': ["Yael Fregier", "Yoyo fregier"],
    'email': ["yael.fregier@gmail.com", "yael.fregier@univ-artois.fr"]
}

# Créer le DataFrame
df = pd.DataFrame(data)

# Sauvegarder le DataFrame dans un fichier Excel
df.to_excel("liste_etudiants.xlsx", index=False)

print("Le fichier liste_etudiants.xlsx a été créé avec succès.")
