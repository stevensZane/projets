import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import seaborn as sns
import webbrowser
import os
from utils import scrap_terrains, scrap_villas , google_forms, kobo_forms, mot_inspirant, streamdata_logo

# define the directory
UPLOAD_DIR = "update_files"

# ceci c'est pour créer le repertoire là ou les fichiers seront sauvegarder s'il n'existes pas déjà
if not os.path.exists(UPLOAD_DIR):
    os.mkdirs(UPLOAD_DIR)

# lister tous les fichiers contenus dans data
files = os.listdir(UPLOAD_DIR)

# La partie CSS pour le styling
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        width: 260px !important; 
        background-color: #f5f2ec; 
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #f0e8d9;
        color: #4b5320;
    }
    
    [data-testid="stHeader"] {
        background-color: #f0e8d9;
    }
    
    [data-testid="stSidebar"] button {
        width: 100%;
        color: #4b5320;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Initialisation de la session state pour le changement des pages
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Accueil"

# fonction pour le changement des pages
def change_page(page):
    st.session_state.selected_page = page

# Sidbar, contenu
with st.sidebar:
    st.title("StreamData")
    
    page = st.selectbox("Choisir une page", ["Accueil", "Scraper", "Upload", "Visualisation", "Bibliothèque", "Feedback"])
    st.session_state.selected_page = page
    st.markdown("---")
    
    st.write(f"**_{mot_inspirant}_**")
    
    # pour le boutton Soutenez-nous
    # en cliquant sur ce boutton, l'utilisateur peut envoyer un mail pour soutenir
    if st.sidebar.button("Soutenez-nous"):
        webbrowser.open("mailto:lasiebazoungoula@gmail.com")
    
    
    # Update the selected page
    
# Les differentes pages de l'appli
# Acceuil
if st.session_state.selected_page == "Accueil":
    st.title("Bienvenu sur StreamData")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"""
        Bienvenu sur **StreamData** - l'outil ultime pour scraper et visualiser vos données \n
        Ici, vous pouvez:
        - **Scraper des données avec BeautifulSoup**
        - **Charger et sauvegarder des fichiers** (CSV, XLSX)
        - **Visualiser** vos données en créant des graphes et autres...
        
        ---
        
        - Bibliothèques Python: streamlit, pandas, matplotlib, seaborn
        - Source de données: coinafrique. [Terrains](https://sn.coinafrique.com/categorie/terrains) | [Villas](https://sn.coinafrique.com/categorie/villas)
        
        ---
         
        ### **Comment ça fonctionne?** 
        1. Chargez votre fichier ou scrapez des données.
        2. Visualisez les données sous différents formats.
        3. Analysez et obtenez des perspectives.
        4. Chaque fichier chargé sera automatiquement sauvegardé.
        5. Accédez à toutes les fichiers en cliquant sur **Bibliothèque** sur la sidebar
        """, unsafe_allow_html=True)

    with col2:
        st.image(streamdata_logo, width=260) 

# La page pour le scraping
elif st.session_state.selected_page == "Scraper":
    st.title("Scraper des données")
    st.write("🌐 Sur cette page, il est possible de scraper avec BeautifulSoup")
    st.write("Le scrapping terminé, vous pourrez retrouver le fichier dans **Bibliothèque**!!")
    st.write("*Ne quittez pas la page tant que le scraping n'est pas terminé!*")
    
    def reset_form():
        st.session_state["categorie"] = "Choisir une catégorie..."
        st.session_state["num_pages"] = 1
        st.session_state["file_name"] = ""
    
    with st.form("scraper_form"):
        categorie = st.selectbox("Choisir une catégorie...", ["Terrains", "Villas"])
        num_pages = st.number_input("📄 Nombre de pages", min_value=1, value=1)
        file_name = st.text_input("💾 Nom du fichier CSV", placeholder="data.csv")
        submit = st.form_submit_button("🚀 Commencer le scraping")

    if submit:
        
        if not file_name:
            st.error("❌ Veuillez donner un nom au fichier!")
        else:
            csv_path = os.path.join(UPLOAD_DIR, file_name)
            
            # pour lancer un minuteur qui afficher le temps du scraping
            start_time = time.time()
            
            # Call the correct function based on selection
            if categorie == "Terrains":
                with st.spinner("Scraping en cours..."):
                    df = scrap_terrains(num_pages)
                    while time.time() - start_time < 60:  # Limite de 60 secondes pour éviter un blocage
                        elapsed_time = time.time() - start_time
                        time.sleep(1)  # Pause d'une seconde pour rafraîchir l'affichage
                        reset_form()

            else:
                with st.spinner("Scraping en cours..."):
                    df = scrap_villas(num_pages)
                    while time.time() - start_time < 60:  # Limite de 60 secondes pour éviter un blocage
                        elapsed_time = time.time() - start_time
                        time.sleep(1)  # Pause d'une seconde pour rafraîchir l'affichage
                        reset_form()


            if not df.empty:
                df.to_csv(csv_path, index=False)
                elapsed_time = time.time() - start_time
                st.success(f"✅ Scraping terminé en {elapsed_time:.2f} secondes !")

                st.success(f"✅ `{file_name}` sauvegardé dans ***Bibliothèque*** ")
                st.dataframe(df) 
            else:
                st.warning("⚠️ Pas de données trouvées!")
    
