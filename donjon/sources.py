"""Résolution des sources dans le seul dossier public transmis au MJ."""
import re


def resoudre_sources(sources, faits):
    """Clés exactes, chemins existants et identifiants de fiches, sans inférence.

    Une référence partagée par plusieurs rubriques n'en désigne aucune seule.
    Une fiche de premier niveau objet:<id> est en revanche une source explicite.
    Le dossier archivé suffit à refaire cette résolution à l'enregistrement.
    """
    identifiants = {}

    def indexer(valeur, racine):
        if isinstance(valeur, dict):
            if isinstance(valeur.get('id'), str):
                identifiants.setdefault(valeur['id'], set()).add(racine)
            for element in valeur.values():
                indexer(element, racine)
        elif isinstance(valeur, list):
            for element in valeur:
                indexer(element, racine)

    def chemin_existe(valeur, chemin):
        if not chemin:
            return True
        if isinstance(valeur, dict):
            for cle in valeur:
                if chemin == cle:
                    return True
                if chemin.startswith(cle + '.') and chemin_existe(valeur[cle], chemin[len(cle) + 1:]):
                    return True
                if chemin.startswith(cle + '[') and chemin_existe(valeur[cle], chemin[len(cle):]):
                    return True
        elif isinstance(valeur, list):
            indice = re.fullmatch(r'\[(\d+)\](?:\.(.+)|(\[.*))?', chemin)
            if indice:
                i = int(indice[1])
                return i < len(valeur) and chemin_existe(valeur[i], indice[2] or indice[3] or '')
            tete, _, suite = chemin.partition('.')
            if tete.isdecimal():
                i = int(tete)
                return i < len(valeur) and chemin_existe(valeur[i], suite)
            fiches = [v for v in valeur if isinstance(v, dict) and v.get('id') == tete]
            return len(fiches) == 1 and chemin_existe(fiches[0], suite)
        return False

    for cle, valeur in faits.items():
        indexer(valeur, cle)
    resolues, inconnues = [], []
    for source in sources:
        cle = source if source in faits else None
        if cle is None:
            candidates = [racine for racine, valeur in faits.items()
                if (source.startswith(racine + '.') and chemin_existe(valeur, source[len(racine) + 1:]))
                or (source.startswith(racine + '[') and chemin_existe(valeur, source[len(racine):]))]
            if candidates:
                cle = max(candidates, key=len)
            elif 'objet:' + source in faits:
                cle = 'objet:' + source
            elif len(identifiants.get(source, ())) == 1:
                cle = next(iter(identifiants[source]))
        destination = resolues if cle is not None else inconnues
        valeur = cle if cle is not None else source
        if valeur not in destination:
            destination.append(valeur)
    return resolues, inconnues
