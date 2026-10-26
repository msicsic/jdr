# Tâche Codex 107 : une proposition de PNJ demande ce que vaut ce qu'elle offre

Petit lot (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul
poste** : priorité réduite, au plus 2 processus de calcul ; le lot 103 (`deliberation`, garde-manger) et le lot 105
(`planification`, coût) tournent en même temps : ce lot reste dans `echanges.py` / `propositions.py` (choix de la demande et de
la contrepartie d'une proposition « faute de mieux »). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par
`QUESTION : …`.

## Le constat (vérifications d'intégration 5c2ce81 et 47d4d25, persistant malgré le lot 57)
Mine, graine 1985, minute 253 : **Odon propose un outil contre toute la bourse de la paie** (200 pièces). À `5c2ce81` : Bram offrait
la clé de la paie qu'il garde, Odon un outil contre toute la paie. Le lot 57 a fait juger la contrepartie par le proposant
(`evaluer_proposition` inversée : ce qu'il garde, ce qui lui est nécessaire, une perte supérieure au gain) ; il n'a pas borné ce
qu'il **demande**. Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\` (audit 12 h, mine 1985 ; `evidence.json`),
rapport `docs/taches/rapport-codex-94-verif-integ.md`, `docs/plan-relations.md` § 7.2 (A2b, « faute de mieux »).

## L'invariant
**Une proposition demande au plus ce dont le proposant a besoin, et dans une mesure que sa contrepartie peut raisonnablement
valoir aux yeux de l'autre** : la demande est la part ou la quantité qui sert son but (une part de la paie pour ce qu'il veut
payer, pas la bourse entière), et le proposant n'attend pas d'acceptation d'une offre que l'évaluation commune (la même que pour
le joueur, `evaluer_proposition`, vue depuis ses croyances) jugerait refusée d'avance par la valeur ; s'il n'en existe aucune
qu'il puisse se permettre, il ne propose pas. Une règle commune pour toutes les propositions de PNJ (objets, parts, pièces), pas
une borne propre à la paie ou à Odon.

## Vérification
- Tests après rechargement : le cas réel (mine 1985 à 253, capture) — la demande est proportionnée ou la proposition n'a pas
  lieu ; un autre cas de même nature (auberge : un bien demandé contre une contrepartie de faible valeur) ; une proposition
  raisonnable inchangée (Brune/Gorm en crue, Odon/Mathe, scènes du lot 45).
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (référence en cache, sinon calculée une fois et rangée) :
  propositions / acceptées, aucune usurpation ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (§ 7.2) si la règle change, `docs/etat-dev.md` (« Branche
`codex-contreparties`, non fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-107-contreparties.md`.
