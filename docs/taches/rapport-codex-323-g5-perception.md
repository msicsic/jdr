# Lot 323 — G5, perception canonique

Lot clos le 2026-10-29 ; **livraison G5 partielle**, branche `codex-g5-perception`,
**non fusionnée**, base `integration 4794376`.

La perception calculable utilise les actions actuelles du moteur. `observer` et
`examiner` sur une cible connue non visible rendent désormais un constat public
sans effet, au lieu d'un refus déduit de sa présence réelle. `rendu.non_perception`
lit `perception.non_vus_connus`, `couverture_vue` et la mémoire visuelle existante :
aucun registre parallèle de présences, aucune position cachée lue pour le récit.
La cible visible garde l'examen et l'observation des signes existants, y compris
la rotation et le bilan de présences moteur.

Quatre situations restent distinctes : la vue actuelle est rendue par `regarder`
ou `decrire` ; une cible non vue reçoit une non-perception, même si elle est
physiquement présente ; une couverture complète autorise seulement un constat
d'absence **dans la partie visible de la salle**, explicitement sans les contenus
cachés ; une dernière observation reste présentée comme passée, sans garantie
de position actuelle. `refus.perception` et les attestations narratives réutilisent
ce même rendu. Le refus commun ne consulte plus la position réelle d'une entité
cachée pour affirmer qu'elle n'est pas ici.

`Plan.perception_canonique` identifie les perceptions seules, sans jet, confirmation,
effet d'échec ou effet proposé autre que l'acquisition de ce qui est perçu.
Leur contre-revue est retirée dans `MJ._auditer_action` ; aucun récit ni audit de
récit n'est demandé pour leur résultat. Compositions, apprentissages de lecture
et autres actes gardent leurs contrôles. Les consignes existantes de choix du mode
sont corrigées : elles demandaient encore un dialogue pour toute question
d'information ; elles exposent maintenant le contrat des actions moteur.
La commande `regarder` enregistre aussi sa réponse avant l'affichage.

**Vérification : 117 tests, onze fichiers, tous verts**, sans erreur ni saut,
24,480 s, deux travailleurs à priorité réduite. Sept nouveaux tests couvrent les
captures réelles `signes-guet` et `signes-noir`, un absent à l'auberge et au Relais,
le souvenir d'une position passée, une cible vue, le texte sur disque avant sa
publication et l'interprétation libre limitée à un appel sans audit. Le monde
complet, le texte, la scène et la carte sont vérifiés après recharge. Les tests
d'écoute et de fouille vide existants passent sans contre-revue de perception.
L'oracle historique du refus dans le noir devient un constat sans signe révélé ;
le test du refus de fidélité est porté sur une attente, avec ses assertions de
motif, plan et non-publication conservées. Bruts initiaux conservés séparément.

**Luna : une passe achevée**, `gpt-6-luna`, priorité réduite, code 0,
104,896 s de bout en bout, 24 tours hors « quitter », dont 17 avec modèle.

| Script | Appels | Constat |
| --- | ---: | --- |
| signes-guet | 9 | Deux questions prises pour des paroles ; un repli après trois rédactions contrôlées. |
| signes-noir | 2 | Observer Ilse et regarder : zéro appel ; peur d'Ilse : dialogue audité, sans absence inventée. |
| luna-restes-ambiance | 7 | Ambiance conservée ; écoute seulement préparée ; position mémorisée reformulée une fois. |
| atelier | 18 | Mur et recherche de pierre : une interprétation chacun, résultat moteur sans audit ; outils : dialogue encore audité. |

Total **36 appels** : 18 interprétations, 10 audits narratifs, quatre
contre-revues d'autres actes, trois révisions et un récit après parole.
Aucune erreur technique, erreur de recharge ou mention sans fondement signalée
par le banc ; ces compteurs ne prouvent pas toute la fidélité des réponses.
Deux tours refusés à l'atelier : lien manquant puis perche hors de portée pour
l'échelle ; mur hors de portée pour le saut. Aucun acte annoncé comme réalisé.
Dans `signes-guet`, « Que fait Brune ? » est prononcé puis reçoit un repli de
paroles ; « Que fait Gorm en ce moment ? » reçoit une demande de destinataire.
Ces demandes d'information n'ont donc pas atteint la voie de perception G5.

**Limite de clôture : G5 partiel.** La perception typée moteur est livrée ; le
routage général du libre n'est pas garanti et le critère global de réponses de
perception sans audit n'est pas atteint. Aucun contrôle de dialogue n'a été
retiré pour masquer ce défaut. La question sur les bruits prépare `ecouter`
sans l'exécuter, selon la frontière actuelle des questions dans `commandes.py` ;
aucun résultat d'écoute n'est revendiqué. La dernière position de la poutre
reste un souvenir correctement borné, mais audité (suite G6). Un détail inconnu
conserve son admission ; ambiance et autres voies conservent leurs contrôles.
L'absence ne porte jamais sur une cache ou une salle hors de vue.

Aucune référence correspondante dans le cache de `main c870c8b` ; aucune
référence relancée, aucun gain comparatif revendiqué. Bruts, analyse détaillée
`analyse-luna.json` et `fin-luna-passe.json` (`ok=true`) dans
`C:/Users/msics/donjon/artifacts/g5-323/`. Le premier échec du lanceur, avant tout
appel modèle, reste dans `fin-luna.json`. Aucun calcul actif ; code et tests
inchangés depuis les 117 tests verts, sans relance à la clôture.
Aucun fichier de décision PNJ modifié : ni banc PNJ, ni suite complète.
Recouvrements : `narration.py` avec G15/320 ; `rendu.py` et `jeu.py` avec U-P/319,
à vérifier à l'intégration. Branche poussée vers origin, **non fusionnée**.
