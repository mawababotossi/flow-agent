# Cartographie TO-BE : Demande de Diplôme du CFA

> **Version** : 1.0 — 2026-03-28
> **Basée sur** : AS-IS `demande-diplome-cfa-as-is.md` + Guide ATD de transformation

---

## Vision Générale

Digitalisation complète de la demande de diplôme du CFA via un portail citoyen (XPortal / Form.io) connecté à un moteur de workflow (XFlow / Camunda Platform 7). Le candidat soumet sa demande en ligne sans déplacement, paie en ligne si duplicata, et reçoit des notifications automatiques à chaque étape. Le back-office traite le dossier via tableau de bord. Seul le retrait physique du diplôme original subsiste.

---

## Architecture Technique

| Composant | Rôle |
|-----------|------|
| **XPortal** | Frontend citoyen — formulaire Form.io Wizard, tâches de correction et de paiement, notifications |
| **XFlow** | Moteur BPMN Camunda Platform 7 — orchestration, routage, escalades temporelles |
| **Odoo (back-office)** | Vérification de l'inscription et des résultats d'examen, tableau de bord agent CFA |
| **Kafka** | Bus de messagerie asynchrone entre XPortal et XFlow (`bpmn.commands`) |
| **Plateforme e-Gov** | Paiement externe — Flooz, TMoney, Visa, Mastercard (hors XPortal et XFlow) |
| **e-ID** | Pré-remplissage automatique des données d'identité du citoyen |
| **flow-notify** | Service de notifications automatiques SMS + e-mail |

---

## Acteurs et Systèmes

| Acteur / Système | Rôle TO-BE |
|------------------|------------|
| **Citoyen / Candidat** | Soumet en ligne, paie en ligne (duplicata), corrige si demandé, retire physiquement |
| **Agent CFA** | Instruit le dossier via back-office Odoo — conformité des pièces et données |
| **Système Odoo** | Vérification automatique de l'inscription et de la réussite à l'examen |
| **XFlow** | Orchestration BPMN — routing, notifications, escalades |
| **XPortal** | Interface citoyen — soumission, suivi, correction, paiement |

---

## Étapes du Processus Digitalisé

### Pool Citoyen (XPortal)

