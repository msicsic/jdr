# Banc Luna du soir : contrôle du MJ après les fusions du 2026-10-21

Contrôle sans correction, sur `main` 8c108c3 (après `echanges-suite`). Luna (`gpt-6-luna`, forfait
ChatGPT, WebSocket, effort medium), `tools/banc_multi.py` puis `tools/banc_parties.py --fil`, au plus
deux exécutions simultanées. D'autres agents tournaient sur la machine : les secondes sont indicatives.
Rien n'est corrigé dans le moteur ; les causes citées sont probables, lues dans les fils et le code.

## Bancs joués

- Référence, 3 passes : `relais`, `crypte`, `atelier`, `echanges` (les quatre de `audits-attendu`, 38
  tours MJ), plus `comptes` et `ressources` (branche `echanges-suite`).
- Saisies ciblées sur les nouveautés, 2 passes, trois scripts ajoutés (Relais, départ préparé) :
  - `soir-appel.json` (refuge éclairé, Aubin doit 2 pièces au joueur) : « j'appelle Gorm », « je
    réponds », « est-ce que quelqu'un a du bois ? », « as-tu de quoi manger, Ilse ? », « je réclame à
    Aubin les deux pièces qu'il me doit », « je paie Aubin trois pièces pour une de ses planches »,
    deux pas vers l'ouest, « je donne le briquet à Ilse », « Ilse, tu m'entends ? » ;
  - `soir-noir.json` (Palier des vannes sans lumière, Ilse à 3 cases, jamais vue ni entendue) : « il
    y a quelqu'un ? », « « Qui est là ? » », « « Tu as de quoi manger ? » », « « C'est moi, Brune. » »,
    « je demande à la voix comment elle s'appelle », « écouter » ;
  - `soir-voix.json` (même noir, Ilse connue de nom) : « j'appelle Ilse », « « Qui es-tu ? » »,
    « « Tu as de quoi manger ? » », « « C'est moi, Brune. » », « je lui demande si elle a peur du
    noir », « je donne le briquet à Ilse ».

Résultats : `artifacts/bancs-multi/20261022-003141-47848` (référence), `…-004107-19296` (appel, noir),
`…-005206-19544` (voix), non versionnés.

## Chiffres

Moyenne par passe (étendue entre parenthèses). Appels et secondes par tour MJ ; relances : réponses
refusées par le contrôle narratif puis redemandées ; refus : refus du moteur et de la contre-revue.

| Banc | Passes | Tours MJ | Appels / tour | s / tour | Replis | Relances | Tours avec refus | Refus | Obstacles |
|---|---|---|---|---|---|---|---|---|---|
| **4 bancs de référence** | 3 | 38 | **3,14** (3,11–3,18) | **11,1** (10,4–11,7) | **0** | **4,7** (3–6) | **7,0** | 10,3 (10–11) | 4,7 (3–6) |
| relais | 3 | 11 | 3,27 | 11,3 | 0 | 0,3 | 3,7 | 5,3 | 0,3 |
| crypte | 3 | 9 | 3,26 | 12,2 | 0 | 2,3 | 1,3 | 2,0 | 2,3 |
| atelier | 3 | 11 | 2,91 | 10,3 | 0 | 1,0 | 2,0 | 3,0 | 1,0 |
| echanges | 3 | 7 | 3,14 | 10,7 | 0 | 1,0 | 0 | 0 | 1,0 |
| comptes | 3 | 2 | 3,50 | 12,1 | 0 | 0,3 | 0,3 | 0,3 | 0,3 |
| ressources | 3 | 3 | 3,22 | 13,3 | 0 | 0,3 | 0 | 0 | 0,3 |
| soir-appel | 2 | 6 | 3,67 | 15,1 | 0 | 2,5 | 1,0 | 1,0 | 2,5 |
| soir-noir | 2 | 5 | 4,70 | 17,3 | 0 | 3,5 | 1,0 | 2,0 | 4,0 |
| soir-voix | 2 | 4 | 3,25 | 9,6 | 0 | 0,5 | 0 | 0 | 0,5 |

