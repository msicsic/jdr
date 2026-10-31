# Tâche Codex 394 : le don direct après U-M social comptes (380)

Régression de la fusion du lot 380 (`20989ed9`), trouvée par le superviseur en bissectant `663d1308..c562aa21` :
`tests.test_promesses.DonLocalTests` passe de vert à rouge sur deux méthodes :
- `test_le_don_de_la_cloche_aboutit_sans_appel_au_modele` : `KeyError: 'proprietaire'`, la cloche n'est pas remise ;
- `test_un_autre_objet_a_un_autre_personnage` : `'joueur' != 'brune'`, le couteau reste au joueur.

Le 380 a fait passer `remettre` par le chemin du consentement U-C (`moteur.py`, autour de la ligne 211 :
`or p.get('action') == 'remettre'`, puis `plan.choix_public` pour une remise). Il a aussi ajouté, dans
`commandes.proposition_descripteur`, un refus quand l'objet relève d'un accord de remise rémunérée. Le don direct («
je donne la cloche à Gorm ») attend maintenant une confirmation que ces tests ne donnent pas. Lis `AGENTS.md` (contrat
du MJ, « Fidélité de la saisie »), `docs/etat-dev.md` (court), les rapports 380 et U-C
(`docs/taches/rapport-codex-*-u-c*.md` ou le lot du consentement ; cherche « consentement » dans
`docs/historique-lots.md`).

## Invariant (un seul)
**Qu'une remise demande une confirmation avant exécution est décidé par la règle commune du consentement (U-C,
`consentement.plan_lourd`, selon les effets typés de l'acte), et non par un aiguillage propre à un geste ; un don direct
qui n'est pas un acte lourd selon cette règle s'exécute comme avant le 380, et une restitution ou une remise liée à un
accord garde le contrôle des termes ajouté par le 380.** Établis ce que dit `plan_lourd` d'un don simple :
- si le don est lourd selon les effets typés, les tests supposaient l'ancien parcours : adapte-les (« tenter ») en
  citant la règle, et vérifie que la ligne « Compris : … » précède bien l'exécution ;
- sinon, l'aiguillage du 380 force une confirmation contraire à U-C : corrige-le pour que seule la règle commune
  décide, sans perdre la protection du 380 sur la remise convenue.

C'est une règle côté joueur : ne la change pas au-delà de ce que dit U-C. Si U-C ne tranche pas le cas du don,
termine par QUESTION avec les deux options.

## Vérification
`test_promesses`, `test_comptes_publics`, `test_consentement` (ou le fichier U-C), `test_echanges_suite`,
`test_rembourser_dette`, et le parcours console et web d'un don et d'une restitution après recharge (zéro appel au
modèle). Pas d'empreintes si seul le chemin du joueur change. Pas de suite complète (une tourne sur `c562aa21`), ni
Luna.

## Contraintes
**Poste : le PC fixe.** Lots en cours : 374 (position crue), 381 (A2 passage), 391 (parité acoustique), 392 (scènes
connues) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs
détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-don-consentement`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-394-don-consentement.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\don-consentement-394\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
