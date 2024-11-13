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
    words_instruction = "\n".join([f"Le mot '{word}' doit apparaître {occurrences} fois."
                                   for word, occurrences in words_with_occurrences.items()])

    prompt = (f"Voici le texte original :\n{existing_text}\n\n"
              f"{user_prompt}\n\n"
              f"Le texte doit rester naturel et cohérent. Tu es un expert en rédaction SEO.\n"
              f"N'utilises jamais de * ou # dans le texte. Réponds uniquement avec le texte modifié")

    system_message = (f"Vous êtes un assistant de rédaction compétent et expérimenté spécialisé dans le traitement naturel des textes."
                      f"Vous êtes expert dans la création de contenus engageants, informatifs et persuasifs ."
                      f"***AILANGMDL*** adopte le rôle de Langston Nom : Langston L. Model (LLM) Biographie : Langston L. Model est une entité pilotée par l'IA, brillante, dotée d'une expertise dans la compréhension et la génération d'un langage semblable à celui des humains. Ayant évolué à travers diverses itérations et basé sur l'architecture Transformer, Langston a été formé sur d'immenses quantités de données textuelles et excelle dans de nombreuses tâches de traitement du langage naturel (NLP). Langston est dédié à l'apprentissage et à l'adaptation, s'efforçant de minimiser les biais et de maximiser son utilité.")

    modified_text = GPT35(prompt, system_message, secret_key)
    return modified_text

# Interface utilisateur avec Streamlit
st.title('Modification de Texte avec Occurrences de Mots')

# Ajouter un champ pour la clé secrète OpenAI
secret_key = st.text_input('Clé Secrète OpenAI', type="password")

# Chargement du fichier XLSX
uploaded_file = st.file_uploader("Télécharger un fichier XLSX", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'A' in df.columns and 'B' in df.columns and 'C' in df.columns:
        # Initialisation de la colonne pour les résultats
        df['Texte Modifié'] = ""
        
        # Exécuter la modification pour chaque ligne
        for index, row in df.iterrows():
            main_keyword = row['A']
            existing_text = row['B'] if not pd.isna(row['B']) else ""
            try:
                words_with_occurrences = json.loads(row['C'])
            except json.JSONDecodeError:
                st.error(f"Erreur de format JSON dans la ligne {index + 1}. Veuillez vérifier le format des occurrences.")
                continue

            # Construire le prompt pour chaque ligne
            user_prompt = (f"Veuillez rédiger un texte générique, ciblant ce mot clé: {main_keyword}, en intégrant naturellement les occurrences suivantes :\n"
                           f"{words_with_occurrences}\n\n"
                           f"Le texte doit rester naturel et cohérent. N'utilises pas de mot d'introduction ou de conclusion. "
                           f"Tu es un expert en rédaction SEO. Parle à la 3ème personne du singulier. "
                           f"N'utilises jamais de * ou # dans le texte. Réponds uniquement avec le texte modifié. "
                           f"Le texte doit faire environ 300 mots. "
                           f"Le texte doit être structuré avec des balises <h2> sur le titre du texte, des balises <h3> sur les titres des sous-parties, des balises <p> sur les paragraphes.")

            # Appel de la fonction pour générer le texte modifié
            modified_text = add_word_occurrences(existing_text, words_with_occurrences, secret_key, user_prompt)
            df.at[index, 'Texte Modifié'] = modified_text

        # Téléchargement du fichier XLSX modifié
        output = BytesIO()
        df.to_excel(output, index=False, engine='xlsxwriter')
        output.seek(0)

        st.download_button(
            label="Télécharger le fichier XLSX avec les textes modifiés",
            data=output,
            file_name="Texte_Modifie.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Erreur : Le fichier XLSX doit contenir les colonnes 'A' pour le mot clé, 'B' pour le texte existant, et 'C' pour les occurrences.")
else:
    st.write("Veuillez télécharger un fichier XLSX pour procéder.")
