# Cartographie TO-BE : Demande et Délivrance du Permis de Conduire

## Vision Générale

Digitalisation du parcours administratif du permis de conduire via le portail citoyen XPortal et le moteur de workflow XFlow (Camunda Platform 7). Le citoyen soumet son dossier en ligne, paie électroniquement, suit l'avancement en temps réel et reçoit des notifications automatiques à chaque jalon. **Restent obligatoirement en présentiel : le relevé des données biométriques, les épreuves physiques (code et conduite) et le retrait du titre sécurisé**, conformément à la loi n°2004-003.

### Analyse de la Valeur Ajoutée (AVA) appliquée

| Étape AS-IS | Classification AVA | Décision TO-BE |
|-------------|-------------------|----------------|
| Inscription auto-école + formation | VAC (valeur ajoutée citoyen) | **Conservée** — pré-requis légal, hors périmètre digital |
| Dépôt physique du dossier au guichet | SVA (sans valeur ajoutée) | **Supprimée** → soumission en ligne via XPortal |
| Vérification manuelle complétude (papier + Excel) | VAB (valeur ajoutée business) | **Automatisée partiellement** → validation formulaire + vérification agent via tableau de bord XFlow |
| Paiement en espèces à la caisse | SVA | **Supprimé** → paiement en ligne (Flooz / TMoney / Visa / Mastercard) |
| Épreuve théorique (QCM code) | VAB + VAC | **Conservée physiquement** — saisie résultats dans XFlow par l'inspecteur |
| Épreuve pratique (circuit + route) | VAB + VAC | **Conservée physiquement** — obligation légale inspecteur assermenté |
| 2e dépôt physique pour délivrance | SVA | **Supprimé** → dossier déjà complet dans le système |
| Production permis (1 poste à Lomé) | VAB | **Optimisée** → système connecté multi-sites, suivi traçable |
| Retrait physique sans notification | SVA partielle | **Optimisé** → notification SMS/Email quand le permis est prêt ; retrait physique maintenu (titre sécurisé) |

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager — soumission, paiement, correction, suivi).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement back-office).
- **Bus de messaging** : Kafka (topics `bpmn.commands`) pour la synchronisation inter-pools XPortal ↔ XFlow.
- **Identité** : Pré-remplissage transparent via e-ID (`config.users`).
- **Paiement** : Module e-Gov intégré (Flooz, TMoney, Visa, Mastercard).
- **Notifications** : Service Tasks `tg.gouv.gnspd.sendNotification` (SMS + Email).
- **Archivage** : GED Odoo pour l'archivage numérique des dossiers.
- **Anti-contrefaçon** : QR Code infalsifiable ATD sur le permis produit.

## Acteurs et Systèmes

| Acteur / Système | Rôle |
|------------------|------|
| **Citoyen / Candidat** | Soumet son dossier en ligne, paie, reçoit les notifications, se présente aux épreuves physiques, retire le permis |
| **Moteur XPortal** | Orchestration des écrans usager (soumission, paiement, correction, suivi statut) en attente des ordres XFlow |
| **Moteur XFlow** | Orchestration métier : vérification conformité, inscription examen, saisie résultats, validation chef, production permis |
| **Agent de réception DTRF** | Vérifie la conformité du dossier via tableau de bord XFlow (GNSPD User Task) |
| **Inspecteur code DTRF** | Saisit les résultats de l'épreuve théorique dans XFlow |
| **Inspecteur conduite DTRF** | Saisit les résultats de l'épreuve pratique dans XFlow |
| **Chef de service DTRF** | Validation finale via interface back-office dédiée |
| **Service de Notification** | Email/SMS automatiques à chaque jalon clé |
| **Service de Paiement** | Traitement des paiements électroniques |
| **GED Odoo** | Archivage numérique des dossiers et pièces justificatives |

## Étapes Digitalisées

### Étape 1 — Soumission en ligne (Citoyen → XPortal)

