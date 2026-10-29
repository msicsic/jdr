# Tâche Codex 303 : avant de servir quelqu'un dont il ignore le lieu, le PNJ le cherche ou l'appelle

Petit lot de planification. Lis `AGENTS.md` et le rapport du diagnostic 289
`docs/taches/rapport-codex-289-service-lieu-inconnu.md` (capture dans `C:\Users\msics\donjon\artifacts\service-289\`),
puis les rapports 251 et 259 (présences requises d'un geste ; une localisation inconnue n'est pas une absence) et 275
(appeler un interlocuteur localisé mais inaccessible).

## Le constat
Diagnostic 289 : Tilo, en cuisine, veut servir la marmite à Mathurine, dont il ignore le lieu. Le plan admet
`servir … pour mathurine` sans trajet (lot 259 : une localisation inconnue n'est pas une absence), puis
`echanges.servir` le refuse sur place, faute de présence. Un geste est perdu ; le service se fait plus tard par hasard.
À la mine, même admission (Mathe, Lucien), plan refusé une fois sans reprise. Limite relevée : un plan peut être mesuré
sans place projetée pour le participant, et chercher ou appeler le bénéficiaire avant le service est un manque de
planification.

## L'invariant
**Un geste qui exige la présence d'un participant (`pnj._a_reunir`) dont le lieu est inconnu du PNJ ne s'exécute pas
d'emblée : le plan passe d'abord par les moyens communs de le rejoindre (inspection, appel négocié, question à un
tiers : `rejoindre`, lots 221, 226 et 275), puis sert quand la présence est crue.** Aucune lecture de la position
réelle. Le lot 259 tient toujours : une localisation inconnue n'est pas une absence, et le but n'est pas abandonné. Une
venue convenue compte comme présence attendue. Pas de délai ni de réessai par le seul temps, et aucun cas propre au
repas, à Tilo ou au bénéficiaire.

## Fichiers attendus
`donjon/planification.py` (mesure et sous-but de contact), `donjon/pnj.py` (`_a_reunir`, `refus_etape`) seulement si la
même règle doit y être lue. Ne touche pas au MJ.

## Vérification
- La capture 289 rechargée : Tilo cherche ou appelle Mathurine, puis sert. Autre cas de même nature : Mathe et Lucien
  à la mine. Pour chacun, vérifie :
  - aucun geste refusé sur place ;
  - aucune position réelle lue ;
  - le service rendu après rencontre ;
  - monde, rendu et scène identiques après recharge, même laps d'un bloc ou découpé.
- Contre-épreuve : un bénéficiaire cru ailleurs dans un lieu connu (lot 251) garde son comportement.
- **Banc rapide** 4 h × quatre graines, auberge, mine et Relais, contre la référence de l'intégration (cache) :
  - aucune boucle nouvelle, usurpation ni hausse des suspects 219 par nuit ;
  - services rendus, appels et recherches comptés.

  Calcul détaché, fichier de fin écrit même en cas d'échec.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le laptop.** Une vérification d'intégration (lot 284) et un lot du MJ y tournent : deux processus au plus,
priorité réduite.

## Livraison
- Branche `codex-service-rejoindre` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur :
  la poussée est autorisée) ; si elle échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-303-service-rejoindre.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\service-303\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
