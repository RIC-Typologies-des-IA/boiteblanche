#!/usr/bin/env python3
"""
Ajoute un pied de page standard à chaque page chapitre.
Le pied de page contient un retour au sommaire et un lien vers la page suivante.
"""

import os
import re

# Définir l'ordre des pages
PAGES_ORDER = [
    ("chapitre1/chapitre1.html", "chapitre2/chapitre2.html"),
    ("chapitre1/chapitre1-1.html", "chapitre2/chapitre2.html"),
    ("chapitre2/chapitre2.html", "chapitre3/chapitre3.html"),
    ("chapitre3/chapitre3.html", "chapitre4/chapitre4.html"),
    ("chapitre4/chapitre4.html", None),  # Dernière page, pas de suivant
]

# Template du pied de page
FOOTER_TEMPLATE = """
        <hr>
        <div style="margin-top: 40px; text-align: center; padding: 20px; background-color: #f8f9fa; border-top: 1px solid #e9ecef;">
            <p style="margin-bottom: 15px;">
                <a href="../index.html" style="margin-right: 20px; text-decoration: none; color: #007bff;">↩ Retour au sommaire</a>
                {next_link}
            </p>
        </div>
"""

NEXT_LINK_TEMPLATE = '<a href="{next_url}" style="text-decoration: none; color: #007bff;">→ Aller à la page suivante</a>'
NO_NEXT_LINK = ''

def add_footer_to_file(filepath, next_page):
    """Ajoute le pied de page à un fichier HTML."""
    
    # Lire le contenu du fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le pied de page existe déjà
    if 'footer-navigation' in content or 'Retour au sommaire' in content:
        print(f"⚠️  Pied de page déjà présent dans {filepath} - ignoré")
        return
    
    # Déterminer le lien suivant
    if next_page:
        # Calculer le chemin relatif
        current_dir = os.path.dirname(filepath)
        next_dir = os.path.dirname(next_page)
        
        # Si les deux fichiers sont dans le même dossier
        if current_dir == next_dir:
            next_url = os.path.basename(next_page)
        else:
            # Remonter au parent commun
            # Ex: chapitre1/chapitre1.html -> chapitre2/chapitre2.html
            # chemin: ../chapitre2/chapitre2.html
            relative_path = os.path.relpath(next_page, current_dir)
            next_url = relative_path
        
        next_link = NEXT_LINK_TEMPLATE.format(next_url=next_url)
    else:
        next_link = NO_NEXT_LINK
    
    # Créer le pied de page
    footer = FOOTER_TEMPLATE.format(next_link=next_link)
    
    # Insérer avant </body>
    new_content = content.replace('</body>', f'{footer}\n    </body>')
    
    # Écrire le contenu modifié
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Pied de page ajouté à {filepath}")
    if next_page:
        print(f"   → Page suivante: {next_page}")
    else:
        print(f"   → Dernière page (pas de suivant)")


def main():
    print("Ajout des pieds de page standard...\n")
    
    for filepath, next_page in PAGES_ORDER:
        if os.path.exists(filepath):
            add_footer_to_file(filepath, next_page)
        else:
            print(f"❌ Fichier non trouvé: {filepath}")
    
    print("\n✨ Tous les pieds de page ont été ajoutés!")


if __name__ == "__main__":
    main()
