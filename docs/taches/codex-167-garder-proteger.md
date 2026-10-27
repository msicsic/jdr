# Tâche Codex 167 (A4b) : les agendas garder et protéger, et s'interposer

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (s'interposer d'abord, puis les deux sortes ; dis ce qui
reste). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (165, vérification Luna) et un sur le laptop (166, côté MJ) : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `agendas.py`, `deliberation.py`, `planification.py`, `defense.py`, `passage.py` si besoin, les
données des scénarios (agendas de départ) et leurs tests ; **pas** `mj.py`, `consignes.py`, `narration.py`, `sources.py`, les
fournisseurs. **Bruts dans `C:\Users\msics\donjon\artifacts\garder-167\` (dépôt principal), jamais dans le worktree.** Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 sortes `garder` et `protéger`, § 6, A4 : « s'interposer », bilans 144 à 146 e),
les rapports des lots 144, 146 b et 146 e, puis la pulsion et `prix_gardes` existants, `protege` et l'appel à l'aide, la défense
4c (`defense.py`) et le passage (`passage.py`).

## Ce qu'il faut faire
1. **S'interposer** (règle commune, joueur compris comme cible) : quand quelqu'un dont le gardien se méfie, ou dont il a lu le
   guet, approche au contact d'un bien gardé, le gardien occupe la case d'accès sans violence et le met en garde par une parole
   typée ; s'il persiste, méfiance et rancune montent (épreuves communes). Aucune violence nouvelle ; la défense 4c reste la
   réponse à une agression.
2. **Les sortes `garder` (chose ou lieu) et `protéger` (personne)** sur le socle des agendas : `garder` reprend ce que fait déjà la
   pulsion de garde (`prix_gardes`) sans double comptage ; `protéger` : rester à portée de voix du protégé, répondre à son appel,
   s'interposer pour lui. Transitions publiées à la sortie du choix (lot 146 b) ; aucune règle propre à un scénario. Une épreuve
   en données (par exemple Anselme garde son ballot à l'auberge, ou Gorm protège Ilse dans la crue), sans changer les nuits
   historiques hors de cette épreuve si possible ; sinon, écarts mesurés et expliqués.

## Vérification
- Tests après rechargement : un voleur cru approche d'un bien gardé, le gardien s'interpose et le met en garde, persistance →
  méfiance ; protecteur qui rejoint son protégé à portée de voix et répond à son appel ; personne de confiance non bloquée ;
  même laps d'un bloc ou découpé, même `data`.
- Empreintes 2 h, quatre scénarios × quatre graines contre la base : identiques hors scénario de l'épreuve, sinon écarts
  expliqués ; banc rapide 4 h du scénario de l'épreuve × quatre graines (vols vus, passages par heure, aucune usurpation ni boucle
  nouvelle) ; `VERIFIER` + spatial 0,2, 2 h ; `tools/mesure_cout.py` sur ce scénario.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-garder-proteger` poussée (pas `main`).
`docs/plan-agendas.md` (A4 : fait et reste), `docs/etat-dev.md` (« Branche `codex-garder-proteger`, non fusionnée »). Rapport d'une
page : `docs/taches/rapport-codex-167-garder-proteger.md`.
