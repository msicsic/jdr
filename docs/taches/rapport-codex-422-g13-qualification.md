# Lot 422 — G13, admission d'une propriété inconnue

31 octobre 2026 — `codex-g13-qualification`, base `origin/integration` / `152a2aa0`.

**Invariant.** Qualifier complète l'inconnu avant usage, sans remplacer l'établi.
`matiere.valider` contrôlait la matière, la masse et le nombre de pièces, mais
laissait `deduire` écraser les mesures partielles et la charge connue.
La dérivation commune `_grandeurs` sert maintenant au contrôle puis à l'application :
dimension, rôle ou charge incompatibles sont refusés avec identifiant, champ,
valeur reçue et valeur acceptée. Une matière jusque-là vide rejoint aussi le
matériau public, donc l'examen et les morceaux hérités. Masse et état restent acquis.

`coherence_physique.propositions` transmet les mesures partielles, les comptes
et les grandeurs connues à la revue ciblée d'admission. Le moteur garde ses
contrôles avant cette revue. Dans `mj`, si le réexamen rencontre un autre obstacle,
son refus déterministe accompagne désormais la transaction de qualification admise ;
il n'est plus remplacé par la seule description de l'objet. Le contrat existant de
`faits_locaux` et des transactions assure enregistrement, sauvegarde, reprise et
héritage aux pièces. Aucun audit retiré, prompt ajouté ni registre d'esprit créé.

**Vérification ciblée.** Huit fichiers, **95 tests verts** sur leurs dernières
exécutions (`tests-voisins.json`, `tests-final.json`, `tests-g13-final.json`), deux
travailleurs au plus à priorité réduite. Planche de bois qualifiée puis découpée ; ficelle de fibres qualifiée
puis nouée en assemblage, avec suite jointe ou réexamen ; nouvel usage après
recharge sans qualification supplémentaire ; monde et rendu stables après laps
entier/découpé. Planches réelles du Relais : admission puis prélèvement et héritage.
Perche de fer de 200 g et mesures contradictoires : refus local avant revue,
monde conservé et examen rendu après recharge.
Deux revues négatives simulées interdisent admission et usage. Un obstacle d'outil
après admission conserve le fait et affiche le refus moteur.

Deux fixtures voisines ont reçu `suite: null`, requis par
`compilation.schema_reponse` depuis A6 ; aucune assertion de sécurité modifiée.
`diagnostics-base.py` / `.log` reproduisent leurs deux échecs sur les sources
exactes de `152a2aa0`. Les premiers lancements ont rencontré les ACL des dossiers
temporaires Windows ; relance autorisée hors bac à sable.

**Empreintes et Luna.** Relais 2 h, graines 1985/7/42/2024 : chroniques, mesures
et états finaux complets **identiques** à `152a2aa0` ; 146,94 s, aucun plantage.
Référence calculée puis cachée une seule fois ; aucun gain CPU revendiqué.
L'atelier n'a pas de scénario PNJ. Une seule passe `gpt-6-luna` sur copies
en cours : `materiaux`, `atelier`, `assemblage`,
`lots`, coffre principal via `SEUIL_AUTH`. Commandes exactes dans `commandes.json`.
Aucune suite complète lancée.

**Limites.** La plausibilité d'une propriété non calculable reste une revue
sémantique, sans garantie générale sur tous les implicites. La découpe des planches
combustibles du Relais échoue déjà sur la base : le morceau hérite de l'usage
combustible sans son compteur (`Combustible invalide`, `diagnostics-base.log`).
Ce défaut de partage d'une ressource combustible reste à traiter dans un lot dédié ;
la découpe réussie vérifiée ici porte sur une planche ordinaire à l'atelier.
La qualification générale ne résout pas ce défaut d'usage.

**Bruts.** `C:/Users/msics/donjon/artifacts/g13-qualification-422/` ;
fichier de fin des deux calculs : `fin.json`.
