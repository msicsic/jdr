# Lot 395 — provenance de l'extinction dans la capture crue 2024

Branche `codex-avis-redits-crue`, base `integration 1fd48fb5`, laptop.
Bruts : `C:/Users/msics/donjon/artifacts/avis-redits-395/`.

**Invariant.** Une observation initiale inchangée ne constitue pas une
nouvelle. Un changement appris rend son état racontable ; une nouvelle vue
du seul locuteur ne rouvre pas les destinataires déjà servis.

**Diagnostic et preuve.** La capture crue à 140 précède `faits_initiaux`.
Brune porte la torche éteinte, avec une croyance `vu` datée de 140 ; le
chargement du 360 ancre donc `allume=false` dans sa provenance initiale.
`social.nouvelles` n'offre aucune extinction de cette torche. Ce comportement
correspond à la migration prudente documentée au 360, qui ne reconstruit pas
le passé d'une ancienne sauvegarde. La chronique atteste pourtant Brune
allumant la torche à **97**, l'éteignant à **104**, puis annonçant son
extinction à **Aubin à 122**. Aubin croit encore l'allumage vu à 100 ; Ilse
et Gorm (`marchand`) celui vu à 102. Le registre de Brune conserve Aubin
comme destinataire de l'extinction ; il ne porte pas les deux autres.
Les croyances, la provenance et l'audience avant/après figurent dans
`provenance.json`, avec les lignes historiques et l'empreinte de la capture.

**Portage de la scène.** Le test restitue par `croire` la vue allumée
antérieure attestée à 97, puis laisse `percevoir` constater l'état actuel
éteint à 140. Il vérifie le silence initial, la nouvelle ensuite disponible,
l'état matériel conservé et le suivi d'Aubin toujours fermé. Cette prémisse
est appliquée une fois avant chacun des deux parcours ; aucune confidence
n'est injectée. Aucun moteur, registre, objet de capture, besoin, lien,
audience ou jet n'est modifié. La capture compressée reste intacte.

**Isolation autorisée par l'utilisateur.** La première passe avec les profils
d'origine conserve l'égalité des deux parcours mais reste sans transmission
(trois tests, deux verts, un échec ; 247,976 s). Brune poursuit notamment des
buts de souci spontané d'autrui. L'utilisateur autorise donc l'isolation de
l'épreuve positive comme pour les lampes du 375 : `secours_spontane=False`
déclare `altruisme=empathie=0` dans les profils de la copie, sans changer
besoins, liens, audience ou jets. Le commentaire du test cite la décision
du 395 et les buts concurrents. **L'assertion de transmission reste intacte.**
Un quatrième test conserve les profils d'origine et vérifie le sens négatif :
aucune redite sans rallumage appris par l'auditeur. Le harnais historique
minier du 375 reste limité à son épreuve existante. README et tests
documentent ces prémisses distinctes.

**Vérifications.** En cours : les quatre méthodes de `test_avis_redits`,
les neuf fichiers de tests modifiés par le 360 et `test_deja_dit`.
Le parcours réel et celui des deux lampes homonymes comparent le monde
entier, le regard, les paroles entendues et la scène après rechargement,
sur un laps entier ou découpé. Deux travailleurs au plus, priorité réduite.
Aucun code du jeu changé : aucun banc, Luna ou suite complète.

Fin attendue : `C:/Users/msics/donjon/artifacts/avis-redits-395/fin.json`,
écrite après `avis.json` et `tests-360.json`. La validation des avis est
lancée détachée, fenêtre cachée ; aucun résultat final n'est encore déclaré.

**Limites.** La transmission spontanée dans la nuit réelle n'est pas prouvée.
Le test déclare une perception attestée dans une ancienne scène ;
il ne fournit pas de reconstruction générale des provenances historiques.
Les heures de transmission et les trajectoires actuelles restent décidées
par le moteur. Aucun résultat universel sur les nuits ou les boucles n'est
déduit de ces captures.
