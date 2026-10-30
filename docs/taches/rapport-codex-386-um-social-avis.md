# Lot 386 — U-M social avis

Branche `codex-um-social-avis`, base `integration` **`cbecf8c8`**.
Code livré ; vérifications voisines et empreintes en cours au premier envoi.

## Invariant et changement

Le menu web propose un destinataire perçu, un lieu public connu de Corvus et
une prévision explicite : menace ou absence de menace d'eau. Aucun lieu ni
aucune valeur ne sont présélectionnés. `avis_publics` ne projette que des
couples identifiant/nom, sans estimation calculée, conviction ou croyance privée.

Le formulaire reprend les callbacks d'information. Son descripteur U-D est
`information`, acte `avis`, sujet et valeur exacts ; `parole_information`
contrôle les choix publics actuels et construit les mots ainsi que le contenu
typé `avis / sujet / menace / oui|non`. La même entrée est rejouée à la
confirmation. Le contrat d'adresse existant refuse toute altération du contenu.
`preparer_direct`, U-C et G18 gardent l'autorité sur la réception et la dispute,
les paroles enregistrées et la sauvegarde avant affichage. Aucun modèle,
compilateur, prompt, registre d'esprit ou mécanique sociale supplémentaire.

Le raccord du descripteur se trouve dans `dialogues.py`, où vit déjà U-M
information ; aucun paramètre ne manque à `paroles.py`. `jeu.py` et `tui.py`
restent inchangés ; le formulaire terminal d'information conserve ses actes.
Le formulaire web de prestation/délai/prix est conservé.

## Vérification et mesures

**5/5 nouveaux tests verts, 111,385 s**, dans `tests/test_avis_publics.py`.
Les vrais callbacks Node soumettent les identifiants choisis ; la boucle de jeu
interdit l'analyse du clic et les appels au modèle. Deux lieux (`echoppe`,
`chambre_cloche`), avis positif/négatif et disputes contraires sont comparés à
la parole typée équivalente : rapports et état complet hors seule conversation
de saisie, source, conviction, paroles et transmission. Après confirmation puis
trois laps découpés avec recharge, mêmes monde, scène, fiche, regard et émissions.
L'aperçu n'exécute rien ; annulation et destinataire parti ne prononcent rien.
Lieu inconnu, valeur inconnue, effet ajouté et contenu altéré sont refusés
atomiquement avec `attendu`. Une croyance privée ne change pas la projection.

**8 clics de formulaire**, puis un clic de confirmation ; une saisie libre
évitée. Les listes gardent leur choix vide et distinguent les homonymes.
Sécurité clavier, blocage occupé, absence de double envoi et fermeture au
rafraîchissement vérifiés par les callbacks. Aucune assertion de sécurité
existante modifiée : le harnais Node partage seulement sa sonde avec l'avis.

Tests voisins : huit fichiers (information web/terminal, G18, avis joueur,
disputes, web, U-D et accords publics), un travailleur réduit. Empreintes :
2 h, crue et Relais, graines 1985/7/42/2024, un travailleur réduit ; référence
exacte `cbecf8c8` pour isoler le lot des changements d'intégration absents de
`main`, références manquantes rangées au cache commun. Bilans définitifs dans
`voisins.json`, `empreintes.json` et `fin-verification.json` ; pas de suite
complète ni Luna. Bruts : `C:/Users/msics/donjon/artifacts/um-social-avis-386/`.

## Limites et livraison

Le prédicat existant concerne seulement la menace d'eau ; cet avis reste une
prévision et n'établit pas la vérité du monde. Pas de portage U-T dans ce lot.
`origin/integration` récupérée et fusion demandée effectuée sans changement
(déjà à jour sur `cbecf8c8`). Les vérifications détachées écrivent leur fichier
de fin en dernier ; leur bilan reste à relever avant clôture du lot.
