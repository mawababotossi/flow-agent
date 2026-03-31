# Cartographie TO-BE : Demande et délivrance du permis de conduire

## Vision Générale
Le service est digitalisé pour permettre une soumission et un suivi intégralement en ligne. Seules les épreuves de conduite et le retrait du titre sécurisé imposent un déplacement physique. L'expérience utilisateur est améliorée par des notifications automatiques et un paiement électronique sécurisé.

## Architecture Technique
- **Frontend (XPortal)** : Portail de soumission Form.io, suivi en temps réel et correction.
- **Orchestration (XFlow)** : Workflow BPMN (Camunda 7) orchestrant les étapes métiers et agents.
- **Interopérabilité** : Connexion e-ID pour le pré-remplissage des données identitaires.
- **Notifications** : SMS/Email via le service de notification GNSPD.
- **Paiement** : Redirection vers la plateforme de paiement e-Gov externe.

## Acteurs et Systèmes
| Acteur / Système | Rôle |
|------------------|------|
| Citoyen | Soumet sa demande en ligne, paie et suit son dossier sur XPortal. |
| Agent Instructeur DTRF | Vérifie les dossiers numériques sur XFlow et valide les pièces. |
| Inspecteur DTRF | Saisit les résultats des épreuves directement dans le système. |
| Chef de Service | Valide la délivrance finale du titre. |
| Système XFlow | Génère les convocations et les ordres de production. |

## Étapes Digitalisées

1. **Soumission en ligne (Citoyen → XPortal)**
   - Remplissage du formulaire intelligent (données e-ID pré-remplies).
   - Upload des documents (Certificat médical numérisé, etc.).
   - Paiement immédiat des frais d'inscription via mobile money ou carte.

2. **Vérification et planification (Système / Agent)**
   - Vérification automatique de l'éligibilité.
   - L'agent valide le dossier et le système planifie la session d'examen.
   - **Notification** : Convocation automatique envoyée au citoyen.

3. **Épreuves — PHYSIQUE (Citoyen / Inspecteur)**
   - Le citoyen se présente avec sa convocation numérique.
   - L'inspecteur saisit les notes en temps réel sur une interface mobile/tablette connectée à XFlow.
   - **Notification** : Résultat envoyé par SMS immédiatement après l'épreuve.

4. **Droits de délivrance (Citoyen → XPortal)**
   - En cas de succès, le citoyen est notifié pour payer les droits de délivrance (15000 FCFA) en ligne.
   - Le paiement déclenche automatiquement la file de production.

5. **Production et Signature (Système / Agent)**
   - Centralisation des données vers le service de personnalisation.
   - Mise à jour du registre national des permis de conduire en temps réel.

6. **Notification de disponibilité (Système)**
   - Notification automatique (SMS/Email) dès que le permis est prêt dans le bureau choisi.

7. **Retrait du titre — PHYSIQUE (Citoyen)**
   - Retrait au guichet sur présentation d'une pièce d'identité.

## Gains Attendus
- **Zéro déplacement inutile** : Déplacement uniquement pour l'examen et le retrait.
- **Transparence** : Suivi du statut du dossier H24 sur le portail citoyen.
- **Rapidité** : Réduction des délais de traitement par l'automatisation des flux.
- **Sécurité** : Paiement électronique traçable et registre national synchronisé.
- **Qualité de service** : Fin des files d'attente et des dossiers perdus.
