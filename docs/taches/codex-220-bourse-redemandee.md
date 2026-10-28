# Tâche Codex 220 : une bourse rendue n'est pas redemandée sans fait nouveau

Défaut relevé par la vérification d'intégration 212 (`docs/taches/rapport-codex-212-verif-integ.md`, « Petits lots à
instruire ») : **mine 1985, dès 288 min, Mathe demande la bourse à Rémy 97 fois et Rémy la demande à Mathe 100 fois**, avec des
restitutions entre-temps. Les échanges de la nuit sont gonflés ; le compteur 199 n'en voit rien (moyens différents sous un même
but). Piste du rapport : l'enrichissement (`planification.enrichir`, `biens.richesse`, engagements) n'intègre pas la restitution
imposée et recrée le même recours à entrées inchangées. Le rapport ne peut pas dater l'apparition de la boucle ; les lots 184 b
(projet de pièces), 207 (réclamation) et 214 (rachat) touchent ce domaine. Base vérifiée `4d4c625` ; l'intégration actuelle contient
aussi 205, 207, 211 et 214.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste (213) : au plus 2 processus, priorité réduite.
Fichiers : `planification.py` (enrichissement et recours monétaires), `biens.py`, `echanges.py`, `pnj_propositions.py`, et leurs
tests ; **pas** `deliberation.py`, `agendas.py` (lot 213), `social.py`, `esprits.py`, `pnj.py` (lot 206), ni le MJ.
**Bruts dans `C:\Users\msics\donjon\artifacts\bourse-220\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 212, 184, 207, 214, 110 (propositions redites, refus retenus selon leur cause), puis
`planification.enrichir`, `biens.richesse`, les demandes de prêt/bourse et la restitution (`biens`, `echanges`). Les bruts de
la nuit sont dans `C:\Users\msics\donjon\artifacts\verif-integ-4d4c625\`.

## L'invariant
**Un PNJ ne redemande pas un bien qu'il vient de rendre, ou qu'on vient de lui reprendre par restitution, tant qu'aucune entrée
nouvelle de sa demande n'est crue (un besoin qui a changé, un moyen nouveau, une autre réponse possible) ; une restitution imposée
compte dans ce qu'il croit posséder et pouvoir obtenir.** Même règle pour tout PNJ, tout bien et pour le joueur qui demande ;
aucune règle propre à Mathe, Rémy, la bourse ou la mine ; aucun délai arbitraire ajouté.

## Vérification
- Reproduire d'abord la boucle (mine 1985, capture rechargeable juste avant 288) sur `4d4c625` **et** sur l'intégration actuelle :
  dire si elle existe encore, depuis quel lot si on peut l'établir, et quelle chaîne de décisions la produit.
- Tests après rechargement : Mathe et Rémy cessent de se redemander la bourse sans fait nouveau ; un autre cas de même nature
  (autre bien prêté ou restitué, autre scénario) ; une demande redevient possible quand une entrée change ; même laps d'un bloc ou
  découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 199** ; échanges,
  demandes répétées, S/F/D du lot 183 ; plus la nuit mine 1985 sur 12 h ; aucune usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-bourse-redemandee` poussée (pas `main`) ; si la poussée
est bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-bourse-redemandee`, non fusionnée ») ; rapport
d'une page `docs/taches/rapport-codex-220-bourse-redemandee.md`.
