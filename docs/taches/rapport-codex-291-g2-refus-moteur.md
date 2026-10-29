# Lot 291 — G2 : les refus publics appartiennent au moteur

2026-10-29. Branche `codex-g2-refus-moteur`, base intégration
`931b22bcfc2c19f00d58e9b82c2810f7d94a32d2` (brief présent). Code : `031e664`.
**Non fusionnée ; tests ciblés verts, mesure Luna en cours.**

Dans `MJ._echanger_prepare`, une proposition d'action refusée reste sans effet.
La correction bornée reçoit toujours `retour_refus` et son `attendu` ; si elle
ne fournit pas d'action admise, le joueur lit `reponse_du_moteur`, avec les
messages publics exacts, distincts, dans l'ordre et sans `attendu`. Cela vaut
aussi lorsque la correction revient en dialogue ou en avis : leur prose
écartée ne déclenche plus d'audit. Un second refus de portée conserve le
premier refus au lieu de le remplacer. Aucune branche propre à un objet,
un scénario ou une formulation n'a été ajoutée.

L'appel final d'explication, `ExplicationCedee`, `_sans_relance` et les chemins
qui les utilisaient sont supprimés. Les erreurs de forme persistantes,
y compris celles de l'enveloppe, donnent une demande de précision moteur :
« Précise la manœuvre que tu veux tenter. Corvus n'a rien tenté. »
Les bornes existantes restent : correction de proposition ordinaire plus
correction de forme, trois propositions au plus ; correction d'enveloppe
distincte dans `_appeler`. Le refus de portée garde sa sortie immédiate.
La contre-revue d'action, la fidélité de parole, les qualifications et les
audits des autres voies restent en place. Aucun changement des mécaniques
PNJ, du fournisseur, du modèle `gpt-6-luna` ou de `donjon/refus.py`.

**Vérification : 209 tests distincts, 16 fichiers verts**, zéro échec, erreur
ou ignoré ; somme des durées des fichiers retenus **377,879 s** (temps sous
la charge d'intégration, aucune comparaison de vitesse). Les sept nouveaux
tests console à fournisseur simulé vérifient le coup de pied réel dans la
poutre hors de portée puis les crochets ; le passage à 10 cm au Relais et
sous une table d'auberge ; deux formes persistantes et l'enveloppe invalide ;
deux refus différents, y compris une portée en correction ; dialogue et
avis de correction écartés. Ils contrôlent le texte exact sauvegardé comme
source moteur, les appels, l'absence d'`attendu` affiché, les objets, le
joueur, le temps, les jets, les esprits, les paroles et le rendu après
recharge. Les cas répétés vérifient aussi qu'un même message n'est lu qu'une
fois. Les attentes historiques adaptées concernent uniquement l'explication
libre ou son coût : `test_artisanat`, `test_defi`, `test_improvisation`,
`test_contrats_internes`, `test_narration`. Les tests de replis, promesses,
don, parole, audits, coupe et franchissement restent verts. Le bac à sable
bloquait les répertoires temporaires des premiers essais ; les résultats
retenus proviennent du lanceur autorisé, un travailleur en priorité réduite.
Ni suite complète ni banc PNJ supplémentaire.

**Luna : une passe détachée**, démarrée le 29 octobre à 13:03:43 (Paris),
sur le code `031e664`, un travailleur en priorité réduite. Scripts `relais`,
`sous-obstacle-relais`, `sous-obstacle-trop-bas`, `atelier` ; variantes
`integ=931b22b`, `lot=.` ; cache commun conservé, références absentes jouées
une fois. Copies seulement, `SEUIL_AUTH` vers le coffre principal. Le
lanceur écrit `fin-luna.json` en dernier, même en cas d'échec, et archive
les parties, les appels/secondes par tour, les explications, les refus par
message public, les relances, les replis et les textes réellement lus.
**Ces mesures ne sont pas encore disponibles : ne pas annoncer un gain
Luna ni la clôture du lot avant leur lecture.** Les secondes du cache ne
permettent pas de comparaison causale.

Bruts : `C:/Users/msics/donjon/artifacts/g2-291/` ; tests `tests-cibles.json`,
`tests-complement.json`, `tests-g2-final.json` ; exécution `lancer-luna.ps1`,
`luna.txt`, `debut-luna.json` ; résultats attendus `mesures-luna.json` et
`fin-luna.json`. Le lot porte la voie de refus d'action ; les autres voies
non portées gardent leurs contrôles, conformément à la transition G0–G21.
