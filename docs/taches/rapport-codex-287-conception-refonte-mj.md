# Lot 287 — conception de la refonte du MJ

29 octobre 2026 — branche `codex-conception-refonte-mj`, **non fusionnée**,
base intégration `a3666ee`. **Conception livrée, décisions ouvertes ; aucun
correctif ni nouvelle garantie du jeu.**

[Document de conception](../conception-refonte-mj.md) : achever et porter
**`origin/prompt-simplifie`**, conformément à la précision de l'utilisateur.
Compilateur d'intention à petit contexte, `MJ._echanger_decouple`, gardes de
`narrateur.py`, ambiance non bloquante et fournisseur local unifié constituent
la base. La conception inventorie les affirmations mécaniques à rendre par
le moteur, les répliques des PNJ, les raccords et les lots successifs.
**Gameplay prioritaire** : intentions comprises/exécutées, vitesse avant effet,
invention ciblée, interactions PNJ ; plan ordonné selon ces quatre axes,
section « mesures du gameplay » et coût/protection de chaque appel.

**Mesures, archives seulement.** 136 parties lues, 34 scripts × deux passes
pour `d85fb54` et `c9459ce`, 136 SHA-256 inchangés après lecture. Dernière
campagne : **187 tours MJ, 561 appels, 3,000 appels/tour, 5,80 s/tour**
(médiane globale 5,17 s), **30 obstacles narratifs, 26 relances, 48 refus de
validation, zéro repli**. Récit/audit/révision : **281 appels et 43,54 % de
l'attente modèle** ; pas une prévision de gain. Interprétation : 162 premiers
appels et 26 supplémentaires. Positions/perception : 13 des 30 obstacles,
cas mixte compris ; ces familles passent en tête. Classement complet par
cause, exemples justes/faux et sources contradictoires conservés. Une issue
d'avis impose le silence des témoins tout en fournissant leurs répliques :
unifier les émissions avant de supprimer leur contrôle. Secondes historiques
sous charges différentes, aucun gain causal annoncé.

**Portage précisé par Git.** Prototype `3c0dcd0` : 20 commits, 25 fichiers,
4 376 insertions/51 suppressions depuis `c870c8b`. Intégration : 225 commits,
mais `mj.py`, `narration.py`, `consignes.py`, `comptes_narratifs.py` et les
fournisseurs sont identiques à cette base. Le lot 180, les refus, actes,
rappels et avis en sont déjà hérités : les raccorder aux voies découplées.
Préserver les changements actuels des PNJ/signes, `jet_persuasion` et de la
page web. Le prototype garde des manques : réplique synchrone, ambiance
relancée, ciblage absent, fondement trop large, raccourcis sémantiques et
négociation de mission mal typée.

**Décisions proposées.** Rendu moteur pour toute mécanique et les répliques
à contenu déterminé ; ambiance libre gardée déterministement, jetée entière
sans relance. Nouveau contrat marqué « décision à l'utilisateur », pas appliqué
à `AGENTS.md`. L'audit cosmétique disparaît ; une compatibilité sémantique
universelle de la prose libre n'est pas garantie. Fidélité d'intention et
qualification interactive non calculable justifient seules des revues ciblées
résiduelles, explicitement exceptionnelles à la voie nominale du compilateur.
Le document compare deux options de répliques et pose sept questions avec
recommandations. 176 devient rendu des signes ; 170 rejoint le compilateur ;
162 devient sans objet pour la narration ; 171 devient rendu des mesures ;
166 reste abandonné. Plan de lots bornés, tests après recharge et mesures
Luna ciblées **à venir**, avec références en cache.

**Vérification et limites.** Lecture des contrats, plans, code et tests du
prototype, rapports 93/95/116/141/153/162/165/168/170/171/176/180/216 et
archives récentes. Bruts 168/171 absents sur ce laptop : diagnostics publiés
cités, sans recomptage prétendu. Un processus Python léger à la fois, aucun
import du jeu, appel Luna, banc ou test moteur. Contrôle documentaire et
`git diff --check` ; seuls trois documents livrés, aucun fichier de jeu,
test ou outil modifié. Bruts/scripts dans
`C:/Users/msics/donjon/artifacts/refonte-287/`. Aucune fusion ni rebase.
