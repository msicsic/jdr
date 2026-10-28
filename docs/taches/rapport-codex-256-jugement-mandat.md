# Lot 256 — jugement du mandat selon l'autorité perçue

Branche `codex-jugement-mandat`, **non fusionnée**, base `integration
4318a5b`, 28 octobre 2026. Aucun scénario, MJ, `social.py`, `esprits.py`
ou `planification.py` modifié ; aucun appel Luna ni suite complète.

`echanges.confier(..., mandat={parent, sorte, parametres})` juge un mandat
explicite, sans sélectionner son destinataire. Le chemin historique des
conditions conserve son jet, désormais extrait dans `_juger_tache` : même
faisabilité, coût / 5, altruisme, liens, volonté et un seul d20. Pour un
mandat social, `agendas.devis_mandat` publie sur une **copie**, puis reprend
le prochain sous-but et son coût du planificateur d'agenda existant.
Il ne traite pas une personne comme un objet transportable.

`relations.autorite_mandat` lit le statut **cru**, seulement pour une voix
identifiée, dans le lieu courant du mandaté et le domaine égal à la sorte
du mandat (`amener` / `informer`). Calibrage : statut pertinent **3 points**
de DD, ascendant **0 à 3**, somme plafonnée à **5**. La dette reste celle du
jet commun (**dette / 20**, au plus 5), jamais ajoutée une seconde fois.
Les refus d'accueil précèdent devis et jet ; aucune peur ne les contourne.
Même statut et ascendant maximaux ne garantissent pas l'accord.

Le parent conserve `jugements` avant la publication et sa chronique :
destinataire, date, charge, issue, raison et, après jet, coût, autorité,
total et DD. « adhésion » signifie que le jet suffisait sans dette ni bonus ;
sinon « dette » s'il suffisait sans bonus ; sinon « autorité » (éventuellement
avec la dette). Un refus garde sa cause d'accueil, d'impossibilité ou son
bilan de jet. La recharge valide ces enregistrements. L'acceptation passe
par `agendas.confier`, avec ses liens réciproques et ses bornes ; une
confirmation conserve l'enfant, même terminal, sans nouveau jet.

**Preuves ciblées : 68 tests verts, neuf fichiers, 32,616 s**, deux processus
à priorité réduite. Sept tests nouveaux : Gorm → Aubin → Brune et une
transmission à Ilse ; statut dans/hors lieu et domaine, dette, ascendant,
adhésion, refus malgré l'autorité maximale, méfiance/rancune et impossibilité
avant jet, pureté du devis, ancienne demande inchangée, ordre jugement puis
chronique, confirmation, désespoir devant agenda. Les deux mandats acceptés
produisent leur parole réelle ; état complet, rendu, scène et paroles entendues
conservés après sauvegarde/recharge et mêmes laps entiers/découpés. Les refus
sont également rechargés. Tests voisins : filiation, activation, déplacements
sociaux, statuts sourcés, ascendant, argent et paroles. `git diff --check` vert.

**Banc rapide demandé : en cours**, cinq scénarios × quatre graines, 4 h,
référence figée `4318a5b`, cache commun, au plus deux processus réduits,
référence puis branche. Sortie et compteur 219 dans
`C:/Users/msics/donjon/artifacts/mandat-256/comparaison.json` ; comparaison
supplémentaire des chroniques, mesures et empreintes complètes dans
`identite.json`, sans rejouer les nuits. Fichier final écrit en dernier :
`fin.json`. Aucune identité des vingt nuits n'est encore déclarée.

Limites : calibrage initial à éprouver dans les futurs profils de scénario ;
le devis est celui du **prochain sous-but social**, pas une garantie du
consentement du tiers ni de réussite complète. Les priorités vitales utilisent
l'arbitrage existant, sans changement de `deliberation.py`. Choix autonome du
mandataire, contrainte, protocole vocal du mandat et évolution d'ascendant
restent aux lots suivants. L'API explicite n'a aucun appelant autonome nouveau.
