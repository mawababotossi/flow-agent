# Status — Demande de Casier Judiciaire (Bulletin n°3)

| Champ | Valeur |
|-------|--------|
| **Étape courante** | GATE:1 (Validation périmètre) |
| **Dernière étape complétée** | STEP:3 (Cartographie TO-BE) |
| **Prochaine étape** | STEP:4 (SRS) — après validation GATE:1 |
| **Date de mise à jour** | 2026-03-24 |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `demande-casier-judiciaire-pipeline.yaml` | Produit |
| Cartographie AS-IS | `demande-casier-judiciaire-as-is.md` | Produit |
| Cartographie TO-BE | `demande-casier-judiciaire-to-be.md` | Produit |
| SRS | `srs-demande-casier-judiciaire.md` | Non commencé |
| Form.io principal | `formio-demande-casier-judiciaire.json` | Non commencé |
| Form.io correction | `formio-correction-demande-casier-judiciaire.json` | Non commencé |
| Form.io paiement | `formio-paiement-demande-casier-judiciaire.json` | Non commencé |
| Form.io instruction | `formio-instruction-demande-casier-judiciaire.json` | Non commencé |
| BPMN | `bpmn-demande-casier-judiciaire.bpmn` | Non commencé |
| Plan de tests | — | Non commencé |
| Manuel utilisateur | — | Non commencé |
| PV de recette | — | Non commencé |

## Blocages / Notes

- Service **hybride** : le retrait du bulletin est obligatoirement physique (signature manuscrite + cachet humide — pas de signature électronique reconnue).
- Fichier des condamnations **non informatisé** : pas d'intégration Odoo/API possible pour la vérification. L'agent consulte manuellement le fichier papier.
- Frais de délivrance : 2 000 FCFA (fixe) → service payant via e-Gov.
