# Cartographie TO-BE : Demande d'extrait d'acte de mariage

## Vision Générale (Version Simplifiée & Optimisée)
Numérisation complète et fluide selon les principes ATD : le paiement est intégré dès la soumission, supprimant une étape bloquante. Les actes identifiables sont pré-vérifiés automatiquement par le système. À la fin, l'officier signe manuellement l'acte, et le citoyen est notifié pour le retirer au guichet ou via la Poste sans que l'agent de guichet n'ait à clôturer le ticket informatique.

## Architecture Technique
- **Frontend / Orchestrateur Citoyen** : XPortal avec composant Form.io dynamique (calcul des coûts `calculate-costs` intégré).
- **Moteur de workflow Métier** : XFlow (Camunda 7).
- **Intégrations** : e-ID (transparence identité), Odoo/LogiEC (vérification automatique), passerelle e-Gov (paiement direct), La Poste Togo (option d'expédition).

## Acteurs et Systèmes
| Acteur / Système | Rôle |
|------------------|------|
| XPortal / Form.io | Soumission, calcul automatique des frais, paiement immédiat, corrections. |
| Odoo / LogiEC | Vérification informatique et silencieuse de l'existence de l'acte si numérisé. |
| Agent d'état civil | Instruction simplifiée (cas nécessitant recherche ou validation finale). |
| Officier d'état civil | Impression du tirage et signature manuscrite formelle (Opération Légale). |

## Étapes Digitalisées

1. **Soumission et Paiement Combinés** (Citoyen → XPortal)
   - L'e-ID remplit l'identité. Le citoyen saisit les détails de l'acte, choisit le mode d'obtention (Guichet ou La Poste).
   - Le système calcule le coût de l'acte et des frais potentiels par l'action système `Calculate Costs`.
   - L'usager paie en fin de formulaire sans interrompre l'expérience. Soumission du dossier.

2. **Vérification Système Préalable** (Système <=> Odoo)
   - XFlow interroge la base des actes numérisés. Si l'acte existe, le dossier arrive à l'agent avec un statut pré-approuvé.

3. **Instruction Métier et Allers-Retours** (XFlow <=> XPortal)
   - Si acte introuvable numériquement, recherche par l'agent.
   - Si corrections nécessaires (pièce floue, erreur), boucle asynchrone côté citoyen (3 tentatives max).

4. **Opération Légale — PHYSIQUE** (Agent → Service Local)
   - La loi impose l'original : l'officier génère le document validé avec un QR code anti-fraude, l'imprime et le signe à la main.

5. **Notification et Clôture Silencieuse** (Système)
   - L'agent indique dans XFlow "Acte prêt pour délivrance".
   - Le système envoie un SMS automatique et clôture le BPMN. Le parcours numérique est terminé.
   - Le document est remis physiquement au guichet par convocation, ou expédié par La Poste.

## Apport direct des Simplifications ATD
- **Zéro délai d'attente sur les paiements** : La combinaison de l'étape 1 (Soumission) et 2 (Paiement) évite les requêtes de XFlow vers XPortal.
- **Réduction du travail agent** : L'automatisation optionnelle sur les registres récents (Odoo) élimine la recherche manuelle.
- **Zéro Ticket Orphelin** : En considérant l'envoi de l'alerte comme la fin du workflow, on évite que des milliers de dossiers ne restent ouverts si l'agent oublie de cliquer "Remis".
- **Zéro Déplacement (Optionnel)** : L'interfaçage d'expédition permet au citoyen de tout faire de chez lui avec réception sécurisée.
