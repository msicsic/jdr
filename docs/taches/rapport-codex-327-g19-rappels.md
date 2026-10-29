# Lot 327 — G19, les rappels

Branche `codex-g19-rappels`, **non fusionnée**, base `integration eb15b5e`.
Implémentation et tests ciblés validés ; passe Luna à conclure depuis
`C:/Users/msics/donjon/artifacts/g19-327/fin.json`.

**Invariant.** Relire une parole entendue restitue ses mots historiques sans
nouvelle émission ni acquisition de connaissance. Les lots 135/156 avaient
déjà une preuve textuelle exacte ; G19 la rattache aux occurrences du registre
G15. `narration.echanges_passes` conserve identifiant, ordre, révision, minute
et désignation publique, même après le départ du locuteur. Cette mémoire ne
l'ajoute pas aux interlocuteurs présents et ne lui donne aucun droit de réponse.
`preuves_rappels` relie les rendus moteur aux émissions entendues ; plusieurs
occurrences identiques restent plusieurs preuves. Une liste sans mots exacts
donne aussi un constat moteur de l'absence de souvenir exact, sans inventer de
réplique. Les discours rapportés ne deviennent jamais des citations littérales.

Les rendus exacts passent par le catalogue commun de `segments_etablis`, sans
audit narratif pour ces segments. Dans un texte mixte, les autres segments
gardent leurs contrôles. Le garde nominal reconnaît l'attribution historique
entière du moteur, y compris celle d'une voix partie, sans établir son identité
présente. `consigner` reconstruit les preuves depuis le monde avant toute
écriture : retrait de l'audition, changement de mots, d'auteur, d'identifiant
ou d'ordre rendent la preuve caduque ; une absence est également revérifiée.
Aucun mode, analyseur de formulations ni consigne supplémentaire à Luna.

**Vérifications.** **153 tests distincts / douze fichiers verts**, zéro
échec, erreur ou saut : 151 tests en 100,011 s, puis le seul fichier G19
repris après ses deux dernières contre-épreuves, **8/8 en 9,123 s**.
Les huit nouveaux tests contrôlent registre, toutes les données du monde
hors journaux d'affichage, conversation, scène et rendu après recharge ;
la carte initiale est préparée avant la saisie comme dans la vraie console.
Cas réel Ilse dans le noir et autre locuteur Aubin ; la parole fausse
« La lune est verte » reste seulement une parole entendue. Le faux rappel
du cas 110/112 et l'autre cas de Gorm restent refusés par les tests existants
de `test_redire_passe`. Tests du départ, de l'absence de mots, des occurrences
identiques, des sources altérées, du texte mixte et de l'identité non prouvée.
MJ simulé, sans réseau. Les premiers essais ont corrigé la préparation de
la carte et deux refus du rendu nouveau ; leurs bruts sont conservés.
Le bac Windows refuse les copies temporaires Python : tests exécutés hors
bac, priorité réduite, deux travailleurs au plus. Ni suite complète ni banc PNJ.

**Luna.** Lanceur détaché préparé pour **une passe**, `soir-noir` et `echanges`,
ChatGPT `gpt-6-luna`, medium/libre, un travailleur réduit. Référence historique
`cdaf371` relue du cache pour les deux scripts, jamais rejouée. Commande exacte,
copies, empreintes, journaux et analyse dans le dossier du lot ; `fin.json`
est écrit en dernier, même en échec. Les résultats Luna ne sont pas encore
revendiqués. Leur analyse compte séparément les propositions exactes et les
citations exactes envoyées à l'audit ; zéro ajout mécanique est prouvé par
les parcours console simulés, pas inféré d'une seule sortie narrative.

**Limites et intégration.** Une paraphrase, une attribution libre, un fragment
arbitraire ou un geste passé garde sa voie sémantique actuelle. La preuve
exacte ne garantit pas la fidélité de toute sélection de souvenir à la demande,
ni la vérité du contenu entendu. L'ordre intra-tour inconnu des anciennes
sauvegardes reste signalé. Recouvrement avec G5/323 et G17/326 :
`donjon/narration.py` ; ni `emissions.py`, ni `mj.py`, ni les formateurs
comptables ne sont modifiés. Aucune fusion de ces branches dans ce lot.
