# Lot 245 — préparer A5, mandat et autorité

`codex-conception-a5`, **non fusionnée**, base `integration 9b69785`,
28 octobre 2026. Lecture seule du moteur et des rapports 122, 146 e,
167 c, 213, 240 et 242 ; aucun code du jeu, test, banc ou appel Luna exécuté.
A5 dispose de briques, pas encore d'un contrat de mandat général.

## Inventaire vérifié

| Élément du plan, § 6.6 et autorité | État sur cette base et manque |
|---|---|
| Mandater | **Partiel.** `echanges.confier` accepte une condition ; `agendas._amener` demande un déplacement propre ; `pnj_propositions.devis_intermediaire` trouve un livreur après refus social. Pas de choix général faire/confier. |
| Jugement du mandaté | **Partiel.** `confier`, `devis_service`, `paroles.jet_persuasion` : faisabilité, coût, altruisme, liens et VOL ; `engager` : paie. Autorité, peur et raisons adhésion/crainte manquent au jugement du mandat. |
| Origine `mandat` | **Absente.** `agendas.prendre` stocke un engagement historique ; `verifier` autorise seulement `scenario/situation/evenement` pour les projets. Ni parent ni `confies`. Cycle/sommeil et contrat 213 existent. |
| Suivi/compte rendu | **Partiel.** `aides_attendues`, `echanges.tenu`, `_amener` et annonces d'abandon ; `planification.Vue` conserve l'aide acceptée sous adoption (240). Aucun `compte_rendu` dans `paroles.TYPES`. Suivi temporel 242 hors base. |
| Réaffectation | **Absente** : ni identité de sous-but attribué ni hystérésis entre titulaires. |
| Parole/voix | **Socle existant** : `echanges.executer` → `pnj.se_parler` ; `accueil`, `relations.percue`, `voix.reconnaitre/entendre`. Types joueur `mandat/compte_rendu` absents ; identité reconnue ≠ statut prouvé. |
| Récursion bornée | **Absente.** L'autonomie imposée par `planification.devis_pulsion` n'est pas une profondeur de mandats ni un contrôle de cycles. |
| Statut | **Absent** comme autorité typée, sourcée et connue ; « gardien du relais » reste un portrait. |
| Ascendant | **Absent.** Cinq `relations.AXES` ; façade, preuves, signatures, estompement et validation réutilisables. |
| Lecture dérivée | **Partielle** : confiance/dette/peur dans `relations.py`, aucune autorité commune. `chance_demande` estime du point de vue du demandeur ; ce n'est pas le jet réel. |

**Dépendance 242.** Rapport et code lus à `origin/codex-suivi-delegation`,
commit `0b37f44`, non ancêtre de cette base : `agendas.aide_echue`,
`suivis_delegations`, `clore_aides_constatees`, `renouveler` ; durée physique
`planification.duree_devis`, échéance dans `echanges.confier`. Visite après
échéance, relance sans deuxième obligation, reprise autonome sont livrées
sur cette branche, pas ici. Ni compte rendu général ni nouveau titulaire.
Charges initiales non datées et devis incertains restent sans délai inventé.
Intégrer ce lot avant A5.

**Épreuve déjà disponible.** `scenario_crue_hameau.json` contient six PNJ :
Gorm (`marchand`), Brune, Ilse, Aubin, Maël, Sève : effectif suffisant.
Aubin ramenant Brune exige l'agenda social `amener` ; `_pulsion` traite
actuellement `objet=tiers, lieu=…` par prise/pose, sans consentement social.

## Lots successifs proposés, 30 à 45 minutes chacun

Chaque ligne porte un invariant. Les fichiers nommés sont dans `donjon/` ;
**tous les autres restent hors lot**, en particulier scénarios avant 11,
MJ avant 9–10, A6/A7/A8, suivi vocal et interposition de lieu.
Les extensions sont **à autoriser dans les futurs briefs**.

**Preuve commune P** : scène indiquée et autre cas de même nature, chaîne
choix → exécution → sauvegarde/recharge → monde et rendu joueur ; laps
entier/découpé. Tests ciblés et voisins, pas de suite complète. Comportement :
banc rapide 4 h, quatre graines, hameau/crue/Relais et
autres scénarios effectivement touchés ; références en cache, suspects 219,
attente, S/F/D, répétitions et coût. Pour un socle neutre : empreintes 2 h,
quatre graines, mêmes scénarios. Une passe Luna ciblée seulement en 9–10.

