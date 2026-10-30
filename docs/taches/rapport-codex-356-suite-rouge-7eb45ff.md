# Lot 356 — attribution de la suite rouge et harnais

Branche `codex-suite-rouge-7eb45ff`, base `integration df03dc2f`, synchronisée
sans rebase avec **`origin/integration 19c9b6da`** (`47769f26`, conflit documentaire seul).
**Terminé, non fusionné ; branche poussée, aucun calcul du lot actif.**
[Tableau exhaustif des 161 incidents](attribution-codex-356-suite-rouge.md).

**Attribution.** 143 échecs et 18 erreurs, 61 fichiers ; **158 bascules sur
parent direct**, sur copies natives du code et des tests. La recherche remonte
en amont du témoin 339 déjà rouge ; absence et saut ne valent jamais succès.
Trois incidents restent non reproduits sur le laptop, même après les rejeux
de fichiers entiers pour l'enfermement et le prêt :
installation gardée, enfermement, rappel du prêt. Leur cause et première
fusion restent **non établies**, sans correctif supposé.
Classement : **48 harnais du consentement, 71 attentes périmées prouvées,
39 régressions conservatrices (dont une corrigée ici), trois non reproduits**.
Le certificat contrôle les **316 labels et verdicts exacts** des deux bornes.

**Contrat des tests.** Les actes lourds simulés reçoivent `tenter`, avec le
harnais existant ou la saisie console : **811 assertions AST / 14 fichiers
contrôlés inchangées**, ainsi que les réponses simulées et les oracles mécaniques.
Un second portage, séparé de ces confirmations, traite les attentes
périmées documentées par **U-C / rapport 325** et **G16 / rapport 345** :
admission et action sur copie jusqu'à confirmation, mots formulés par le
moteur, observation de ses préparations sans inventer un appel au fournisseur.
Identités, adresses, auteurs, montants, propriétés, historique et recharge
restent contrôlés ; les faisabilités ne sont pas confirmées automatiquement.

**Correctif commun d'une ligne, exception autorisée par le brief.** Le portage
révèle que G16 refuse sa propre réponse collective comme « mots non fixés ».
`repliques_moteur.reponse` joint désormais les émissions par un saut de ligne :
chaque rendu enregistré conserve sa frontière, même si le prochain locuteur
commence par une minuscule. Aucun contrôle de publication n'est assoupli.
Un test fonctionnel reproduit **deux erreurs avant correction**, au Relais et
à l'auberge ; il contrôle après correction les mots, les objets hors orientation,
le joueur, le temps, le journal, la scène et le monde rechargés. Aucun fichier de code
des lots 353, 354 ou 355 n'est édité.
**Mesures et reprise.** Bissection utile v2 : **12 653,186 s** ; compléments
MiMo/imports/fichiers entiers : **375,509 s**, deux travailleurs réduits au plus.
Défaut d'import du lanceur et dépendance MiMo manquante corrigés ; traces
invalides et reprises conservées, aucun saut MiMo compté comme succès.
**Validation finale : 201/201 tests, 18 fichiers ciblés, 763,976 s, zéro échec,
erreur ou saut.** Tous les tests livrés et les répliques G16/G17/G18 voisines
sont verts sur `19c9b6da` synchronisé. Empreintes des sources identiques avant
et après la passe ; **`fin-validation-finale.json ok=true`**, code tests 0.
Ni suite complète, Luna ou banc ; les contrôles lourds restent à l'intégration.

**Réserves.** Le tableau classe conservativement les ruptures sans preuve de
changement voulu en régressions à traiter/arbitrer séparément : ouï-dire/337,
cause/330, plan différé perdu après discussion/U-C, lampe après la nuit/312,
couverture/341 et préfixe KV/G6 : **38 ruptures historiques réservées**, à
rapprocher aussi des corrections fusionnées entre-temps, sans leur attribuer
un état courant non mesuré. Les scènes déjà portées par d'autres lots
ne sont pas créditées ici. La suite globale n'est **pas déclarée verte** et
les trois incidents non reproduits demandent une vérification sur le PC fixe.

Bruts, certificats, assertions AST, résultats et lanceurs :
`C:/Users/msics/donjon/artifacts/suite-rouge-356/` ; détail dans l'annexe.
