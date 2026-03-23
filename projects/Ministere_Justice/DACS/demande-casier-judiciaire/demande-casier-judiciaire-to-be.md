# Cartographie TO-BE : Demande de Casier Judiciaire (Bulletin n°3)

## Vision Générale

Digitalisation du parcours citoyen via le portail XPortal et le moteur de workflow XFlow (Camunda Platform 7). Le citoyen soumet son dossier en ligne, paie électroniquement et reçoit des notifications automatiques à chaque jalon. **Reste obligatoirement en présentiel : le retrait du bulletin original (document officiel à signature manuscrite et cachet humide), conformément au Code de procédure pénale togolais.** Ce retrait unique est optimisé grâce à une notification SMS/Email qui garantit que le citoyen ne se déplace qu'une seule fois, lorsque le bulletin est effectivement prêt.

---

## Analyse de la Valeur Ajoutée (AVA) appliquée

| Étape AS-IS | Classification AVA | Décision TO-BE |
|-------------|-------------------|----------------|
| Paiement en espèces au guichet de caisse | SVA | **Supprimée** — paiement en ligne (Flooz / TMoney / Visa / Mastercard) |
| Dépôt physique du dossier au guichet | SVA | **Supprimée** — soumission en ligne via XPortal |
| Vérification manuelle de complétude (papier) | VAB | **Automatisée partiellement** — validation Form.io au fil de la saisie + vérification agent via tableau de bord XFlow |
| Consultation manuelle du fichier condamnations | VAB | **Conservée** (fichier non informatisé à ce jour) — l'agent instruit via le tableau de bord XFlow avec accès à toutes les informations |
| Rédaction, signature et cachet du bulletin | VAB + VAC | **Conservée** — obligation légale ; résultat saisi par l'agent dans XFlow |
| Validation chef de service | VAB | **Conservée et numérisée** — validation via tableau de bord XFlow |
| Second déplacement pour retrait sans notification | SVA | **Optimisée** — notification SMS/Email quand le bulletin est prêt ; **un seul déplacement** maintenu (titre officiel) |

---

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager — soumission, paiement, correction, suivi).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement back-office).
- **Bus de messaging** : Kafka (topic `bpmn.commands`) pour la synchronisation inter-pools XPortal <-> XFlow.
- **Identité** : Pré-remplissage transparent via e-ID (`config.users`) — le citoyen ne ressaisit pas ses données personnelles.
- **Paiement** : Plateforme de paiement e-Gov externe (Flooz, TMoney, Visa, Mastercard) — montant fixe 2 000 FCFA. Le citoyen est redirigé vers la plateforme ; la confirmation de paiement revient de manière asynchrone.
- **Notifications** : Service Tasks `tg.gouv.gnspd.sendNotification` (SMS + Email) à chaque jalon clé.
- **Archivage** : GED Odoo pour l'archivage numérique des dossiers et preuves de paiement.

---

## Acteurs et Systèmes

| Acteur / Système | Rôle |
|------------------|------|
| **Citoyen / Demandeur** | Soumet le dossier en ligne, paie, reçoit les notifications, se présente une seule fois au guichet pour retirer le bulletin |
| **Moteur XPortal** | Orchestration des écrans usager (soumission, paiement, correction, suivi statut) en attente des ordres XFlow |
| **Moteur XFlow** | Orchestration métier : vérification conformité, instruction, validation chef de service, notifications |
| **Agent de réception DACS** | Vérifie la conformité du dossier via tableau de bord XFlow (GNSPD User Task) |
| **Agent instructeur DACS** | Consulte le fichier des condamnations, saisit le résultat (néant ou mentions) dans XFlow, signe le bulletin |
| **Chef de service DACS** | Validation finale du bulletin via interface back-office |
| **Service de Notification** | SMS/Email automatiques à chaque changement de statut |
| **Plateforme de Paiement e-Gov** | Plateforme externe de paiement électronique (Flooz, TMoney, Visa, Mastercard) — le citoyen est redirigé hors de XPortal pour payer |
| **GED Odoo** | Archivage numérique des dossiers, pièces justificatives et preuves de paiement |

