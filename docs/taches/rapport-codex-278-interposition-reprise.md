# Lot 278 — Établissement de l’interposition reprise

29 octobre 2026, branche `codex-interposition-reprise`, base `792816c`,
**non fusionnée**. **La reprise signalée est admissible : aucun correctif moteur.**
La clause d’arrêt du brief s’applique ; son hypothèse de départ doit être rectifiée.

**Preuve réelle.** Rejeu de la nuit hameau 1985 sur les sources exactes de
`0bad227`, avec la sonde de cette archive, un seul processus à priorité réduite :
296,773 s. Identité à l’archive 274 des empreintes, chronique, mesures, récit et
souvenirs ; aucun plantage. Douze captures, dont avant 635 et avant 642,
rechargées : **36 égalités monde/rendu/scène**, toutes vraies.

| Capture / instant (dixièmes de seconde) | Croyance de Gorm sur Aubin | État réel relevé par la sonde |
|---|---|---|
| Avant 635 : `380658` | `antichambre`, `[5,2]`, `entendu`, minute 634 | `antichambre`, `[5,3]` |
| Avant 642 : `384600` | `antichambre`, `[1,2]`, `entendu`, minute 635 | `crypte`, `[4,3]` |
| Reprise : `385475` | `antichambre`, `[5,1]`, `entendu`, minute 642 | `antichambre`, `[5,1]` |
| Retrait : `385500` | lieu/case inconnus, `vu`, minute 642 | `antichambre`, `[5,3]` |

À la reprise, Brune est crue et vue dans `antichambre`, `[7,3]`, minute 642 :
distance de Chebyshev 2 avec Aubin. Les rôles du brief étaient inversés :
`{type: interposer, qui: brune, objet: aubin}` désigne **Brune approchante et
Aubin protégé**. Le départ annoncé à 642 est en fait un retour : la chronique
place Aubin dans la **Conduite basse à `385265`**, puis au **Refuge du relais
à `385373`** ; ce dernier est précisément la salle d’identifiant `antichambre`.
Aubin est donc revenu **10,2 secondes avant** la décision, et sa localisation
crue a été renouvelée. La capture avant 642, prise à 641, ne suffit pas à
décrire l’état à `385475`.

**Chemin réellement emprunté.** La pile enregistrée donne `pnj._avancer` →
`deliberation.choisir` → `evaluer` → méthode du candidat
`defense.interposition` (lot 167), inscrit par `_candidats` au palier
`PAROLE_DUE`. Le générateur recalcule les lieux/cases des deux cibles sur les
croyances et le poste `[6,2]` ; ce n’est ni `_reprendre_demande`, ni un agenda
`garder`/`protéger`, ni un ancien suffixe recopié. `pnj.agir` appelle de nouveau
`defense.interposition` à `385475` avant le pas de placement. À `385490`, la
localisation d’Aubin devient inconnue (`source=vu`) ; à `385500`, `choisir`
retire l’interposition. Aucune nouvelle mise en garde de Gorm n’est affichée
entre 641 et 643 dans la chronique.

**Livraison et limites.** Seuls ce rapport et `docs/etat-dev.md` changent ;
aucune fonction du moteur, aucun test, `agendas.py` et `signes.py` inchangés.
Poussée tentée depuis le PC fixe : échec d’authentification Git (`wincredman`,
puis absence de terminal pour demander l’identifiant). Commit conservé
localement ; aucun recours à l’API GitHub.
Pas de nouveau banc 4 h, de Luna ni de suite complète : la correction
conditionnelle est arrêtée à l’établissement. Le diagnostic porte sur
`0bad227`, pas sur une nouvelle nuit de `792816c` ; ni un second cas, ni
l’invariance par découpage temporel, ni le contrat général de toute
interposition ne sont certifiés. Le classement suspect 219 reste inchangé.

Bruts : `C:/Users/msics/donjon/artifacts/interposition-278/` ;
`fin-etablissement.json` (`ok=true`), `preuve-diagnostic.json`,
`fil-choix.json`, `appels-interposition.json`, `revisions.json`,
`recharges.json` et captures `choix-385475-96-avant/apres.json`.
Le script `etablissement.py` et les sources archivées y sont conservés.

**QUESTION : requalifier l’alerte 274 comme reprise admissible, puisque
Aubin est revenu et que les deux présences sont revalidées, plutôt
qu’appliquer le correctif fondé sur son départ supposé ?**
