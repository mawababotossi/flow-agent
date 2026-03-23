#!/usr/bin/env python3
"""
Nettoyeur de fichiers Form.io JSON — Supprime les attributs par défaut inutiles.
Usage: python3 clean-formio-defaults.py <fichier.json> [--dry-run]
       python3 clean-formio-defaults.py --all [--dry-run]
"""
import json
import sys
import os
import glob

# Attributs scalaires par défaut à supprimer (clé: valeur par défaut)
DEFAULT_SCALARS = {
    "placeholder": "",
    "prefix": "",
    "suffix": "",
    "customClass": "",
    "tabindex": "",
    "tooltip": "",
    "description": "",
    "errorLabel": "",
    "labelPosition": "top",
    "hidden": False,
    "hideLabel": False,
    "disabled": False,
    "autofocus": False,
    "modalEdit": False,
    "multiple": False,
    "protected": False,
    "unique": False,
    "persistent": True,
    "clearOnHide": True,
    "refreshOn": "",
    "redrawOn": "",
    "dbIndex": False,
    "encrypted": False,
    "showCharCount": False,
    "showWordCount": False,
    "allowMultipleMasks": False,
    "allowCalculateOverride": False,
    "calculateServer": False,
    "customDefaultValue": "",
    "calculateValue": "",
    "dataGridLabel": False,
    "spellcheck": True,
    "mask": False,
    "inputFormat": "plain",
    "inputType": "text",
    "truncateMultipleSpaces": False,
    "tree": False,
    "lazyLoad": False,
    "tableView": False,
    "refreshOnChange": False,
    "customConditional": "",
    "nextPage": "",
    "validateWhenHidden": False,
    "saveOnEnter": False,
    "navigateOnEnter": False,
    "scrollToTop": False,
    "collapsible": False,
    "applyMaskOn": "change",
    "autocomplete": "",
    "case": "",
    "inputMask": "",
    "displayMask": "",
}

# Attributs objet/tableau vides à supprimer
DEFAULT_EMPTIES = {
    "tags": [],
    "properties": {},
    "attributes": {},
    "addons": [],
    "logic": [],
}

# Objets structurés par défaut à supprimer
DEFAULT_OBJECTS = {
    "overlay": {"style": "", "left": "", "top": "", "width": "", "height": ""},
    "widget": None,
}

# Conditional par défaut (toutes les variantes)
DEFAULT_CONDITIONALS = [
    {"show": None, "when": None, "eq": ""},
    {"show": None, "when": None, "eq": "", "json": ""},
]

# Attributs validate par défaut à nettoyer (supprimer les sous-clés inutiles)
VALIDATE_DEFAULTS = {
    "custom": "",
    "customPrivate": False,
    "strictDateValidation": False,
    "multiple": False,
    "unique": False,
    "json": "",
    "minLength": "",
    "maxLength": "",
    "pattern": "",
    "customMessage": "",
    "step": "any",
    "integer": "",
    "min": "",
    "max": "",
}


def clean_validate(validate_obj):
    """Nettoie l'objet validate en supprimant les sous-clés par défaut."""
    if not isinstance(validate_obj, dict):
        return validate_obj
    cleaned = {}
    for k, v in validate_obj.items():
        if k in VALIDATE_DEFAULTS and v == VALIDATE_DEFAULTS[k]:
            continue
        cleaned[k] = v
    # Si validate est complètement vide après nettoyage, ne pas le garder
    if not cleaned:
        return None
    # Si validate ne contient que required: false, ne pas le garder
    if cleaned == {"required": False}:
        return None
    return cleaned


