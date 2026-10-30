# Lot 356 — attribution de la suite rouge et harnais

Branche `codex-suite-rouge-7eb45ff`, base `integration df03dc2f`, synchronisée
sans rebase avec **`origin/integration 19c9b6da`** (`47769f26`, conflit documentaire seul).
**Dernière validation ciblée détachée ; `fin-validation-finale.json` attendu.**
[Tableau exhaustif des 161 incidents](attribution-codex-356-suite-rouge.md).

**Attribution.** 143 échecs et 18 erreurs, 61 fichiers ; **158 bascules sur
parent direct**. Le témoin après le lot 339 était déjà rouge pour plusieurs
familles : la recherche remonte donc au-delà de lui. Copies natives du code
et des tests, mêmes labels de sous-tests aux deux bornes ; une absence ou un
saut n'est jamais vert. Les deux fichiers devenus verts isolément ont aussi
été rejoués entiers. Trois incidents restent non reproduits sur le laptop :
installation gardée, enfermement, rappel du prêt. Leur cause et première
fusion restent **non établies**, sans correctif supposé.
Classement : **48 harnais du consentement, 71 attentes périmées prouvées,
39 régressions conservatrices (dont une corrigée ici), trois non reproduits**.
Le certificat contrôle les **316 labels et verdicts exacts** des deux bornes.

**Contrat des tests.** Les actes lourds simulés reçoivent `tenter`, avec le
harnais existant ou la saisie console. La première étape conserve exactement
**811 assertions AST / 14 fichiers contrôlés**, réponses simulées et oracles
de paiement, possession, parole, rendu et recharge compris. Elle passe
100 tests dans neuf fichiers ; cinq fichiers mixtes gardent alors 15 incidents.
Un second portage, séparé de ces confirmations, traite seulement leurs attentes
périmées documentées par **U-C / rapport 325** et **G16 / rapport 345** :
admission et action sur copie jusqu'à confirmation, mots formulés par le
moteur, observation de ses préparations sans inventer un appel au fournisseur.
Les identités, adresses, auteurs, montants, propriétés, historique et recharge
restent contrôlés. Le consentement n'est pas ajouté aux questions de faisabilité.

**Correctif commun d'une ligne, exception autorisée par le brief.** Le portage
révèle que G16 refuse sa propre réponse collective comme « mots non fixés ».
`repliques_moteur.reponse` joint désormais les émissions par un saut de ligne :
chaque rendu enregistré conserve sa frontière, même si le prochain locuteur
commence par une minuscule. Aucun contrôle de publication n'est assoupli.
Un test fonctionnel reproduit **deux erreurs avant correction**, au Relais et
à l'auberge ; il contrôle après correction les mots, l'absence de mutation des
objets/temps/journal, la scène et le monde rechargés. Aucun fichier de code
des lots 353, 354 ou 355 n'est édité.
Après correction : fichier d'audience **10/10**, nouveau test Relais/auberge
vert (**17,918 s**) ; la reprise du premier oracle de ce nouveau test autorise
le seul changement d'orientation déjà produit par l'ouïe, sans écarter aucun
autre champ d'objet ni aucune ressource.

**Mesures et reprise.** Bissection utile v2 : **12 653,186 s** ; compléments
MiMo/imports/fichiers entiers : **375,509 s**, deux travailleurs réduits au plus.
Les résultats invalides du premier lanceur (masquage de `tests` par
`tools/tests.py`) sont gardés et exclus des preuves. `jsonschema` déclaré dans
`requirements-mimo.txt` est installé dans les seuls artifacts du worktree ;
aucun saut MiMo ne sert de succès. Les reprises de portage sont conservées,
y compris les attentes secondaires révélées après la première assertion.
La validation finale porte sur **18 fichiers ciblés**, tous les tests livrés
et les répliques G16/G17/G18 voisines, sans suite complète, Luna ou banc.

**Réserves.** Le tableau classe conservativement les ruptures sans preuve de
changement voulu en régressions à traiter/arbitrer séparément : ouï-dire/337,
cause/330, plan différé perdu après discussion/U-C, lampe après la nuit/312,
couverture/341 et préfixe KV/G6. Les scènes déjà portées par d'autres lots
ne sont pas créditées ici. La suite globale n'est **pas déclarée verte** et
les trois incidents non reproduits demandent une vérification sur le PC fixe.

Bruts : `C:/Users/msics/donjon/artifacts/suite-rouge-356/` :
`attribution-qualifiee.json`, `certificat-bornes.json`, `assertions-harnais.json`,
`validation-harnais.json`, lanceurs et journaux ; résultats intermédiaires
du worktree copiés à la clôture. Fin attendue : **`fin-validation-finale.json`**.
