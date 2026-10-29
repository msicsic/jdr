# Lot 337 — fin de garde apprise par ouï-dire

Branche `codex-fin-garde-ouidire`, **non fusionnée**, base
`integration 9bef3f6`. Ni Luna ni suite complète. Bruts :
`C:/Users/msics/donjon/artifacts/garde-337/`.

**Invariant.** Les confidences existantes transmettent ensemble lieu cru,
porteur, propriétaire, permission et remise autorisée, photographiés lors
du constat. Leur identité `[objet, lieu, possession]` est distincte de la
localisation nue d'une accusation. Les changements de droits rouvrent
le fait ; une autre date, case ou source ne le répète pas. Une accusation
antérieure ne masque plus le constat et ne peut écraser ses droits reçus.
La fin matérielle est également proposée comme constat, avec sa désignation
observée pour rester formulable après retrait des restes. Pas de nouvelle
action de parole : seuls les candidats des nouvelles communes sont enrichis.

`social.faits_dits`, `reviser_dits`, `_constats`, `_meme_constat`,
`_lieu_dit`, `phrase` et `_apprendre_lieu` portent ce raccord.
`recevoir`/`_adopter` conservent le jet commun, la source `dit:`, la date
d'observation et la confiance dégradée par relais. Aucun droit réel n'est
consulté à l'adoption. Les preuves propres plus récentes, ou propres à
date égale, priment. Une information devenue fausse peut être crue.

**Preuve négative nécessaire.** `esprits.constater_fin_objet` conserve
aussi une fin `None` datée quand aucune fin matérielle n'est constatée : effacer
une réparation permettrait à une ancienne destruction racontée de revenir.
La date est celle du dernier constat ; confirmer une fin déjà établie par
son propre geste conserve cette source. Les lectures de `agendas.py`
et `biens.capacites_crues` testent désormais la valeur de fin. Causes, publication différée, choix
interrompu et irréversibilité des agendas utilisent le contrat existant.
Responsabilité/prix de garde et propriétaire projeté sont déjà représentés
dans `_entrees`, test ajouté. La preuve négative n'ajoute aucun moyen :
empreintes d'agenda et de recherche la normalisent à l'absence de fin.

**Vérification. 196/196 tests, quinze fichiers**, zéro échec, erreur ou saut,
132,735 s ; `cibles-finales/fin.json ok=true`. Quatorze nouveaux tests.
Perte au Relais malgré une
ancienne accusation, restitution à l'auberge, destruction/consommation,
doute, preuves propres récentes ou à date égale, réparation, droits changés
à distance, fausse nouvelle crue, relais à 0,56, absence de répétition,
publication différée et interruption, laps entier/découpé ; monde, rendu et
scène réellement rechargés. Deux tests supplémentaires : fin transmise après
retrait des restes et confidence émise pendant le laps entier/découpé.
Les assertions historiques d'absence de fin
deviennent une preuve négative explicite ; la date de confirmation change.
Premier passage voisin : **159 tests, cinq échecs**, conservé dans
`cibles-1/`. Quatre scènes isolent désormais les confidences d'inventaire
initiales par un placement d'auteur avec leurs faits déjà partagés, sans
modifier leurs assertions. Rémy a révélé un lecteur de fin oublié dans les
capacités ; corrigé, le test historique repasse inchangé. Reprises conservées
dans `reprise-1/` et `reprise-2/`. **Banc rapide détaché en cours** :
cinq scénarios, quatre graines, 4 h, aucune hausse des suspects 219 par nuit.
Référence exacte `9bef3f6`, nuits présentes relues du cache, absentes seulement
jouées et rangées. Fin attendue `banc-final/fin.json`, écrite en dernier même
sur échec. PID réel **48324**, priorité réduite et activité vérifiées au départ.
Branche poussée vers origin, code/tests `e2822a1`. Tests réutilisés après contrôle des empreintes ; ni autre passe
de tests ni temps du cache comparés. Bilan du banc à lire avant clôture.

**Limites et recouvrements.** PNJ seulement : le joueur n'a pas les relations
subjectives nécessaires au jet d'adoption commun. Pas de reconstruction
omnisciente des droits passés pour une ancienne sauvegarde ; acquisition
lors d'un nouveau constat. Un ancien constat sans désignation ne se formule
pas après retrait des restes ; sa preuve reste conservée pour la décision.
Ni scène historique ni prompt MJ modifié.
Recouvrement de code avec **335 et 336 : `agendas.py`, `planification.py`** ;
lectures de fin et empreintes dans ce lot. `docs/etat-dev.md` également commun.
Le banc passif ne prouvera pas l'absence universelle de boucles.