# La page pour charger les fichiers, intituler "upload"
elif st.session_state.selected_page == "Upload":
    st.title("Charger un fichier")
    st.write("Sur cette page vous pouvez charger des données à partir de votre ordinateur.")
    file_uploader = st.file_uploader("Choisir un fichier", type=["csv", "xlsx"])
    
    
    if file_uploader is not None:
        # Save the uploaded file to the specified directory
        file_path = os.path.join(UPLOAD_DIR, file_uploader.name)
    
    # Write the uploaded file to the file system
        with open(file_path, "wb") as f:
            f.write(file_uploader.getbuffer())
            
        st.success(f"**{file_uploader.name}** a été chargé et sauvegarder dans Bibliothèque")

# La page réservée au Visualisation
elif st.session_state.selected_page == "Visualisation":
    st.title("Visualisation des données")
    st.write("Ici vous pouvez visualiser vos données.")
    st.write("Notamment avec graphes et autres selon votre choix")
    st.write("_Pour certaines variables, les graphiques ne seront pas optimaux._")
    
    options = [""] + files
    
    selected_file = st.selectbox('Sélectionner un fichier:', options)
    
    if selected_file:
        df = pd.read_csv(os.path.join(UPLOAD_DIR, selected_file))

        # Step 3: un résumé du dataframe
        st.subheader(f"Résumé de {selected_file}")
        st.write(f"Shape du dataframe: {df.shape}")
        st.write("Les colonnes")
        for i in df.columns:
            st.write(f"- **{i}** | Type de données: **{df[i].dtype}**")
        
        st.write("Aperçu des premières lignes: ")
        st.dataframe(df.head())
        
        # ici l'utilisateur pourra choisir une colonne pour faire un graphe
        # la colonne choisit fera l'objet d'une condition pour vérifier si 
        # elle est numeric ou catégorielle afin de faire le graph approprié
        st.subheader("Partie graphes")
        
        if len(df.columns) > 6:
            st.error("Visualisation non disponible")
        else:
            
            selected_column = st.selectbox('Choisissez une colonne pour faire un graphe:', df.columns)
            
            # on vérifie d'abord si le dataframe a plus de 5 variables, si non on ne fait rien
            # selon les capacités de l'appli
            # on vérifie la nature de la variable
            if df[selected_column].dtype in ['int64', 'float64']:
                st.subheader(f"Graphe pour : {selected_column}")
                
                # Display a histogram or other plot
                fig, ax = plt.subplots()
                sns.histplot(df[selected_column], kde=True, ax=ax)
                st.pyplot(fig)
        
            elif df[selected_column].dtype == 'object':  # Categorical column
                st.subheader(f"Graphe pour: {selected_column}")
                
                # Display a bar chart
                fig, ax = plt.subplots()
                df[selected_column].value_counts().plot(kind='bar', ax=ax)
                st.pyplot(fig)
            
            else:
                st.warning(f"Type de colonne non pris en charge pour la visualisation: {df[selected_column].dtype}")

# La Bibliothèque, là ou tous les fichiers sont stockés, on peut télécharger ou supprimer des fichiers 
elif st.session_state.selected_page == "Bibliothèque":
    st.title("Bibliothèque")
    st.write("Accéder tous les fichiers stockés sur le site!!")
    delete_message = st.empty()
    
    
    if files:
        for file_name in files:
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            col1, col2, col3 = st.columns([3, 0.5, 0.5])

            with col1:
                if st.button(f"📄 {file_name}"):
                    file_ext = file_name.split(".")[-1]
                    if file_ext in ["csv", "xlsx"]:
                        try:
                            df = pd.read_csv(file_path) if file_ext == "csv" else pd.read_excel(file_path)
                            st.write(f"### Lecture du fichier {file_name}")
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"Erreur lors de la lecture du fichier")
                    else:
                        st.write("⚠️ Ce type de fichier n'est pas supporté.")

            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️",
                        data=f,
                        file_name=file_name,
                        mime="application/octet-stream",
                        key=f"download_{file_name}"
                    )

            with col3:
                if st.button(f"🗑️", key=f"delete_{file_name}"):
                    try:
                        os.remove(file_path)
                        delete_message.success(f"✅ {file_name} a été supprimé avec succès.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la suppression du fichier")

        

    else:
        st.write("*Aucun fichier n'a encore été sauvegardé.*")

# La page Feedback permet aux utilisateurs de donner une note à l'appli
elif st.session_state.selected_page == "Feedback":
    st.title("Aider nous à améliorer notre application")
    form = st.selectbox("Choisissez un formulaire à remplir...", ["Formulaire google forms", "Formulaire Kobo"])
    
    if form == "Formulaire google forms":
        st.write(google_forms, unsafe_allow_html=True)
    else:
        st.write(kobo_forms, unsafe_allow_html=True)
    
# Si aucune page n'est sélectionnée, ce message s'affiche
else:
    st.title("Bienvenu!")
    st.write("Choisir une page sur la sidebar pour commencer.")
