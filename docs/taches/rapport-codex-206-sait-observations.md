# Lot 206 — Savoir attribué à l’auditeur

Branche `codex-sait-observations`, **non fusionnée, validation globale non acquise**.
Base initiale `a488f1f`, reprise demandée sur **aadab7c** (205/207), fusion
`1457239` ; `cca5f50` ajoute seulement des briefs. Code mesuré : `7e1d9dd`.
Deux travailleurs au plus, priorité réduite, aucun Luna. Sans clé configurée,
commits non signés. Bruts : `C:/Users/msics/donjon/artifacts/sait-206/`.

**Invariant.** `social.bavarder` consulte uniquement les paroles, audiences et
observations communes du locuteur. `reviser_dits` ne rouvre plus les registres
des autres sur acquisition privée. La réception conserve `_connait_reception` :
une confirmation ne remplace pas la preuve personnelle, ni ne réapprend une
agression. `esprits.percevoir_tous` collecte les acquisitions d’une même passe,
avec support physique commun et témoin perçu. `voir_ensemble` couvre aussi les
états/possessions ; `pnj._temoins` conserve le geste public avant interprétation
individuelle. `social.observation_commune` persiste immédiatement valeur et
audience dans le registre existant. Regards physiques réutilisés dans la passe,
aucune ancienne croyance privée comme preuve. Témoin caché, arrivée ultérieure
et absence inférée de positions privées sont exclus. Fichiers interdits et
`_abriter` inchangés par ce lot.

**Diagnostic 191.** Neutraliser `_sait` partout reproduit deux échecs de défense ;
le retirer seulement de la décision en laisse un : avant d’intervenir, le
protecteur confie à Aubin l’agression déjà vécue et la torche éteinte. Réception
des confirmations et observation commune rétablissent ces cas. Les onze tests
de trajets passent sans reproduire l’ancienne régression ; aucun réancrage.

**Preuves.** Cas réel mine 3 : Rémy a lu seul le guet d’Odon ; Josse, qui
l’ignore, le lui redit. Autre cas : vivres épuisés connus par essai indépendant.
Huit nouveaux tests vérifient témoins visibles/cachés, geste réel, changements
privés/communs, salle, état et mots après rechargement. **57 ciblés finaux verts**.
Suite complète : **2 430 tests / 281 fichiers, 14 échecs, zéro erreur,
16 ignorés** ; quatre fragments terminés conservés, aucun fichier terminé
rejoué sur cette base. Recalcul pur/mémorisé vert.

Échecs maintenus : cinq comparaisons de registres après rotations, recours
(40 passages pour 12 permis), appel mine, source de perception, avis crue,
deux captures, confirmation supplémentaire, deux accusations de portage tues
au témoin. Deux comparaisons diagnostiquées diffèrent uniquement sur l’audience
joueur (4/12 champs) : ses rotations changent son regard ; six recharges
monde/rendu identiques. Cela n’explique pas tous les échecs ; leur caractère
préexistant sur aadab7c n’est pas établi. Assertions historiques non réancrées.

**Banc : vingt paires de quatre heures**, cinq scénarios × 1985/7/42/2024,
compteur des changements d’avis actif. Cache consulté, aucune nuit disponible :
vingt références calculées/rangées, puis branche. Sommes des quatre graines :

| Scénario | Confidences | Constats | Avis | Avertissements redits | Retours suspects |
|---|---:|---:|---:|---:|---:|
| Relais | 30 → 43 | 23 → 35 | 0 → 0 | 0 → 0 | 0 → 0 |
| Mine | 84 → 157 | 76 → 140 | 0 → 0 | 6 → 8 | 1 → 1 |
| Auberge | 57 → 75 | 56 → 74 | 0 → 0 | 1 → 2 | 5 → 6 |
| Crue | 56 → 334 | 41 → 319 | 4 → 3 | 0 → 7 | 9 → 15 |
| Hameau | 74 → 385 | 40 → 354 | 12 → 9 | 0 → 6 | 9 → 6 |

**Critères non validés.** Zéro plantage/usurpation, mais répétitions **2 → 23**,
demandes en boucle **0 → 26** ; suspects en hausse auberge 7, crue 7/42.
Exemples : Brune→Gorm, crue 1985, 54 confirmations ; Gorm→Aubin, hameau 7, 27.
L’audit normalise les hauteurs successives : ces comptes ne prouvent pas une
même valeur répétée, mais leur effet reste à résoudre. Entrées à expliquer
**204 → 204**, distinctes des retours non justifiés **24 → 28**.

**Reprise : ne pas fusionner comme correction validée.** Analyser confirmations
fréquentes et 14 échecs sans lecture privée ni exception sur l’eau. Anciennes
audiences manquantes non reconstructibles ; plafond de 512 identités inchangé.
Coprésence seule ne rend pas publiques intentions/prévisions. Preuves :
`suite-integration.json`, `banc-integration.json`, `synthese-banc-final.json` ;
ancienne passe a488f1f archivée séparément.
