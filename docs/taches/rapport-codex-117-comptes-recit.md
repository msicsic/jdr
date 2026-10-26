# Lot 117 — Comptes du récit par références : validation non acquise

26 octobre 2026 — branche `codex-comptes-recit`, **non fusionnée**,
base `6519588`. **Ne pas intégrer en l'état** : le contrat est implémenté,
mais le critère de conservation des refus justes échoue ; aucun gain de délai.

**Cause établie avant modification.** Attribution 113 et entrées exactes des
archives 91a4351 : le dossier fournit déjà `etat`, `issue`, `offres`, avec
rôles, quantités et références publiques. Le schéma exige pourtant une seconde
construction des comptes depuis la prose, y compris les pronoms du locuteur.
Au soir, « elles sont à moi » devient une absence de dette-objet ; « les pièces
sont rendues ; la planche te sera remise » perd les deux termes de l'issue.
Une offre conditionnelle de la crypte devient une dette exigible. L'inversion
réelle « Tu m'en dois deux » reste un refus juste, distinct de ces erreurs.
Les quarante fichiers sources relus gardent leurs SHA-256 archivés.

**Changement.** `narration.references_comptes` catalogue les seuls comptes
publics fournis, avec priorité et dédoublonnage de l'issue ; `mj._appeler`
transmet ce dossier commun. `schema_audit` demande, par segment, un jugement
obligatoire pour chaque référence : `non_evoque`, `restitue`, `contredit`.
Aucun rôle, quantité ou terme n'est réextrait. `controler` conserve ces liens
dans l'audit canonique, refuse les contradictions et vérifie la couverture de
l'issue avant enregistrement. L'ancien format reste contrôlé pour les sauvegardes
historiques. Aucun scénario, `echanges.py`, modèle ou prompt narratif modifié.
Un essai par listes, puis une reconversion erronée vers l'ancien contrôle,
ont été abandonnés ; leurs bruts `essai-*` sont exclus des mesures finales.

**Vérifications.** Console et recharge avec MJ simulé : remboursements de Gorm
et d'Aubin, autre dette et autre bien, refus de Brune, paiement du soir avec
pièces rendues et planche encore due ; pas de relance sur les récits conformes.
Une inversion signalée par l'audit reste refusée et non publiée. Conservation,
relecture et altération des liens contrôlées. Suite complète unique : **2 035
tests, 16 ignorés, 220 fichiers, 1 865,15 s**, deux processus réduits ; une
erreur dans le générateur d'exemples d'un test, qui remplissait le nouveau champ
objet comme une chaîne. Générateur corrigé ; **sept tests du fichier repris
verts en 2,93 s**, aucune seconde suite complète. Aucun défaut de production
signalé par la suite.

Rejeu Luna des **16 refus narratifs exacts** de 91a4351 : onze refus, cinq
admissions, aucun illisible ni erreur. Cinq écarts rejoués cinq fois par schéma :

| Cas (passe 2, tour, audit) | Refus ancien → final / 5 |
|---|---:|
| Crypte, 24, 2 : offre | 5 → 0 |
| Ambiance, 1, 1 | 4 → 0 |
| Soir-appel, 2, 4 : possession | 3 → 0 |
| Soir-appel, 2, 7 : **inversion réelle** | **5 → 3** |
| Soir-appel, 5, 7 : livraison future | 4 → 2 |

**Deux passes finales**, comptes / soir-appel / ressources / crypte,
91a4351 en cache (huit parties, aucune référence rejouée) :

| Ensemble, 36 tours MJ par variante | Référence → final |
|---|---:|
| Appels / appels par tour | 149 / 4,139 → 129 / 3,583 |
| Relances / replis | 13 / 2 → 6 / 1 |
| Secondes par tour, moyenne | 14,723 → 15,335 |

Aucun arrêt ni erreur technique ou de recharge. Poste partagé, temps historiques,
lots 112/113/116 déjà présents : aucune causalité de latence isolée.

**Limite décisive.** Les comptes viennent désormais du moteur, mais leur liaison
au texte reste sémantique. L'inversion réelle est admise deux fois sur cinq,
contre zéro auparavant ; le seuil des méthodes 93/95/116 est dépassé.
Des faux refus et une omission de Brune subsistent. Cette branche est un
candidat refusé à la validation, **pas une solution générale livrée**.
Bruts et scripts : `artifacts/comptes-117/` ; banc final
`artifacts/bancs-multi/20261026-073528-44328/`.
