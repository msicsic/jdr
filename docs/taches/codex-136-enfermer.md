# Tâche Codex 136 (force 4d, suite) : enfermer quelqu'un et s'évader

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `tenir.py`, `pnj.py`, `moteur.py`, `commandes.py`, `planification.py` (gestes d'évasion) et
leurs tests ; **pas** `narration.py`, `mj.py`, `noms.py` (lot 135), ni `echanges.py`, `agendas.py` (lot 133). Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-force.md` (« Enfermer et s'évader », 4d), les rapports des lots 126 et 134, puis `donjon/tenir.py`,
`pnj.CONTRAINTES`, le verrouillage des PNJ (`pnj.py`, opérations `verrouiller`/`deverrouiller`), le crochetage et `force.py`
(forcer une serrure, lot `petits-correctifs-pnj`).

## Les règles (plan force, décidées ; un seul lot car elles forment une seule mécanique)
- **Le joueur reçoit `verrouiller`** (porte fermée, clé qui l'ouvre), symétrique de `deverrouiller`, avec fiche et refus `attendu`.
- **Enfermer est un verrouillage** : quand l'auteur, joueur ou PNJ, croit quelqu'un dans la salle qu'il ferme à clé, sans autre
  sortie qu'il croie ouverte, le geste entre au registre comme **contrainte** (victimes : ceux qu'il y croit), avec témoins,
  souvenirs et relations par les voies communes. La victime l'apprend en essayant la porte (constat commun).
- **S'évader** par les gestes communs : crocheter (existant), **forcer la porte** (le `frapper` du joueur sur une porte, déjà
  partagé avec les PNJ pour lever une serrure : vérifie qu'il s'applique à une porte de sortie, bruyant, dégâts sur
  l'intégrité jusqu'à la briser), appeler à l'aide (existant). Un PNJ enfermé cherche ces moyens par son planificateur, sans
  règle propre au scénario ; un protecteur qui l'entend vient ouvrir s'il a la clé.
- Aucun PNJ n'enferme personne de son propre chef dans ce lot. L'inquiétude « captif » et la volonté brisée restent au lot
  suivant (ne les commence pas).

## Vérification
- Épreuves du plan : `--etat ilse:enferme:beffroi` (la clé chez Gorm : Ilse appelle et Gorm vient ouvrir),
  `--etat brune:enferme:beffroi` (pied-de-biche à portée : Brune force la porte et le bruit se rend). Si `banc_pnj --etat`
  ne connaît pas encore `enferme`, ajoute-le comme préparation d'épreuve, sans règle de comportement.
- Joueur : il assomme Brune, la traîne au beffroi (lot 134), ferme et verrouille ; contrainte enregistrée, témoins, puis
  Brune réveillée constate la porte et s'évade ; tout tient après rechargement et sur le même laps découpé.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache) : nuits identiques attendues (personne n'enferme) ;
  sinon expliquer chaque écart. Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-enfermer` poussée (pas `main`). `docs/plan-force.md`
(4d), `docs/mecaniques.md`, `docs/etat-dev.md` (« Branche `codex-enfermer`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-136-enfermer.md`.
