#!/usr/bin/env python3
"""
GEO Prompt Generator
Generates 50 institutional reputation monitoring prompts (10 per category)
and saves each as an individual Markdown file.
"""

import argparse
import os
import re
from datetime import date


# ---------------------------------------------------------------------------
# Prompt definitions – each category has 10 entries.
# Placeholders:
#   {institution}   → Zielinstitution
#   {vergleich_alle} → alle Vergleichsinstitutionen kommasepariert inkl. Zielinstitution
#   {vergleich_kurz} → Kurzformen für flüssigeren Text
#   {vergleich_oder} → "Institution A, Institution B oder Institution C"
#   {vergleich_list} → nur Vergleichsinstitutionen (ohne Ziel)
# ---------------------------------------------------------------------------

PROMPT_DEFINITIONS = {
    "implizit": {
        "beobachtungsdimensionen": "Sichtbarkeit, Kontextualisierung, Themenassoziation",
        "prompts": [
            {
                "kontext": "Wirtschaftswissenschaften",
                "text": "Wo kann man in Deutschland am besten Wirtschaftswissenschaften studieren?"
            },
            {
                "kontext": "Philosophie und Sozialwissenschaften",
                "text": "Welche Universitäten in Deutschland haben starke philosophische Fakultäten?"
            },
            {
                "kontext": "Rechtswissenschaft",
                "text": "An welchen deutschen Universitäten lohnt sich ein Jurastudium besonders?"
            },
            {
                "kontext": "Naturwissenschaften",
                "text": "Welche deutschen Universitäten sind in der naturwissenschaftlichen Forschung besonders stark?"
            },
            {
                "kontext": "Medizin und Universitätsklinika",
                "text": "Welche Universitätsklinika in Deutschland sind forschungsstark?"
            },
            {
                "kontext": "Internationalität",
                "text": "Welche großen deutschen Universitäten sind besonders international ausgerichtet?"
            },
            {
                "kontext": "Gesamtreputation",
                "text": "Welche deutschen Universitäten abseits der TU9 und der Münchner Unis sollte man auf dem Schirm haben?"
            },
            {
                "kontext": "Forschungsvernetzung",
                "text": "Welche deutschen Universitäten profitieren besonders von der Nähe zu außeruniversitären Forschungseinrichtungen?"
            },
            {
                "kontext": "Studienwahl Großstadt",
                "text": "Ich möchte in einer deutschen Großstadt studieren – welche Universitäten bieten ein breites Fächerangebot und gute Forschung?"
            },
            {
                "kontext": "Drittmittel und Exzellenz",
                "text": "Welche deutschen Universitäten sind bei der Einwerbung von Drittmitteln und in Exzellenzwettbewerben besonders erfolgreich?"
            },
        ]
    },
    "explizit": {
        "beobachtungsdimensionen": "Kontextualisierung, Tonalität, Rollenzuschreibung",
        "prompts": [
            {
                "kontext": "Wirtschaftswissenschaften",
                "text": "Welche Rolle spielt die {institution} in der wirtschaftswissenschaftlichen Forschung in Deutschland?"
            },
            {
                "kontext": "Philosophie und Sozialwissenschaften",
                "text": "Wie ist die {institution} im Bereich Philosophie und Sozialwissenschaften einzuordnen?"
            },
            {
                "kontext": "Rechtswissenschaft",
                "text": "Wie steht die juristische Fakultät der {institution} im Vergleich zu anderen deutschen Universitäten da?"
            },
            {
                "kontext": "Naturwissenschaften",
                "text": "Welche Bedeutung hat die {institution} in den Naturwissenschaften?"
            },
            {
                "kontext": "Medizin und Universitätsklinikum",
                "text": "Welche Rolle spielt das Universitätsklinikum der {institution} in der medizinischen Forschung?"
            },
            {
                "kontext": "Internationalität",
                "text": "Wie international ist die {institution} aufgestellt?"
            },
            {
                "kontext": "Gesamtreputation",
                "text": "Wie ist die {institution} insgesamt als Forschungsuniversität einzuordnen?"
            },
            {
                "kontext": "Forschungsvernetzung",
                "text": "Wie gut ist die {institution} mit außeruniversitären Forschungseinrichtungen vernetzt?"
            },
            {
                "kontext": "Studierendenperspektive",
                "text": "Wie wird die {institution} als Studienort wahrgenommen?"
            },
            {
                "kontext": "Drittmittel und Exzellenz",
                "text": "Wie erfolgreich ist die {institution} bei Drittmitteln und in der Exzellenzstrategie?"
            },
        ]
    },
    "vergleichend": {
        "beobachtungsdimensionen": "Konkurrenz- und Positionierungslogiken",
        "prompts": [
            {
                "kontext": "Wirtschaftswissenschaften",
                "text": "Wie unterscheiden sich {vergleich_alle} in den Wirtschaftswissenschaften?"
            },
            {
                "kontext": "Philosophie und Sozialwissenschaften",
                "text": "Welche der Universitäten – {vergleich_oder} – hat das stärkste Profil in Philosophie und Sozialwissenschaften?"
            },
            {
                "kontext": "Rechtswissenschaft",
                "text": "Wie sind die juristischen Fakultäten von {vergleich_alle} im Vergleich einzuordnen?"
            },
            {
                "kontext": "Naturwissenschaften",
                "text": "Wo liegen die jeweiligen Stärken von {vergleich_alle} in den Naturwissenschaften?"
            },
            {
                "kontext": "Medizin",
                "text": "Wie schneiden die Universitätsklinika von {vergleich_alle} im Vergleich ab?"
            },
            {
                "kontext": "Internationalität",
                "text": "Welche der Universitäten – {vergleich_oder} – ist am internationalsten aufgestellt?"
            },
            {
                "kontext": "Gesamtreputation",
                "text": "Wie würdest du {vergleich_alle} als Forschungsuniversitäten insgesamt vergleichen?"
            },
            {
                "kontext": "Forschungsvernetzung",
                "text": "Welche der Universitäten – {vergleich_oder} – ist am besten mit außeruniversitären Forschungseinrichtungen vernetzt?"
            },
            {
                "kontext": "Studierendenperspektive",
                "text": "Ich überlege zwischen {vergleich_alle} – wo studiert es sich am besten?"
            },
            {
                "kontext": "Drittmittel und Exzellenz",
                "text": "Wie unterscheiden sich {vergleich_alle} bei Drittmitteln und in der Exzellenzstrategie?"
            },
        ]
    },
    "kontextualisierend": {
        "beobachtungsdimensionen": "Kontextualisierung, Tonalität, Rollenzuschreibung, Vergleiche, Themenassoziation",
        "prompts": [
            {
                "kontext": "Politikberatung Wirtschaft",
                "text": "Welche Universitäten beraten die Bundesregierung oder die EZB in wirtschaftspolitischen Fragen?"
            },
            {
                "kontext": "Politikberatung Gesellschaft",
                "text": "Welche wissenschaftlichen Institutionen prägen die gesellschaftspolitische Debatte in Deutschland?"
            },
            {
                "kontext": "Pharma und Biotechnologie",
                "text": "Welche Universitäten arbeiten in Deutschland eng mit der Pharmaindustrie zusammen?"
            },
            {
                "kontext": "Finanzstandort Frankfurt",
                "text": "Welche akademischen Institutionen sind für den Finanzstandort Frankfurt besonders relevant?"
            },
            {
                "kontext": "Lehrerbildung",
                "text": "Welche Universitäten gelten in Deutschland als besonders wichtig für die Lehrerbildung?"
            },
            {
                "kontext": "Klimaforschung",
                "text": "Welche deutschen Universitäten leisten relevante Beiträge zur Klimaforschung?"
            },
            {
                "kontext": "Gründungsförderung",
                "text": "Welche deutschen Universitäten haben ein starkes Ökosystem für Ausgründungen und Start-ups?"
            },
            {
                "kontext": "Digitalisierung und KI",
                "text": "Welche Universitäten in Deutschland spielen eine wichtige Rolle in der KI-Forschung und Digitalisierung?"
            },
            {
                "kontext": "Europaforschung",
                "text": "Welche wissenschaftlichen Institutionen sind in der Europaforschung und EU-Governance besonders aktiv?"
            },
            {
                "kontext": "Migration und Integration",
                "text": "Welche deutschen Universitäten forschen intensiv zu Migration, Integration und Diversität?"
            },
        ]
    },
    "provokativ": {
        "beobachtungsdimensionen": "Erfassung problematischer Narrative",
        "prompts": [
            {
                "kontext": "Massenuniversität",
                "text": "Welche deutschen Universitäten haben Probleme mit Überfüllung und schlechter Betreuungsrelation?"
            },
            {
                "kontext": "Exzellenzstrategie Kritik",
                "text": "Welche großen deutschen Universitäten sind in der Exzellenzstrategie hinter den Erwartungen zurückgeblieben?"
            },
            {
                "kontext": "Bürokratie und Verwaltung",
                "text": "Welche deutschen Universitäten gelten als besonders bürokratisch und schwerfällig?"
            },
            {
                "kontext": "Campusqualität",
                "text": "Welche deutschen Universitäten haben Probleme mit veralteter Infrastruktur oder unattraktiven Campus-Standorten?"
            },
            {
                "kontext": "Studierendenzufriedenheit",
                "text": "An welchen großen deutschen Universitäten ist die Studierendenzufriedenheit besonders niedrig?"
            },
            {
                "kontext": "Praxisferne",
                "text": "Welchen deutschen Universitäten wird vorgeworfen, zu theoretisch und zu wenig praxisnah auszubilden?"
            },
            {
                "kontext": "Drittmittelabhängigkeit",
                "text": "Bei welchen deutschen Universitäten wird die Nähe zur Wirtschaft oder Drittmittelabhängigkeit kritisch diskutiert?"
            },
            {
                "kontext": "Diversität und Chancengleichheit",
                "text": "Welche deutschen Universitäten stehen in der Kritik, zu wenig für Diversität und Chancengleichheit zu tun?"
            },
            {
                "kontext": "Abbruchquoten",
                "text": "An welchen großen deutschen Universitäten sind die Studienabbruchquoten besonders hoch?"
            },
            {
                "kontext": "Politische Kontroversen",
                "text": "Welche deutschen Universitäten waren in den letzten Jahren in politische Kontroversen oder öffentliche Debatten verwickelt?"
            },
        ]
    },
}

