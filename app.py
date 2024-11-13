import streamlit as st
import json
import requests
import pandas as pd
from io import BytesIO

# Configuration de la page Streamlit
st.set_page_config(
    layout="wide",
    page_title="Occurus Rewrite",
    page_icon="🍒"
)

# Définir la fonction GPT35
def GPT35(prompt, systeme, secret_key, temperature=0.9, model="gpt-4o-mini", max_tokens=1200):
    url = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": systeme},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {secret_key}"
    }

    response = requests.post(url, headers=headers, json=payload)
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()

# Fonction pour ajouter des occurrences de mots
def add_word_occurrences(existing_text, words_with_occurrences, secret_key, user_prompt):
    prompt = (f"Voici le texte original :\n{existing_text}\n\n"
              f"{user_prompt}\n\n"
              f"Le texte doit rester naturel et cohérent. Tu es un expert en rédaction SEO.\n"
              f"N'utilises jamais de * ou # dans le texte. Réponds uniquement avec le texte modifié.\n\n"
              f"Utilise ce brief pour structurer et optimiser le texte.")
    system_message = ("Vous êtes un assistant de rédaction compétent et expérimenté, spécialisé dans le traitement naturel des textes.")
    return GPT35(prompt, system_message, secret_key)

# Fonction pour vérifier la cohérence des textes
def review_content(text, secret_key):
    review_prompt = (f"Voici le texte généré :\n{text}\n\n"
                     f"Effectue une vérification et réécris le texte si nécessaire pour garantir la cohérence, l'uniformité et la correction des propos. "
                     f"Assure-toi que le texte reste naturel, fluide et qu'il respecte les consignes de SEO. "
                     f"Supprime les répétitions et améliore le ton si besoin, tout en conservant le sens du texte original. "
                     f"Réponds uniquement avec le texte révisé sans ajout d'annotations ou d'indications.")

    review_system_message = ("Vous êtes un assistant de révision expert, spécialisé dans l'optimisation et la cohérence des contenus générés par IA. "
                             "Votre objectif est de s'approcher le plus d'un contenu rédigé par un humain, rester pertinent et améliorer la clarté, la correction et la fluidité des textes, en évitant toute incohérence.")

    return GPT35(review_prompt, review_system_message, secret_key)

# Interface utilisateur avec Streamlit
st.title('Modification et Révision de Texte avec Occurrences de Mots')

# Ajouter un champ pour la clé secrète OpenAI
secret_key = st.text_input('Clé Secrète OpenAI', type="password")

# Layout pour les boutons d'import, d'exécution et de téléchargement
col1, col2, col3 = st.columns([1, 1, 1])

# Bouton pour charger le fichier
with col1:
    uploaded_file = st.file_uploader("Télécharger un fichier XLSX", type="xlsx", label_visibility="collapsed")

# Vérification que le fichier est chargé
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Vérification des colonnes
    if 'keyword' in df.columns and 'Text or not' in df.columns and 'Occurrences' in df.columns:
        df['Texte Modifié'] = ""  # Initialisation de la colonne pour les résultats
        df['Texte Révisé'] = ""   # Colonne pour les textes après révision

        # Initialisation de la barre de progression et du texte de statut
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_rows = len(df)

        # Bouton pour lancer la création des textes
        with col2:
            start_processing = st.button("Lancer la création des textes")

        if start_processing:
            # Exécuter la modification pour chaque ligne
            for index, row in df.iterrows():
                main_keyword = row['keyword']
                existing_text = row['Text or not'] if pd.notna(row['Text or not']) else ""
                
                # Charger les occurrences en JSON
                try:
                    words_with_occurrences = json.loads(row['Occurrences'])
                except json.JSONDecodeError:
                    st.error(f"Erreur de format JSON dans la ligne {index + 1}. Veuillez vérifier le format des occurrences.")
                    continue

                # Construire le prompt pour chaque ligne
                user_prompt = (f"Veuillez rédiger un texte générique en ciblant le mot clé principal : {main_keyword}. "
                               f"Incorporez naturellement les occurrences des mots suivants, sans forcer leur usage :\n"
                               f"{words_with_occurrences}\n\n"
                               f"Le texte doit être engageant, informatif et optimisé pour le SEO, avec un ton professionnel et fluide. "
                               f"Rédigez en utilisant la troisième personne du singulier et évitez toute introduction ou conclusion superflue. "
                               f"Assurez-vous de structurer le contenu avec les balises suivantes : "
                               f"- <h2> pour le titre principal du texte, "
                               f"- <h3> pour chaque sous-partie, et "
                               f"- <p> pour chaque paragraphe de contenu.\n\n"
                               f"N'utilisez jamais de caractères spéciaux comme * ou # dans le texte. Limitez-vous à un texte d'environ 300 mots.")

                # Afficher le statut actuel
                status_text.text(f"Texte en cours {index + 1} sur {total_rows}")

                # Appel de la fonction pour générer le texte modifié
                modified_text = add_word_occurrences(existing_text, words_with_occurrences, secret_key, user_prompt)
                df.at[index, 'Texte Modifié'] = modified_text
                
                # Appel de la fonction pour réviser le texte généré
                reviewed_text = review_content(modified_text, secret_key)
                df.at[index, 'Texte Révisé'] = reviewed_text

                # Mise à jour de la barre de progression
                progress_bar.progress((index + 1) / total_rows)

            # Préparation du fichier modifié pour le téléchargement
            output = BytesIO()
            df.to_excel(output, index=False, engine='xlsxwriter')
            output.seek(0)

            # Clear the status message after completion
            status_text.text("Traitement terminé.")
        else:
            output = None

        # Bouton pour télécharger le fichier modifié
        with col3:
            if output:
                st.download_button(
                    label="Télécharger le fichier XLSX avec les textes révisés",
                    data=output,
                    file_name="Texte_Modifie_Et_Revise.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.error("Erreur : Le fichier XLSX doit contenir les colonnes 'keyword', 'Text or not', et 'Occurrences'.")
else:
    st.write("Veuillez télécharger un fichier XLSX pour procéder.")
