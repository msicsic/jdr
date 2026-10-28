# Lot 251 — présences requises par un geste

**`codex-service-repropose`, non fusionnée**, base `integration 854bb10`.
Pas de Luna, scénario ni `social.py` modifié ; aucune suite complète.

**Reproduction et cause.** Auberge 2024, départ tiré, 4 h : aucune tentative
échouée de service sur la base courante. Le rejeu détaché de `942a3c2`
reproduit l'échec de Mireille à **135695** et sa reproposition à **135725**.
La capture antérieure à l'exécution situe Mireille en cuisine et Mathurine,
réellement et selon la croyance de Mireille, dans la salle commune. La part
existe et reste disponible : c'est la présence requise du bénéficiaire qui
manque. `echanges.servir` impose la même salle avant de contrôler la parole.
La mesure du plan ne vérifiait que les cibles touchées (ici la marmite), et
`refus_etape` ne contrôlait que l'eau. L'échec n'apportait aucune information
capable de réparer cette admission : la bonne croyance était déjà présente.
La protection `manque` évitait une seconde exécution dans la minute, pas une
nouvelle proposition de ce même plan.

**Invariant corrigé.** Une étape n'est admissible que si toutes les présences
qu'elle requiert sont compatibles avec ses lieux projetés et les croyances
courantes. `pnj._a_reunir` étend le contrat des cibles touchées au participant
d'un service ; il ne transforme pas ce dernier en cible de contact. Le même
contrat est lu par `planification._mesurer_direct` pendant la recherche et par
`pnj.refus_etape`, déjà partagé par admission, revalidation et `agir` (213).
Une étape portée ou préparée par une ouverture reste jugée dans sa projection.
Aucune échéance, mémoire d'échec supplémentaire, règle de lieu ou exception
de personnage : l'obstacle est déjà représenté par la croyance de localisation.
Le mécanisme d'obstacle retenu du 225 n'a donc pas besoin d'une nouvelle cause.

**Vérification ciblée.** **28 tests distincts verts, cinq fichiers**, sur les
passes ciblées : service, garde, contrat d'engagement, présences et trajet
estimé ; dernière passe des deux fichiers modifiés **8/8, 10,923 s**.
La capture versionnée et une scène de la mine (Mathe/Lucien, vivres portés)
vérifient refus, choix répétés après recharge, état et rendu sauvegardés,
reprise immédiate après croyance de retour, 4 minutes d'un bloc ou découpées,
absence de proposition immédiate invalide et de service exécuté en échec.
Deux contre-épreuves rouges en rétablissant l'ancien contrat des seules cibles
touchées. Le service présent réussit sans imposer le contact au bénéficiaire.
Le test de garde de la mine a été réancré près du repas, assertions conservées :
son ancien placement perdait Lucien de vue après déverrouillage, puis servait
sans le situer (preuve comparée à la base verte, journaux dans les bruts).

**Banc en cours.** Lancé détaché, priorité réduite, un travailleur : 4 h,
cinq scénarios × quatre graines, référence figée `854bb10`, puis branche.
Cache de cette base absent sur ce poste au lancement : remplissage unique
des références manquantes par l'outil commun, aucune référence existante
relancée. À réception de `banc.termine.json`, examiner `comparaison.json` :
compteur 219, suspects sans hausse, préemptions, « à expliquer », plantages
et usurpations. **Ces résultats ne sont pas encore validés.**

**Limites.** Le correctif garantit l'admission sur la présence crue requise ;
il ne constitue pas une mémoire générale de toutes les causes d'échec.
Une présence crue ne certifie pas l'ouïe réelle ni l'immobilité future d'autrui.
Un bénéficiaire perdu de vue n'est plus servi sans localisation ; aucune
nouvelle stratégie de recherche du bénéficiaire n'est introduite ici.
Bruts et scripts : `C:/Users/msics/donjon/artifacts/service-251/` ; fichier de
fin : `C:/Users/msics/donjon/artifacts/service-251/banc.termine.json`.
