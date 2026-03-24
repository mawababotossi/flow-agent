# Cartographie TO-BE : Demande d'Extrait d'Acte de Naissance

## Vision Globale

La demande d'extrait d'acte de naissance devient un service **100% en ligne pour la soumission et le suivi**, tout en conservant le retrait physique obligatoire du document signé. Le citoyen n'a plus besoin de se déplacer dans la commune de naissance pour déposer sa demande — il soumet en ligne depuis n'importe quel appareil. L'agent DACS instruit le dossier depuis son interface XFlow, et le citoyen est notifié à chaque étape.

### Contraintes physiques maintenues (non digitalisables)
- **Signature manuscrite** de l'officier d'état civil sur l'extrait
- **Cachet officiel** (cachet humide) de la commune ou du DACS
- **Remise du document** : obligatoirement en main propre au guichet, contre présentation de la pièce d'identité originale

---

## Gains de la Transformation

| Friction AS-IS | Solution TO-BE | Gain |
|----------------|----------------|------|
| Déplacement obligatoire pour déposer la demande | Formulaire en ligne accessible H24 | 1 déplacement → 0 (pour la soumission) |
| Méconnaissance des procédures | Guide interactif dans le formulaire + aide contextuelle | Zéro retour au guichet par ignorance |
| Aucun suivi en temps réel | Notifications SMS/Email automatiques à chaque étape | Transparence totale |
| Falsifications non détectables | QR Code d'authentification ATD sur l'extrait (futur) | Sécurisation de bout en bout |
| Paiement en espèces non traçable | Service gratuit (premier extrait) — hors périmètre e-Gov | N/A pour la première délivrance |
| Gestion papier des dossiers | Dossier numérique traçable dans XFlow/Odoo | Archivage 100% numérique de la demande |

---

## Architecture Technique Cible

```
Citoyen (mobile/PC)
       │
       ▼
[XPortal — Portail Citoyen]
  • Formulaire Form.io Wizard (soumission demande)
  • Authentification e-ID (pré-remplissage identité)
  • Suivi en temps réel (statuts BPMN)
  • Formulaire de correction (si demandé)
       │ Kafka (MSG_ACTENAISSANCE_START)
       ▼
[XFlow — Camunda Platform 7]
  • Réception et enregistrement automatique
  • File de traitement agent état civil
  • Notification email/SMS (GNSPD flow-notify)
  • Décision : Trouvé / Correction / Rejet
  • Validation chef de service
       │
       ▼
[DACS — Guichet physique]
  • Impression de l'extrait
  • Signature officier + cachet
  • Remise au citoyen
```

---

## Étapes TO-BE

### Étape 1 — Soumission en ligne *(Citoyen / XPortal)*
- Le citoyen accède au portail et s'authentifie (e-ID).
- Les champs **nom, prénom, email, téléphone** sont pré-remplis automatiquement depuis le profil e-ID.
- Il complète : date de naissance, commune de naissance, type d'extrait souhaité (avec filiation / copie intégrale), objet de la demande, lien de parenté si demande pour un tiers.
- Il joint une copie numérique de sa pièce d'identité (PDF/JPEG, max 2 Mo).
- Un **numéro de dossier unique** est généré à la soumission.
- **Statut portail** : `Submited`

### Étape 2 — Accusé de réception automatique *(XFlow / Système)*
- XFlow reçoit le dossier via Kafka.
- Notification automatique **email + SMS** : accusé de réception avec numéro de référence.
- Le dossier apparaît dans la file de l'agent état civil.
- **Statut portail** : `PendingBackOffice`

### Étape 3 — Instruction par l'agent état civil *(Agent DACS / XFlow)*
- L'agent ouvre le dossier dans son interface XFlow.
- Il consulte le registre (papier ou numérisé) pour localiser l'acte.
- Il enregistre sa décision dans le formulaire d'instruction :
  - **Acte trouvé** → prépare l'extrait, passe à l'étape 4
  - **Information insuffisante** → demande de correction (motif renseigné)
  - **Acte introuvable** → rejet avec orientation vers jugement supplétif
- **SLA** : 72h

### Étape 3a — Correction du dossier *(Citoyen / XPortal — Boucle)*
- Le citoyen reçoit une notification email/SMS avec le motif de correction.
- Il accède au portail et corrige les informations demandées (commune précisée, date rectifiée, etc.).
- La demande corrigée est automatiquement renvoyée à l'agent.
- **Maximum 3 corrections**. Au-delà, la demande est automatiquement clôturée.
- **SLA** : 15 jours pour répondre, sinon clôture automatique.
- **Statut portail** : `PendingUser`

### Étape 4 — Validation Chef de Service *(Chef DACS / XFlow)*
- Après instruction positive de l'agent, le chef de service valide la délivrance.
- Il peut approuver ou rejeter (ex : dossier frauduleux, anomalie détectée).
- **SLA** : 48h
- **Statut portail** : `PendingBackOffice`

### Étape 5 — Notification du résultat *(XFlow / Système)*
- **Si accepté** : notification SMS+Email "Votre extrait d'acte de naissance est prêt. Présentez-vous au guichet DACS avec votre pièce d'identité et votre numéro de dossier."
- **Si rejeté** : notification SMS+Email avec motif et, si pertinent, orientation vers la procédure de jugement supplétif.
- **Statut portail** : `Success` ou `Fail`

### Étape 6 — Retrait physique *(Citoyen → Guichet DACS) — PHYSIQUE*
- Le citoyen se présente au guichet DACS.
- L'agent vérifie l'identité (CNI/passeport original) et le numéro de dossier.
- L'officier d'état civil signe l'extrait et appose le cachet officiel.
- Le document est remis en main propre.
- **(Futur)** QR Code ATD apposé sur l'extrait pour vérification d'authenticité en ligne.

---

## Règles Métier

| Règle | Description |
|-------|-------------|
| **Éligibilité** | Être l'intéressé(e), un parent direct, ou un représentant légal dûment mandaté |
| **Boucle de correction** | Maximum 3 resoumissions. Délai de réponse : 15 jours par cycle. Au-delà : clôture automatique |
| **SLA instruction** | 72h ouvrables pour l'agent, 48h pour le chef de service |
| **Timer d'escalade** | Sans action de l'agent après 72h, alerte automatique au chef de service |
| **Service gratuit** | Aucun frais pour la première délivrance. Duplicata : à préciser selon barème DACS |
| **Acte introuvable** | Orientation vers jugement supplétif au TGI — hors périmètre de ce service digital |
| **Retrait tiers** | Autorisé avec procuration notariée + pièce d'identité du mandataire |

---

## KPIs Cibles TO-BE

| KPI | Cible |
|-----|-------|
| Délai moyen de traitement (acte trouvé) | < 72h (vs 1–4 semaines AS-IS) |
| Taux de satisfaction citoyen | ≥ 85% |
| Taux de dossiers complets à la première soumission | ≥ 70% |
| Délai de notification après décision | < 5 minutes (automatique) |
| Taux d'utilisation du canal en ligne | ≥ 60% (an 1) → ≥ 85% (an 3) |
