# Status — Demande de Casier Judiciaire (Bulletin n°3)

| Champ | Valeur |
|-------|--------|
| **Étape courante** | GATE:3b (Validation BPMN) |
| **Dernière étape complétée** | STEP:6 (BPMN) |
| **Prochaine étape** | STEP:7 (Plan de tests + Manuel utilisateur) — après validation GATE:3b |
| **Date de mise à jour** | 2026-03-24 |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `demande-casier-judiciaire-pipeline.yaml` | Produit |
| Cartographie AS-IS | `demande-casier-judiciaire-as-is.md` | Produit |
| Cartographie TO-BE | `demande-casier-judiciaire-to-be.md` | Produit |
| SRS | `srs-demande-casier-judiciaire.md` | Produit |
| Form.io principal | `formio-demande-casier-judiciaire.json` | Non commencé |
| Form.io correction | `formio-correction-demande-casier-judiciaire.json` | Non commencé |
| Form.io paiement | `formio-paiement-demande-casier-judiciaire.json` | Non commencé |
| Form.io instruction | `formio-instruction-demande-casier-judiciaire.json` | Non commencé |
| BPMN | `bpmn-demande-casier-judiciaire.bpmn` | Produit — 6 messages, 5 messageFlows, P1-P4 appliqués |
| Plan de tests | — | Non commencé |
| Manuel utilisateur | — | Non commencé |
| PV de recette | — | Non commencé |

## Blocages / Notes

- Service **hybride** : le retrait du bulletin est obligatoirement physique (signature manuscrite + cachet humide — pas de signature électronique reconnue).
- Fichier des condamnations **non informatisé** : pas d'intégration Odoo/API possible pour la vérification. L'agent consulte manuellement le fichier papier.
- Frais de délivrance : 2 000 FCFA (fixe) → service payant via e-Gov.
