# Lot 257 — préalable au choix faire ou confier

Branche `codex-faire-ou-confier`, **non fusionnée**, base `integration
5e08b76`, 28 octobre 2026. Commit de brief vérifié par `git log -1`.
**Arrêt au constat prévu par le brief** : le choix autonome n'est pas
implémenté ; aucun fichier du moteur, scénario ou MJ modifié.

Le contrat manquant est un devis du plan d'un acteur **vu par un autre**.
`agendas.devis_mandat` copie le monde, publie un enfant hypothétique avec
`confier`, puis appelle `planifier` comme titulaire. C'est le bon devis pour
le jugement réel du mandaté (256), mais pas pour le classement du mandant.
La copie conserve les connaissances privées du titulaire. `_amener` lit ses
croyances, ses aides et ses refus ; la transmission vérifie son contenu cru.
Changer seulement sa position de départ ne supprime donc pas ces lectures.

Autres dépendances à projeter : `planification.Vue` prend les salles depuis
le lieu réel de l'acteur ; `depart` prend son lieu et ses possessions réels.
Les coûts lisent ses besoins et son caractère, `agendas.poids` ses liens.
`relations.autorite_mandat` exprime l'autorité reconnue par le destinataire,
pas celle que le mandant croit avoir. `chance_demande` offre déjà une
estimation du demandeur sans lire l'autre esprit ; elle ne fournit pas
la projection du trajet, des moyens et de l'autorité manquante.

**Preuve exécutée sur la base inchangée**, deux profils de test du lot 256 :
Gorm (`marchand`) → Aubin → Brune (`amener`, chambre de la cloche), puis
information à Ilse (`informer`). Retirer uniquement la croyance privée
d'Aubin sur le lieu de la cible conserve exactement l'esprit de Gorm et
tous les objets du monde. Le devis passe pourtant de **0,225 à impossible**,
puis de **0,166667 à impossible**. Les deux devis initiaux sont purs.
Chaque variante est sauvegardée et rechargée : état complet, rendu joueur,
scène perçue et résultat du devis identiques avant/après recharge.
Ce n'est pas un défaut du jugement réel ; réutiliser ce devis pour classer
les candidats introduirait une lecture privée injustifiée.

**Lot neutre préalable proposé, un invariant** : le devis d'un acteur vu
par un observateur ne dépend que des données autorisées de l'observateur.
Introduire un contexte explicite séparant observateur et acteur dans les
devis sociaux : départ et possessions crus, connaissances accessibles,
refus/relations de l'observateur, politique explicite d'estimation pour les
capacités ou préférences inconnues. Ne pas recopier l'esprit du mandant en
le présentant comme celui du tiers. Garder intact le devis réel du 256 et
ne raccorder aucun choix autonome dans ce préalable. Inclure toutes les
lectures projetées dans `_entrees`, avec séparation des caches réel/estimé.
Épreuves : les deux charges ci-dessus, déplacement réel hors perception,
variation du savoir privé, des possessions et des liens privés sans effet ;
variation des croyances de l'observateur avec effet ; recharge monde/rendu,
pureté et empreintes neutres. Reprendre ensuite le choix du sous-but et le
choix du mandataire dans deux fonctions distinctes à appel unique.

Bruts : `C:/Users/msics/donjon/artifacts/confier-257/diagnostic_257.py`
et `diagnostic.json`. Rejouer le script depuis la racine de ce worktree
avec le Python du dépôt principal (pas de `.venv` local). La première
exécution a rencontré les permissions des temporaires Python ; la preuve
a ensuite réussi hors bac à sable, sans sauvegarde de partie utilisateur.
Ni suite complète, Luna, banc rapide ni mesure de coût : arrêt avant tout
changement de comportement, conformément à la clause du brief. Aucun
calcul actif. La stabilité du choix, les refus sans boucle, les laps
découpés et les vingt nuits ne sont **pas validés** par ce diagnostic.
