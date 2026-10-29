# Tâche Codex 283 (A5, lot 6) : un compte rendu informe le mandant sans rendre son contenu vrai

Contexte : `docs/plan-agendas.md` (mandat), conception A5 `docs/taches/rapport-codex-245-conception-a5.md` (ligne 6 du
tableau), et les lots A5 déjà fusionnés : filiation `agendas.confier` (252), jugement du mandat (256), faire ou confier
selon les croyances du mandant (257, 258, 260), suivi des délégations sur échéance (242). Aujourd'hui, le mandant apprend
l'issue d'une charge confiée seulement en la constatant lui-même (ou par une nouvelle ordinaire) : aucun compte rendu
n'est rendu par le mandaté, et `paroles.TYPES` n'a pas de `compte_rendu`.

## L'invariant
**Le mandaté qui a fini (réussi, échoué ou renoncé à) une charge confiée en rend compte au mandant par la parole commune
quand il le croit à portée de voix, avec un contenu typé (charge, issue). Le mandant reçoit ce compte rendu comme une
parole entendue : il établit qu'elle a été dite, pas qu'elle est vraie ; sa croyance sur l'issue prend la provenance
`dit` et le poids de la source (confiance, relation), et un constat propre contradictoire, antérieur ou postérieur, la
dément selon les règles existantes.** Un mandaté peut mentir (règle d'honnêteté existante) ; le mandant n'en sait rien
tant qu'il ne constate pas. Hors de portée, rien n'est appris. Aucune clôture omnisciente de l'agenda du mandant : il
clôt sa charge sur ce qu'il croit. Pas de protocole joueur dans ce lot (lots 9–10).

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le PC fixe**, deux
processus au plus, priorité réduite (une suite complète peut y tourner : un seul processus tant qu'elle n'est pas finie).

**Fichiers attendus** : `donjon/agendas.py`, `donjon/echanges.py`, `donjon/social.py` ; extensions autorisées :
`donjon/ouie.py`/`donjon/voix.py` seulement pour le transport typé et l'attribution, `donjon/paroles.py` pour déclarer
le type de contenu. Ni nouvel estimateur, ni modification du jugement de mandat (256) ni du choix faire/confier (260).

## Vérification
- Épreuve : crue étendue au hameau (`crue_hameau`), Gorm confie à Aubin d'amener Brune, puis une information à
  transmettre (comme aux lots 256/260). Réussite, échec et mensonge (Aubin peu honnête en fixture de test) sur les deux
  charges ; hors portée, rien n'est appris ; réception après recharge ; constat contradictoire qui dément ; aucune clôture
  omnisciente. Autre cas de même nature (autre mandant/mandaté ou autre scénario). Monde, rendu et scène identiques
  après recharge et laps entier/découpé.
- Tous les fichiers de tests qui exercent les fonctions modifiées (agendas socle, transferts, engagements, parole/voix).
- Si aucun mandat n'est prononcé naturellement dans les nuits (cas actuel), empreintes 2 h (`tools/comparer_bancs.py
  --empreintes`), cinq scénarios × quatre graines, contre l'intégration à ta base : identiques ou écarts expliqués ; sinon
  banc rapide 4 h. Calcul long détaché.

## Livraison
- Branche `codex-compte-rendu` poussée (si la poussée échoue, laisse le commit local, donne son hash et dis l'erreur
  exacte, sans passer par l'API GitHub). Rapport d'une page `docs/taches/rapport-codex-283-compte-rendu.md` ; entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\compte-rendu-283\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