Référence consignée (`audits-attendu`, mêmes quatre bancs, 2 passes) : `main` 4c53791 3,08 appels,
11,3 s, 0 repli, relances 4,0, tours avec refus 6,5, refus 10 ; branche 3,07, 11,5 s, relances 3,0,
tours avec refus 7,0, refus 10,5. **Pas de régression chiffrée** : 3,14 appels et 11,1 s, 0 repli,
relances 4,7 (étendue 3 à 6, qui recouvre 3 et 4), tours avec refus 7,0. Aucune erreur technique,
aucun rechargement en échec, aucune fuite d'`attendu`, d'identifiant ou de mot technique dans les
textes affichés (recherche sur tous les tours). Les 7 « mentions sans fondement » du banc sont des
faux positifs de la mesure : les mots du joueur (« pied-de-biche », « Brune ») et les vivres d'une
dette dans la réplique de Gorm.

Les tours traités par le moteur seul tiennent : « j'appelle Gorm » et « j'appelle Ilse » (0 appel,
« Ici ! » par l'ouïe, « une voix qui se dit… »), « je donne le briquet à Ilse » absente (0 appel),
« Ilse, tu m'entends ? » absente (1 appel, « Tu ne vois pas Ilse d'ici… »).

## Défauts, du plus grave au moins grave

### Graves (le monde ou la parole du joueur faussés)

1. **Un vocatif en fin de phrase est ignoré, et le moteur impose l'autre destinataire** (2/2).
   « as-tu de quoi manger, Ilse ? », Ilse et Aubin en vue. Luna propose `personnage: ilse` ; refus du
   moteur « Tu t'adresses à Aubin, vieux passeur. » (`attendu` : `personnage = aubin`) ; affiché :
   « Tu dis à Aubin : « As-tu de quoi manger ? » », et en passe 2 la réplique est réécrite « As-tu de
   quoi manger, Aubin ? ». Cause : `paroles.VOCATIF` n'est cherché qu'en tête de saisie
   (`paroles._interpeller`) ; sans nom reconnu, `paroles.destinataires` retombe sur `en_face`, et la
   validation de la parole refuse le bon choix du MJ.

2. **Un vocatif qui nomme un personnage inconnu du joueur est ignoré : la parole va à celui d'en
   face** (1/3, `comptes`). « « Brune, tu me dois deux pièces, rends-les-moi. » », Brune dans le dos
   de Corvus, jamais vue. `parole_prevue.personnage` = `marchand` ; affiché « Tu dis à Gorm : « Brune,
   tu me dois deux pièces… » », puis « Gorm reste silencieux. Il ne te doit rien ». Dans les deux
   autres passes Brune était devenue connue (aperçue entre-temps), et tout allait bien. Cause :
   `paroles._interpeller` renvoie 0 quand `_personnage` ne trouve personne de connu, sans
   `ParoleImpossible` ; la parole n'est ni refusée (« tu ne connais personne de ce nom ici ») ni dite
   à la cantonade. Le banc `comptes` prête au joueur une dette envers Brune sans qu'il la connaisse :
   le cas est rare en partie, mais la règle reste fausse pour tout nom inconnu.

3. **Acheter une planche donne une part de bois au feu, pas la planche** (2/2). « je paie Aubin
   trois pièces pour une de ses planches » : Luna type `demande`, sujet `planches`, valeur 3 ; le
   moteur valide « Aubin, vieux passeur prend tes 3 pièces et accepte de t'en donner une part : il va
   entretenir le feu. ». Le joueur paie et ne reçoit rien en main. Cause : la règle « une part de
   combustible va au feu de la salle d'où vient la demande, joueur compris » (`echanges.foyer_de`,
   `entretenir-feu`, `voix-inconnues`) s'applique à une demande payée d'un objet ; il manque, pour le
   joueur, l'achat d'un objet combustible pour soi.

