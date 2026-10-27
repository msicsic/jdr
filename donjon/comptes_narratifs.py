"""Rendu des comptes typés publics et garde locale de leur domaine narratif.

La preuve exacte porte sur les phrases recalculées, jamais sur un drapeau du MJ.
La garde lexicale est conservatrice et ne constitue pas une grammaire du français.
"""
import re

from .monde import normaliser
from .refus import audit


def phrases(faits):
    """Une phrase par compte de l'issue ; aucun solde privé ni nom déduit."""
    def personne(ref):
        if ref == "joueur":
            return "toi"
        public = faits.get("interlocuteurs", {}).get(ref, {})
        public = public or faits.get("objet:" + ref, {})
        return public.get("nom", "une personne")

    textes = []
    for c in faits.get("comptes", {}).get("issue", []):
        # Les comptes entre tiers ne sont jamais racontés au joueur.
        if "joueur" not in (c["debiteur"], c["creancier"]):
            continue
        de, vers = personne(c["debiteur"]), personne(c["creancier"])
        if c.get("objet"):
            objet = faits.get("objet:" + c["objet"], {})
            bien = objet.get("nom", "le bien convenu")
            quantite = f"{c['montant']} × {bien}"
        else:
            quantite = f"{c['montant']} pièce{'s' if c['montant'] != 1 else ''}"
        if c["etat"] == "rendu":
            texte = f"Remise effectuée : de {de} à {vers}, {quantite}."
        elif c["etat"] == "du":
            texte = f"Reste dû : de {de} à {vers}, {quantite}."
        elif c["etat"] == "absent":
            texte = (f"Aucune dette de {de} envers {vers} pour "
                     + (bien if c.get("objet") else "les pièces") + ".")
        else:
            # Une forme nouvelle ne doit jamais disparaître silencieusement.
            from .monde import ErreurMonde
            raise ErreurMonde("Ce compte ne peut pas encore être raconté.",
                              f"comptes.issue.etat : reçu {c['etat']!r} ; du, rendu ou absent")
        textes.append(texte)
    return list(dict.fromkeys(textes))


def completer(texte, faits):
    from .narration import segments
    presents = set(segments(texte))
    return " ".join([texte.strip(), *(p for p in phrases(faits)
                                     if not set(segments(p)) <= presents)]).strip()


# Domaine commun des comptes, sans personnage, objet ni formulation de scénario.
# Les verbes de mouvement ordinaires restent du ressort de l'audit mécanique.
DOMAINE = re.compile(
    r"\b(?:dettes?|creances?|debiteur|creancier|rembours\w*|paiement\w*|"
    r"pay\w*|paie\w*|livr\w*|redev\w*|dues?)\b"
    r"|\b(?:\d+|une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|vingt|cent|"
    r"aucunes?|les|des|ces|mes|tes|ses)\s+pieces?\b"
    r"|\b(?:me|te|lui|leur|nous|vous)\s+(?:dois|doit|devons|devez|doivent)\b")


def controler(texte, faits, partie="texte"):
    from .narration import segments, textes_etablis
    etablis = textes_etablis(faits)
    passages = segments(texte)
    obstacles = []
    for i, passage in enumerate(passages):
        if passage not in etablis and DOMAINE.search(normaliser(passage)):
            obstacles.append(audit(
                "Les comptes sont racontés par le moteur.",
                "prose libre sans montant, dette ni transfert ; comptes.issue : "
                + str(faits.get("comptes", {}).get("issue", [])),
                partie=partie, segment=i, texte=passage, recu=passage))
    for phrase in dict.fromkeys(s for p in phrases(faits) for s in segments(p)):
        if phrase not in passages:
            obstacles.append(audit("Le texte moteur d'un compte manque.",
                f"comptes.issue : conserver exactement {phrase!r}",
                partie=partie, segment=0, texte=texte, recu=texte))
    return obstacles
