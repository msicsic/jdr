# Lot 387 — Connaissance explicite au terminal d'information

Branche `codex-information-terminal-connu`, base `integration` : `a77727ab`.
Tests livrés dans `490ef509` ; **lot validé, non fusionné** le 2026-10-31.

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

La passe finale valide **26 tests distincts, zéro échec, erreur ou saut** :
`test_information_terminal` **9/9** (1 313,194 s), `test_information_publique`
**12/12** (582,562 s, dont les vrais choix web), `test_catalogue_connu` **5/5**
(50,770 s). Durée écoulée totale : **1 313,203 s**, deux travailleurs réduits
au plus, détachés. Les **34 parcours mesurés**, 17 console et 17 TUI, passent,
dont le bois et les crochets après recharge et comparaison au web ; **zéro appel
au modèle**. Le journal TUI ne contient que des diagnostics de lenteur asyncio.
`fin-calcul.json` porte `succes=true` ; aucun calcul actif. La suite complète,
Luna et les empreintes ne sont pas lancées, conformément au brief sans changement
du jeu. Branche poussée ; fusion laissée au superviseur.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/information-terminal-387/` :
`diagnostic-base.json`, journaux du formulaire, `lancement.json`, `fin-calcul.json`
et journaux de la passe finale. Les sondes de diagnostic reproduisent la préparation fautive
des quatre parcours, sans rejouer leurs boucles avant correction. Aucun élargissement
du contrat de connaissance, aucune migration d'une ancienne mention en prose.