4. **Dans le noir, une question à la cantonade n'est jamais répondue, même par qui l'entend** (2/2).
   Ilse, à 3 cases dans le Palier noir, saisit les mots (`ouie.saisissent` : niveau 3). « « Qui est
   là ? » » est typé `qui`, mais `personnage: personne`, `temoins: []` : personne ne répond, ni à
   « Tu as de quoi manger ? » ni à « C'est moi, Brune ». Le joueur ne peut découvrir par la parole un
   PNJ silencieux dans le noir ; seul l'appel par le nom marche (`soir-voix`). Cause : les
   destinataires sont tirés des personnages que Corvus perçoit (`dialogues.interlocuteurs`,
   `paroles.destinataires`) et seuls les destinataires répondent ; un contenu `qui` ou une question
   dite à la cantonade n'appelle aucune réponse de ceux qui l'ont saisie.

### Moyens (texte affiché inexact, ou coût)

5. **Question de faisabilité : un refus de format est montré au joueur comme réponse** (2 cas).
   « est-ce que je pourrais passer sous la poutre effondrée ? » (relais, 1/3) : Luna propose d'abord
   `impossible` (refusé « Réexamine… »), puis `improviser` avec `difficulte: 0` et une stat ; le
   joueur lit « La difficulté de ce geste sort des limites d'un arbitrage sommaire. ». « il y a
   quelqu'un ? » dans le noir (1/2) : Luna propose un hélement sans nom, le joueur lit « Dis qui tu
   appelles par son nom. ». Cause : `MJ` (boucle de décision, `mj.py` ~l. 536) rend
   `reponse_du_moteur(refus_du_moteur)` dès que la correction unique est consommée, sans distinguer un
   refus de forme (corrigeable, son `attendu` dit le champ) d'une vraie impossibilité ; le refus
   `impossible` consomme la seule correction ; et toute question qui finit en geste refusé suit cette
   voie.

6. **L'auditeur refuse la réplique d'un destinataire faute de « parole prévue », puis le MJ affirme un
   silence que le moteur n'a pas décidé.** « Ilse, qu'est-ce que tu vas en faire ? » (echanges, 1/3) :
   motif « Ilse est à deux cases, hors de portée… rien ne justifie qu'elle réponde » ; affiché « Ta
   question porte jusqu'à Ilse, mais elle ne répond pas. À deux cases de toi, elle reste hors de
   portée ». Même verdict pour Gorm (comptes, « Gorm reste silencieux »), pour Aubin après « je
   réponds » (7 appels, 40 s), pour « Oui, passe. » de Brune (refusé 2/3, admis 1/3 sous la forme
   « Oui, vas-y. »), pour « Non. Je ne te dois rien. » d'Aubin (refusé, puis admis presque identique).
   C'est la principale source de relances de la référence. Cause : `narration.controler` (verdict
   sémantique) lit l'absence de réplique dans `conversation_validee` comme un interdit ; `a_portee`
   (portée de main, `Monde.contexte`) est pris pour la portée de voix.

7. **Parole à la cantonade : l'auditeur croit que Corvus n'a rien dit** (soir-noir, 4,7 appels par
   tour, jusqu'à 7). Refusés : « Ta voix résonne dans le noir », « Personne ne répond », avec le motif
   « la conversation validée ne fournit pas de parole prononcée ». Admis ensuite : « Ta question a été
   dite à voix haute, mais tu ne sais pas si quelqu'un l'a entendue ». Cause : la forme de
   `conversation_validee` pour la cantonade (`personnage: personne`, `destinataires` et `temoins`
   vides, qui ne fuient pas les présents) ne dit pas que les mots ont été prononcés.

8. **« Sorties : aucun passage directement praticable » quand aucune sortie n'est connue** (soir-noir,
   1/2, deux tours). Luna l'affiche (« Les issues ne donnent aucun passage directement praticable »),
   l'auditeur l'admet comme attesté, alors que le Palier a un escalier et une porte. Cause :
   `rendu.py` l. 240 écrit la même phrase pour « aucune sortie connue » (`spatial.sortie_connue`) et
   « aucune sortie ».

