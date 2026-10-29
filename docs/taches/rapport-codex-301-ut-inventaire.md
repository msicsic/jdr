# Lot 301 — U-T inventaire

Branche `codex-ut-inventaire`, **non fusionnée**. Base `integration 79beaf1`,
puis fusion sans rebase d'`origin/integration 2537e4f` (U-M outils 300),
commit de fusion `99855aa`.

## Invariant et changement

Console et TUI proposent les gestes de besace dans leur liste numérotée :
poser, remettre à une personne choisie, manger une portion, allumer,
éteindre et prélever une pièce. Chaque numéro capture le même
`DescripteurPublic` que le menu web : référence exacte du bien, quantité
admise et destinataire public. Le numéro passe directement à la boucle U-D,
sans analyse de texte ni modèle ; le moteur revalide le choix à réception.

`donjon/inventaire_public.py` reçoit les deux projections précédemment dans
`web/pont.py`, qui les réexporte pour compatibilité. Web et terminaux lisent
ainsi les mêmes affaires portées et personnes vues à portée.
`gestes_publics.gestes_inventaire` compose les choix publics ;
`gestes_du_monde` fournit la même liste figée à la console et au pont TUI.
Une ligne de remise inclut déjà la personne et sa référence : un numéro
suffit, sans seconde saisie. Les homonymes restent distinguables.
La besace est disponible aussi sans carte et dans le noir, sans exposer
de contenu fermé ou d'identité privée.

La reprise conserve le catalogue commun enrichi par 300, ses offres
paramétrées et sa projection des ressources. Les outils restent hors de ce
lot terminal ; aucune offre incomplète n'est soumise. `page.html` est
identique à celui de `2537e4f`. Aucun MJ ou mécanisme PNJ modifié.

## Vérification et mesures

**87 tests distincts / huit fichiers verts**, zéro échec, erreur ou ignoré
dans le bilan retenu : sept fichiers voisins de la reprise (77 tests,
dont les **28 TUI existants inchangés**), puis le fichier inventaire
corrigé (10 tests). Deux travailleurs réduits au plus. Reprise groupée :
471,101 s ; rejeu du seul inventaire : 355,769 s. `bilan.json` assemble
les résultats retenus sans recompter les tests rejoués.

Douze couples geste/bien sont comparés dans les deux interfaces aux vrais
callbacks Node de la page : deux biens homonymes, deux destinataires
homonymes, lots de deux/quatre pièces, portions, torche et lanterne.
Descripteur, plan et texte exact identiques ; monde, scène, fiche, carte
et état web comparés après recharge. Pour chaque geste : numéro inconnu
ou ambigu sans effet, bien périmé sans substitution. Personne partie ou
éloignée, lot devenu pièce unique, noir, contenu fermé et absence de carte
sont aussi vérifiés. Analyseur interdit et MJ actif interdit d'appel.

`mesures.json` : **24 parcours, 3 touches** depuis la liste (deux chiffres
et Entrée), **4 avec F7** en TUI. Coût du choix jusqu'à l'effet, hors
déplacement préalable ; aucun délai humain ou réseau déduit.

## Limites et livraison

Quantités du menu existant : lot entier pour poser/remettre, une portion
ou une pièce pour manger/prélever. Pas de quantité arbitraire ni de
formulaire d'outil ajouté. Les offres ne promettent ni accord ni réussite.
La numérotation est propre à chaque vue ; le descripteur capturé reste
l'identité du choix jusqu'au verdict du moteur.

Deux lancements ont rencontré les droits des répertoires `tempfile` du
bac à sable Windows ; les vérifications retenues tournent hors de ce bac
à sable, toujours à priorité réduite. Une première fixture de deux PNJ
occupait la même case et n'initialisait pas le second esprit : corrigée
par placement distinct et reconstruction du monde, sans changement moteur.
La sonde de plans comptait aussi la préparation canonique récursive ; elle
enregistre désormais le seul descripteur U-D soumis. Ces essais restent
archivés et ne sont pas retenus comme validations. Ni Luna, ni banc PNJ,
ni suite complète : entrée d'interface seule ; intégration au superviseur.

Bruts : `C:/Users/msics/donjon/artifacts/ut-inventaire-301/`,
bilan retenu `bilan.json`, fichier de clôture `fin-cloture.json` écrit
en dernier. Branche livrée sur `origin/codex-ut-inventaire` ; aucun calcul actif.