---

## Étapes Digitalisées

### Étape 1 — Soumission en ligne (Citoyen -> XPortal)

- Le citoyen s'authentifie sur le portail e-Gov. Son identité est pré-remplie via e-ID (nom, prénom, téléphone, email).
- Il remplit le formulaire Form.io (wizard multi-étapes) avec les informations complémentaires nécessaires.
- Il uploade les **pièces justificatives** numérisées :
  - Copie de la pièce d'identité nationale ou passeport en cours de validité (PDF/JPEG)
  - Copie de l'acte de naissance (PDF/JPEG)
- **Validation au fil de l'eau** : Form.io bloque les erreurs pendant la saisie (formats, tailles de fichiers, champs obligatoires).
- **Durée** : Immédiat

### Étape 2 — Paiement en ligne (Citoyen -> Plateforme e-Gov externe)

- Le système affiche le montant fixe de **2 000 FCFA** et redirige le citoyen vers la **plateforme de paiement e-Gov externe**.
- Le citoyen procède au paiement sur cette plateforme (Flooz / TMoney / Visa / Mastercard).
- Confirmation de paiement automatique (reçu électronique par SMS/Email) retournée à XPortal.
- Le dossier complet (formulaire + pièces + preuve de paiement) est transmis au back-office XFlow via Kafka (`MSG_CJ_START`).
- **SLA** : Si le paiement n'est pas confirmé sous 30 minutes, la demande est annulée automatiquement.
- **Durée** : Immédiat

### Étape 3 — Accusé de réception (Système -> Citoyen)

- XPortal envoie automatiquement un **accusé de réception** par SMS + Email au citoyen avec :
  - Le numéro de suivi de la demande
  - La liste des pièces reçues
  - Le délai de traitement estimé (3 jours ouvrables)
- **Durée** : < 5 minutes après soumission

### Étape 4 — Vérification de conformité du dossier (Agent DACS -> XFlow)

- L'agent de réception reçoit le dossier dans son **tableau de bord XFlow**.
- Il vérifie la conformité des pièces justificatives (authenticité, lisibilité, validité de la pièce d'identité, présence de l'acte de naissance).
- **Trois décisions possibles** :
  - **Conforme** — transmission à l'agent instructeur
  - **Correction nécessaire** — notification au citoyen avec motif détaillé
  - **Rejet définitif** — notification au citoyen avec motif (ex : faux documents)
- **Durée** : <= 24h ouvrables
- **SLA** : Rappel automatique à l'agent après 24h (N06) + escalade au superviseur après 48h (N08)

### Étape 4a — Boucle de correction (Citoyen -> XPortal)

- XFlow publie un message Kafka `MSG_CJ_RETURN` (action: "correction") vers XPortal.
- XPortal réveille le dossier citoyen et affiche un **écran de resoumission** Form.io avec le motif de l'agent.
- Le citoyen corrige et resoumets les pièces via son dossier existant (**sans recréer de nouveau dossier**).
- Le flux retourne à XFlow pour nouvelle vérification.
- **Limite** : Maximum 3 tentatives de correction. Au-delà, rejet automatique avec notification.
- **Timer** : Si le citoyen ne resoumets pas dans les **15 jours**, le dossier est clôturé automatiquement.

### Étape 5 — Instruction du bulletin (Agent instructeur -> XFlow)

- Une fois le dossier validé conforme, l'agent instructeur reçoit une **tâche XFlow** dans son tableau de bord.
- Il consulte le fichier national des condamnations et saisit le résultat dans XFlow :
  - **Néant** — aucune condamnation enregistrée
  - **Mentions** — saisie des condamnations définitives
