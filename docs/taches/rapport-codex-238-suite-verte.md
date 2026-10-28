# Lot 238 — suite verte et protection du résultat payé

Branche `codex-suite-verte`, non fusionnée ; base `e84d5a7`. Reprise moteur
autorisée après l'arrêt initial. Aucun MJ, adaptateur, `pnj_propositions`,
`signes.place` ni `pnj.agir` modifié ; assertions historiques inchangées.

**Cause exacte.** Hameau 1985 : allumage réussi à `3188`, trace créée à
`3288` par `echanges.tenu → biens.retenir_service`, puis clôturée dans ce
même choix par `agenda → argent_projet.obtenir → chercher → _entrees_communes
→ services_proteges`. Brune emporte la torche dans l'antichambre, Ilse reste
crue dans l'échoppe : le déplacement du résultat est pris pour un départ
d'Ilse. Le lot 232 publie normalement cette mauvaise clôture ; ni devis
isolé ni erreur de publication. Extinction par Brune à `3615`, combustible
59 : classement fautif 227 juste, inférence de départ moteur fausse.

**Correction commune dans `biens.py`.** Le lieu cru du bénéficiaire au constat
de réussite est sauvegardé dans `services_rendus.lieu_beneficiaire` (optionnel,
validé à la recharge). Clore pour départ exige de croire le bénéficiaire
ailleurs que ce lieu et que le résultat courant, sans portage par lui.
Les anciennes traces mobiles sans ancrage ne permettent plus de déduire un
départ, même si le résultat est ensuite posé. Les résultats fixes gardent
leur référence spatiale. `menager_flamme` et le filtre des transitions
reçoivent la même protection, sans changer leur code ni la transaction 232.
Les raccords nécessaires dans `retenir_service`/`verifier` ont été
explicitement autorisés après clarification du périmètre.

**MiMo : simulation périmée.** `arguments` renvoyait `verdict` et `comptes`,
interdits par le schéma actuel qui exige `nature` ; rejet de format puis
appel supplémentaire sur l'atelier (`6 != 5`). Faux audit remis au contrat,
source `resultat_resolu`, extractions selon les faits fournis. Aucun compte
d'appels ni assertion de sauvegarde/reprise/exécution unique changé.
Correction poussée dans `ad44754` ; deux fichiers entiers : 13 tests verts.

**Tests.** Initialement 36 tests, trois échecs. Après correction finale :
**50 tests verts / cinq fichiers, 34,530 s**. Trois nouveaux tests couvrent le
hameau 1985 complet (réussite non vacuement observée, dix minutes ou 5 + 5),
Joss/Odile et lanterne d'auberge (prestataire mobile, portage puis dépôt par
le bénéficiaire, départ cru, bloc/découpe), et une ancienne sauvegarde sans
ancrage. Monde complet, rendu et scène comparés après recharge. Aucun oracle
affaibli ni capture réancrée. Une tentative ciblée a échoué sur les droits
d'écriture temporaires ; reprise autorisée. Une suite commencée a été arrêtée
pour renforcer les anciennes traces ; seule passe complète finale achevée :
**2 529 tests / 292 fichiers, 2 518,071 s, zéro échec, une erreur, zéro ignoré**.
`test_tui.TUITests.test_sortie_galerie_vers_palier_noir_garde_joueur_sur_la_carte`
échoue avant l'action : `Monde.sauver`, `os.replace`, `PermissionError [WinError 5]`
sur `tmpc6saqte2.json.tmp → tmpc6saqte2.json`. Le test inchangé repasse seul
en **1,020 s**. Origine du verrou non identifiée, aucun changement à la TUI
ou à la sauvegarde : **suite brute non verte**, erreur Windows non reproduite,
pas de seconde suite complète. Les trois échecs initiaux sont corrigés.

**Banc final : vingt paires de 4 h**, Relais/mine/auberge/crue/hameau,
graines 1985/7/42/2024. Vingt références `e84d5a7` manquantes calculées une
fois, rangées puis toutes relues au banc final ; aucun temps comparé.

| Compteur total | Base | Branche |
|---|---:|---:|
| Pertes fautives 227 | 1 | 0 |
| Cessations physiques | 5 | 6 |
| Retours suspects 219 | 2 | 2 |
| Plantages | 0 | 0 |

Suspects **0/0/2/0/0** inchangés par scénario, sans hausse sur aucune nuit.
L'extinction fautive devient un épuisement physique ultérieur. Limites : pas
de reconstruction d'un ancrage ancien ou inconnu, donc protection conservée
faute de preuve ; aucun entretien ajouté, aucune garantie universelle des
boucles. Deux calculs réduits au plus, aucun Luna. Créneau dépassé par les
vérifications et la reprise de périmètre ; aucun code changé pendant la passe finale.
Bruts : `C:/Users/msics/donjon/artifacts/suite-238/` (`avant`, `mimo-apres`,
`cibles-finaux-v2`, `banc-final`, `suite`, `reprise-tui`, diagnostics et passe
interrompue ; correctif mesuré et empreintes de code archivés).
