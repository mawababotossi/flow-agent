# Cartographie TO-BE : Demande de Carte Nationale d'Identité (CNI)

## Vision Générale

Digitalisation partielle du parcours citoyen via le portail XPortal et le moteur de workflow XFlow (Camunda Platform 7). Le citoyen pré-remplit son dossier en ligne, paie électroniquement et réserve son créneau de rendez-vous biométrique. Il ne se déplace qu'une seule fois au Centre de Documentation pour la capture biométrique. Après production par la DGDN, il est notifié par SMS/Email et retourne au CD uniquement pour retirer sa CNI physique. **Restent obligatoirement en présentiel : la capture biométrique (obligation légale) et le retrait du titre physique (CNI biométrique sécurisée).**

---

## Analyse de la Valeur Ajoutée (AVA) appliquée

| Étape AS-IS | Classification AVA | Décision TO-BE |
|-------------|-------------------|----------------|
| Déplacement au CD pour dépôt du dossier | SVA | **Supprimée** — pré-remplissage + soumission en ligne via XPortal |
| Paiement en espèces au guichet caisse | SVA | **Supprimée** — paiement en ligne (Flooz / TMoney / Visa / Mastercard) |
| Files d'attente au CD pour capture bio | SVA | **Réduite** — réservation de créneau RDV en ligne |
| Vérification manuelle de complétude (papier) | VAB | **Automatisée** — validation Form.io au fil de la saisie + vérification agent via XFlow |
| Transmission par lot à la DGDN (VPN) | VAB | **Conservée** — infrastructure VPN sécurisée maintenue ; statut de transmission tracé dans XFlow |
| Personnalisation / impression DGDN | VAC | **Conservée** — chaîne sécurisée obligatoire ; avancement tracé dans XFlow |
| 2e déplacement pour retrait sans notification | SVA | **Optimisée** — notification SMS/Email quand la CNI est disponible ; **un seul déplacement retrait** |
| Aucune notification de statut | SVA | **Supprimée** — SMS/Email à chaque jalon (reçu, RDV confirmé, en production, disponible) |

---

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable — soumission, paiement, RDV info, correction, suivi).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7 — orchestration back-office CD + DGDN).
- **Bus de messaging** : Kafka (topic `bpmn.commands`) pour la synchronisation inter-pools XPortal ↔ XFlow.
- **Identité** : Pré-remplissage transparent via e-ID (`config.users`) — nom, prénom, date de naissance, téléphone, email.
- **Paiement** : Plateforme de paiement e-Gov externe (Flooz, TMoney, Visa, Mastercard). Montant variable selon le type de demande. Le citoyen est redirigé vers la plateforme ; la confirmation revient de manière asynchrone.
- **Notifications** : Service Tasks `tg.gouv.gnspd.sendNotification` (SMS + Email) à chaque jalon clé.
- **Archivage** : GED Odoo pour l'archivage numérique des dossiers.

---

## Acteurs et Systèmes

| Acteur / Système | Rôle |
|------------------|------|
| **Citoyen / Demandeur** | Soumet le dossier en ligne, paie, choisit son créneau RDV ; se présente UNE fois au CD pour la capture biométrique ; retourne au CD quand notifié que sa CNI est prête |
| **Moteur XPortal** | Orchestration des écrans usager (soumission, paiement, RDV confirmé, correction, suivi statut) en attente des ordres XFlow |
| **Moteur XFlow** | Orchestration métier : vérification conformité, confirmation RDV, enregistrement biométrique, validation superviseur, transmission DGDN, suivi production, notifications |
| **Agent de réception CD** | Vérifie la conformité du dossier via tableau de bord XFlow |
| **Opérateur biométrique CD** | Capture les données biométriques et valide les données biographiques dans XFlow |
| **Superviseur CD** | Contrôle qualité et validation avant transmission à la DGDN |
| **Agent DGDN** | Marque la CNI comme produite dans XFlow (complétant le cycle de production) |
| **Service de Notification** | SMS/Email automatiques à chaque changement de statut |
| **Plateforme de Paiement e-Gov** | Plateforme externe (Flooz, TMoney, Visa, Mastercard) — le citoyen est redirigé hors de XPortal |
| **GED Odoo** | Archivage numérique des dossiers et preuves |

---

## Étapes Digitalisées

### Étape 1 — Soumission en ligne (Citoyen → XPortal)

