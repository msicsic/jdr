# Comparaison DeepSeek V4.1 Flash / Codex Sol 6.1 (note de travail)

Point de reprise pour décider de l'usage de DeepSeek sur les lots futurs. Mise à jour du 29 octobre 2026, nuit ; à
compléter quand les deux versions du lot 273 auront fini.

## Lot 270 (diagnostic sans code), DeepSeek seul
DeepSeek V4.1 Flash Free, via OpenCode sur le PC fixe, réflexion par défaut (non réglée, donc probablement basse).
Livré complet en une seule passe, sans relance, rapport juste vérifié sur échantillon des bruts : 15 départs →
11 cas distincts, tous justifiés, doublons repérés, captures rechargées, rejeu sur `c870c8b` aux empreintes exactes.
Consignes respectées (seulement le rapport et l'état). Coût 0 $. Qualité comparable à Sol medium sur ce type de lot.

## Lot 273 (correction de contrat commun), en double
Même brief, même base `c9459ce`. Sol 6.1 high sur le laptop ; DeepSeek V4.1 Flash Free high sur le PC fixe (premier
lancement en réflexion par défaut annulé et refait en high). Temps non comparables (postes différents).

| | Sol 6.1 high | DeepSeek V4.1 Flash high |
|---|---|---|
| Correctif initial | demande conservée, revalidée ; capture Aubin 117503 + Mathe/Lucien | demande conservée, revalidée ; capture 117503 + mine 1985 (pain → vivres) |
| Tests ciblés au premier passage | 49/50 (KeyError Lucien/Anselme), banc bloqué par le code de retour | 92 verts |
| Test modifié | prémisses du test Lucien explicitées, 30 assertions intactes (à relire) | — |
| Banc 4 h, suspects 219 | 1 → 0, Aubin disparu | 1 → 0, Aubin disparu |
| Richesse S mine | 25,75 → 15,25 (−41 %) | 25,75 → 17,25 (−33 %) |
| Cause du recul de la mine | **prouvée** sur capture : la part reçue d'un lot (biscuits_1) n'est pas reconnue par la demande conservée ; 21 recharges identiques | **hypothèse** non prouvée : demande sans moyen qui attend sans borne au lieu du sommeil (dérives de Gorm mesurées) |
| Consignes | conformes | banc à 4 processus au lieu de 2, `rixe` au lieu du hameau ; commits sans accents |
| Relances du superviseur jusque-là | 4 (test en erreur, banc non lancé, recul de la mine, correction) | 2 (bilan du banc, correction) |
| État au soir | corrige les deux causes, banc à relancer | **arrêté** : quota gratuit épuisé ; version payante `opencode-go/deepseek-v4.1-flash` refusée (« requires Global regions », réglage Privacy de l'espace OpenCode Go à changer par l'utilisateur) |

## Premières observations
- DeepSeek livre vite et teste large ; il formule de bonnes hypothèses, mais prouve moins que Sol sur capture.
- Il s'écarte davantage des consignes de charge et de périmètre du banc : à rappeler explicitement dans ses consignes.
- Sol est plus rigoureux sur la preuve causale, mais demande plus de relances (arrêt sur erreur, banc non lancé).
- Décision provisoire de l'utilisateur (29 octobre) : DeepSeek pour les diagnostics seulement, version non gratuite,
  en attendant le bilan complet du lot 273.
