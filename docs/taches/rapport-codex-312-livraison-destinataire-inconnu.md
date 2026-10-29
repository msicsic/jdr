# Lot 312 — livrer à un destinataire de lieu inconnu

29 octobre 2026. Branche **`codex-livraison-inconnu`, non fusionnée**, base
**`06465d9`**. Vérifications longues en cours ; ce rapport sera complété à leur
retour. Aucun MJ, scénario, `biens.py`, `dialogues.py` ni `mj.py` modifié.

**Invariant et code.** Un lieu inconnu prépare un contact, au lieu de prouver
l'impossibilité d'une remise. `_devis_remise` vérifie encore l'acquisition du
bien, puis chiffre inspection, appel ou question par `_localiser` et `_chercher`.
`_localiser` est extrait du contrat de service du 303, qui l'utilise aussi.
Le plan publié s'arrête au préfixe certain : aucune remise ni restauration de
charges sur une présence supposée. `devis_pulsion`, `planifier_tache`,
`echanges.devis_service`, `empeche` et l'annulation lisent ce devis inchangé dans
leurs appelants. `_contact_possible` écarte mort et départ **crus**, aussi pour
`rejoindre` ; aucune position cachée n'est interrogée, aucun champ de sauvegarde,
délai ou registre de réessai ajouté.

**Preuves ciblées.** Relais 7 repris à **856**, avant `agendas.echoir`, avec la
livraison d'origine encore active : Gorm garde but, motif, date et charges
suspendues, demande Aubin à Brune puis remet `vivres_1`. La capture 308 à ce même
instant était prise après le choix et l'annulation ; le nouveau point la
précède. Contre-épreuve avec la fonction du devis extraite de `06465d9` : plan
`None` et empêchement vrai, alors que le contact propose déjà la question.
Autre chaîne : Mathe cherche Lucien à la mine puis lui remet les vivres.
Pour les deux, monde, rendu, scène et textes identiques après sauvegarde réelle,
rechargement et **huit minutes d'un bloc ou huit fois une minute** ; parole
tenue mémorisée, aucun abandon de cette livraison. Devis pur et invariant sous
tous les déplacements réels cachés du destinataire. Départ cru, même avec une
ancienne localisation connue, continue d'annuler ; bien cru détruit et absence
de tout recours continuent d'empêcher. Le seul temps ne rouvre pas une recherche.

**Mesures disponibles.** Cinq premiers tests verts (**49,693 s**), puis la
sixième preuve sans recours verte (**4,620 s**). La première passe conservée a
révélé deux fixtures de lieu sans champs spatiaux, corrigées sans modifier
l'oracle. Le lanceur exécute les **onze fichiers directement concernés** à un
travailleur réduit, puis le banc **4 h × quatre graines × Relais/auberge/mine**,
référence `06465d9` par le cache commun, référence puis branche. Il produit
`tests-cibles.json`, `banc.json`, les livraisons tenues/annulées, portions et
suspects 219 par nuit dans `synthese.json`, et écrit **`fin.json` en dernier**.
Les résultats du banc et l'analyse des nouveaux constats restent à lire.

**Limites.** Trouver quelqu'un ou obtenir une réponse n'est pas garanti. Les
recherches épuisées restent fermées sans indice nouveau. La règle historique
d'échéance des paroles (`ENGAGEMENT_MAX`, 240 min), explicitement testée dans
les contrats existants, reste inchangée : ce lot corrige l'empêchement dû au lieu
inconnu, pas cette échéance générale. Aucune garantie universelle contre les
boucles n'est annoncée avant la lecture du banc. Ni Luna ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/livraison-312/`.