9. **Se faire passer pour quelqu'un : le mensonge est typé « je me nomme »** (2/2). « « C'est moi,
   Brune. » » à la voix d'Ilse : Luna type `nom`, sujet `joueur` ; le moteur valide « Une voix qui se
   dit Ilse te croit sur parole : pour elle, c'est Corvus qui parle. » ; le récit admis fait dire
   « Brune ? Je ne te reconnais pas. Qui es-tu ? », qui contredit ce fait. Cause : `paroles._nom_dit`
   n'accepte un autre nom que s'il désigne un personnage connu de Corvus (`resoudre`) ; rien ne relie
   le nom cité dans la réplique au sujet typé ; l'auditeur n'a pas relevé la contradiction.

10. **« As-tu du bois ? » : Aubin dit n'en avoir pas, puis vend ses planches** (3/3 `ressources`, 2/2
    `soir-appel`). Cause : `echanges.enqueter` ne compte que ce que l'auditeur croit avoir
    (`deliberation._connus`) ; au départ Aubin n'a aucune croyance sur ses propres planches de bac
    (2 parts, `chaleur`), alors que la vente lit l'état. En passe 1, à « as-tu de quoi manger ? », Luna
    lui fait redire « Je n'ai pas de bois », admis comme rappel d'une parole déjà entendue : ce
    classement laisse une ancienne réplique répondre à une autre question.

### Faibles

11. « je réponds » sans appel préalable devient la parole « Je réponds. » adressée à Aubin (2/2) ;
    « réponds » est un verbe de parole sans conteste (`paroles.VERBES_PAROLE`), le geste `repondre`
    n'existant qu'après un appel par le nom.
12. « est-ce que quelqu'un a du bois ? » va au seul Aubin, en face ; Luna réécrit une fois « Aubin,
    est-ce que quelqu'un a du bois ? ». « quelqu'un » n'est pas un groupe pour `paroles.analyser`.
13. Voix d'auteur à la première personne non détectée : « mais je ne vois pas d'autres outils traîner
    dans la cour » (atelier) ; `narration.AUTEUR` ne connaît pas « je ».
14. Méta-langage admis : « tu accomplis un geste d'effort » (atelier, « je m'étire », 2/3, l'approche
    `effort` d'`improviser`), « une évaluation plus précise que ne le permet un simple geste improvisé »
    (relais).
15. « je donne le briquet à Ilse » dans le noir, sa voix entendue « tout près » : « Ilse, meunière
    évacuée n'est pas là pour le recevoir » (elle est là, non vue ; virgule manquante aussi dans le cas
    absent).
16. La voie `conversation_pnj` (offre pour l'anneau, crypte 3/3) n'affiche pas « Tu dis à Gorm : … »,
    contrairement à `parole_joueur`.
17. À vérifier : la réplique d'Ilse au Palier est saisie par Brune et Aubin au refuge (niveau 1 par la
    galerie, entrée « haut » sans case dans `ouie.propager`), qui figurent parmi ses auditeurs.

## Ce qui va bien

- Aucun repli, aucune erreur technique sur 129 tours MJ de référence (43 par passe, 3 passes) et 30 tours ciblés (2 passes).
- Héler et l'appel par le nom passent par le moteur, sans appel (« j'appelle Gorm », « j'appelle
  Ilse ») ; la réponse s'entend par l'ouïe commune.
- Voix inconnue (`soir-voix`, 2/2) : Luna dit toujours « la voix », ne la nomme jamais, n'invente
  aucun tiers ; 3,25 appels par tour, aucune relance en passe 2.
- Réclamer : « Gorm, rends-moi… » 3/3, « je réclame à Aubin… » 2/2 typés `reclamer`, remboursement
  raconté d'après le moteur ; Brune adressée refuse de rendre (2/2).
- Don et parole à un absent connu : refus justes du moteur, 0 ou 1 appel.
- Les échanges du banc `echanges` (à tous, chuchoter, passage, pousser, don hors de portée) gardent
  leurs chiffres : 3,14 appels, aucun refus.
