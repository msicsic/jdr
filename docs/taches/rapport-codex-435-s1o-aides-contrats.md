# Lot 435 — S1o, aides et connaissances de contrat

31 octobre 2026, PC fixe · `codex-s1o-aides-contrats` · base exacte `integration 364e8722`.
Vérifications finales enchaînées en fond ; ce rapport ne conclut pas encore à l'identité des empreintes.

**Invariant et code.** `memoire.py` possède les aides attendues, les deux moitiés des
rendez-vous, les mandats perçus, les traces de service et de restitution, avec leurs
validateurs historiques. Les lectures rendent des copies profondes et les admissions
copient leurs entrées. Les métiers gardent leurs décisions, délais, jets et conséquences.
Les mandats passent par le brouillon d'`agendas.evaluation` : une évaluation imbriquée
publie dans son parent et une interruption ne publie rien.

`agendas.en_cours` reste une façade compatible de la vue des propres engagements du
titulaire. L'archive exécutoire, l'allocation de séquence, les identités/versions,
l'accord initial et la clôture réelle restent sous l'autorité d'`agendas`. La mémoire
résout une référence connue dans ces archives sans ajouter de registre persistant.
`issues_connues` exige l'acquittement du titulaire ; ce marqueur ne prête aucune
connaissance au bénéficiaire. Les créances non annoncées restent exclues des dettes
connues ; les permissions de prêt passent par la vue du participant. Aucun stockage
historique ni format de sauvegarde n'est changé.

**Contrôle et tests.** Inventaires fermés par expression pour les suivis subjectifs et
les archives mécaniques ; contre-épreuves d'alias, clés indirectes, méthodes détachées,
écritures et retours. Les seules expressions subjectives restantes hors porte sont
des dictionnaires homonymes de diagnostic. Les sondes actives passent aussi par les vues ;
l'audit charge sa porte de lecture pour observer une référence antérieure à cette API.
Les anciens inventaires gardent leurs exceptions exactes, sans élargissement de portée.

Les nouveaux tests couvrent copies imbriquées, admissions, corruptions, références
après saturation des 40 épisodes, évaluations imbriquées/interrompues et clôture réelle
distante non connue. Deux chaînes réelles (Bram/Josse dans la mine et Gorm/Aubin au Relais)
comparent un laps entier et découpé, l'état complet et l'ordre JSON, le rendu, la scène
et les émissions après rechargement. Les fichiers historiques des contrats datés
conservent leurs cas de livraison d'huile et de fermeture du garde-manger.
Première passe : **56 tests verts** sur appel, rendez-vous, mandat et contrats datés.
Passes élargies brutes : 237 tests, puis 78 (fichiers communs compris) ; les **8 nouvelles
épreuves S1o**, les 6 tests du socle d'agendas et les 43 tests des sondes sont verts.
Les autres rouges des familles appel/aide/agenda sont en attribution sur la base exacte.
Sur la base, le rouge annoncé du gardien est confirmé : l'oracle omet `suite_conditionnelle`.
Il n'est pas réécrit. Deux erreurs des nouvelles fixtures sont corrigées : réviser
l'issue sans changer l'identité du mandat, et attendre le refus public `ErreurMonde`.
Le garde d'autorité d'`agendas` admet exactement les cinq expressions portées dans
la mémoire (fonction, expression, lecture/écriture), sans exemption globale de porte.
Résultat final : `tests-cibles.json`, puis `tests-final.json` et `tests-socles-final.json`.

**Empreintes.** Enchaînées après validation ciblée : 2 h × graines 1985/7/42/2024 × Relais/mine/auberge/crue,
référence exacte `364e8722`, cache partagé, deux travailleurs réduits au plus. Aucun
temps ne sera comparé au cache. Le contrôle court (0,02 h, Relais/7) est identique.
Le premier lanceur a échoué sur son import (`tools/tests.py` masquait `tests`),
avant les empreintes. `reprise-definitive.py` reprend les étapes manquantes sans
rejouer les passes achevées ; il exige des rouges identiques à la base, puis des
contrôles après fusion verts. **Fin attendue : `fin-reprise.json`**, écrit en dernier.
Les échecs de lancement restent dans `fin.json` et `fin-tests.json`. Pas de suite
complète ni Luna ; aucun résultat d'empreintes 2 h n'est encore revendiqué.

**Limites et voisinage.** Politiques historiques conservées ; le contrôle AST est
syntaxique local, sans preuve de tous les flux interprocéduraux Python. La vue d'issues
n'est pas un nouveau compte subjectif complet du bénéficiaire (S2). Recouvrement avec
434 limité à deux fonctions d'`echanges.py`, enregistrement d'aide et abandon reçu ;
aucun changement de `dialogues.py`, `compilation.py`, `mj.py` ou `portee_narrative.py`.
`origin/integration b21d4656` fusionnée par `c22a8d78` : conflit documentaire seul,
K2 modifie une autre fonction d'`echanges.py`. L'exception exacte du schéma public
de K2 dans l'inventaire est actualisée, sans accès au stockage ajouté. Les empreintes
restent attachées à `ef9154e6` avant fusion ; les contrôles après fusion incluent
les inventaires, les huit épreuves S1o et `test_negociation_aide`. Bruts :
`C:/Users/msics/donjon/artifacts/s1o-435/`.

**Publication.** Git local reste sans authentification utilisable. Après un premier
envoi d'arbre rejeté sans motif, le connecteur accepte l'envoi des objets séparés ;
publication de la branche par cette voie, avec vérification de l'arbre distant.
