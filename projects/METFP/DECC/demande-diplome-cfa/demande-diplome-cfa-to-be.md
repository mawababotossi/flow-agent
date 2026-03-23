# Cartographie TO-BE : Demande de Diplôme du CFA

## Vision Générale

Digitalisation complète de la demande de diplôme CFA via le portail citoyen XPortal connecté au moteur de workflow XFlow (Camunda Platform 7). Le citoyen soumet sa demande 100% en ligne, son identité est pré-remplie via e-ID, le paiement (duplicata) s'effectue sur la plateforme e-Gov externe, l'agent DECC instruit le dossier depuis son tableau de bord, et le diplôme est généré automatiquement (PDF signé + QR code anti-fraude). Le citoyen est notifié à chaque étape clé par email, SMS et notification in-app.

## Analyse de la Valeur Ajoutée (AVA) — Diagnostic AS-IS

| Étape AS-IS | Classification | Action TO-BE |
| --- | --- | --- |
| Déplacement physique au guichet | **SVA** | **Supprimée** — soumission 100% en ligne |
| Remplissage du formulaire papier | **SVA** | **Supprimée** — formulaire Form.io wizard en ligne |
| Vérification manuelle d'identité (copie CNI) | **SVA** | **Supprimée** — pré-remplissage e-ID automatique |
| Vérification de complétude du dossier | **VAB** | **Automatisée** — validation Form.io au fil de l'eau |
| Attribution manuelle du numéro de dossier | **SVA** | **Supprimée** — attribution automatique (xref) |
| Vérification des résultats d'examen CFA | **VAB** | **Automatisée** — consultation Odoo (search_read) |
| Décision de l'agent (conformité) | **VAC/VAB** | **Optimisée** — userTask agent avec données pré-vérifiées |
| Production physique du diplôme (impression, cachet) | **VAB** | **Automatisée** — génération PDF + QR code + signature E-Cert |
| Notification par téléphone/courrier | **SVA** | **Supprimée** — notifications tricanales automatiques |
| Retrait physique obligatoire | **SVA** | **Remplacée** — téléchargement numérique sur le portail (retrait physique optionnel) |
| Paiement en espèces (duplicata) | **SVA** | **Remplacé** — plateforme de paiement e-Gov externe |

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement).
- **Bus de messaging** : Kafka (topics `bpmn.commands`) pour la synchro inter-pools.
- **Identité** : Remplissage transparent e-ID (`config.users`).
- **Registre métier** : Odoo (`search_read` pour vérifier inscription/résultats CFA).
- **Génération documentaire** : Chaîne complète `generateTemplate` → `generateUrlQrcode` → `pdfImage` → `certSign`.
- **Notifications** : Injecteurs Service Task `tg.gouv.gnspd.sendNotification` (email + SMS + in-app).
- **Paiement** : Plateforme de paiement e-Gov **externe** (Flooz, TMoney, Visa, Mastercard). Le paiement ne se fait **ni dans XPortal ni dans XFlow** — le citoyen est redirigé vers la plateforme externe, et la confirmation revient de manière asynchrone.

## Acteurs et Systèmes

| Acteur / Système | Rôle |
| --- | --- |
| Citoyen (apprenti / ancien apprenti) | Soumet la demande en ligne, uploade les pièces, paie les frais (si duplicata), télécharge le diplôme. |
| Moteur XPortal | Orchestration des écrans usager (soumission, paiement, correction, suivi) en attente des ordres XFlow. |
| Plateforme de Paiement e-Gov | Plateforme **externe** — le citoyen est redirigé hors de XPortal pour payer (duplicata uniquement). |
| Moteur XFlow (Back-Office) | Orchestration métier : vérification Odoo, instruction agent, génération documentaire, notifications. |
| Agent DECC | Instruit le dossier via tableau de bord : vérifie les pièces, consulte les résultats Odoo, prend la décision. |
| Odoo (ERP) | Registre des inscriptions et résultats CFA — consultation automatique (`search_read`). |
| Service de Génération PDF | Production du diplôme numérique (template PDF + QR code + signature E-Cert). |
| Service de Notification | Envoi automatique des notifications tricanales (email + SMS + in-app) à chaque jalon. |

## Étapes Digitalisées

1. **Soumission en ligne** (Citoyen → XPortal)
   - Formulaire Form.io wizard multi-onglets : qualification de la demande (original/duplicata), identité pré-remplie e-ID, informations de formation (centre, métier, année), upload des pièces justificatives.
   - Validation au fil de l'eau (Form.io) : formats, tailles, champs obligatoires.
   - Accusé de réception automatique immédiat (email + SMS + in-app).
   - **Règles appliquées** : R1 (zéro papier), R2 (e-ID), R4 (capture à la source), R5 (validation temps réel).
   - Durée : immédiat

