# Lot 372 — A6, soupçon déduit et projet de récupération

30 octobre 2026, PC fixe. Branche `codex-soupcon-deduit`, base
`origin/integration d8567324` (la référence locale `integration` était ancienne).
Livraison non fusionnée ; aucun appel à Luna.

**Invariant.** Le registre perceptif commun compare deux constats, puis conserve
les candidats et leurs poids. L'occasion exige une présence vue ou entendue dans
la salle depuis le dernier regard ; ni une réputation seule, ni le profil secret,
ni la position réelle du bien ne désignent quelqu'un. `esprits._candidats_soupcon`
donne un poids de présence de 1, augmenté de la confiance du guet lu envers le bien
ou son contenant, et de 0,5 pour un antécédent de prise retenu dans les relations.
Les lectures périmées et une lecture de garde ne valent pas convoitise.

`relations.deduire_soupcon` conserve tous les candidats ; un maximum unique
désigne le suspect, une égalité s'abstient. La conviction vaut
`0,4 × poids maximal / somme des poids` : elle reste faillible et module l'épreuve
commune de méfiance, avec la PSY existante. Une conséquence concomitante
(contenant vide et bien absent) n'ajoute pas une seconde pénalité. Anciennes
sauvegardes lisibles ; nouvelles pondérations contrôlées au chargement.

`agendas._biens_soupconnes` ouvre `récupérer {objet, qui}` seulement pour une
disparition propre attribuée. L'origine garde la preuve et son caractère supposé ;
aucune possession n'est ajoutée aux croyances ou aux portages. Le projet utilise
`rejoindre`, la question de localisation déjà exécutée par le moteur, les refus
retenus et la recherche commune. La question demande où est le bien, sans affirmer
que l'interlocuteur l'a pris. Plafond, coût, publication différée et sommeil restent
ceux des agendas. Un bien retrouvé ailleurs ou un portage constaté retire le
soupçon ; son projet est alors clos, et la voie du portage prouvé reste distincte.
La levée restitue seulement la confiance réellement perdue.

**Vérification.** 161 méthodes distinctes vertes, consolidées sur 15 fichiers :
24 ciblées (soupçon et nouveaux agendas), puis voisins des naissances, fins,
relations, constats, localisation, réclamation, signes et récit. Deux anciennes
attentes adaptées à l'invariant demandé : une disparition attribuée ouvre désormais
un projet ; deux passants égaux sont conservés sans auteur, pénalité ni projet.
Leurs autres assertions de sécurité restent conservées. Les premières reprises
ont corrigé le placement physique des acteurs et les attentes du harnais, sans
contournement moteur. Gorm/Brune/vivres au Relais et Anselme/Lucien/ballot à l'auberge :
prise exécutée hors du regard, disparition perçue, enquête et refus retenu ; monde,
rendu, scène perçue et récit identiques après recharge. Deux minutes entières ou
1 + 1 donnent le même monde et le même rendu dans les deux scènes. Retour ailleurs,
autre porteur vu, égalité, guet/garde, antécédent, écoute, péremption, mémoire courte
vidée, mutation de l'état caché et sauvegarde invalide couverts.

**Empreintes.** Banc de 2 h × quatre graines × six scénarios (Relais, mine,
auberge, crue, rixe et hameau) en cours, base exacte cachée une seule fois puis
branche, deux travailleurs réduits. Résultats et captures dans
`C:/Users/msics/donjon/artifacts/soupcon-deduit-372/` ; fin attendue
`empreintes.fin.json`. Ni suite complète, ni campagne Luna.

**Limites et recouvrements.** Soupçon de salle, pas de reconstitution spatiale fine ;
antécédents bornés aux motifs relationnels retenus, et convoitise aux lectures encore
actives. Une déclaration négative ou un inventaire simplement aperçu n'innocente
pas. La question de localisation existante ne renseigne qu'un lieu cru dans une
salle ; elle ne révèle pas un inventaire caché. Aucun nouveau dialogue d'accusation,
de dénonciation ou de sanction. Les poids sont une règle de jeu explicite, sans
calibration statistique. Recouvrement avec 370 sur `agendas.py` et avec les autres
lots sociaux possible sur les accès à l'esprit ; aucun fichier des choix ou du MJ
modifié. Le détail des naissances et de la récupération est à conserver à la fusion.
