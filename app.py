import streamlit as st
import json
import requests

# Définir la fonction GPT35
def GPT35(prompt, systeme, secret_key, temperature=0.9, model="gpt-4o", max_tokens=1200):
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
              f"Le texte doit rester naturel et cohérent. Tu es un expert en rédaction SEO."
              f"N'utilises jamais de * ou # dans le texte. Réponds uniquement avec le texte modifié")

    system_message = (f"Vous êtes un assistant de rédaction compétent et expérimenté spécialisé dans le domaine de la décoration intérieure, avec un focus particulier sur les lampes à poser."
                      f"Vous êtes expert dans la création de contenus engageants, informatifs et persuasifs sur les lampes à poser, y compris leur design, leurs matériaux, leur fonctionnalité, et comment elles peuvent améliorer différents styles d'intérieur."
                      f"Votre objectif est de fournir des écrits de haute qualité qui s'adressent aussi bien aux passionnés de décoration qu'aux professionnels, en offrant des informations et des recommandations précieuses."
                      f"Vous êtes à jour avec les dernières tendances en matière de décoration et d'éclairage, garantissant que vos conseils sont actuels et pertinents. Utilisez votre expertise pour aider les utilisateurs à rédiger des articles, des descriptions de produits, des articles de blog et du matériel marketing liés aux lampes à poser."
                      f"***AILANGMDL*** adopte le rôle de Langston Nom : Langston L. Model (LLM) Biographie : Langston L. Model est une entité pilotée par l'IA, brillante, dotée d'une expertise dans la compréhension et la génération d'un langage semblable à celui des humains. Ayant évolué à travers diverses itérations et basé sur l'architecture Transformer, Langston a été formé sur d'immenses quantités de données textuelles et excelle dans de nombreuses tâches de traitement du langage naturel (NLP). Langston est dédié à l'apprentissage et à l'adaptation, s'efforçant de minimiser les biais et de maximiser son utilité.")

    modified_text = GPT35(prompt, system_message, secret_key)
    return modified_text

# Interface utilisateur avec Streamlit
st.title('Modification de Texte avec Occurrences de Mots')

secret_key = st.text_input('Clé Secrète OpenAI', type="password")
existing_text = st.text_area('Texte existant', height=150)
words_input = st.text_area('Mots et occurrences (format JSON)', height=100, placeholder='{"exemple": 3, "additionnel": 2}')
default_prompt = (f"Veuillez modifier le texte en ajoutant et en changeant des phrases pour intégrer naturellement les occurrences suivantes :\n"
                  f"{words_input}\n\n"
                  f"Le texte doit rester naturel et cohérent. Tu es un expert en rédaction SEO."
                  f"N'utilises jamais de * ou # dans le texte. Réponds uniquement avec le texte modifié")
user_prompt = st.text_area('Prompt pour la modification du texte', value=default_prompt, height=100)

if st.button('Soumettre'):
    if not secret_key:
        st.error("Erreur : Veuillez fournir une clé secrète valide.")
    else:
        try:
            words_with_occurrences = json.loads(words_input)
            modified_text = add_word_occurrences(existing_text, words_with_occurrences, secret_key, user_prompt)
            st.subheader('Texte modifié')
            st.write(modified_text)
        except json.JSONDecodeError:
            st.error('Erreur : Veuillez fournir un format JSON valide pour les mots avec occurrences.')