- Le citoyen s'authentifie sur le portail e-Gov (e-ID pré-remplie : nom, prénom, date de naissance, téléphone, email).
- Il sélectionne le **type de demande** : Première inscription à l'examen / Duplicata (perte ou vol).
- Il choisit la **catégorie de permis** demandée (A / B / C / D / E).
- Il remplit le formulaire Form.io (wizard multi-étapes) avec les informations complémentaires.
- Il uploade les **pièces justificatives** numérisées :
  - Certificat médical d'aptitude (PDF, daté de moins de 3 mois)
  - Attestation de formation auto-école agréée (PDF)
  - Copie pièce d'identité (PDF/JPEG)
  - Copie acte de naissance (PDF/JPEG)
  - Photos d'identité 4x4 cm (JPEG, x4)
  - [Si duplicata] Déclaration de perte/vol police/gendarmerie (PDF)
  - [Si duplicata] Copie du permis perdu (si disponible)
- **Validation au fil de l'eau** : Form.io bloque les erreurs pendant la saisie (formats, tailles de fichiers, champs obligatoires).
- **Accusé de réception** automatique par SMS + Email avec numéro de suivi.
- **Durée** : Immédiat

### Étape 2 — Paiement en ligne (Citoyen → XPortal)

- Le système **calcule automatiquement** le montant selon le type de demande :
  - Inscription à l'examen : 5 000 FCFA
  - Droits de délivrance du permis : 15 000 FCFA
  - Duplicata : 15 000 FCFA
- Le citoyen procède au paiement via le module e-Gov intégré (Flooz / TMoney / Visa / Mastercard).
- Confirmation de paiement automatique (reçu électronique par SMS/Email).
- Le dossier est transmis au back-office XFlow via Kafka.
- **Durée** : Immédiat

### Étape 3 — Vérification de conformité (Agent DTRF → XFlow)

- L'agent de réception reçoit le dossier dans son **tableau de bord XFlow**.
- Il vérifie la conformité des pièces justificatives (authenticité, lisibilité, validité).
- **Trois décisions possibles** :
  - **Conforme** → convocation pour le relevé biométrique
  - **Correction nécessaire** → notification au citoyen avec motif détaillé
  - **Rejet définitif** → notification au citoyen avec motif (ex : faux documents)
- **Durée** : 1-3 jours ouvrables
- **SLA** : Escalade automatique si > 48h sans action agent

### Étape 3a — Boucle de correction (Citoyen → XPortal)

- XFlow publie un message Kafka `correction` vers XPortal.
- XPortal réveille le dossier citoyen et affiche un **écran de resoumission** Form.io (`Activity_P_Corrections`) avec le motif de l'agent.
- Le citoyen corrige et resoumets les pièces via son dossier existant (**sans recréer de nouveau dossier**).
- Le flux retourne à XFlow pour nouvelle vérification.
- **Limite** : Maximum 3 tentatives de correction. Au-delà, rejet automatique avec notification.
- **Timer** : Si le citoyen ne resoumets pas dans les 15 jours, le dossier est clôturé automatiquement.

### Étape 4 — Relevé des données biométriques — PHYSIQUE (Citoyen → DTRF)

- Une fois le dossier validé conforme, le citoyen est **convoqué par SMS/Email** à se rendre à la DTRF (ou au bureau régional de son choix) pour le relevé de ses données biométriques.
- **Données capturées** : photo biométrique, empreintes digitales, signature manuscrite.
- L'agent DTRF effectue la capture et enregistre les données dans le système XFlow.
- Cette étape est un **pré-requis obligatoire** avant l'inscription aux sessions d'examen.
- **Durée** : 1 jour (rendez-vous)

### Étape 5 — Inscription à la session d'examen (Agent DTRF → XFlow)

