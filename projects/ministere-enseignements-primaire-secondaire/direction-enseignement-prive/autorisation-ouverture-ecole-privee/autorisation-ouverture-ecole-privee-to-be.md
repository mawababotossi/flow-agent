# Cartographie TO-BE : Demande d'autorisation d'ouverture d'un établissement d'enseignement privé

## Vision Générale
Digitalisation du service d'autorisation pour simplifier drastiquement le parcours des promoteurs d'écoles privées. La soumission devient 100% en ligne via XPortal, avec paiement électronique unifié. Les agents de la DEP (Direction de l'Enseignement Privé) traitent les dossiers de manière asynchrone via XFlow. L'inspection sur site reste obligatoire mais sa planification et son suivi sont intégrés numériquement. À l'issue du processus, l'usager est convoqué pour retirer physiquement son arrêté ministériel signé.

## Architecture Technique
- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN citoyen traitant les formulaires et le suivi temporel).
- **Plateforme de Paiement e-Gov** : Externe (TMoney, Flooz, Visa) pour le règlement unifié des frais administratifs et d'inspection (40 000 FCFA).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7) pour gérer l'instruction, les retours de correction et l'orchestration métier.
- **Bus de messaging** : Kafka (`bpmn.commands`) pour relier dynamiquement XPortal et XFlow.
- **Notifications** : SMS et Emails automatiques à chaque étape (accusé de réception, corrections, planification, avis final).
- **Identité** : E-ID automatique pour le pré-remplissage des données de l'usager.
- **Génération de documents** : L'arrêté ministériel est rédigé puis signé manuellement par les autorités compétentes (procédure physique).

## Acteurs et Systèmes
| Acteur / Système | Rôle |
|------------------|------|
| Moteur XPortal (Citoyen) | Portails d'interaction citoyen (Dépôt initial, resoumission de pièces). |
| Plateforme de Paiement e-Gov | Sécurisation et traitement du paiement des frais de la démarche. |
| Moteur XFlow (Back-Office) | Moteur de traitement d'intégrité et de gestion administrative des étapes métier. |
| Agent instructeur DEP | Évaluation de la conformité du dossier pédagogique, financier et architectural. |
| Inspecteur de visite | Visite de terrain et saisie du PV d'inspection sur tablette/mobile. |
| Directeur / Commission | Validation intellectuelle finale. |
| Service de Notification | Communication active des changements d'état du dossier. |

## Étapes Digitalisées

1. **Soumission en ligne** (Citoyen → XPortal)
   - Remplissage du formulaire P-Studio (Form.io) 100% numérique, upload des pièces (plan de situation, conformité sanitaire, diplômes, justificatif financier).
   - Validation temps-réel (bloquant ainsi les dossiers évidemment incomplets).
   - Durée : Immédiat.

2. **Paiement unique des frais** (Citoyen → e-Gov)
   - Redirection depuis XPortal pour payer 40 000 FCFA. Ce passage simplifie la procédure en évitant un second paiement plus tard.
   - Notification de confirmation (XPortal & SMS/Email).

3. **Examen de conformité et Allers-Retours (XFlow <=> XPortal)**
   - L'Agent instructeur vérifie la cohérence du dossier.
   - **Décision "Correction"** : Un message Kafka `correction` est publié. Le promoteur reçoit un lien pour resoumettre les documents défectueux via `Activity_P_Corrections`.
   - **Décision "Conforme"** : On progresse à l'étape d'inspection.

4. **Visite d'inspection sur site — PHYSIQUE** (Inspecteur → XFlow)
   - Convocation automatique par SMS/Email au promoteur avec la date de visite.
   - L'inspecteur se rend sur place et complète le PV d'inspection de conformité directement sur son interface métier connectée. 

5. **Délibération et Décision** (Directeur/Commission → XFlow)
   - La décision finale (Autorisé/Rejeté) est actée sur le tableau de bord avec une traçabilité parfaite en fonction de l'avis de la commission et du rapport d'inspection.

6. **Convocation et Retrait du document — PHYSIQUE** (Agent d'accueil DEP → XFlow)
   - L'usager reçoit une notification par SMS/Email l'invitant à venir retirer son arrêté.
   - Le citoyen se déplace pour le retrait physique du document. 
   - L'agent d'accueil DEP finalise la remise dans XFlow, ce qui clôture le processus.

### Pattern pour sous-étapes (boucles, notifications intermédiaires)

3a. **Boucle de correction** (Citoyen → XPortal)
   - L'instructeur signale sur XFlow le(s) document(s) à corriger motivé(s).
   - Notification XFlow → Citoyen.
   - Resoumission asynchrone ; si la demande n'est pas corrigée dans un délai de 15 jours (SLA technique), clôture ou rejet automatique. Limité à 2 essais.

## Patterns d'orchestration inter-pools (OBLIGATOIRE)
- **P1. Symétrie des gateways** : Les décisions (Notamment l'acceptation ou le rejet après instruction) seront miroirs entre XPortal et XFlow.
- **P2. Convergence** : Les flux de correction convergent en une `ReceiveTask` côté XFlow.
- **P3. Notification PUIS SendMessage** : Les ServiceTasks de notification citoyen (SMS/Email) s'exécutent toujours avant l'envoi du message BPMN Kafka au Portail.
- **P7. Terminaison Explicite** : Tout avis défavorable finira en `EndEvent` dédié.

## Gains Attendus
- **Fin des déplacements physiques fastidieux**, limités désormais à l'inspection stricte programmée et au retrait du document final.
- **Réduction majeure du temps d'instruction** due au blocage des dépôts incomplets et des paiements hors ligne.
- **Paiement instantané 100% traçable**.
