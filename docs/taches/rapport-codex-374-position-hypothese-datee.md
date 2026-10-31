# Lot 374 — position crue comme hypothèse datée

31 octobre 2026, PC fixe, branche `codex-position-hypothese`. Intégration
`3999bb3a` fusionnée dans `b3233153`, portes et vues mémoire S1a–S1e conservées.
Bruts : `C:/Users/msics/donjon/artifacts/position-hypothese-374/`.
**Fusion suspendue au nouveau banc du contact consommé.**

**Invariant et réalisation.** Une position d'autrui est datée : confiance initiale
× `2 ** (-âge / demi_vie)` depuis la preuve d'origine, sans cumul par tick.
`data.positions_hypotheses` : seuil 0,5 ; demi-vies 15/60/120 min selon mobilité
crue (mobile, posée, retenue). Soi, objets et feux exclus ; aucune position réelle
lue pour planifier. `_lieu_cru`, `croit_present`, `_chercher`, `_normaliser_suites`
et `_agir` partagent le contrôle ; règle, expiration et consommation entrent dans
`_entrees`. Le préfixe typé conserve sa progression sous le même but/motif/demande.

Inspection, appel, question et constat d'absence consomment la piste expirée :
`croyances[sujet].lieu.hypothese_consommee={minute,lieu}` survit à l'absence, au
temps et aux anciens relais. Retrouver la même position clôt aussi le résultat de
sa propre inspection. Seule une nouvelle preuve peut rouvrir la piste ; un bruit
attribué conserve date et origine. Aucun épisode écrit hors porte mémoire.
La première reprise arrêtait les vérifications de témoins, mais le contact requis
pouvait encore convertir la piste consommée en recherche des autres salles.
**Dernière correction : `_chercher` et `s_enquerir` ferment aussi cette reprise.**
Un contact positivement localisé et frais reste possible.

**Attribution rechargée.** Auberge 371/7 à 240 : Lucien cru au couloir depuis 174 ;
mine 69/7 à 470 : Rémy cru au baraquement. Variantes parti/resté exécutées,
monde/croyances/rendu/scène rechargés, position réelle cachée modifiée sans changer le plan.
Les 170 captures anciennes sont rechargeables, leurs 11 rejeux reproduisent les
empreintes de `7986b7d2` (`reprise/attribution-rechargee.json`).

- Aubin crue 42 : deux questions à 10800/10926 sur la voix d'Ilse de minute 3,
  puis inspection ; consommation commune. Passages de salle première heure : **24→54→24**.
- Brune crue 1985 : inspection 190 rafraîchit Aubin vu à 175 ; cette propre
  observation expire à 205 et réveille l'agenda. Répétition corrigée, test 190/205/220/235.
- Lucien mine 1985 : abri→repos à 102→abri à 108, sans quitter le baraquement ;
  repos 90,1→78,1, Mathe revue à 101/107 : retour légitime après satisfaction du besoin.
- Brune crue 2024 : après refus, case d'Ilse inconnue→[0,12], entrée acoustique
  nouvelle qui lève le refus. Confirmé aussi dans le dernier banc à 136784/136791.
- Nouveau signal Lucien auberge 7 : ancienne question 142, Hugues revu à 168,
  hypothèse fraîche à 175 puis expirée à 183 : première vérification de cette
  nouvelle preuve. Pas de répétition de la piste précédente.

**Mesures réalisées (`8a3b0725`, avant dernière fermeture).** 16 nuits × 4 h,
Relais/auberge/mine/crue, quatre graines ; zéro plantage et usurpation.
`VERIFIER` Relais 7, 1 h : vert, 30,927 s. Appels base→branche :
**4→7 / 13→84 / 9→25 / 35→50**. Deux retours stricts attribués ci-dessus.
Les 84 appels d'auberge restent trop nombreux pour conclure sans la dernière
fermeture : capture Lucien/Hugues à 42, piste déjà consommée, nouvelle recherche
dans le couloir (`position-374-auberge-42-42-consommee.json.gz`). La ventilation
complète de l'ancienne réserve **46/38 appels** est renforcée par les captures de
chaque appel ; un bruit attribué ancien ne compte plus comme nouvelle preuve.

**Tests.** Avant dernière fermeture : 118 tests ciblés, 116 verts, deux écarts de
texte déjà reproduits sur `3999bb3a` (contact contenant et reprise Ilse ; lot 390).
Après fermeture : passe de 53, **52 verts, seul écart contenant hérité** ;
**13 tests position verts**, dont nouvelle capture de contact requis. Oracles hérités
intacts. Pas de suite complète ni Luna. Nouveau banc 16 nuits et voisins à finir,
deux travailleurs, priorité réduite ; base 3999bb3a en cache, historique b83f5a59
relu sans rejeu, aucun temps CPU comparé au cache. Fin attendue :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/fin-contact-consomme.json`.
Aucune certification d'absence de boucle avant ses résultats ; demi-vies non calibrées.