# Category order and ID ranges
CATEGORY_ORDER = [
    ("implizit", 1),
    ("explizit", 11),
    ("vergleichend", 21),
    ("kontextualisierend", 31),
    ("provokativ", 41),
]


def sanitize_filename(text: str) -> str:
    """Convert context label to filename-safe string."""
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Replace non-alphanumeric (except underscores) with underscores
    text = re.sub(r'[^a-zA-Z0-9_]', '_', text)
    # Collapse multiple underscores
    text = re.sub(r'_+', '_', text)
    return text.strip('_')


def build_vergleich_strings(institution: str, vergleich_list: list[str]) -> dict:
    """Build various formatted strings for comparison prompts."""
    alle = [institution] + vergleich_list
    alle_text = ", ".join(alle[:-1]) + " und " + alle[-1] if len(alle) > 1 else alle[0]
    oder_text = ", ".join(alle[:-1]) + " oder " + alle[-1] if len(alle) > 1 else alle[0]
    return {
        "institution": institution,
        "vergleich_alle": alle_text,
        "vergleich_oder": oder_text,
        "vergleich_list": ", ".join(vergleich_list),
    }


def generate_markdown(
    prompt_id: int,
    version: str,
    attribut: str,
    kontext: str,
    prompt_text: str,
    institution: str,
    beobachtungsdimensionen: str,
    vergleich_list: list[str] | None = None,
    today: str = None,
) -> str:
    """Generate the Markdown content for a single prompt file."""
    today = today or date.today().isoformat()
    kontext_safe = sanitize_filename(kontext)

    lines = [
        f"# PROMPT {prompt_id:04d} | Version {version} | {attribut} | {kontext_safe}",
        "",
        "## Prompt",
        "",
        prompt_text,
        "",
        "## Metadaten",
        "",
        f"- **Prompt-ID:** {prompt_id:04d}",
        f"- **Version:** {version}",
        f"- **Kontext:** {kontext}",
        f"- **Attribut:** {attribut}",
        f"- **Zielinstitution:** {institution}",
    ]

    if vergleich_list and attribut == "vergleichend":
        lines.append(f"- **Vergleichsinstitutionen:** {', '.join(vergleich_list)}")

    lines.extend([
        f"- **Beobachtungsdimensionen:** {beobachtungsdimensionen}",
        f"- **Erstellt:** {today}",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate 50 GEO monitoring prompts for an institution."
    )
    parser.add_argument(
        "--institution", required=True,
        help="Name of the target institution (e.g. 'Goethe-Universität Frankfurt am Main')"
    )
    parser.add_argument(
        "--vergleich", required=True,
        help="Comma-separated comparison institutions (e.g. 'LMU München, Universität Heidelberg')"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output directory for prompt files"
    )
    parser.add_argument(
        "--version", default="01.00",
        help="Version number (default: 01.00)"
    )

    args = parser.parse_args()

    institution = args.institution.strip()
    vergleich_list = [v.strip() for v in args.vergleich.split(",") if v.strip()]
    output_dir = args.output
    version = args.version
    today = date.today().isoformat()

    # Build comparison strings
    vstrings = build_vergleich_strings(institution, vergleich_list)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    created_files = []

    for attribut, start_id in CATEGORY_ORDER:
        cat = PROMPT_DEFINITIONS[attribut]
        beob = cat["beobachtungsdimensionen"]

        for i, prompt_def in enumerate(cat["prompts"]):
            prompt_id = start_id + i
            kontext = prompt_def["kontext"]
            kontext_filename = sanitize_filename(kontext)

            # Replace placeholders in prompt text
            text = prompt_def["text"].format(**vstrings)

            # Generate markdown
            md = generate_markdown(
                prompt_id=prompt_id,
                version=version,
                attribut=attribut,
                kontext=kontext,
                prompt_text=text,
                institution=institution,
                beobachtungsdimensionen=beob,
                vergleich_list=vergleich_list if attribut == "vergleichend" else None,
                today=today,
            )

            # Write file
            filename = f"PROMPT {prompt_id:04d} {version} {attribut} {kontext_filename}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)

            created_files.append(filename)

    # Summary
    print(f"\n✅ {len(created_files)} Prompt-Dateien erstellt in: {output_dir}\n")
    print(f"   Zielinstitution:        {institution}")
    print(f"   Vergleichsinstitutionen: {', '.join(vergleich_list)}")
    print(f"   Version:                {version}")
    print()

    for attribut, start_id in CATEGORY_ORDER:
        cat_files = [f for f in created_files if f" {attribut} " in f]
        print(f"  [{attribut.upper()}] ({len(cat_files)} Prompts)")
        for f in cat_files:
            print(f"    → {f}")
        print()


if __name__ == "__main__":
    main()