| N° | Étape | Description | Acteur | Délai |
|----|-------|-------------|--------|-------|
| C01 | Soumission du formulaire | Le candidat accède à XPortal, s'authentifie (e-ID pré-rempli). Il remplit le formulaire Wizard 5 onglets : qualification (initiale/duplicata), identité, centre d'examen, pièces jointes, récapitulatif. Il soumet. Un numéro de dossier unique est généré. Notification SMS/e-mail de réception envoyée. | Citoyen | Immédiat |
| C02 | Réception demande de paiement | Si duplicata : le citoyen reçoit une notification XPortal lui demandant de régler les frais. Il est redirigé vers la plateforme e-Gov externe. | Citoyen | < 15 min |
| C03 | Paiement en ligne (duplicata) | Le citoyen effectue le paiement sur la plateforme e-Gov (Flooz, TMoney, Visa, Mastercard). La confirmation revient de façon asynchrone à XFlow. | Citoyen | À la demande (max 48h) |
| C04 | Réception notification vérification | Le citoyen reçoit une notification indiquant l'état de vérification de son dossier : en cours / correction requise / décision finale. | Système | Selon traitement |
| C05 | Correction du dossier (si requise) | Le citoyen reçoit la liste précise des corrections demandées. Il accède à un formulaire de correction dans XPortal, modifie les données ou remplace les pièces, et resoumet **sans créer un nouveau dossier**. | Citoyen | Max 5 jours ouvrés |
| C06 | Réception notification finale | Le citoyen reçoit la décision finale par SMS et e-mail : acceptation (diplôme en cours d'édition / disponible) ou rejet définitif avec motif. | Système | < 10 min |
| C07 | Retrait du diplôme — PHYSIQUE | Le citoyen retire son diplôme au lieu de retrait choisi lors de la soumission : Direction des examens CFA, CCom, CPM, CRM, ou envoi postal (frais additionnels). | Citoyen | Selon mode de retrait |

### Pool Back-Office (XFlow + Odoo)

| N° | Étape | Description | Acteur | Délai |
|----|-------|-------------|--------|-------|
| B01 | Initialisation du processus | XFlow reçoit le message de démarrage depuis XPortal (Kafka). Chargement des données. Évaluation de la gateway `duplicata ?`. | Système | Immédiat |
| B02 | Demande de paiement (duplicata) | Si duplicata : XFlow envoie une Send Task vers XPortal avec le montant à régler (depuis référentiel tarifaire CFA). | Système | < 5 min |
| B03 | Attente confirmation paiement | Receive Task : XFlow attend la confirmation asynchrone du paiement. Si délai dépassé (48h) → annulation automatique + notification citoyen. | Système | Max 48h |
| B04 | Extraction et normalisation données | Script Task : extraction et normalisation des données du formulaire. Vérification automatique : format, cohérence, complétude. | Système | < 2 min |
| B05 | Vérification Odoo | Service Task : interrogation de la base Odoo pour vérifier l'inscription du candidat et la réussite à l'examen dans la spécialité et session déclarées. | Système + Odoo | < 5 min |
| B06 | Instruction du dossier | User Task assignée à l'agent CFA : examen du dossier, vérification des pièces justificatives, cohérence des informations. Interface Odoo. | Agent CFA | Selon SLA CFA (max 5 j. ouvrés) |
| B07 | Notification de correction | Send Task : si anomalies détectées, notification envoyée au portail avec liste précise des corrections. Démarrage du timer de 5 jours ouvrés. | Système | < 15 min |
| B08 | Enregistrement de la décision | Service Task : enregistrement de la décision d'acceptation dans la base de données. Génération du récépissé de validation. | Système | < 2 min |
| B09 | Rejet définitif | Send Task : notification de rejet définitif avec motif détaillé envoyée au portail et au citoyen (SMS + e-mail). Fin du processus. | Système | < 5 min |
| B10 | Notification d'acceptation | Send Task : notification d'acceptation envoyée — diplôme en cours d'édition / disponible au retrait. Fin du processus back-office. | Système | < 5 min |

---

## Boucle de Correction (Détail)

La boucle de correction est un mécanisme central du workflow. Elle garantit que le citoyen peut corriger son dossier **sans recréer une nouvelle demande** :

1. L'agent détecte une anomalie lors de l'instruction (B06) → déclenche B07
2. XFlow envoie une Send Task vers XPortal avec la liste des corrections
3. Le citoyen reçoit une notification et accède au formulaire de correction (C05)
4. Après resoumission, le dossier réintègre le cycle d'instruction (B04)
5. Si le citoyen ne corrige pas dans les 5 jours ouvrés → rejet automatique + notification

**Maximum 3 itérations de correction autorisées** avant rejet définitif.

---

## Escalades Temporelles

| Déclencheur | Délai | Action |
|-------------|-------|--------|
| Délai instruction agent dépassé | Selon SLA CFA | Escalade automatique vers superviseur CFA — email + dashboard |
| Délai correction citoyen dépassé | 5 jours ouvrés | Rejet automatique + notification SMS + e-mail |
| Délai confirmation paiement dépassé | 48h | Annulation de la demande + notification |
| Indisponibilité XFlow > 15 min | — | Alerte email Admin ATD |

---

## Gains par rapport à l'AS-IS

| Point de friction AS-IS | Remède TO-BE | Règle ATD |
|------------------------|--------------|-----------|
| Déplacements multiples (dépôt, correction, retrait) | Soumission 100% en ligne, correction en ligne | Règle 1 — Zéro papier |
| Formulaire papier non disponible à distance | Formulaire Form.io Wizard accessible H24/7 | Règle 1 |
| Identité ressaisie manuellement | Pré-remplissage e-ID automatique | Règle 2 — État civil automatique |
| Paiement espèces à la caisse (duplicata) | Paiement en ligne via plateforme e-Gov | Règle 3 — Paiement sans contact |
| Consultation manuelle des registres d'examen | Vérification automatique via API Odoo | Règle 4 — Orchestration BPMN |
| Aucun suivi en temps réel | Notifications SMS/e-mail à chaque jalon | Règle 5 — Communication proactive |
| Délais longs et imprévisibles | SLA définis et timers d'escalade automatiques | Règles 2 + 4 |
| Risque de perte de dossiers papier | Dossiers numériques horodatés et traçables | Règle 1 |
| Diplôme falsifiable (papier + signature manuscrite) | Génération PDF sécurisé + QR Code ATD | Règle 6 — Sécurisation |

---

## Notifications Automatiques

| Jalon | Canal | Message |
|-------|-------|---------|
| Réception de la demande | SMS + e-mail | Numéro de dossier + accusé de réception |
| Demande de paiement (duplicata) | Notification XPortal + SMS | Montant + lien paiement |
| Confirmation de paiement | SMS + e-mail | Paiement reçu, traitement en cours |
| Correction requise | Notification XPortal + SMS + e-mail | Liste des corrections + délai |
| Resoumission reçue | SMS | Dossier reçu, traitement en cours |
| Diplôme disponible | SMS + e-mail | Lieu et modalités de retrait |
| Rejet définitif | SMS + e-mail | Motif détaillé du rejet |