def clean_component(comp):
    """Nettoie un composant Form.io en supprimant les attributs par défaut."""
    if not isinstance(comp, dict):
        return comp

    cleaned = {}
    for key, value in comp.items():
        # Supprimer les IDs auto-générés (e + hash)
        if key == "id" and isinstance(value, str) and (value.startswith("e") and len(value) >= 4):
            continue

        # Supprimer les scalaires par défaut
        if key in DEFAULT_SCALARS and value == DEFAULT_SCALARS[key]:
            continue

        # Supprimer les tableaux/objets vides par défaut
        if key in DEFAULT_EMPTIES and value == DEFAULT_EMPTIES[key]:
            continue

        # Supprimer widget null ou widget {"type": "input"}
        if key == "widget" and (value is None or value == {"type": "input"}):
            continue

        # Supprimer overlay par défaut
        if key == "overlay" and isinstance(value, dict):
            if all(value.get(k) == v for k, v in DEFAULT_OBJECTS["overlay"].items()):
                continue

        # Supprimer conditional par défaut
        if key == "conditional" and isinstance(value, dict):
            if value in DEFAULT_CONDITIONALS:
                continue

        # Nettoyer validate
        if key == "validate" and isinstance(value, dict):
            cleaned_validate = clean_validate(value)
            if cleaned_validate is not None:
                cleaned[key] = cleaned_validate
            continue

        # Nettoyer errors vide
        if key == "errors" and value == "":
            continue

        # Récurser dans les sous-composants
        if key == "components" and isinstance(value, list):
            cleaned[key] = [clean_component(c) for c in value]
        elif key == "columns" and isinstance(value, list):
            cleaned_cols = []
            for col in value:
                if isinstance(col, dict) and "components" in col:
                    col_copy = dict(col)
                    col_copy["components"] = [clean_component(c) for c in col.get("components", [])]
                    # Supprimer les attributs par défaut des colonnes
                    for dk in ["offset", "push", "pull"]:
                        if col_copy.get(dk) == 0:
                            del col_copy[dk]
                    if col_copy.get("size") == "md":
                        del col_copy["size"]
                    if "currentWidth" in col_copy and col_copy["currentWidth"] == col_copy.get("width"):
                        del col_copy["currentWidth"]
                    cleaned_cols.append(col_copy)
                else:
                    cleaned_cols.append(col)
            cleaned[key] = cleaned_cols
        elif key == "rows" and isinstance(value, list):
            # Pour les tables
            cleaned_rows = []
            for row in value:
                if isinstance(row, list):
                    cleaned_row = []
                    for cell in row:
                        if isinstance(cell, dict) and "components" in cell:
                            cell_copy = dict(cell)
                            cell_copy["components"] = [clean_component(c) for c in cell.get("components", [])]
                            cleaned_row.append(cell_copy)
                        else:
                            cleaned_row.append(cell)
                    cleaned_rows.append(cleaned_row)
                else:
                    cleaned_rows.append(row)
            cleaned[key] = cleaned_rows
        elif key == "values" and isinstance(value, list):
            # Nettoyer les valeurs radio/select
            cleaned_vals = []
            for v in value:
                if isinstance(v, dict):
                    v_clean = {vk: vv for vk, vv in v.items() if not (vk == "shortcut" and vv == "")}
                    cleaned_vals.append(v_clean)
                else:
                    cleaned_vals.append(v)
            cleaned[key] = cleaned_vals
        else:
            cleaned[key] = value

    return cleaned


def clean_root(data):
    """Nettoie la racine du JSON Form.io."""
    if isinstance(data, dict):
        # Nettoyer les composants racine
        if "components" in data and isinstance(data["components"], list):
            data["components"] = [clean_component(c) for c in data["components"]]

        # Supprimer les attributs racine par défaut
        root_defaults = {
            "access": [],
            "submissionAccess": [],
            "fieldMatchAccess": {},
            "fieldBasedResourceAccess": {},
        }
        for k, v in root_defaults.items():
            if data.get(k) == v:
                del data[k]

        if data.get("settings") == {}:
            del data["settings"]

    return data


def process_file(filepath, dry_run=False):
    """Traite un fichier JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    data = json.loads(original)
    cleaned = clean_root(data)
    output = json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n"

    original_lines = original.count("\n") + 1
    output_lines = output.count("\n") + 1
    reduction = round((1 - output_lines / original_lines) * 100)

    print(f"  {os.path.basename(filepath)}: {original_lines} → {output_lines} lignes (-{reduction}%)")

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

    return original_lines, output_lines


def main():
    dry_run = "--dry-run" in sys.argv
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if "--all" in sys.argv or len(sys.argv) == 1:
        files = []
        files += glob.glob(os.path.join(base, "exemples", "**", "*.json"), recursive=True)

        if not files:
            print("Aucun fichier trouvé.")
            return

        print(f"{'[DRY RUN] ' if dry_run else ''}Nettoyage de {len(files)} fichiers:\n")
        total_before = 0
        total_after = 0
        for f in sorted(files):
            before, after = process_file(f, dry_run)
            total_before += before
            total_after += after

        print(f"\nTotal: {total_before} → {total_after} lignes (-{round((1 - total_after/total_before)*100)}%)")
    else:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"Fichier non trouvé: {filepath}")
            sys.exit(1)
        process_file(filepath, dry_run)


if __name__ == "__main__":
    main()