- Le citoyen s'authentifie sur le portail e-Gov. Son identité est pré-remplie via e-ID.
- Il sélectionne le **type de demande** (1ère demande, renouvellement, duplicata, urgence).
- Il complète les informations complémentaires.
- Il uploade les **pièces justificatives** selon le type de demande :
  - 1ère demande / renouvellement : acte de naissance, ancienne CNI (si renouvellement)
  - Duplicata : déclaration de perte/vol (police ou gendarmerie), acte de naissance
- Il sélectionne son **Centre de Documentation** et un **créneau de rendez-vous** souhaité pour la capture biométrique.
- **Validation au fil de l'eau** : Form.io bloque les erreurs pendant la saisie.
- **Durée** : Immédiat (15–20 min)

### Étape 2 — Paiement en ligne (Citoyen → Plateforme e-Gov externe)

- Le système affiche le montant calculé selon le type de demande :
  - 4 000 FCFA (1ère demande / renouvellement)
  - 8 000 FCFA (duplicata)
  - 20 000 FCFA (urgence)
- Redirection vers la **plateforme de paiement e-Gov externe** (Flooz / TMoney / Visa / Mastercard).
- Confirmation de paiement automatique (reçu électronique par SMS/Email).
- Le dossier complet + preuve de paiement est transmis au back-office XFlow via Kafka (`MSG_CNI_START`).
- **SLA** : Si le paiement n'est pas confirmé sous 30 minutes, la demande est annulée automatiquement.
- **Durée** : Immédiat

### Étape 3 — Accusé de réception et vérification de conformité (Système + Agent CD → XFlow)

- XFlow envoie automatiquement un **accusé de réception** par SMS + Email avec le numéro de dossier.
- L'agent de réception du CD vérifie dans XFlow la conformité du dossier (authenticité des pièces, concordance des informations, validité de la déclaration police pour duplicata).
- **Trois décisions possibles** :
  - **Conforme** — le CD confirme le créneau RDV biométrique
  - **Correction nécessaire** — notification au citoyen avec motif
  - **Rejet définitif** — notification au citoyen avec motif
- **SLA** : ≤ 48h ouvrables
- **Durée** : ≤ 48h ouvrables

### Étape 3a — Boucle de correction (Citoyen → XPortal)

- XFlow publie un message Kafka `MSG_CNI_RETURN` (action: "correction") vers XPortal.
- XPortal réveille le dossier citoyen et affiche un **écran de resoumission** avec le motif de l'agent.
- Le citoyen corrige et resoumets les pièces sans créer un nouveau dossier.
- **Limite** : Maximum 3 tentatives de correction. Au-delà, rejet automatique.
- **Timer** : Si le citoyen ne resoumets pas dans les **15 jours**, le dossier est clôturé automatiquement.

### Étape 4 — Confirmation du rendez-vous biométrique (Agent CD → XFlow → Citoyen)

- L'agent CD confirme le créneau RDV (ou propose un nouveau créneau si le souhaité est indisponible).
- XFlow envoie un message `MSG_CNI_RETURN` (action: "rdv_confirme") vers XPortal.
- XPortal met à jour le statut du dossier : **"Rendez-vous confirmé"** avec les détails (lieu, date, heure).
- Le citoyen reçoit une **notification SMS/Email** avec les informations de rendez-vous.
- **Durée** : < 24h ouvrables après validation conformité

### Étape 5 — Capture biométrique au CD — PHYSIQUE (Citoyen → CD)

- Le citoyen se présente au CD à la date et l'heure confirmées.
- L'opérateur biométrique capte photo numérique, empreintes digitales (10 doigts) et signature.
- L'opérateur valide les données biographiques dans XFlow.
- Le superviseur CD valide le dossier complet avant transmission.
- **Durée** : 1 visite (20–30 min au guichet)
- **Contrainte légale** : présence physique obligatoire — non digitalisable

### Étape 6 — Transmission à la DGDN et production

- Le superviseur CD transmet le lot via le système VPN sécurisé DGDN.
- XFlow enregistre la transmission et notifie le citoyen que son dossier est en production.
- L'agent DGDN marque la CNI comme produite dans XFlow une fois la chaîne d'impression terminée.
- **Délai production** : 15 à 30 jours ouvrables (standard) / 48h (urgence)

### Étape 7 — Notification disponibilité et archivage (Système → Citoyen)

