# Status — Demande de Diplôme du CFA

| Champ | Valeur |
|-------|--------|
| **Étape courante** | STEP:7 — BPMN |
| **Dernière étape complétée** | STEP:7 — BPMN |
| **Prochaine étape** | GATE:2 — Validation SRS + BPMN |
| **Date de mise à jour** | 2026-03-28 |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `demande-diplome-cfa-pipeline.yaml` | Produit |
| Cartographie AS-IS | `demande-diplome-cfa-as-is.md` | En cours |
| Cartographie TO-BE | `demande-diplome-cfa-to-be.md` | Non commencé |
| SRS | `srs-demande-diplome-cfa.md` | Non commencé |
| Formulaire principal JSON | `formio-demande-diplome-cfa.json` | Non commencé |
| Formulaire correction JSON | `formio-correction-demande-diplome-cfa.json` | Non commencé |
| Formulaire paiement JSON | `formio-paiement-demande-diplome-cfa.json` | Non commencé |
| Formulaire instruction agent JSON | `formio-instruction-demande-diplome-cfa.json` | Non commencé |
| BPMN | `bpmn-demande-diplome-cfa.bpmn` | Produit |

## Blocages / Notes
- Service avec deux parcours distincts : demande initiale (gratuit) et duplicata (payant)
- Paiement externe e-Gov uniquement pour le duplicata
- Retrait du diplôme reste physique (étape 5)
