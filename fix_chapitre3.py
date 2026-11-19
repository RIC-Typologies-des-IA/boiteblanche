#!/usr/bin/env python3
import os

filepath = "chapitre3/chapitre3.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter le pied de page standard avant </body>
footer = """
        <hr>
        <div style="margin-top: 40px; text-align: center; padding: 20px; background-color: #f8f9fa; border-top: 1px solid #e9ecef;">
            <p style="margin-bottom: 15px;">
                <a href="../index.html" style="margin-right: 20px; text-decoration: none; color: #007bff;">↩ Retour au sommaire</a>
                <a href="../chapitre4/chapitre4.html" style="text-decoration: none; color: #007bff;">→ Aller à la page suivante</a>
            </p>
        </div>
"""

new_content = content.replace('</body>', f'{footer}\n    </body>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Pied de page ajouté à chapitre3/chapitre3.html")
