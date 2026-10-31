# Lot 422 — G13, admission d'une propriété inconnue

31 octobre 2026 — `codex-g13-qualification`, base `origin/integration` / `152a2aa0`,
code `e6211a98`. **Portage moteur vérifié ; validation Luna partielle.**

**Invariant et changement.** Qualifier complète l'inconnu avant usage, sans remplacer
l'établi. `matiere.valider` contrôlait matière, masse et pièces, mais laissait
`deduire` écraser les mesures partielles et la charge connue. `_grandeurs` fournit
la même dérivation au contrôle et à l'application : dimension, rôle ou charge
incompatibles sont refusés avec identifiant, champ, reçu et accepté. Une matière
jusque-là vide rejoint le matériau public et les morceaux hérités.
`coherence_physique.propositions` transmet aussi mesures, comptes et grandeurs
établies à la revue d'admission. Dans `mj`, un autre obstacle au réexamen conserve
la qualification admise et affiche le refus déterministe. Le contrat existant de
`faits_locaux` et des transactions assure enregistrement, sauvegarde et reprise.
Aucun audit retiré, prompt ajouté ni registre d'esprit créé.

**Tests.** Huit fichiers, **95 tests verts**, deux travailleurs au plus à priorité
réduite ; dernières exécutions dans `tests-voisins.json`, `tests-final.json` et
`tests-g13-final.json` (76,89 s cumulées par fichier). Planche qualifiée puis découpée ;
ficelle qualifiée puis nouée en assemblage, suite jointe ou réexamen ; nouvel usage
après recharge sans qualification supplémentaire ; monde et rendu après laps
entier/découpé. Cas réel du Relais : qualification, prélèvement et héritage des
planches. Perche de fer de 200 g et mesures contradictoires refusées avant revue ;
deux revues négatives interdisent admission et usage. Deux fixtures ont reçu
`suite: null`, requis depuis A6, sans changer leurs assertions de sécurité :
`diagnostics-base.log` reproduit leurs échecs sur `152a2aa0`. Les ACL temporaires
Windows ont nécessité une relance autorisée hors bac à sable. Aucune suite complète.

**Empreintes.** Relais 2 h, graines 1985/7/42/2024 : chroniques, mesures et états
finaux complets **identiques** à `152a2aa0`, aucun plantage, 146,94 s. Référence
calculée puis cachée une fois ; aucun gain CPU revendiqué. L'atelier n'a pas de banc PNJ.

**Luna : une passe sur copies**, coffre principal, `gpt-6-luna`, quatre scripts :
**54 appels / 19 tours MJ**, soit **2,84 appels et 12,56 s/tour** ; 282 s écoulées.
Aucun repli, erreur technique ou de recharge ; trois tours avec refus.
`materiaux` : planches admises en **7 appels / 27,04 s**, examen suivant sans modèle.
`lots` : admission en **6 appels / 22,26 s**, tentative en **11 appels / 44,26 s**
cumulés. Chaque admission passe une seule revue physique ; la qualification répétée
au réexamen est refusée localement. Mais la tentative prend **le tas entier** pour
« une planche » : le coût jusqu'au prélèvement fidèle n'est donc pas démontré.
La correction `prelever` a été rejetée par la reprise qui conservait `deplacer`,
puis une revue a admis le déplacement du lot. `assemblage` réussit en
**2 appels / 13,57 s**, puis découpe la ficelle en **2 / 10,88 s** ; les propriétés
étaient déjà fournies par le scénario. `atelier` n'admet aucune qualification
physique. La longueur de la torche est refusée par le garde de portée au motif de
perception requise ; l'examen suivant n'établit aucune longueur. La qualification
utile générale par Luna n'est donc pas démontrée. Aucun second essai.

**Limites.** La plausibilité non calculable reste sémantique. La découpe des planches
combustibles du Relais échoue déjà sur la base : le morceau hérite de l'usage sans
compteur (`Combustible invalide`, `diagnostics-base.log`). Ce partage de ressource
reste à corriger dans un lot dédié ; la découpe vérifiée ici porte sur une planche
ordinaire à l'atelier. Les limites de portée et de fidélité Luna restent ouvertes.

**Bruts.** `C:/Users/msics/donjon/artifacts/g13-qualification-422/` : commandes
exactes, tests, diagnostics de base, empreintes, quatre fils Luna, `mesures.json`
et `conclusion-luna.json`. `fin.json` : deux codes zéro ; calculs du lot terminés.
