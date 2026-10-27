# Lot 213 (196 c) — engagement minimal, validation finale en cours

**Branche `codex-contrat-engagement`, non fusionnée ; ne pas fusionner en l'état.**
Départ `cca5f50`, reprise demandée sur `d2243c2` (211), fusion `2a2d766`.
Version figée après revue 217 : `b215938`. Aucun Luna, deux travailleurs réduits
au plus ; pas de clé de signature configurée. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/engagement-213/`.

**Contrat.** `choisir` revalide avant l'arbitrage ; une intention revalidée, garde
ou attente à plan vide comprise, cède à un palier supérieur ou à une domination
avec marge. `marge_engagement` applique partout `INERTIE + VOL/4` : aucun coût de
trajet passé, aucune addition de minutes aux points d'urgence. Les coûts futurs
des moyens restent au planificateur ; leur raccord explicite à la bascule reste
à définir. `_candidats` sépare naissance et poursuite des demandes de condition
et d'agenda. `_reprendre_demande` peut poursuivre un secours hors de vue sur sa
détresse crue ; `_fin_demande` interprète les fins et démentis connus.

**217.** Identité, parent éventuel, condition de fin et raison crue sont conservés
par la façade `agendas.py`, liés à l'intention exacte. Ce registre auxiliaire
respecte le validateur inchangé d'`esprits.py` et ne crée aucun agenda de secours.
Les phases du dernier arbitrage (naître, continuer, attendre, finir), la dernière
sortie attestée et ses faits survivent à la recharge. Une évaluation indéterminée
reste distincte d'une fin. Un geste manqué libère l'engagement avant une nouvelle
planification. Une seule transition est conservée, sans seconde pile de buts.

**Preuves ciblées.** 35 tests distincts verts, dont huit du contrat : captures
réelles 209 Rémy/mine 42 et Mireille/auberge 1985 ; cas transmis par 211 au Relais
1985 ; autre PNJ, autre scénario et secours contre le froid ; plan coupé, démenti,
préemption d'une ronde, VOL, causes persistées. Monde complet et rendu après
rechargement, laps entiers/découpés contrôlés. Le cycle d'Aubin au Relais 2024 ne
réapparaît pas dans le banc. `_lieu_cru`/`salle_crue` sont identiques à `d2243c2` ;
aucun autre fichier de production que délibération/agendas n'est modifié par 213.

**Banc final après 217 : 20 paires de 4 h**, cinq scénarios × quatre graines,
compteur 199 inchangé, 20 références relues du cache. Zéro plantage/usurpation.
Retours : sommes ; attente/sans recours/eau : moyennes PNJ·min ; S/F/D selon 183.

| Scénario | Retours | Attente / sans recours | Eau | S/F/D avant → après |
|---|---:|---|---:|---|
| Relais | 4 → 0 | 0/0 → 0/0 | 0 → 0 | 11,25/3,75/1,5 → 9,75/3,5/1,438 |
| Mine | 1 → 1 | 0/0 → 0/0 | 0 → 0 | 22/4,25/1,607 → 25,5/4,5/1,964 |
| Auberge | 2 → 2 | 0/20 → 0/20 | 0 → 0 | 12/4,25/1,063 → 11/4,25/1 |
| Crue | 2 → 2 | 178,75/0 → 170/0 | 2,5 → 3,75 | 14/6,75/2 → 17/6,75/2,375 |
| Hameau | 7 → 0 | 128,75/0 → 178,75/0 | 10 → 31,25 | 31/8/2,542 → 31,25/7,75/2,5 |

**Réserves.** Total 16 → 5, aucun scénario en hausse. Trois restants suivent un
`MANQUE` (acheter/servir/demander), sortie permise par R2 ; deux retours d'a1 en
crue restent à élucider. Brune hameau 42 passe 110 min dans l'eau : la trace
montre un geste manqué libérant le but, puis le même début de plan reproposé ;
l'exécution refuse son séjour en péril d'eau. **Absence d'entêtement non validée**,
aucun gain uniforme d'attente ou de richesse. A1 de Brune hameau 2024 : activations/
sommeils 5/6 → 4/3, cause non supprimée. Gorm conserve des relevés sans but,
classés en charge confiée ou attente ; ces relevés ne prouvent pas seuls une
intention perdue. Les captures de diagnostic conservent monde/rendu rechargés.

**Vérification finale en cours** sur la version figée après 217. Le passage ancien
(2 428 tests, 14 échecs, zéro erreur) est archivé ; le premier passage sur 211 a
été interrompu à réception de 217. Aucune conclusion de suite verte à ce stade.

**Limites explicites.** `None` du planificateur ne distingue toujours pas borne,
coût et impossibilité ; les sources sans demande persistante doivent réémettre
leur cible. La liste fermée n'est pas garantie sur toutes les voies. Le raccord
entre admissibilité crue et exécution, y compris les préparatifs d'évacuation,
reste ouvert. **218** reprend la suspension temporaire non portée ici : Gorm
ouvre sa réserve pour livrer Aubin, hameau 1985 min 6, et la reconstruction perd
la protection de cette charge. Aucune correction de ce cas revendiquée.