| Lot / invariant | Fichiers ; extensions prévisibles | Épreuve et preuve particulière, en plus de P |
|---|---|---|
| **1. L'ascendant neutre conserve les choix.** | `relations.py` ; extensions : validation `deliberation.py`, consommateurs d'axes, tests `relations_*`/AST. Ni jet ni attribution. | Deux liens orientés, lecture pure, signatures, anciennes données sans migration ; empreintes neutres. |
| **2. Un statut n'agit que comme croyance sourcée et de portée définie.** | `esprits.py`, `relations.py` ; extension : validation de profil `deliberation.py`, transport d'affirmation dans `social.py` et tests ouïe. Ni bonus au jet ni scénario. | Statut déclaré en fixture de Gorm, autre employeur ; ignorance et prétention contradictoire ne deviennent pas savoir réel. |
| **3. Une filiation de mandat reste unique et bornée.** | `agendas.py`, `echanges.py` ; extension : validation `esprits.py`, tests socle/transferts/engagements. Ni sélection ni conversion des anciens contrats. | API commune, `amener` et `informer` ; refus sans enfant, relance idempotente, cycle A→B→A refusé, profondeur persistée. |
| **4. Le destinataire juge le mandat selon son autorité perçue, sans obéissance automatique.** | `relations.py`, `echanges.py`, `agendas.py` ; extension : raccord étroit de `paroles.jet_persuasion` et urgence dans `deliberation.py`. Ni jet des demandes ordinaires changé par défaut ni choix du mandataire. | Aubin accepte/refuse ; autre mandaté endetté ou craintif ; même règle, raison enregistrée avant récit. Besoin désespéré, alarme, eau restent prioritaires. |
| **5. Faire ou confier se compare sur les seules croyances du mandant.** | `agendas.py`, `planification.py`, `deliberation.py` ; extension : adaptations des devis sociaux et de `_entrees`, tests `amener_*`/intermédiaires. Ni nouveau suivi ni changement des marchés `pnj_propositions.py`. | Gorm→Aubin→Brune, puis une information à transmettre ; déplacer réellement le candidat hors perception ne change pas le choix. Coût, fiabilité, égalité par identifiant ; demande sociale à Brune, pas portage implicite. |
| **6. Un compte rendu informe le mandant sans rendre son contenu vrai.** | `agendas.py`, `echanges.py`, `social.py` ; extension : `ouie.py`/`voix.py` seulement pour transport typé et attribution, tests parole/voix. Ni protocole joueur ni nouvel estimateur. | Réussite, échec et mensonge sur les deux charges ; hors portée, rien n'est appris. Réception après recharge, constat contradictoire et absence de clôture omnisciente. |
| **7. Réaffecter conserve une attribution cohérente et respecte les nouvelles disponibles.** | `agendas.py`, `deliberation.py` ; extension : raccord 242 dans `echanges.py` et `planification.py`, tests de suivi. Ni délai arbitraire ni reprise du refus inchangé. | Aubin en retard puis remplacement, autre charge à la mine ; résultat appris en route arrête la visite. Ancien titulaire non informé peut continuer : aucune annulation télépathique ; hystérésis VOL et absence de navette à contrôler. |
| **8. L'ascendant évolue une fois par issue ou abus perçu.** | `relations.py`, `agendas.py` ; extension : souvenirs `esprits.py` et transport `social.py`, tests preuves/relations. Ni réputation/sanction A7 ni nouvelle règle de violence. | Ordre abouti, échec et abus définis par prédicats moteur, autre relation ; témoin ignorant inchangé, compte rendu incertain distinct du constat, recharge sans double gain. |
| **9. Mandater ou recevoir un mandat côté joueur utilise le même contrat.** | `paroles.py`, `agendas.py`, `echanges.py` ; extension : schéma/contexte `mj.py`, `narration.py`, `rendu.py`, tests dialogue/MJ. Ni nouveau modèle ni comparaison. | Corvus donne puis reçoit un mandat, autre charge ; voix inconnue/prétendue, refus, fiche persistée ; pas d'exécution forcée du joueur ni fuite d'agenda secret. |
| **10. Le compte rendu du joueur conserve la provenance d'une parole.** | `paroles.py`, `agendas.py`, `echanges.py` ; extensions MJ/rendu identiques à 9 et contre-revue du contenu. Ni modification du jugement de mandat. | Corvus annonce vrai/faux sur deux charges ; moteur enregistre parole et croyance avant réponse, jamais déplacement/ressource fictifs. |
| **11. Les données du banc n'ajoutent aucune règle de décision.** | `scenario_crue_hameau.json`, tests/scènes et scripts ciblés ; extension : données de savoir/statut et compteurs `banc_pnj.py`, audit `tools/audit_nuits.py`. Aucun moteur. | Six PNJ existants, statut et liens approuvés ; Gorm confie Brune selon coûts, sans attribution forcée. Contre-épreuve même scénario sans autorité, autre scène hors crue ; banc rapide avant intégration lourde groupée. |

Lot 5 : **sous-but et mandataire : deux fonctions séparées, chacune appelée
en un seul endroit**. Le devis vu du mandant ne lit pas l'esprit privé
d'Aubin : projection de connaissances à prévoir, ou lot neutre préalable
si le créneau ne suffit pas ; aucun classement partiellement omniscient.

## Arbitrages à soumettre avant les briefs concernés

- **Gorm (2/11)** : responsable reconnu par tous ou par certains occupants ?
  Recommandation : portée limitée aux lieux, connaisseurs déclarés.
  Ascendants initiaux : neutres ou liens explicitement renseignés.
- **Effet de l'autorité (4/8)** : conserver les refus d'accueil actuels,
  ou permettre à la peur de les dépasser pour un mandat ? Recommandation :
  les conserver ; les lever changerait une règle actuelle. Le bonus reste
  borné, sans obéissance automatique. Pour son calibrage : départ neutre et
  petites variations, ou liens initiaux contrastés à déclarer ; proposer
  coefficients, estompement et preuves d'abus avant implémentation.
- **Profondeur (3)** : une seule transmission, ou deux niveaux permettant
  au mandaté de sous-déléguer ? Recommandation : deux arêtes depuis
  l'agenda racine, cycles interdits ; chiffre à confirmer.
- **Retard (7)** : avertir l'ancien titulaire quand il est joignable puis
  réaffecter sur croyances, ou attendre son acquittement avant tout secours ?
  Recommandation : premier choix, avec risque explicite de deux intervenants
  tant que l'annulation n'est pas entendue. Ne pas fermer à distance son agenda.

Acquis du 23 octobre conservés : trois sources d'autorité, trois agendas
actifs maximum, hystérésis VOL, priorités vitales, Luna `gpt-6-luna` sans
secrets. Aucune garantie d'évacuation ni validation des futures mécaniques ;
preuves du 242 citées, non rejouées.
