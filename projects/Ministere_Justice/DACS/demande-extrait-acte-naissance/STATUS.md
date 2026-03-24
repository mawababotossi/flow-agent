# Status — Demande d'Extrait d'Acte de Naissance

| Champ | Valeur |
|-------|--------|
| **Étape courante** | GATE:3b (Validation BPMN) |
| **Dernière étape complétée** | STEP:6 (BPMN) |
| **Prochaine étape** | STEP:7 (Plan de tests + Manuel utilisateur) — après validation GATE:3b |
| **Date de mise à jour** | 2026-03-24 |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `demande-extrait-acte-naissance-pipeline.yaml` | Produit |
| Cartographie AS-IS | `demande-extrait-acte-naissance-as-is.md` | Produit |
| Cartographie TO-BE | `demande-extrait-acte-naissance-to-be.md` | Produit |
| SRS | `srs-demande-extrait-acte-naissance.md` | Produit |
| Form.io principal | `formio-demande-extrait-acte-naissance.json` | Produit |
| Form.io correction | `formio-correction-demande-extrait-acte-naissance.json` | Produit |
| Form.io instruction | `formio-instruction-demande-extrait-acte-naissance.json` | Produit |
| Form.io validation | `formio-validation-demande-extrait-acte-naissance.json` | Produit |
| BPMN | — | Non commencé |
| Plan de tests | — | Non commencé |
| Manuel utilisateur | — | Non commencé |
| PV de recette | — | Non commencé |

## Blocages / Notes

- Service **hybride** : le retrait de l'extrait est obligatoirement physique (signature manuscrite + cachet de l'officier d'état civil — pas de signature électronique reconnue).
- Registres de l'état civil **non informatisés** dans la majorité des mairies : la recherche de l'acte est manuelle.
- Service **gratuit** pour la première délivrance — pas de circuit de paiement e-Gov.
- En cas d'acte introuvable : la procédure bascule vers le jugement supplétif au TGI (hors périmètre de ce service).
