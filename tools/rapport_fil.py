"""Rapport HTML du fil d'un banc : pour chaque tour, chaque appel (prompt, réponse) et chaque verdict.

  python tools/rapport_fil.py artifacts/bancs/<banc>.json

Le banc doit avoir été lancé avec --fil. Le rapport s'écrit à côté du JSON (même nom, .html).
"""
import html
import json
from pathlib import Path
import sys

STYLE = """
:root{--fond:#fbfaf7;--texte:#1d1c1a;--doux:#6b6760;--cadre:#e3dfd6;--bloc:#f2efe8;
--ok:#2f6f4f;--ko:#a33a2a;--avis:#8a5a00;--pense:#3f4f8f}
@media (prefers-color-scheme:dark){:root{--fond:#171614;--texte:#ece9e2;--doux:#9b968c;
--cadre:#34312c;--bloc:#211f1c;--ok:#7cc4a0;--ko:#f08a78;--avis:#e0b060;--pense:#a9b6f0}}
*{box-sizing:border-box}body{margin:0;padding:24px 16px 48px;background:var(--fond);color:var(--texte);
font:15px/1.5 system-ui,sans-serif}main{max-width:1000px;margin:auto}h1{font-size:1.4rem;margin:0 0 4px}
.meta{color:var(--doux);margin-bottom:24px}.tour{border:1px solid var(--cadre);border-radius:10px;
padding:14px 16px;margin:0 0 18px;background:var(--fond)}.saisie{font-weight:600;font-size:1.05rem}
.resume{color:var(--doux);font-size:.85rem;margin:2px 0 8px}.final{background:var(--bloc);border-radius:8px;
padding:8px 12px;white-space:pre-wrap}.etape{border-left:3px solid var(--cadre);margin:10px 0 0;padding:4px 0 4px 12px}
.etape.appel{border-color:var(--pense)}.etape.refus{border-color:var(--ko)}.etape.avis{border-color:var(--avis)}
.titre{font-weight:600}.ko{color:var(--ko)}.ok{color:var(--ok)}.avis{color:var(--avis)}.pense{color:var(--pense)}
details{margin:4px 0}summary{cursor:pointer;color:var(--doux)}pre{background:var(--bloc);border-radius:6px;
padding:8px 10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font:12px/1.45 ui-monospace,monospace;
max-height:480px;overflow-y:auto}
"""


def _pre(valeur):
    texte = valeur if isinstance(valeur, str) else json.dumps(valeur, ensure_ascii=False, indent=1)
    return "<pre>" + html.escape(texte) + "</pre>"


def _replie(titre, valeur, ouvert=False):
    return f"<details{' open' if ouvert else ''}><summary>{html.escape(titre)}</summary>{_pre(valeur)}</details>"


def _reponse(brut):
    """Réflexion résumée et appel d'outil d'une réponse brute (Claude ou OpenAI)."""
    morceaux = []
    if isinstance(brut, dict) and brut.get("tentatives"):
        return "".join(_replie(f"Appel fournisseur {a.get('numero')} — essai {a.get('essai', 0) + 1}", a.get('requete'))
                       + _reponse(a) + _replie("Événements complets", a.get('evenements', []))
                       for a in brut['tentatives'])
    if isinstance(brut, dict):
        morceaux.append(f"<div>arrêt : {html.escape(str(brut.get('stop_reason')))}"
                        f"{'' if brut.get('strict', True) else ' — schéma non strict'}</div>")
        blocs = brut.get("contenu", [])
    else:
        blocs = brut or []
    for b in blocs:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "transcription":
            morceaux.append("<div class='avis'>Réponse rendue en texte : relance pour la transcrire en appel.</div>")
        elif b.get("type") == "thinking":
            morceaux.append("<div class='pense'>Réflexion :</div>" + _pre(b.get("thinking") or "(non affichée)"))
        elif b.get("type") == "tool_use":
            morceaux.append("<div>Réponse (" + html.escape(str(b.get("name"))) + ") :</div>" + _pre(b.get("input")))
        elif b.get("type") == "function_call":
            try:
                arguments = json.loads(b.get("arguments") or "{}")
            except ValueError:
                arguments = b.get("arguments")
            morceaux.append("<div>Réponse (" + html.escape(str(b.get("name"))) + ") :</div>" + _pre(arguments))
        elif b.get("type") == "text" and b.get("text"):
            morceaux.append("<div>Texte hors outil :</div>" + _pre(b["text"]))
        elif b.get("type") == "message":
            for contenu in b.get("content", []):
                if contenu.get("type") == "output_text":
                    morceaux.append("<div>Message LLM (canal texte) :</div>" + _pre(contenu.get("text", "")))
        elif b.get("type") == "reasoning" and b.get("summary"):
            morceaux.append("<div class='pense'>Réflexion :</div>" + _pre(b["summary"]))
    return "".join(morceaux) or "<div class='ko'>Aucune réponse reçue.</div>"