- Après la capture biométrique, l'agent inscrit le candidat à la prochaine session d'examen du code disponible dans le **calendrier géré par le système**.
- Le candidat reçoit une **convocation par SMS/Email** (date, lieu, heure du centre d'examen).
- **Durée** : 1-2 jours

### Étape 6 — Épreuve théorique — PHYSIQUE (Inspecteur code → XFlow)

- Le candidat se présente physiquement au centre d'examen.
- L'inspecteur code surveille l'épreuve QCM (40 questions).
- **L'inspecteur saisit les résultats directement dans XFlow** (note sur 40).
- Le système notifie automatiquement le candidat par SMS/Email :
  - **Succès (≥ 35/40)** : inscription automatique à la session pratique suivante + convocation.
  - **Échec** : possibilité de se réinscrire à la session suivante.
- **Durée** : 1 jour (épreuve) + notification immédiate

### Étape 7 — Épreuve pratique — PHYSIQUE (Inspecteur conduite → XFlow)

- Le candidat passe l'épreuve pratique (circuit fermé + route ouverte) en présence d'un inspecteur assermenté.
- **L'inspecteur saisit les résultats dans XFlow** (note sur 20, grille normalisée).
- Le système notifie automatiquement le candidat :
  - **Succès (≥ 10/20)** : passage à la validation finale.
  - **Échec** : possibilité de réinscription. Après 3 échecs consécutifs, le système exige une attestation de formation complémentaire de 5h.
- **Durée** : 1 jour (épreuve) + notification immédiate

### Étape 8 — Validation finale et production du permis (Chef de service → XFlow)

- Le chef de service reçoit le dossier complet (pièces + résultats + données biométriques) dans son **interface de validation XFlow**.
- Il valide ou rejette la délivrance du permis.
- En cas de validation : le système lance la **production du titre sécurisé** (carte plastifiée avec photo biométrique, empreintes, données biographiques, catégories autorisées, date d'expiration, **QR Code anti-contrefaçon ATD**).
- Archivage numérique automatique dans la GED Odoo.
- Mise à jour de la **base de données nationale centralisée** (accessible par tous les bureaux régionaux).
- **Durée** : 2-5 jours (production)

### Étape 9 — Notification et retrait — PHYSIQUE (Système → Citoyen)

- Le citoyen est **notifié automatiquement par SMS/Email** que son permis est prêt au retrait.
- Il se rend au guichet DTRF ou au bureau régional de son choix (Lomé, Kara, Atakpamé, Sokodé, Dapaong).
- Signature manuscrite obligatoire au retrait (exigence légale).
- Clôture automatique du dossier dans XFlow.
- **Durée** : Immédiat (après notification)

## Synthèse des Remèdes Digitaux Appliqués

| Friction AS-IS | Règle ATD appliquée | Solution TO-BE |
|----------------|---------------------|----------------|
| F1 — Dépôt physique obligatoire (multiples déplacements) | R1 Éliminer la poursuite papier | Soumission 100% en ligne via XPortal |
| F2 — Délai production 15-30 jours | R2 Parallélisation | Système connecté multi-sites + suivi temps réel |
| F3 — Gestion manuelle (papier + Excel) | R8 Automatisation par défaut | BDD centralisée, workflow orchestré par XFlow |
| F4 — Absence de notification | R5 Communication proactive | Notifications SMS/Email automatiques à chaque jalon |
| F5 — Paiement espèces uniquement | R3 Paiement sans contact | E-paiement intégré (Flooz, TMoney, Visa, MC) |
| F6 — Pas de BDD centralisée | R3 Zéro saisie redondante / R9 Standardisation | Base de données nationale unique, accessible tous bureaux |
| F7 — Pas d'anti-contrefaçon | R6 Sécurisation et génération auto | QR Code infalsifiable ATD sur le titre |
| F8 — Personnel insuffisant régions | R8 Automatisation | Traitement centralisé, calendrier automatisé |
| F9 — Pas de transparence statut | R6 Transparence totale | Suivi en temps réel sur XPortal + notifications |

## Gains Attendus

- **Réduction des déplacements** : de 4-5 visites physiques à **3 seules** (relevé biométrique + épreuves + retrait du titre)
- **Réduction du délai de traitement** : objectif **-50%** sur la délivrance post-examen
- **Zéro perte de dossier** : archivage numérique GED Odoo
- **Traçabilité complète** : chaque action horodatée et traçable
- **Inclusivité régionale** : soumission accessible depuis n'importe où, 24h/24
- **Réduction des erreurs de saisie** : validation Form.io au fil de l'eau
- **Transparence totale** : le citoyen connaît son statut en temps réel
- **Anti-fraude** : QR Code ATD + base de données nationale unifiée
- **Paiement sécurisé et traçable** : fin du cash, reçus électroniques
