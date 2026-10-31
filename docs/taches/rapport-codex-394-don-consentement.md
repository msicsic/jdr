# Lot 394 — Don et consentement U-C

Branche `codex-don-consentement`, base `origin/integration df7352b7`
(moteur de l'intégration `c562aa21`), PC fixe, 31 octobre 2026.

**Décision établie.** Un don ordinaire produit l'effet typé `donner`, absent
des `EFFETS_LEGERS` de `donjon/consentement.py`. Selon `effets_lourds` et
`plan_lourd`, cet acte est donc lourd, comme tout effet non classé léger.
C'est bien la règle U-C du [lot 325](rapport-codex-325-uc-consentement.md) :
la gravité dépend des effets du plan entier, pas du verbe ou de l'objet.
Le passage de `remettre` par U-C ajouté au lot 380 n'impose pas lui-même
une confirmation inconditionnelle : `Moteur.preparer` appelle `plan_lourd`.
La restitution produit elle aussi `donner` ; une remise rémunérée produit
`remettre`, également lourd. Aucun arbitrage supplémentaire n'est requis.

**Changement.** Les deux tests de `DonLocalTests` supposaient l'ancien parcours
immédiat. Ils soumettent désormais `tenter`, sans retirer leurs assertions de
transfert, propriété, souvenir du don et résultat sauvegardé. Ils vérifient
aussi l'ordre « Compris : … » puis « Tu donnes … ». Aucun fichier de production,
classification U-C, garde de compte ou registre d'esprit n'est modifié.

`test_don_consentement.py` ajoute huit parcours dans la vraie boucle : cloche
à Gorm et couteau à Brune, don et restitution, console et descripteur public
du pont web. Les scènes sont placées au contact dans le moteur spatial réel.
Les contrôles portent sur les effets typés, la gravité commune, l'aperçu,
l'annulation sans effet, la confirmation, l'absence de paiement et la clôture
du prêt. À chaque étape, toute la sauvegarde est comparée au monde vivant,
ainsi que fiche, regard, scène perçue et comptes publics. L'état hors historique
d'affichage reste identique avant confirmation. Une seconde ouverture réelle
réaffiche le résultat enregistré sans rejouer le geste. Zéro appel au modèle.

**Vérification.** La reproduction initiale retrouve exactement les deux rouges
du brief : `KeyError: proprietaire` et couteau resté au joueur. Les huit nouveaux
parcours sont verts en **49,738 s** (une méthode unittest, huit sous-cas).
Les cinq fichiers prescrits (`test_promesses`, `test_comptes_publics`,
`test_consentement`, `test_echanges_suite`, `test_rembourser_dette`) passent :
**65/65 tests en 507,696 s**, y compris les parcours TUI d'U-C.
Total : **66/66 méthodes**, zéro échec, erreur ou saut ; aucune assertion
mécanique ancienne retirée. `git diff --check` est propre.
Leurs tests de comptes conservent notamment le refus de convertir une restitution
en remise rémunérée et le refus d'un compte périmé entre aperçu et confirmation.

**Limites et livraison.** Le lot adapte les attentes au consentement déjà
implémenté ; il ne rend pas le don immédiat et ne modifie aucune règle joueur.
Le transport web est exercé par `PontWeb` et ses descripteurs ; aucune session
graphique de navigateur n'est revendiquée. Pas de Luna, d'empreintes, de banc
ni de suite complète. Deux travailleurs au plus, priorité réduite.
Bruts : `C:/Users/msics/donjon/artifacts/don-consentement-394/`
(`avant-dons.txt`, `cibles.json`, `placement.json`, `voisins.json`,
`mesures-uc.jsonl`, `fin-verification.json`).
La première passe des nouveaux tests, avant placement spatial, reste archivée.
Branche poussée vers `origin`, aucun calcul restant ; fusion et vérification
d'intégration laissées au superviseur.