def _etape(t):
    if t.get("etape") == "appel":
        u = t.get("usage") or {}
        cache = (u.get("cache_read_input_tokens") or (u.get("input_tokens_details") or {}).get("cached_tokens")
                 or (u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
        tete = (f"<div class='titre'>Appel {html.escape(t['fonction'])} — {t.get('secondes', 0)} s, "
                f"{u.get('input_tokens', u.get('prompt_tokens', 0))} tokens en entrée dont {cache} en cache, "
                f"{u.get('output_tokens', u.get('completion_tokens', 0))} en sortie</div>")
        if t.get("erreur"):
            tete += f"<div class='ko'>Erreur : {html.escape(t['erreur'])}</div>"
        corps = (_replie("Instructions", t.get("instructions", "")) + _replie("Entrée (faits, message)", t.get("entree"))
                 + _replie("Schéma de l'outil", t.get("schema")) + _reponse(t.get("brut")))
        return f"<div class='etape appel'>{tete}{corps}</div>"
    if t.get("etape") == "validation":
        return (f"<div class='etape refus'><div class='titre ko'>Refus du moteur (tentative {t.get('tentative', '?')})</div>"
                f"<div>{html.escape(str(t.get('obstacle', '')))}</div>{_replie('Retour transmis au modèle', {k: v for k, v in t.items() if k in ('attendu', 'consigne', 'qualification_requise')})}</div>")
    if t.get("etape") == "contrôle narratif":
        obstacles = "".join(f"<li>{html.escape(str(o.get('motif', '')))}<br><span class='resume'>{html.escape(str(o.get('texte', ''))[:300])}</span>"
                            + (f"<br><span class='resume'>attendu : {html.escape(str(o['attendu']))}</span>" if o.get("attendu") else "")
                            + "</li>"
                            for o in t.get("obstacles", []))
        return (f"<div class='etape refus'><div class='titre ko'>Contrôle de la prose (tentative {t.get('tentative', '?')})</div>"
                f"<ul>{obstacles}</ul></div>")
    if t.get("etape") == "couverture de l'action":
        rapport = t.get("rapport") or {}
        classe = "ok" if rapport.get("conforme") else "ko"
        return (f"<div class='etape avis'><div class='titre {classe}'>Contre-revue : "
                f"{'conforme' if rapport.get('conforme') else 'non conforme'}</div><div>{html.escape(str(rapport.get('motif', '')))}</div></div>")
    if t.get("erreur"):
        return f"<div class='etape refus'><div class='titre ko'>Erreur ({html.escape(str(t.get('etape')))})</div><div>{html.escape(t['erreur'])}</div></div>"
    return ""


def rendre(partie):
    tours = []
    for n, tour in enumerate(partie.get("tours", []), 1):
        if not isinstance(tour, dict) or not tour.get("appels"):
            continue
        resume = (f"{tour['appels']} appel(s), {tour.get('secondes', 0)} s"
                  + (f", {len(tour['refus'])} refus" if tour.get("refus") else "")
                  + (f", {len(tour['controle'])} objection(s) de la prose" if tour.get("controle") else "")
                  + (", repli" if tour.get("replis") else ""))
        fil = "".join(_etape(t) for t in tour.get("fil", [])) or "<div class='resume'>Fil non enregistré (banc lancé sans --fil).</div>"
        tours.append(f"<section class='tour'><div class='saisie'>{n}. « {html.escape(tour['saisie'])} »</div>"
                     f"<div class='resume'>{html.escape(resume)}</div><div class='final'>{html.escape(tour.get('texte', ''))}</div>{fil}</section>")
    return (f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Fil du banc — {html.escape(str(partie.get('script')))}</title><style>{STYLE}</style></head><body><main>"
            f"<h1>Fil du banc : {html.escape(str(partie.get('script')))}</h1>"
            f"<div class='meta'>Chaque tour confié au MJ : la saisie, le texte affiché, puis chaque tentative "
            f"(prompt, réponse) et le verdict du moteur ou des contrôles.</div>{''.join(tours)}</main></body></html>")


def ecrire(chemin_json):
    chemin = Path(chemin_json)
    sortie = chemin.with_suffix(".html")
    sortie.write_text(rendre(json.loads(chemin.read_text(encoding="utf-8"))), encoding="utf-8")
    return sortie


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        print(ecrire(argument))
