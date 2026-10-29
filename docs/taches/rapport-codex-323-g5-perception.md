# Lot 323 — G5, perception canonique

Branche `codex-g5-perception`, **non fusionnée**, base `integration 4794376`.

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

**Luna : une passe à lancer détachée**, quatre scripts : `signes-guet`, `signes-noir`,
`luna-restes-ambiance`, `atelier`. Le cache du commit local de `main`
`c870c8b4797b5c4072a3b0a63043e212aae62a39` ne contient aucune partie correspondant
aux clés actuelles : aucune référence relancée, aucune comparaison chiffrée encore
disponible. La commande exacte, les sorties et le fichier de fin sont rangés dans
`C:/Users/msics/donjon/artifacts/g5-323/` ; reprendre après `fin-luna.json` pour lire
la passe et clore le lot. Aucun résultat Luna revendiqué à ce stade.

**Limites.** Le libre nécessite toujours l'interprétation de Luna ; son choix
sémantique du mode n'est pas garanti par ce lot. S'il choisit encore une prose de
dialogue, ses audits restent actifs : aucun dialogue libre n'est dispensé de contrôle.
Un détail inconnu conserve son admission actuelle ; ambiance et autres voies
inchangées. L'absence porte sur la surface couverte, jamais sur une cache ou une
salle hors de vue. Aucun fichier de décision PNJ modifié : ni banc PNJ, ni suite
complète. Recouvrements : `narration.py` avec G15/320 ; `rendu.py` et `jeu.py` avec
U-P/319, à vérifier à l'intégration.
