# Lot 319 — U-P, le récapitulatif du plan admis

29 octobre 2026. Branche `codex-up-recapitulatif`, **non fusionnée** ; base
`integration 75b6dfb`. Aucun appel à Luna, banc ou suite complète.

Le moteur expose le plan admis par « Compris : … ». `comprehension.plan_admis`
réutilise les titres des compilateurs et leurs sous-plans, puis développe tous
les paramètres typés utiles : références publiques, parties, destination,
outil, méthode, prix, quantités et branches conditionnelles. Le raccourci de
vol avec finesse montre ses deux étapes, attente de deux minutes puis prise
discrète ; il ne promet aucune orientation du PNJ. Une composition conserve
son ordre et son arrêt au premier échec. La justification et les récits libres
du MJ ne servent jamais à décrire une conséquence mécanique.

`transactions_admises` restitue les actes de parole, les termes des offres,
le destinataire et la portée fixés par le moteur. Un avis reste une prévision,
une parole ne prouve pas son contenu. Les admissions de détails et de savoirs
gardent leur rendu public existant : leurs dossiers internes, qui peuvent
contenir des savoirs privés de PNJ, ne sont pas publiés par ce récapitulatif.

La boucle commune `jeu.py` place la ligne après les résultats légers et dans
la fiche existante avant les tentatives déjà soumises à confirmation.
`Plan.compris` permet aux panneaux TUI et web d'afficher la même fiche sans
modifier `gestes_publics.py`, `tui.py` ni `web/pont.py`. Les questions au MJ,
y compris une perception proposée, et la faisabilité préparent sans exécuter
et le disent. Clic et menu ne produisent aucune nouvelle ligne « Compris ».
Un plan périmé échoue avant la publication de son récapitulatif de résultat.

Le tour et son récapitulatif sont sauvegardés avant affichage. L'option
`Monde.memoriser(complet=True)` conserve les rendus moteur sans la troncature
historique à 4 000 caractères. Le dernier tour enregistré est relu tel quel
au démarrage, avec son récapitulatif même si la confirmation a été suivie d'un
résultat ; aucune exécution n'est rejouée. Une proposition non exécutée reste
un historique, pas une confirmation restaurée automatiquement.

## Vérification

Oracles textuels figés dans `tests/data/comprehension.json`, MJ simulé sans
réseau. Treize parcours par console, pont web et vraie TUI : paiement réel du
corpus G1 puis autre offre d'huile, avis individuel et collectif, parole
adressée et chuchotement, question sans action, vol avec/sans attente,
perche puis saut, prise légère, faisabilité et question de perception.
Les contre-épreuves montrent aussi une compilation infidèle (prix différent,
attente omise), sans la corriger silencieusement. Monde complet sérialisable,
objets, ressources, journal, paroles, scène et fiche sont contrôlés à la
recharge ; le pont contrôle l'enregistrement avant affichage. Cible disparue,
menu console, clic direct sans appel et rendu de plus de 4 000 caractères
sont également exercés. La séquence perche/saut est ajoutée sur l'atelier :
elle n'existe pas parmi les 91 saisies du fichier G1 indiqué par le brief.

**5 nouveaux tests verts**, 39 parcours d'interface, **72,869 s**.
**115 tests de régression ciblée**, dix fichiers, **495,177 s** : 113 verts,
un ignoré (`jsonschema` facultatif absent), un échec TUI de l'inscription,
dont la trace s'arrête avant l'envoi de la commande. Ce même test, inchangé,
**repasse seul en 5,012 s** ; cela évoque une course de synchronisation,
sans prouver son origine. La première passe n'est pas déclarée entièrement
verte ; sa trace est conservée avec celle de la reprise. Aucun oracle
préexistant affaibli. La sonde WebSocket attend désormais explicitement le
résultat moteur suivi du récapitulatif sauvegardé.
Bruts : `C:/Users/msics/donjon/artifacts/up-319/`.

## Limites

U-P montre le plan admis, sans démontrer sa fidélité au français du joueur.
Aucune revue, contre-revue ou garde du MJ n'est retirée ; compilateur,
schémas et consignes Luna restent inchangés. La classification générale des
effets lourds et leur consentement restent U-C : paiement et avis gardent
ici leur politique d'exécution actuelle. Le récapitulatif des improvisations
porte leurs effets typés, pas une garantie sur leur manière libre.
