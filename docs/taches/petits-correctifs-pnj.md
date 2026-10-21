# Tâche : petits correctifs des PNJ

Tâche autonome, pensée pour une session cloud (`claude --cloud`). Aucun appel à Luna ni à un
modèle n'est possible ni nécessaire : tout se vérifie par les tests et le banc sans joueur.

## Avant de commencer

- Lis `AGENTS.md`, `CLAUDE.md`, `docs/etat-dev.md` et `docs/plan-planificateur.md`. Leurs règles
  s'imposent : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel et
  un autre cas de même nature après rechargement ; `ErreurMonde` avec `attendu`, une cause par
  refus ; aucun état hors de `data` (`tests/test_temps_etat.py`) ; `planification.VERIFIER` :
  toute lecture nouvelle de la recherche entre dans `_entrees` ; dire les limites. Les anciennes
  sauvegardes n'ont pas à être conservées : aucune migration.
- Environnement Linux : `CLAUDE.md` décrit le poste Windows (`.venv\Scripts\python.exe`). Ici,
  crée un environnement (`python -m venv .venv && . .venv/bin/activate`) et installe
  `requirements-tui.txt` et `requirements-chatgpt.txt`. Tests :
  `python -m unittest discover -s tests -q` (ceux du clic demandent Node ; s'il manque, dis-le).
  `pip install pyflakes`, à passer sur les fichiers touchés.
- Crée la branche `petits-correctifs-pnj` depuis `main`, commite dessus et pousse-la
  (`git push -u origin petits-correctifs-pnj`). Ne touche jamais à `main`, ne fusionne rien.
- Les tests de scène construisent le monde avec `depart="fixe"` (départ déclaré) ; le banc
  tire le départ de la graine par défaut.

## Les quatre correctifs

1. **Lumière jugée devant la serrure.** La lumière crue d'une salle se constate à la case où
   le PNJ se tient (`esprits.constater_lumiere`, `deliberation.lumiere_crue`) : un essai de
   crochetage peut être tenté sur la foi de la lumière de la case de départ et perdu en arrivant
   devant la serrure plus sombre. Invariant : avant un geste dont la chance dépend de la lumière,
   le PNJ la constate là où il l'accomplit et renonce si elle rend le geste impossible ou plus
   coûteux que prévu, sans essai perdu.
2. **Part payée jamais servie.** Un achat payé d'avance dont la part n'est jamais servie
   (promesse expirée, vendeur empêché) n'est pas remboursé (`echanges.py`, `biens.py`, argent
   dans `docs/plan-social.md`, « Argent, prêts et garde confiée »). Invariant : un paiement dont
   la contrepartie n'est pas livrée à l'échéance est rendu, ou devient une dette que le payeur
   connaît et peut réclamer ; pour le joueur comme pour les PNJ.
3. **Forcer, pour les PNJ.** Les PNJ savent crocheter un contenant ou une porte, pas forcer.
   Le joueur le peut : « forcer » et « défoncer » sont des alias de l'action `frapper`
   (`commandes.py`, `moteur.py` : outil qui coupe ou fait choc, bonus de percussion, bruit).
   Attention : dans `pnj.py`, le geste nommé « forcer » n'est que l'essai de crochetage manqué
   (témoins) ; ne le confonds pas. Ajoute au planificateur le geste de forcer un contenant ou une
   porte par la règle de `frapper` du joueur, déclaré une fois : chance selon la FOR modulée et
   l'outil, bruit bruyant (`ouie.NATURES`), faute au prix des valeurs (honnêteté, et douceur pour
   le dégât), même effet sur l'objet que pour le joueur. Aucune branche par objet.
4. **Gorm et les planches.** Au Relais, Gorm demande les planches d'Aubin plutôt que d'aller
   chercher son propre bois. Diagnostique d'abord avec `--diagnostic` (coûts des plans comparés)
   et dis la cause ; corrige le coût ou la croyance en cause dans la règle commune, pas Gorm.

## Vérifications

- Pour chaque correctif, un test qui vérifie l'état après rechargement, sur le cas réel et un
  autre cas de même nature.
- Suite complète verte ; `VERIFIER` sur une nuit de chaque scénario.
- Bancs 8 h, `main` contre la branche, lancés au même moment :
  `python -m donjon.banc_pnj --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche`,
  puis `--scenario mine --joueur galerie`, `--scenario auberge --joueur dortoir`,
  `--scenario crue --joueur chambre_cloche` (4 graines). Rapporte avant → après : minutes sans
  recours et en attente, événements, échanges, achats, crochetages et forçages (essais,
  réussites), vols vus, nuits distinctes, usurpations et violations (aucune tolérée), temps d'une
  nuit. Explique les écarts.
- Mets à jour `docs/plan-planificateur.md` (ou `docs/plan-social.md` pour l'argent) et
  `docs/etat-dev.md` (« Branche `petits-correctifs-pnj`, non fusionnée », compte de tests).

## Rapport final

En français, concis : causes, règles changées (fonctions), cas vérifiés, bancs avant → après,
limites, nom de la branche poussée et dernier commit.
