# Lot 387 — Connaissance explicite au terminal d'information

Branche `codex-information-terminal-connu`, base `integration` : `a77727ab`.
Code et tests livrés ; **vérification des trois fichiers en cours**, sans validation finale annoncée.

**Invariant.** Le formulaire ne propose un bien précis que si Corvus le connaît.
Une mention lexicale du bois dans le contexte ne constitue pas ce savoir ; connaître
un bien ne donne ni sa présence ni sa possession. Le moteur du lot 365 respecte
ce contrat : **aucun code du jeu ni donnée de scénario modifié**.

**Attribution des cinq erreurs.** Le `StopIteration` est reproduit sur cette base
dans `FormulaireTests.test_projection_figee_choix_explicites_et_limite_objet`.
Les quatre autres occurrences sont les méthodes `test_quatre_actes_reponses_croyances_et_recharge`
et `test_autre_scenario_homonymes_et_mefiance`, chacune en console et en TUI.
Les sondes de leurs préparations retrouvent toutes `bois` inconnu et absent des
ressources proposées ; le parcours demande pourtant ce choix. Ce sont cinq
prémisses devenues fausses après le 365, pas cinq défauts du terminal. L'état
initial commun `ressources` reste inchangé : les seuls tests qui choisissent ce
bien ajoutent explicitement son souvenir à `connus`. Aucune assertion existante
n'est retirée ou affaiblie.

**Contre-épreuve et chaîne complète.** Un nouveau test parcourt les états connu
et inconnu pour `bois` et `crochets`. Il vérifie après sauvegarde/rechargement
l'état entier, la scène perçue, la fiche et le texte de scène ; la consultation
ne modifie aucun état. Le formulaire numéroté et les vrais callbacks web Node
proposent exactement les mêmes ressources et formulaires. Un bien inconnu
n'apparaît pas dans le rendu et son descripteur forgé est refusé avec `attendu`.
Un souvenir explicite le rend choisissable sans rendre l'objet visible ni le
déplacer. Les parcours existants conservent leurs contrôles de réponse, parole,
croyance, sauvegarde avant publication et parité web/console/TUI. Un parcours
supplémentaire sur les crochets connus vérifie aussi le refus de possession
« Je n'en ai pas. » après rechargement.

**Vérifications.** Les deux tests de formulaire existants passent après correction
des prémisses. La nouvelle contre-épreuve passe en **19,090 s**. Sa première
passe avait une erreur de harnais : l'état web ajoute les définitions de
formulaires au catalogue ; la comparaison porte désormais sur cette structure
complète. Le premier essai sous bac à sable a rencontré un refus d'accès aux
répertoires temporaires ; les essais suivants utilisent le même Python du dépôt
principal hors bac à sable, à priorité réduite.

La passe finale porte sur `test_information_terminal`, `test_information_publique`
(dont les vrais choix web) et `test_catalogue_connu` : **26 tests attendus**,
deux travailleurs au plus, détachés. Fichier de fin écrit par le lanceur :
`C:/Users/msics/donjon/artifacts/information-terminal-387/fin-calcul.json`.
Lire son résultat avant de valider le lot ; la suite complète, Luna et les
empreintes ne sont pas lancées, conformément au brief sans changement du jeu.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/information-terminal-387/` :
`diagnostic-base.json`, journaux du formulaire, `lancement.json` et journaux de
la passe finale. Les sondes de diagnostic reproduisent la préparation fautive
des quatre parcours, sans rejouer leurs boucles avant correction. Aucun élargissement
du contrat de connaissance, aucune migration d'une ancienne mention en prose.