2. **Paiement des frais de duplicata** (Citoyen → Plateforme e-Gov externe) — **Conditionnel**
   - Uniquement si `typeDemande = duplicata`.
   - Le citoyen est redirigé vers la plateforme de paiement e-Gov externe.
   - Confirmation de paiement asynchrone — le dossier avance automatiquement.
   - **Règle appliquée** : R3 (paiement sans contact).
   - Durée : immédiat à quelques minutes

3. **Transmission automatique au back-office** (XPortal → XFlow via Kafka)
   - SendTask XPortal vers XFlow : transmission des données soumises et des pièces.
   - Création automatique du dossier et attribution du numéro de suivi (xref).
   - **Règle appliquée** : R8 (automatisation par défaut).
   - Durée : immédiat

4. **Vérification Odoo automatique** (XFlow — Système)
   - ServiceTask `tg.gouv.gnspd.odoo` — `search_read` sur le modèle des inscriptions CFA.
   - Recherche par nom, prénom, année d'examen, centre de formation.
   - Le résultat Odoo (trouvé/non trouvé, notes, statut) est attaché au dossier pour l'agent.
   - **Règles appliquées** : R3 (zéro saisie redondante), R8 (automatisation).
   - Durée : immédiat

5. **Instruction du dossier** (Agent DECC → XFlow)
   - UserTask agent : consultation des données soumises, des pièces justificatives et du résultat Odoo.
   - Formulaire d'instruction présentant toutes les informations consolidées.
   - Décisions possibles :
     - **Conforme** → passe à la génération du diplôme.
     - **Correction nécessaire** → notification au citoyen avec motif, boucle de correction.
     - **Rejet** → notification au citoyen avec motif, fin du processus.
   - **Règle appliquée** : R1 (simplicité — l'agent ne fait que valider, pas saisir).
   - SLA : 72h

5a. **Boucle de correction** (Citoyen → XPortal) — **Conditionnel**
   - XFlow envoie un message Kafka `correction` vers XPortal avec le motif de l'agent.
   - Le citoyen reçoit une notification tricanale avec les consignes de correction.
   - Il corrige et resoumets via son dossier existant (pas de nouvelle demande).
   - Maximum 3 tentatives. Timer : 15 jours avant clôture automatique.
   - **Règles appliquées** : R6 (transparence — motif explicite), R5 (validation au fil de l'eau).

6. **Génération du diplôme CFA** (XFlow — Système)
   - Chaîne de production documentaire complète :
     1. `generateTemplate` : génération du PDF du diplôme à partir du template et des données validées.
     2. `generateUrlQrcode` : génération du QR code de vérification (URL portail + xref).
     3. `pdfImage` : apposition du QR code sur le diplôme PDF.
     4. `certSign` : signature électronique E-Cert du document.
   - Mise à jour Odoo : enregistrement du statut "diplôme délivré" (`write`).
   - **Règles appliquées** : R6 (sécurisation anti-fraude), R8 (automatisation).
   - Durée : immédiat

7. **Notification finale et mise à disposition** (XFlow → XPortal)
   - Notification tricanale (email + SMS + in-app) : diplôme disponible au téléchargement.
   - Le diplôme PDF signé est téléchargeable depuis le portail citoyen.
   - Mise à jour du statut du dossier sur XPortal : "Terminé — Document disponible".
   - **Règle appliquée** : R6 (transparence totale).
   - Durée : immédiat

7a. **Retrait physique du diplôme — PHYSIQUE** (Citoyen → Lieu de retrait) — **Optionnel**
   - Le citoyen peut choisir de retirer le diplôme original physique au lieu sélectionné (DECC, Ccoms, CPM, CRM, poste).
   - Convocation par notification une fois le diplôme imprimé et disponible.
   - Le diplôme numérique signé reste toujours accessible sur le portail.
   - Frais postaux supplémentaires si envoi par la poste.

## Gains Attendus

| Indicateur | AS-IS | TO-BE | Gain |
| --- | --- | --- | --- |
| Délai de traitement total | 12-35 jours | 3-5 jours | **-80%** |
| Déplacements physiques | 2-4 (dépôt + relances + retrait) | 0 à 1 (retrait optionnel) | **-90%** |
| Traçabilité | Aucune | Temps réel (notifications tricanales) | **100%** |
| Risque de perte de dossier | Élevé (papier) | Nul (archivage numérique) | **100%** |
| Risque de falsification | Élevé (signature manuelle) | Nul (QR code + E-Cert) | **100%** |
| Vérification des résultats | Manuelle (registres papier) | Automatique (Odoo search_read) | **-95% temps agent** |
| Paiement duplicata | Espèces au guichet | e-Gov externe (mobile money, carte) | **100% digital** |
