# Cartographie TO-BE : Demande de Mise à la Retraite et de Liquidation de Pension

**Version** : 1.0
**Date** : 2026-03-25
**Organisme** : Caisse de Retraite du Togo (CRT) / Ministère de la Fonction Publique

---

## Vision Générale

Le processus de liquidation de pension est entièrement repensé via une approche **Digital-First** : le fonctionnaire soumet son dossier en ligne depuis n'importe quel lieu, la CRT instruit via un tableau de bord back-office centralisé, et le titre de pension est généré automatiquement et mis à disposition sur le portail. Le contrôle d'existence annuel devient biométrique à distance. Le délai de traitement cible passe de **3-6 mois à moins de 30 jours ouvrables** après réception du dossier complet.

---

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement back-office).
- **Bus de messaging** : Kafka (topics `bpmn.commands`) pour la synchronisation inter-pools.
- **Identité** : Pré-remplissage transparent via e-ID (`config.users`).
- **Notifications** : Service Tasks `tg.gouv.gnspd.sendNotification` (SMS + Email).
- **Génération de documents** : Service Task `flow-generate-template` (PDF normé).
- **Signature** : Signature physique du DG CRT (hybride — préparation numérique + visa physique ou qualification électronique à terme).
- **Paiement** : Néant — service gratuit.
- **SIRH** : Saisie manuelle des données de carrière par le liquidateur (pas d'interconnexion active).

---

## Analyse de la Valeur Ajoutée (AVA) — Suppression des Sans-Valeur-Ajoutée

| Étape AS-IS | Classification | Action TO-BE |
|-------------|---------------|--------------|
| Courses de guichet en guichet pour rassembler les pièces | SVA | Supprimée — toutes les pièces uploadées en ligne |
| Transmission papier DRH → CRT | SVA | Supprimée — transmission électronique |
| Dépôt physique du dossier | SVA | Supprimé — soumission en ligne |
| Enregistrement manuel (Access/Excel) | SVA | Supprimé — enregistrement automatique |
| Notification par courrier postal | SVA | Supprimée — SMS/email instantanés |
| Calcul de la pension | VAB | Conservé — calcul par le liquidateur |
| Déplacement annuel contrôle d'existence | SVA (partiel) | Biométrie mobile ou bureau régional |
| Instruction et vérification droits | VAB | Conservée — user task back-office CRT |
| Contre-vérification contrôleur | VAB | Conservée — user task back-office CRT |
| Signature DG CRT | VAB | Conservée — hybride (préparation numérique + visa DG) |

---

## Acteurs et Systèmes TO-BE

| Acteur / Système | Rôle |
|------------------|------|
| Fonctionnaire (citoyen) | Soumet le dossier en ligne, reçoit les notifications, télécharge son titre |
| e-ID (XPortal) | Pré-remplit automatiquement les données d'identité du demandeur |
| Système XPortal | Orchestration des écrans usager (soumission, correction, suivi) |
| Système XFlow (Camunda) | Orchestration back-office CRT (instruction, validation, génération) |
| Liquidateur CRT | Instruit le dossier via tableau de bord XFlow |
| Contrôleur CRT | Contre-vérifie via tableau de bord XFlow |
| Directeur Général CRT | Signe le titre (hybride) — tableau de bord + visa physique |
| Service comptable CRT | Reçoit l'ordre de mise en paiement automatiquement |
| Service SMS/Email | Notifications automatiques aux jalons clés |

---

## Étapes Digitalisées

### 1. Soumission du dossier en ligne (Citoyen → XPortal)

**Remplace** : Étapes AS-IS 1, 2, 3 (information, constitution du dossier, dépôt physique)

- Accès au portail citoyen, authentification via e-ID
- Les données d'identité (nom, prénom, date de naissance, numéro matricule, adresse) sont **pré-remplies automatiquement**
- Formulaire wizard en plusieurs étapes :
  - Étape 1 : Identification (pré-remplie)
  - Étape 2 : Type de demande (retraite d'office / anticipée / invalidité / réversion)
  - Étape 3 : Informations de carrière (dernier poste, ministère d'affectation)
  - Étape 4 : Upload des pièces justificatives avec liste de contrôle interactive
  - Étape 5 : Coordonnées bancaires (RIB/CCP)
  - Étape 6 : Récapitulatif et validation
- La liste de contrôle interactive **bloque la soumission si une pièce obligatoire est manquante**
- Accusé de réception immédiat par email et SMS avec numéro de dossier

**Gains** : Suppression des 2-3 mois de constitution de dossier, zéro déplacement, 0 % d'incomplétude bloquante

---

### 1a. Boucle de correction — Retour citoyen (XPortal)

**Remplace** : Notification par courrier + aller-retour physique au guichet

- Déclenchée par la décision "Correction requise" de l'agent CRT (step 3)
- XFlow publie un message Kafka `correction` vers XPortal
- XPortal réveille le dossier citoyen et affiche un écran de resoumission (`Activity_P_Corrections`)
- Le citoyen reçoit un SMS/email avec le motif précis de la demande de correction
- Il corrige uniquement les éléments signalés, **sans recréer un nouveau dossier**
- Après resoumission, le flux retourne à XFlow pour instruction
- Maximum **3 tentatives** ; au-delà → rejet automatique avec notification
- Timer : clôture automatique si pas de resoumission dans **15 jours calendaires**

---

### 2. Réception et enregistrement automatique (Système — XFlow)

**Remplace** : Étape AS-IS 4 (enregistrement manuel)

- Enregistrement instantané dans la base de données CRT
- Attribution automatique d'un numéro de référence officiel
- Contrôle de format des pièces jointes (PDF/JPEG, taille max 5 MB par fichier)
- Notification de réception envoyée au demandeur (SMS + email)
- Durée : **immédiat**

---

### 3. Instruction du dossier — Vérification des droits (Liquidateur CRT — XFlow userTask)

**Remplace** : Étape AS-IS 5 (instruction manuelle)

- Le liquidateur reçoit une notification de nouveau dossier dans son tableau de bord
- Il accède aux pièces uploadées et aux données de carrière saisies.
- Le calcul de pension est effectué par le liquidateur.
- Le liquidateur vérifie, ajuste si nécessaire, et prend une décision :
  - **Conforme** → passe à la contre-vérification (step 4)
  - **Correction requise** → renvoie au citoyen (boucle 1a) avec motif détaillé
  - **Rejet** → notification de rejet au demandeur avec motif et voies de recours
- SLA : **10 jours ouvrables**

---

### 4. Contre-vérification (Contrôleur CRT — XFlow userTask)

**Remplace** : Étape AS-IS 6 (vérification contrôleur)

- Le contrôleur vérifie le calcul et les données avant production du titre
- En cas d'erreur interne : renvoie au liquidateur (boucle interne)
- Validation → passage à la signature DG
- SLA : **5 jours ouvrables**

---

### 5. Signature du titre de pension — PHYSIQUE/HYBRIDE (DG CRT)

**Conservée** : Obligation légale (signature manuscrite)

- Le système génère automatiquement le **projet de titre de pension** en PDF (template normé ATD)
- Le DG CRT reçoit la liste des titres à signer dans son tableau de bord
- Il signe physiquement les titres préparés (ou via signature électronique qualifiée si habilitée)
- Le titre signé est numérisé et versé dans le dossier numérique par un agent CRT
- SLA : **3 jours ouvrables**

---

### 6. Génération PDF et notification finale (Système — XFlow)

**Remplace** : Notification par courrier postal + remise du livret

- Génération automatique du titre de pension en PDF normé.
- Mise à disposition sur le portail citoyen (téléchargement sécurisé)
- Notification SMS + email au demandeur : "Votre titre de pension est disponible"
- Transmission automatique au service comptable pour ordonnancement du premier versement
- Mise à jour automatique du fichier des pensionnés actifs
- Durée : **immédiat**

---

### 7. Contrôle d'existence annuel — HYBRIDE

**Partiellement numérisé** : Contrainte légale allégée

- Rappel automatique 30 jours avant l'échéance (SMS + email)
- Le pensionné peut attester son existence via :
  - **Option A (numérique)** : Authentification biométrique sur l'application mobile (empreinte digitale via e-ID mobile)
  - **Option B (physique)** : Présentation au guichet CRT ou à un bureau régional ou mairie habilitée
- En cas de non-renouvellement dans les **60 jours** suivant l'échéance : suspension automatique de la pension avec notification
- Interconnexion avec le registre de l'état civil : détection automatique des décès déclarés → suspension immédiate des versements

---

## Boucles de Correction et Cas d'Erreur

### Boucle de Correction Dossier Incomplet

```
XFlow (step 3 : Correction requise)
  → Kafka MSG_PENSION_RETURN (correction)
  → XPortal réveille Activity_P_Corrections
  → Citoyen corrige et resoumets
  → Kafka MSG_PENSION_RESUB
  → XFlow reprend à l'instruction (step 3)
  → Maximum 3 tentatives, timer P15D
```

### Cas de Rejet

- Notification détaillée au demandeur avec le motif précis
- Information sur les voies de recours (recours gracieux à la CRT, recours contentieux)

---

## Gains Attendus (KPIs Cibles)

| Indicateur | AS-IS | TO-BE Cible |
|------------|-------|-------------|
| Délai constitution dossier | 2-3 mois | Immédiat (formulaire en ligne) |
| Délai traitement CRT | 3-6 mois | < 30 jours ouvrables |
| Taux dossiers incomplets | ~50 % | < 5 % (liste de contrôle interactive) |
| Déplacements citoyen | 5-10 déplacements | 0 (sauf retrait titre si souhaité) |
| Calcul de la pension | Partiellement manuel | Saisie et calcul par liquidateur |
| Fraude pensions décédés | Non détectée en temps réel | Détection automatique (interconnexion état civil) |
| Contrôle d'existence physique | 1 déplacement/an | Option biométrie mobile |
| Notifications | Courrier postal (2-5 jours) | SMS/email immédiat |

---

## Contraintes et Limites

| Contrainte | Nature | Traitement |
|------------|--------|-----------|
| Signature manuscrite du DG CRT sur le titre de pension | Légale obligatoire | Processus hybride : préparation numérique + signature physique |
| Acte de mise à la retraite signé par le Ministre de la FP | Légale obligatoire | Uploadé comme pièce justificative numérisée par l'agent |
| Contrôle d'existence physique (forme actuelle) | Légale / pratique | Biométrie mobile introduite comme alternative, présence physique conservée en option |
