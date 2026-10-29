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

## Lot 273, résultat de la reprise (nuit du 29 octobre, vers 3 h)
Même consigne de reprise pour les deux (corriger les deux causes du recul de la mine, puis vingt nuits sur les cinq
scénarios du brief). DeepSeek a repris en version payante `opencode-go/deepseek-v4.1-flash` high (nouvel agent dans
le même espace, quota gratuit épuisé), banc conforme cette fois (cinq scénarios, deux processus).

| | Sol 6.1 high (`7d0fce7`) | DeepSeek V4.1 Flash Go high (`dfa2181`) |
|---|---|---|
| Correctifs | provenance transitive lot → part ; sommeil des demandes sans plan admissible | `_meme_demande_tenue` (même raison = même demande, sauf mission d'objet précis) ; sommeil des demandes sociales de fourniture, garde/lieu/ronde/mission gardent l'attente |
| Tests | 16 ciblés verts ; 449 compléments, 5 échecs instruits (2 hérités, 3 nouveaux, dont un défaut réel de présence au service de Tilo, déjà présent sur le parent) | 47 + 106 ciblés verts |
| Suspects 219 (20 nuits) | **1 → 3** : critère non tenu | **1 → 3** (Gorm, crue 42) : critère non tenu |
| Richesse S mine (référence 19–32, moyenne 25,75) | **16** : hors étendue | **16,75** : hors étendue |
| Conclusion de l'agent | fusion différée | les deux critères échouent |

**Les deux réalisations indépendantes convergent vers le même échec** : à preuve égale, ce n'est plus une question de
modèle mais de conception du lot 273. Garder la demande adoptée après l'échec d'un moyen coûte de la richesse à la mine
et ajoute des suspects, quelle que soit la façon de la revalider. À trancher avec l'utilisateur avant toute nouvelle
reprise (piste : borner la conservation d'une demande à la revalidation immédiate de ses moyens, ou garder la clôture
historique et ne corriger que la renaissance perceptive du lot 272).

**Pour l'évaluation de DeepSeek** : sur ce lot de code, il égale Sol sur le résultat mesuré, avec moins de relances et
plus de tests, mais un écart de méthode (même raison = même demande, que le brief demandait d'éviter hors exception)
et des écarts de consignes au premier banc. Sol a apporté la preuve causale décisive (part de lot non reconnue) et un
défaut réel de plus (Tilo).
