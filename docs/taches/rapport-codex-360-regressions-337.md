# Lot 360 — régressions du 337 : état intermédiaire

Branche `codex-regressions-337`, base `integration 0b62a4fa`.
**En cours, non fusionné : ne pas considérer le lot comme validé.**
Bruts : `C:/Users/msics/donjon/artifacts/regressions-337-360/`.

**Décision de l'utilisateur, 30 octobre.** Ne pas raconter l'inventaire de
départ. Une possession inchangée ne devient pas une nouvelle parce qu'on la
revoit, la date autrement ou la découvre plus tard. Un transfert ou un
changement de droits appris, une perte, une restitution et une destruction
restent transmissibles par les règles communes de confiance et d'auditeur.

**Contrat porté.** `esprits.installer` et la première perception établissent
`faits_initiaux`, un registre de provenance sauvegardé, distinct des croyances
et des faits dits. Il n'accorde aucune connaissance d'un tiers et n'atteste
aucune parole. `social.reviser_dits` retire définitivement l'ancrage d'une
propriété changée : un retour à sa valeur de départ reste donc une nouvelle.
`social._constats/_nouvelles` filtrent le contenu initial avec l'identité
commune `faits_dits`, sans règle de scénario, de personnage ou d'objet.
`esprits.preuve_possession` mutualise la photographie des droits ; leur
réception ne relit toujours pas les droits réels. Ni Luna ni le moteur
d'action ne sont modifiés.

**Mesures acquises.** Reproduction native : 23 méthodes, 24 échecs et trois
erreurs, 206,194 s. L'ablation diagnostique des nouvelles propriétés du 337
fait repasser 21 méthodes ; elle n'est pas le correctif livré. Les tentatives
de portage d'inventaires déjà racontés ont été annulées après l'arbitrage.
Dernier rejeu des 23 : **18 méthodes vertes, cinq encore rouges** (5 échecs,
une erreur avec sous-cas), 148,317 s, avant le dernier filtre des relais.
Contrôle court final : **23/23 verts, 15,082 s**, dans `initiaux-final.log` ; inventaires
initiaux, première découverte, transfert inédit, retour, droits datés,
réception/recharge et les 16 tests du 337 y sont exercés. Monde complet,
rendu terminal et scène web sont comparés après rechargement.

**Vérification détachée.** `tools/valider_regressions_360.py` exécute 28 fichiers
ciblés et la classe du passage spontané, puis vingt empreintes de 2 h (cinq
scénarios, quatre graines), au plus deux travailleurs à priorité réduite.
`origin/main` désigne le vrai `main 0bad227` ; la branche locale `main` de ce
poste est ancienne. Les références sont relues du cache partagé, seules les
absentes calculées. `constats-confies.json` donnera les comptes par nuit :
aucune baisse chiffrée n'est affirmée avant sa production. Les empreintes
peuvent différer avec ce changement voulu ; plantages et divergences seront
analysés à la reprise. Fin écrite en dernier : `validation/fin.json`.

**Réserves à reprendre.** Les cinq méthodes non closes portent sur la capture
d'allumage 1985, l'appel vain du donneur, Lucien après reprise du ballot,
les deux captures d'étapes chaînées et l'aide du hameau à 541. Aucun oracle
n'est recalé pour les faire passer. Le passé d'une ancienne sauvegarde sans
provenance initiale n'est pas reconstructible : l'installation ancre ses
inventaires présents et ses anciennes localisations sans droits, sans
inventer de transfert ; la distinction exacte entre un inventaire initial
et un transfert ancien encore non raconté n'est alors pas garantie.
Recouvrement **361** : seul
`LaisserPasserJoueurTests.test_cas_reel_brune_s_ecarte_du_seuil` est porté au
texte résolu de G7 ([preuve 343](rapport-codex-343-g7-deplacements.md)), avec
l'autorisation explicite de l'utilisateur. `DemanderLePassageTests` est intact.
Pas de suite complète, de Luna, ni de fusion dans ce lot.
