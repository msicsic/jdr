# Lot 56 — sens des comptes

Branche `codex-sens-dette`, non fusionnée ; base **f033364**, brief **0b2ea87**.
`main`, `planification.py` et les fonctions sociales réservées au lot 55 inchangées.
Luna reste `gpt-6-luna`.

**Invariant et cause.** Le contenu `reclamer` et le moteur orientaient correctement
la question réelle ; le récit pouvait inverser la dette sous couvert de parole de
PNJ. `biens.compte` et `etat_comptes_joueur` donnent maintenant débiteur, créancier,
objet ou pièces, quantité et état dû/rendu/absent. Le prêt va de l'emprunteur au
prêteur ; `_reclamer` transmet le solde et les remises effectuées dans
`conversation_validee.comptes`. L'absence monétaire dit « aucune pièce » ; l'absence
en main ne s'énonce plus comme absence générale de dette.

`mj._echanger` fournit les seuls comptes connus de Corvus, avec la projection
habituelle des identités. `narration.schema_audit` impose l'extraction des comptes
affirmés dans chaque segment, même une réplique. `controler` compare les rôles,
l'objet, l'état et toute quantité explicite à l'issue, sinon aux comptes courants.
Rapport incomplet : illisible ; compte incompatible : un refus et son `attendu`
citant les rôles reçus et l'issue. `consigner` refait le contrôle. Les fixtures
d'audit existantes déclarent leurs comptes vides.

**Vérification.** Neuf nouveaux tests : Aubin et Brune sans dette, inversions,
remboursement de deux pièces, refus conservant la créance, prêt échu réclamé au
joueur, restitution d'objet, narration ordinaire/montant faux, garde persistant,
comptes privés exclus. Console et MJ simulé vérifient affichage, textes persistants,
état et fiche après recharge. Dernière reprise : **50 tests verts**, 25,1 s.

Suite complète unique, trois processus à priorité réduite : **1 793 tests,
16 ignorés, 1 302,4 s**. Deux défauts dans le résultat brut : placement de prêt
par le joueur non autorisé, remplacé par une restitution valide ; attente du
harnais artisanat oubliant `comptes`, corrigée. Les trois fichiers concernés sont
rejoués verts. **Bilan consolidé : 175 fichiers, 1 793 tests, 16 ignorés, aucun
défaut restant** ; aucune seconde suite complète. Empreintes Relais, 2 h × quatre
graines : chronique, mesures et état complet identiques à f033364, référence mise
en cache. Bruts : `artifacts/suite56.*`, `reprises56.json`,
`tests-consolides56.json`, `empreintes56.*`.

**Luna, une passe.** `ressources` : **3/3/7 appels**, contre **3/3/3** dans la
première référence intégrée f033364 en cache ; 3 → 4,33 appels/tour,
10,73 → 14,70 s/tour (charges différentes). Question de comptes : trois refus,
deux relances, un repli affichant « Aubin, vieux passeur ne te doit rien ».
Les inversions refusées ne sont pas enregistrées. La première réplique mélangeait
« Tu ne m'as rien prêté » et « je ne te dois rien » : l'extraction provoque aussi
un faux refus. La précision finale « aucune pièce » est vérifiée sans modèle après
cette passe. `comptes` : zéro appel des deux côtés, noms non appris ; règlement
couvert uniquement par les tests simulés. Aucune erreur de recharge. Le `main`
local 42bb9c0 n'a pas de cache adapté et son essai échoue sur l'import d'`agendas`
dans le lanceur récent ; comparaison lue dans le cache f033364, sans le relancer.
Bruts : `artifacts/bancs-multi/20261024-231400-31536/`, `luna56-relecture.txt`.

**Limites.** La comparaison est déterministe sur les comptes extraits ; leur
reconnaissance, leurs pronoms et leurs omissions restent sémantiques. Aucune garantie
absolue contre les inversions ou faux refus. Une question typée `reclamer` garde le
règlement existant ; aucun nouveau mode de consultation, prêt par le joueur ou
endettement monétaire du joueur n'est ajouté.