- L'agent prépare le bulletin physique (signature manuscrite + cachet humide — obligation légale).
- **Durée** : 1–3 jours ouvrables
- **SLA** : Délai global (conformité + instruction) <= 3 jours ouvrables

### Étape 6 — Validation chef de service (Chef de service -> XFlow)

- Le chef de service reçoit le bulletin instruit dans son **tableau de bord XFlow** pour validation finale.
- Il contrôle la conformité du bulletin (données correctes, signature, cachet).
- **Trois décisions possibles** :
  - **Valider** — bulletin mis à disposition pour retrait (`MSG_CJ_RETURN` action: "accepte")
  - **Renvoyer en correction** — retour à l'agent instructeur pour complément
  - **Rejeter définitivement** — notification au citoyen (`MSG_CJ_RETURN` action: "rejete")
- **Durée** : <= 4h ouvrables

### Étape 7 — Notification et retrait du bulletin — PHYSIQUE (Citoyen -> DACS)

- Le système **notifie automatiquement** le citoyen par SMS + Email que son bulletin est prêt :
  - Lieu de retrait (guichet DACS, Lomé ou tribunal régional selon préférence)
  - Documents à présenter (récépissé de dossier + pièce d'identité originale)
- Le citoyen se présente **une seule fois** au guichet pour retirer le bulletin signé et cacheté.
- Cette étape est un **pré-requis légal obligatoire** : le Code de procédure pénale togolais exige que le bulletin porte une signature manuscrite et un cachet humide d'un agent habilité.
- **Durée** : 1 visite (déplacement + 10 minutes au guichet)

---

## Récapitulatif des Gains

| Friction AS-IS | Remède TO-BE | Gain |
|---------------|-------------|------|
| 2 déplacements obligatoires | 1 seul déplacement (retrait) | Économie de 1 voyage + temps |
| Paiement uniquement en espèces | Plateforme e-Gov externe (Flooz, TMoney, Visa, Mastercard) | Traçabilité 100 %, file d'attente supprimée |
| Dépôt physique du dossier | Soumission en ligne 24h/7j | Accessibilité totale, zéro déplacement pour le dépôt |
| Aucune notification | SMS + Email à chaque jalon | Transparence totale, déplacement certifié utile |
| 15 % dossiers incomplets au guichet | Validation Form.io au fil de la saisie | Taux de complétude cible >= 90 % |
| Délai imprévisible | SLA de 3 jours ouvrables + escalade automatique | Prévisibilité et respect des engagements |

---

## Contraintes Légales et Limites de la Digitalisation

| Élément | Statut | Justification légale |
|---------|--------|---------------------|
| Retrait du bulletin original | **Maintenu PHYSIQUE** | Code de procédure pénale — signature manuscrite + cachet humide obligatoires |
| Consultation du fichier des condamnations | **Inchangée** (fichier papier) | Fichier non informatisé à ce jour — à terme, digitalisation du fichier réduira le délai à 24h |
| Bulletin électronique sécurisé (QR code) | **Vision future** | Nécessite réforme légale reconnaissant la valeur probante de la signature électronique pour cet acte |

---

## Boucle de Correction — Détail Technique

La boucle de correction est un mécanisme asynchrone **XFlow <-> XPortal** :

1. L'agent DACS indique dans XFlow le motif de non-conformité.
2. XFlow publie un message Kafka `MSG_CJ_RETURN` (action: "correction") vers XPortal.
3. XPortal réveille le dossier du citoyen avec le formulaire de correction pré-rempli du motif.
4. Le citoyen uploade les pièces corrigées et resoumets.
5. XPortal publie un message Kafka `MSG_CJ_RESUB` vers XFlow.
6. XFlow reprend l'instruction au niveau de la vérification de conformité.
7. **Timer** : si pas de resoumission sous 15 jours — clôture automatique (`MSG_CJ_RETURN` action: "rejete").
8. **Limite** : si `nbCorrections > 3` — rejet automatique (`MSG_CJ_RETURN` action: "rejete").
