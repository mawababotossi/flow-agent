# Status — Demande de Mise à la Retraite et de Liquidation de Pension

| Champ | Valeur |
|-------|--------|
| **Étape courante** | GATE:2 — Validation SRS |
| **Dernière étape complétée** | STEP:4 — SRS |
| **Prochaine étape** | STEP:5 — Formulaire Form.io principal |
| **Date de mise à jour** | 2026-03-25 |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `demande-pension-retraite-pipeline.yaml` | Produit |
| Cartographie AS-IS | `demande-pension-retraite-as-is.md` | Produit |
| Cartographie TO-BE | `demande-pension-retraite-to-be.md` | Produit |
| Fiche SRS | `srs-demande-pension-retraite.md` | Non commencé |
| Formulaire principal | `formio-demande-pension-retraite.json` | Non commencé |
| Formulaire correction | `formio-correction-pension-retraite.json` | Non commencé |
| Formulaire instruction agent | `formio-instruction-pension-retraite.json` | Non commencé |
| Formulaire contre-vérification | `formio-contreverification-pension-retraite.json` | Non commencé |
| BPMN | `bpmn-demande-pension-retraite.bpmn` | Non commencé |

## Blocages / Notes
- Service **gratuit** — pas de module de paiement.
- Parties **non digitalisables** : signature du DG CRT sur le titre de pension (physique/hybride) ; contrôle d'existence annuel (partiellement digitalisable via biométrie mobile).
- Processus **hybride** : l'acte de mise à la retraite (signé par le Ministre de la FP) est uploadé comme pièce justificative.
- GATE:1 requis avant de démarrer le SRS.
