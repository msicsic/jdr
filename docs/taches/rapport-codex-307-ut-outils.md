# Lot 307 — U-T outils et destinations

Branche `codex-ut-outils`, base `integration d7302a4`, **non fusionnée**.

## Invariant et changement

Console et TUI proposent les mêmes couples geste–ressource que les menus
de carte et de besace : déverrouiller, crocheter, forcer/frapper, alimenter
et mettre dans. Un numéro choisit un descripteur U-D complet, avec l'outil
ou la destination sous sa référence publique exacte. Les homonymes restent
distinguables. Le moteur revalide le choix à réception ; aucun substitut,
aucune capacité ni propriété inconnue n'est déduite par l'interface.

`gestes_publics.gestes_materiels` lit les formulaires du catalogue commun,
leurs conditions publiques et leurs filtres de ressources. `liste_gestes`
ajoute les choix complets après les gestes simples, avec dédoublonnage des
portes apparaissant sur plusieurs sorties. `gestes_du_monde` dessert déjà
`jeu.py` et `tui.py` : aucun second chemin de sélection n'est nécessaire.
Les premiers gestes gardent leurs numéros dans une même projection.

La projection `ressources_publiques` quitte `web/pont.py` pour
`inventaire_public.py` ; le pont la réexporte. Web et terminaux lisent
ainsi les mêmes affaires portées et objets vus à portée, sans contenu
fermé ni inventaire privé d'un PNJ. Son corps reste identique, seuls
ses imports deviennent relatifs au nouveau module. Aucun changement
du MJ, de `page.html`, des règles d'atelier ou des mécaniques PNJ.

## Vérification et mesures

**98 tests distincts / neuf fichiers verts**, aucun échec, erreur ou test
ignoré : 13 nouveaux tests, puis 85 tests voisins, dont les **28 TUI
existants inchangés** et cinq tests de cases. Deux étapes détachées,
349,652 s puis 685,068 s ; deux travailleurs réduits au plus.
`fin-verification.json` : **ok=true, code 0**, bilan `bilan.json`.
Les tests utilisent les vrais callbacks Node de la page,
les vrais numéros console et les touches de la TUI, avec analyseur et
appels du MJ interdits. Descripteur, plan et texte public exact, monde,
scène, fiche, carte et état web sont comparés après sauvegarde/recharge.

Deux scènes par geste : contenant/porte, foyer/lampe et destinations au
sol/portées, avec deux ressources homonymes. Ressource partie, destination
fermée, mauvais outil, propriété inconnue, numéro inconnu ou ambigu,
besace dans le noir et sans carte sont aussi exercés. Les filtres de
ressources et libellés du catalogue sont modifiés en test pour prouver
leur lecture effective par les deux interfaces.

`mesures.json` : **20 parcours**, dix par interface ; **3 touches** pour
déverrouiller, crocheter, frapper et alimenter, **4 pour mettre dans**
(numéros à trois chiffres), depuis la liste jusqu'à l'effet. **4 à 5 avec
F7 en TUI**. Hors déplacement préalable et temps de lecture de la liste ;
zéro appel modèle, aucun délai humain ou réseau déduit.

## Limites et livraison

La liste énumère les couples complets ; sa longueur croît avec le nombre
de cibles et de ressources publiques. Elle ne promet pas la réussite.
Comme au lot 300, aucune capacité maximale des destinations n'existe dans
le moteur ; ce lot ne garantit donc pas le refus d'une destination pleine.
Les propriétés inconnues gardent leur voie d'admission distincte.

Les premiers essais de sauvegarde dans le bac à sable Windows ont été
refusés par les droits des dossiers temporaires ; les vérifications
retenues ont tourné hors de ce bac, sur copies, avec deux travailleurs
au plus, à priorité réduite. Ni Luna, ni banc PNJ, ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-outils-307/`.
`origin/integration` relue et fusionnée sans rebase au lancement puis à
la clôture : toujours `d7302a4`, branche à jour. Le lot 305 n'y est pas
encore présent ; aucune compatibilité avec son futur catalogue n'est
prétendue. Code et tests validés au commit `79c9b89`, inchangés depuis.
Branche poussée vers `origin/codex-ut-outils`, aucun calcul actif.
Clôture `fin-cloture.json` écrite en dernier ; intégration du lot et
suite complète laissées au superviseur.