- Dès que la CNI est produite et disponible au CD, XFlow :
  - Archive le dossier dans la **GED Odoo** (données biographiques + photo + résultat)
  - Notifie automatiquement le citoyen par SMS + Email avec le lieu de retrait et les documents à présenter
  - Envoie `MSG_CNI_RETURN` (action: "dispo") à XPortal pour mise à jour du statut

### Étape 8 — Retrait de la CNI — PHYSIQUE (Citoyen → CD)

- Le citoyen se présente au CD avec son récépissé et sa pièce d'identité.
- L'agent délivre la CNI physique et fait signer le registre de délivrance.
- **Contrainte légale** : remise du titre physique obligatoire — non digitalisable

---

## Récapitulatif des Gains

| Friction AS-IS | Remède TO-BE | Gain |
|---------------|-------------|------|
| 2 déplacements pour le dépôt + retrait | 2 déplacements (bio + retrait) mais dépôt supprimé | Suppression du déplacement dépôt + économie temps paiement |
| Files d'attente au CD | Réservation créneau en ligne | Attente réduite, expérience optimisée |
| Paiement uniquement en espèces | Plateforme e-Gov externe (Flooz, TMoney, Visa, Mastercard) | Traçabilité 100 %, file d'attente supprimée |
| Aucune notification de statut | SMS + Email à 4 jalons (AR, RDV, en production, disponible) | Transparence totale, 0 déplacement inutile |
| 15 % dossiers incomplets au 1er dépôt | Validation Form.io au fil de la saisie | Taux de complétude cible ≥ 90 % |
| Délai de production imprévisible | Suivi XFlow en temps réel + notification proactive | Prévisibilité + réduction des déplacements inutiles |
| Pas de traçabilité numérique | Pipeline XFlow + GED Odoo | Audit trail complet pour chaque CNI |

---

## Contraintes Légales et Limites de la Digitalisation

| Élément | Statut | Justification légale |
|---------|--------|---------------------|
| Capture biométrique (photo, empreintes, signature) | **PHYSIQUE OBLIGATOIRE** | Décret n°2010-091 — capture biométrique en présence physique dans un CD agréé |
| Remise du titre physique (CNI biométrique) | **PHYSIQUE OBLIGATOIRE** | La CNI est un titre sécurisé avec puce électronique et éléments de sécurité physiques |
| CNI électronique dématérialisée | **Vision future** | Nécessite réforme de la Loi n°98-004 et reconnaissance légale d'une identité numérique souveraine |

---

## Boucle de Correction — Détail Technique

La boucle de correction est un mécanisme asynchrone **XFlow ↔ XPortal** :

1. L'agent CD indique dans XFlow le motif de non-conformité.
2. XFlow publie `MSG_CNI_RETURN` (action: "correction") vers XPortal via Kafka.
3. XPortal réveille le dossier du citoyen avec le formulaire de correction pré-rempli du motif.
4. Le citoyen uploade les pièces corrigées et resoumets.
5. XPortal publie `MSG_CNI_RESUB` vers XFlow via Kafka.
6. XFlow reprend à la vérification de conformité.
7. **Timer** : si pas de resoumission sous 15 jours → clôture automatique (`MSG_CNI_RETURN` action: "rejete").
8. **Limite** : si `nbCorrections > 3` → rejet automatique (`MSG_CNI_RETURN` action: "rejete").

---

## Messages Kafka inter-pools

| Message | Direction | Déclencheur | Payload |
|---------|-----------|-------------|---------|
| `MSG_CNI_START` | XPortal → XFlow | Paiement confirmé | Données formulaire + pièces + RDV souhaité |
| `MSG_CNI_PAY_ORDER` | XFlow → XPortal | AR envoyé — XFlow commande le paiement | Montant, référence |
| `MSG_CNI_PAY_CALLBACK` | Externe → XFlow | Confirmation paiement par la plateforme e-Gov | Statut paiement, référence transaction |
| `MSG_CNI_PAY_CONFIRM` | XFlow → XPortal | Paiement validé — dossier transmis | Confirmation |
| `MSG_CNI_RETURN` | XFlow → XPortal | Tout retour XFlow (correction / rdv_confirme / dispo / rejete) | action + payload contextuel |
| `MSG_CNI_RESUB` | XPortal → XFlow | Resoumission citoyen après correction | Pièces corrigées |
