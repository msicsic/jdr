# Tâche Codex 92 (coût, P3) : un plan ne s'arrête que dans une salle où il a quelque chose à faire

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 3 processus de calcul. Le lot 90 (`deliberation.choisir`, recours de lumière,
`eclairer(tenir=True)`) et le lot 91 (MJ) tournent en même temps ; ce lot touche `planification.py` (`gestes`, `Vue.allers`,
la référence de `VERIFIER` s'il le faut), pas `choisir` ni les fichiers du MJ. Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

**Décision de l'utilisateur (2026-10-25)** : on continue les lots de coût avant d'avancer `main`. Après le lot 87, l'auberge 1985
coûte encore **×1,91 (fixe) / ×3,63 (tiré)** contre `42bb9c0`, surtout après 8 h.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : principe « réduire l'espace plutôt qu'ajouter un cache », P2/P3 ;
entrées des lots 46, 48, 52 (C1 : règle juste, **aucun gain**), 76, 81, 86, 87), les rapports
`docs/taches/rapport-codex-76-bissection-auberge.md` et `rapport-codex-87-borne-attente.md`, `docs/plan-planificateur.md`, puis
`donjon/planification.py` (`gestes`, `Vue.allers`, `Vue.route`, `Vue.pression`, `_explorer_etats`, `chercher`, `_verifier`),
`donjon/trajet_estime.py`, `donjon/route_admissible.py`.

## D'abord, mesurer (court ; si la piste ne rapporte pas, arrête-toi et dis-le)
Sur l'intégration **9810f4a**, auberge 1985 départ tiré, la tranche 8–12 h (capture ou rejeu des recherches comme les lots 81/86/87) :
part des successeurs produits par `aller`, part des états développés dont la salle n'offre **aucun** geste autre qu'`aller`
(ni objet, ni porte, ni personne utile, ni lieu du but), et ce que coûte un état (µs/nœud). Si les `aller` vers des salles sans
geste pèsent moins de ~15 % des états développés, **n'implémente rien** : rapporte la décomposition (ce qui domine désormais le
coût de fin de nuit, par but et par geste) et termine par `QUESTION :` avec la piste que la mesure désigne.

## L'invariant (P3)
**Un plan ne s'arrête que dans une salle où il a quelque chose à faire** : `gestes` n'offre `aller` que vers une salle d'intérêt
pour cet état (un objet ou une porte que les gestes peuvent toucher, une personne à qui parler ou chercher, le lieu que vise le
but, un lieu où le but se tient en restant : abri, lumière, chaleur, garde), les trajets directs d'`allers` couvrant le passage
par les autres. Ce n'est **exact** que si s'arrêter dans une salle sans geste ne peut jamais donner un plan moins cher : prouve-le
pour le coût d'une route (`cout_route`, pression par salle et par minute : noir, garde, eau, compagnie), l'admissibilité
(`route_admissible`, eau, retour) et les portes ; **là où la preuve manque, la salle reste d'intérêt** (conservateur), jamais un
plan perdu. Une seule définition de « salle d'intérêt », lue par la recherche jouée et par la référence de `VERIFIER` ; ce
qu'elle lit entre dans `_entrees`. Aucun coût, prix, plafond, scénario ni règle de choix changé.

**Contrat** (lots 46 et 48) : mêmes décisions quand la référence ne plafonne pas ; si elle plafonne, autre résultat permis
seulement au coût de la recherche complète (`REFERENCE`), ou aucun plan si elle n'en trouve pas.

## Vérification (minimale)
- Captures auberge et mine de fin de nuit (celles des lots 81/86/87 suffisent) : recherches rejouées avec et sans la règle,
  **mêmes plans et coûts**, nœuds et µs comparés ; monde et rendu identiques après recharge.
- Empreintes 2 h, quatre scénarios × quatre graines (`tools/comparer_bancs.py --empreintes --reference 9810f4a`, référence en
  cache si elle y est) : identiques.
- `VERIFIER` + `spatial.VERIFICATION=1`, auberge 42, 2 h : sans écart.
- CPU : auberge 1985 et mine 1985, 12 h, fixe et tiré, `42bb9c0`, base et branche **lancés ensemble** (un processus chacun,
  `--sans-cache`), avec la tranche 8–12 h ; `comparer --calcul` : mêmes résultats de recherche.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la règle et sa preuve), `docs/etat-dev.md`
(« Branche `codex-aller-utile`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-92-aller-utile.md`.
