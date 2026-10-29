# Lot 265 — faux positifs des compteurs 219 et 227

28 octobre 2026, laptop. Branche `codex-compteurs-faux-positifs`, **non fusionnée**,
base `integration c32cc7d`. Outils et tests seulement, aucun fichier de `donjon/`
modifié, aucune exception par personnage ou scénario. Ni Luna ni suite complète.

**Invariant.** La sonde conserve les preuves publiées par le moteur avant de
qualifier un retour ou une perte. Dans `tools/detecter_changements_avis.py` :
`observer_avis` observe les retraits effectifs du registre des services après
`biens.clotures_services_du_choix`, enregistre trace, instant et croyances ; un
choix interrompu, imbriqué sans publication ou fait sur une copie ne clôt rien
dans l'audit. La perte physique ultérieure reste comptée, sous la classe
`service_clos_avant_perte`, sans violation. Le critère de présence reprend
l'ancrage du bénéficiaire du 238. Le souvenir de paiement et l'historique de
clôture survivent à l'éviction de la mémoire bornée.

`enregistrer_choix` retient le geste réellement manqué et le plan complet du
retour. `analyser_episodes` reconnaît un `changement_moyen_admissible` seulement
si ce plan évite le geste manqué (identité opération/cible/lieu du contrat commun)
et respecte les renoncements encore tenus. Un détour qui reprend ensuite le même
obstacle reste suspect. `appel.retrouves` fournit la preuve d'un rendez-vous clos :
le retour n'est justifié que si son plan cible le partenaire de cette attente
intermédiaire. Une attente simplement absente, rompue ou expirée ne suffit pas.
Les règles antérieures gardent leur priorité. `audit_nuits` expose les classes
dynamiquement ; l'empreinte du détecteur invalide déjà le cache du comparateur.

**Cas exacts.** Reprise des captures 264 avec les sources `c870c8b` extraites en
copie, sans nouveau worktree ni changement de branche : Bram mine 2024, retour
`367860`, **suspect → changement de moyen admissible** ; Gorm hameau 7, retour
`409744`, **suspect → rendez-vous intermédiaire accompli**. Pour chacun, même
état complet, rendu `regarder` et `scene_percue` avec/sans sonde, avant/après
recharge. Épisode 263 rejoué sur les mêmes sources jusqu'à 42 min : torche
éteinte à `24600`, service clos à **`24090`**, **violation → service clos avant
perte**. Les anciens et nouveaux observateurs partagent ces exécutions sans
modifier le jeu ; les témoins des deux captures tournent sans observateur.

**Tests.** **26 tests ciblés verts**, 92,011 s, un processus réduit ; reprise
de deux contrôles d'archives/restauration verte. Trois tests supplémentaires :
autre moyen et contre-exemples ; rendez-vous effectivement clos contre attente
effacée, avec recharge ; service clos, réunion et perte sur une serrure, avec
recharge et identité avec/sans sonde. Les scènes fautives de torche et serrure
restent des violations ; le suspect historique Brune hameau `123253` reste
signalé. Les premiers essais ont rencontré le refus Windows des fichiers
temporaires ; le passage final hors bac à sable est vert.

**Vingt nuits achevées : 20/20 identités, 180 contrôles verts, zéro plantage.**
Cinq scénarios × graines 1985/7/42/2024, 4 h, départ tiré, placements passifs
habituels, moteur de la base `c32cc7d`. Un processus réduit détaché via WMI ;
2 338,585 s au total (durée, pas une comparaison de performance). Deux
observateurs (avant/après) sur le même parcours, puis témoin sans sonde :
état complet, chronique, empreintes, mesures, récit, souvenirs, état rechargé,
`regarder` et `scene_percue` identiques. L'empreinte du détecteur exécuté est
identique au fichier livré. `fin.json` indique `ok=true`, 20 nuits.

| Classe | Avant | Après |
|---|---:|---:|
| Cycles accomplis | 489 | 489 |
| Préemptions de palier supérieur | 46 | 46 |
| Retours suspects | 2 | 1 |
| Entrées à expliquer | 55 | 47 |
| Changements de moyen admissibles | 0 | 9 |
| Pertes : cessation physique | 4 | 4 |
| Pertes : prestataire, bénéficiaire parti | 1 | 1 |

Les neuf reclassements concernent la crue : huit entrées à expliquer et le
suspect d'Aubin graine 7 à `2059`. Le suspect courant restant est à l'auberge
2024. Le suspect historique **Mireille, auberge 1985, retour `36720`** de
l'archive 219 reste signalé. Les épisodes exacts 263/264 sont vérifiés
séparément ci-dessus ; les vingt nuits actuelles ne les reproduisent pas.
Bruts : `C:/Users/msics/donjon/artifacts/compteurs-265/` (`bilan.json`,
vingt archives par nuit, `suspect-219.json`, traces des reprises historiques,
tests, scripts et `fin.json`). Aucun calcul actif. Branche poussée,
correctif `91377b1` ; cette reprise complète seulement la documentation.

**Limites.** Certification causale générale toujours fausse : horizon de 60 min,
prédicats de fin hérités, voies non instrumentées. Une archive sans les nouvelles
preuves doit être rejouée ; aucune clôture n'est déduite de la seule absence d'un
registre. Le compteur des pertes physiques est conservé, même quand la clôture
les justifie. Aucune stabilité générale du jeu n'est affirmée.

**Suite relevée par le [lot 268](rapport-codex-268-agenda-brune.md).** Les réveils
d'agenda justifiés par un objet acquis, une position nouvellement apprise ou un
engagement effectivement accompli ne sont pas couverts par une règle propre de
ce lot : le changement de moyen exige un geste manqué observé puis évité.
Preuve dans le banc terminé : Brune hameau 2024, retours `591` et `929`, reste
en `entree_nouvelle_a_expliquer` avant et après correction. Leur justification
et celle des réveils historiques du 268 restent à intégrer à la sonde dans un
lot suivant, sans modification du moteur ici.
