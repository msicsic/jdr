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

Vérification ciblée en cours : 13 tests nouveaux, puis huit fichiers
voisins (85 tests, dont les 28 TUI existants et cinq tests de cases),
enchaînés automatiquement si le ciblage passe ; fin :
`fin-verification.json`. Aucun résultat provisoire n'est une
validation. Les tests utilisent les vrais callbacks Node de la page,
les vrais numéros console et les touches de la TUI, avec analyseur et
appels du MJ interdits. Descripteur, plan et texte public exact, monde,
scène, fiche, carte et état web sont comparés après sauvegarde/recharge.

Deux scènes par geste : contenant/porte, foyer/lampe et destinations au
sol/portées, avec deux ressources homonymes. Ressource partie, destination
fermée, mauvais outil, propriété inconnue, numéro inconnu ou ambigu,
besace dans le noir et sans carte sont aussi exercés. Les conditions et
libellés du catalogue sont modifiés en test pour prouver leur lecture
effective par les deux interfaces. Les mesures comptent les chiffres du
numéro et Entrée, ainsi que F7 pour ouvrir la liste TUI.

## Limites et livraison

La liste énumère les couples complets ; sa longueur croît avec le nombre
de cibles et de ressources publiques. Elle ne promet pas la réussite.
Comme au lot 300, aucune capacité maximale des destinations n'existe dans
le moteur ; ce lot ne garantit donc pas le refus d'une destination pleine.
Les propriétés inconnues gardent leur voie d'admission distincte.

Les premiers essais de sauvegarde dans le bac à sable Windows ont été
refusés par les droits des dossiers temporaires ; les vérifications
retenues se lancent hors de ce bac, sur copies, avec deux travailleurs
au plus, à priorité réduite. Ni Luna, ni banc PNJ, ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-outils-307/`.
`origin/integration` relue et fusionnée sans rebase : toujours `d7302a4`
au lancement. Le lot 305 n'y est pas encore présent ; relire et fusionner
à la clôture s'il y est entré. Intégration du lot et suite complète
laissées au superviseur.
