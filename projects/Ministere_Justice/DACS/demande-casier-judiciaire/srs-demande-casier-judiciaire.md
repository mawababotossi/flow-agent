# Spécifications Fonctionnelles et Techniques (SRS)
# Demande de Casier Judiciaire (Bulletin n°3)

---

| Champ | Valeur |
|-------|--------|
| **FDS** | Ministère de la Justice — Direction des Affaires Civiles et du Sceau (DACS) |
| **Service parent** | Direction des Affaires Civiles et du Sceau |
| **Intégrateur** | ATD — Agence Togo Digital |
| **Chef de projet ATD** | À renseigner |
| **Point focal FDS** | À renseigner |
| **Date de création** | 2026-03-24 |
| **Date de dernière mise à jour** | 2026-03-24 |
| **Back-office** | XFlow (Camunda Platform 7) |
| **Déploiement cible** | XPortal — Portail national des services publics |
| **Version** | 1.0.0 |

---

## Historique des changements

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-03-24 | ATD | Création initiale du SRS |

---

## Section 1 — Identification du service

### 1.1 Description fonctionnelle

Le casier judiciaire (Bulletin n°3) est un document officiel délivré par la Direction des Affaires Civiles et du Sceau (DACS) du Ministère de la Justice. Il atteste de l'absence ou de la présence de condamnations pénales dans le fichier national et est exigé dans de nombreuses situations de la vie civile et professionnelle : recrutements dans la fonction publique, candidatures aux concours des grandes écoles, demandes de visa, création d'entreprise, adoption, etc.

Dans le cadre du Plan d'Accélération de la Digitalisation (PAD) du Togo, ce service bascule vers un mode hybride : la soumission de la demande, le paiement des frais et le suivi du dossier se font entièrement en ligne via XPortal, tandis que le retrait du bulletin physique reste obligatoire au guichet de la DACS — la signature manuscrite et le cachet humide étant légalement requis par le Code de procédure pénale et non substituables par une signature électronique à ce stade. Ce basculement permet d'éliminer le premier déplacement (dépôt du dossier), de supprimer les rejets pour pièces manquantes grâce à la validation temps réel, et de notifier automatiquement le citoyen à chaque étape de traitement.

### 1.2 Fiche d'identité du service

| Attribut | Valeur |
|----------|--------|
| **Code service** | SRV-DACS-2026-001 |
| **Catégorie** | Justice — Etat civil et casier judiciaire |
| **Bénéficiaires** | Toute personne physique (citoyen togolais ou résident) majeure souhaitant obtenir son bulletin de casier judiciaire n°3 |
| **Fréquence d'usage** | Ponctuelle (sur besoin) |
| **Délai réglementaire** | 3 jours ouvrables (AS-IS) → 2–3 jours ouvrables (TO-BE, hors délai postal) |
| **Coût** | 2 000 FCFA (fixe, payable en ligne) |
| **Langue** | Français |
| **Canaux de soumission** | XPortal (web + mobile) |
| **Canal de retrait** | Guichet physique DACS (obligation légale) |
| **Service hybride** | Oui — retrait physique obligatoire |

### 1.3 Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|--------|--------|----------------------|---------------|-------------------|
| **Citoyen** | Toute personne physique majeure | Soumet la demande en ligne, paie, corrige si demandé, retire le bulletin au guichet | XPortal (portail citoyen) | N/A |
| **Agent instructeur DACS** | Agent administratif DACS habilité | Vérifie les pièces, consulte le fichier national des condamnations (papier), rédige le bulletin | XFlow (UserTask instruction) | 72h max |
| **Chef de service DACS** | Responsable hiérarchique DACS | Contrôle le bulletin rédigé, valide ou rejette | XFlow (UserTask validation) | 24h max |
| **Agent de guichet DACS** | Agent administratif affecté au guichet | Vérifie le récépissé et la pièce d'identité originale, remet le bulletin | Guichet physique (hors système) | N/A |
| **Système XFlow** | Moteur de workflow Camunda 7 | Orchestre le processus back-office, envoie les notifications, gère les états | XFlow (automatique) | Temps réel |
| **Plateforme e-Gov** | Système de paiement externe | Traite les paiements en ligne et renvoie le callback à XFlow | API callback (externe) | Temps réel |
| **Centre d'appel N1** | Support citoyen ATD | Assiste les citoyens en difficulté sur le portail | XPortal (consultation) | 4h réponse |

---

## Section 2 — Design du formulaire Form.io

### 2.1 Structure du formulaire (Wizard)

| Étape | Clé (`key`) | Titre | Description |
|-------|-------------|-------|-------------|
| 1 | `stepIntro` | Présentation du service | Landing page : objet, conditions, pièces, tarif, étapes |
| 2 | `stepIdentite` | Identité du demandeur | Champs e-ID pré-remplis et verrouillés |
| 3 | `stepDemande` | Informations de la demande | Motif, usage, informations complémentaires |
| 4 | `stepPieces` | Pièces justificatives | Upload pièce d'identité + acte de naissance |
| 5 | `stepRecapitulatif` | Récapitulatif et soumission | Récapitulatif intelligent + certification |

### 2.2 Détail des champs par onglet

#### Onglet 1 — Présentation du service (`stepIntro`)

Panel de type landing page premium. Aucun champ de saisie. Contient des composants `htmlelement` richement formatés (Info Pills, conditions, pièces requises, étapes, tarif). Pas de bouton submit (géré nativement par P-Studio).

#### Onglet 2 — Identité du demandeur (`stepIdentite`)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom de famille | `textfield` | Oui | Texte, max 100 car. | Profil Citoyen (`config.users.lastName`) | Verrouillage dynamique `logic` si non vide |
| `prenom` | Prénom(s) | `textfield` | Oui | Texte, max 100 car. | Profil Citoyen (`config.users.firstName`) | Verrouillage dynamique `logic` si non vide |
| `dateNaissance` | Date de naissance | `datetime` | Oui | Format JJ/MM/AAAA, antérieure à J | Saisie citoyen | `enableMaxDateInput: true` avec date du jour |
| `lieuNaissance` | Lieu de naissance | `textfield` | Oui | Texte, max 150 car. | Saisie citoyen | Ville et pays si naissance à l'étranger |
| `nationalite` | Nationalité | `select` | Oui | Liste déroulante | API (`config.apiBaseUrl/references/nationalites`) | `dataSrc: "url"` |
| `numeroCNI` | Numéro de la pièce d'identité | `textfield` | Oui | Alphanumérique, 6–20 car. | Saisie citoyen | `validateOn: "blur"`, message custom |
| `typePiece` | Type de pièce d'identité | `select` | Oui | CNI / Passeport / Titre de séjour | `dataSrc: "values"` | Valeurs statiques |
| `numeroTelephone` | Numéro de téléphone | `phoneNumber` | Oui | Format `228 99 99 99 99` | Profil Citoyen (`config.users.phone`) | `inputMask: "228 99 99 99 99"`, verrouillage dynamique |
| `eMail` | Adresse email | `email` | Oui | Format email valide | Profil Citoyen (`config.users.email`) | Verrouillage dynamique |

#### Onglet 3 — Informations de la demande (`stepDemande`)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `motifDemande` | Motif de la demande | `select` | Oui | Liste valeurs statiques | `dataSrc: "values"` | Valeurs : Emploi public, Concours grandes écoles, Visa, Adoption, Création entreprise, Autre |
| `motifAutre` | Précisez le motif | `textarea` | Non | Texte libre, max 300 car. | Saisie citoyen | `customConditional: "show = (data.motifDemande === 'Autre');"` |
| `usagePrevu` | Usage prévu du bulletin | `textarea` | Non | Texte libre, max 500 car. | Saisie citoyen | Champ informatif |
| `organismeDestinataire` | Organisme destinataire | `textfield` | Non | Texte, max 200 car. | Saisie citoyen | Ex: "Ministère de l'Éducation Nationale" |
| `langueDocument` | Langue du bulletin | `select` | Oui | Français / Anglais (si disponible) | `dataSrc: "values"` | Défaut : Français |

#### Onglet 4 — Pièces justificatives (`stepPieces`)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pieceIdentite` | Pièce d'identité (recto/verso) | `file` | Oui | PDF, JPG, PNG — max 2 MB | Upload citoyen | `storage: "base64"`, `multiple: false` |
| `acteNaissance` | Acte de naissance | `file` | Oui | PDF, JPG, PNG — max 2 MB | Upload citoyen | `storage: "base64"`, `multiple: false` |
| `photoIdentite` | Photo d'identité récente | `file` | Non | JPG, PNG — max 1 MB | Upload citoyen | Optionnel selon instructions DACS |

#### Onglet 5 — Récapitulatif (`stepRecapitulatif`)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | (Récapitulatif dynamique) | `htmlelement` | — | Parseur JS ATD | Calculé | Exclut : `luEtApprouve`, champs hidden |
| `luEtApprouve` | Je certifie sur l'honneur l'exactitude des informations fournies et reconnais que toute fausse déclaration m'expose à des poursuites pénales | `checkbox` | Oui | `validateOn: "submit"` | Saisie citoyen | Bloque la soumission si non coché |

### 2.3 Actions du formulaire (P-Studio)

| Action | Type | Configuration | Déclencheur |
|--------|------|---------------|-------------|
| **Publish to RabbitMQ** | `rabbitmq` | Topic : `submissions.topic` — Queue : `workflows-engine.main.queue` — Payload : `{{ submission.data }}` | À chaque soumission validée |

> **Note** : Ce service est payant (2 000 FCFA). Le paiement est orchestré par XFlow via la plateforme e-Gov externe et un formulaire de paiement dédié (`formio-paiement-demande-casier-judiciaire.json`). L'action `Calculate Costs` (mode `fixed`, `fixedPrice: 2000`) est configurée dans ce formulaire distinct.

### 2.4 Configuration des environnements

Le bloc `config` du formulaire Form.io principal est structuré comme suit :

```json
{
  "development": {
    "apiBaseUrl": "https://api.dev.gouv.tg/api/v1/admin",
    "appName": "Développement",
    "users": {
      "firstName": "user.firstName",
      "lastName": "user.lastName",
      "fullName": "user.fullName",
      "email": "user.email",
      "username": "user.username",
      "userId": "user.userId",
      "accountType": "user.accountType",
      "language": "user.language",
      "phone": "user.phone"
    }
  },
  "sandbox": {
    "apiBaseUrl": "https://api.sandbox.gouv.tg/api/v1/admin",
    "appName": "Sandbox",
    "users": { "/* idem */" }
  },
  "preproduction": {
    "apiBaseUrl": "https://api.preprod.gouv.tg/api/v1/admin",
    "appName": "Pré-production",
    "users": { "/* idem */" }
  },
  "production": {
    "apiBaseUrl": "https://api.gouv.tg/api/v1/admin",
    "appName": "Production",
    "users": { "/* idem */" }
  }
}
```

**Endpoints API consommés par le formulaire :**

| Endpoint | Usage |
|----------|-------|
| `config.apiBaseUrl/references/nationalites` | Liste des nationalités (select dynamique) |
| `config.apiBaseUrl/references/pays` | Liste des pays (si besoin) |

**Configuration KMS du startEvent XFlow** (distincte du formulaire) :

```json
{
  "development": {},
  "sandbox": {},
  "preproduction": {},
  "production": {}
}
```

> **Exception documentée (Pattern P5)** : Le fichier national des condamnations n'est pas informatisé. Aucune intégration Odoo ou API n'est prévue pour la vérification automatique. L'agent instructeur consulte manuellement le fichier papier. Le startEvent XFlow porte des blocs de configuration vides.

---

## Section 3 — Le processus BPMN 2.0

### 3.1 Vue d'ensemble

| Attribut | Valeur |
|----------|--------|
| **Nom du processus** | Demande de Casier Judiciaire (Bulletin n°3) |
| **Type** | Collaboration dual-pool XPortal / XFlow |
| **Plateforme** | Camunda Platform 7.17 |
| **Fichier** | `bpmn-demande-casier-judiciaire.bpmn` |
| **Messages Kafka** | 6 (service payant) |
| **Pools** | 2 (XPortal + XFlow), tous deux `isExecutable="true"` |
| **Service payant** | Oui — 2 000 FCFA via e-Gov |
| **Boucle de correction** | Oui — max 3 tentatives, timer 15 jours |
| **Retrait physique** | Oui — obligation légale (étape hors BPMN) |
| **Intégration Odoo** | Non (fichier non informatisé — pattern P5) |

### 3.2 Étapes détaillées

#### Lane PORTAL (côté citoyen)

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|----|----------------|-------------|--------|-------|---------------------|
| 01 | **Soumission de la demande** | Le citoyen remplit le formulaire en ligne (identité pré-remplie), uploade ses pièces et soumet. | Citoyen | Immédiat | Dossier soumis → SendTask vers XFlow (MSG_CASIERJUD_START) |
| 02 | **Attendre réponse XFlow** | XPortal attend le retour du moteur XFlow (ReceiveTask multi-entrante MSG_CASIERJUD_RETURN). | Système | Variable | Reçoit `action` : `paiement_requis` / `correction` / `accepte` / `rejete` |
| 03 | **Paiement des frais** | Sur ordre de XFlow, le citoyen est redirigé vers la plateforme e-Gov externe (tarification). 2 000 FCFA. | Citoyen | Immédiat | Paiement effectué → SendTask confirmation vers XFlow (MSG_CASIERJUD_PAY_CALLBACK) |
| 04 | **Recevoir confirmation paiement** | XPortal reçoit la confirmation de paiement de XFlow (MSG_CASIERJUD_PAY_CONFIRM). | Système | Immédiat | Retour vers ReceiveTask multi-entrante 02 |
| 05 | **Corriger le dossier** | Si correction demandée, le citoyen corrige ses pièces via son dossier existant (formulaire de correction pré-rempli). Max 3 tentatives, timer 15 jours. | Citoyen | 0–15 jours | Resoumission → SendTask vers XFlow (MSG_CASIERJUD_RESUB) |
| 06 | **Demande acceptée** | Le bulletin est prêt au retrait. Le citoyen se présente au guichet DACS avec son récépissé. | — | — | EndEvent `End_P_Accepte` |
| 07 | **Demande rejetée** | Le dossier est clôturé suite à un rejet définitif. | — | — | EndEvent `End_P_Rejete` |

#### Lane XFLOW (côté back-office)

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|----|----------------|-------------|--------|-------|---------------------|
| B01 | **Réception du dossier** | XFlow reçoit la soumission initiale via Kafka (StartEvent MSG_CASIERJUD_START). | Système | Immédiat | Dossier enregistré |
| B02 | **Mise à jour statut — Soumis** | XFlow met à jour le statut portail (`Submited`). | Système | Immédiat | Statut actualisé |
| B03 | **Accusé de réception** | Notification tricanale (email + SMS + in-app) au citoyen. | Système | Immédiat | N01 envoyée |
| B04 | **Ordonner le paiement** | XFlow envoie l'ordre de paiement à XPortal (MSG_CASIERJUD_PAY_ORDER). | Système | Immédiat | XPortal affiche UserTask paiement |
| B05 | **Recevoir callback paiement e-Gov** | XFlow reçoit le callback de la plateforme de paiement (IntermediateCatchEvent MSG_CASIERJUD_PAY_CALLBACK). | Système | 0–30 min | Callback reçu |
| B06 | **Vérifier paiement** | Gateway : paiement confirmé ou non. | Système | Immédiat | Oui → B07 / Non → B14 (rejet) |
| B07 | **Confirmer paiement à XPortal** | XFlow envoie la confirmation de paiement à XPortal (MSG_CASIERJUD_PAY_CONFIRM). | Système | Immédiat | XPortal reprend le flux |
| B08 | **Mise à jour statut — En instruction** | Statut portail passe à `PendingBackOffice`. | Système | Immédiat | Statut actualisé |
| B09 | **Instruction du dossier** | L'agent instructeur vérifie les pièces, consulte le fichier des condamnations (papier), rédige le bulletin. SLA : 72h. Timer boundary non-interrompant : escalade après 72h. | Agent instructeur | 72h max | Décision : Conforme / Correction / Rejet |
| B10 | **Notifier correction** | Si correction, notification au citoyen avec motif (N03). | Système | Immédiat | N03 envoyée |
| B11 | **Envoyer ordre correction** | XFlow envoie l'action `correction` à XPortal (MSG_CASIERJUD_RETURN). | Système | Immédiat | XPortal affiche UserTask correction |
| B12 | **Attendre resoumission** | XFlow attend la resoumission du citoyen (ReceiveTask MSG_CASIERJUD_RESUB). Timer 15 jours. | Système | 0–15 jours | Resoumission reçue → retour B09 |
| B13 | **Validation par le chef de service** | Le chef valide le bulletin rédigé. SLA : 24h. | Chef de service | 24h max | Validé / Rejeté |
| B14 | **Notifier rejet** | Notification tricanale de rejet au citoyen (N05 ou N06). Chemin DRY (Pattern P4). | Système | Immédiat | N05/N06 envoyée |
| B15 | **Envoyer rejet à XPortal** | XFlow envoie `action: rejete` à XPortal (MSG_CASIERJUD_RETURN). | Système | Immédiat | EndEvent `End_X_Reject` |
| B16 | **Mise à jour statut — Succès** | Statut portail passe à `Success`. Le récépissé de retrait est disponible. | Système | Immédiat | N04 envoyée |
| B17 | **Notifier bulletin prêt** | Notification tricanale (N04) : bulletin prêt au retrait au guichet DACS. | Système | Immédiat | N04 envoyée |
| B18 | **Envoyer acceptation à XPortal** | XFlow envoie `action: accepte` à XPortal (MSG_CASIERJUD_RETURN). | Système | Immédiat | EndEvent `End_X_Success` |

### 3.3 Matrice des échanges inter-pools (Kafka)

| Message Kafka | Direction | Source | Cible | Déclencheur |
|---|---|---|---|---|
| `MSG_CASIERJUD_START` | XPortal → XFlow | SendTask 01 | StartEvent B01 | Soumission initiale du formulaire |
| `MSG_CASIERJUD_PAY_ORDER` | XFlow → XPortal | SendTask B04 | ReceiveTask 02 | Ordre de paiement après réception du dossier |
| `MSG_CASIERJUD_PAY_CALLBACK` | e-Gov → XFlow | Plateforme externe | IntermediateCatch B05 | Callback de la plateforme de paiement |
| `MSG_CASIERJUD_PAY_CONFIRM` | XFlow → XPortal | SendTask B07 | ReceiveTask (paiement) | Confirmation de paiement |
| `MSG_CASIERJUD_RETURN` | XFlow → XPortal | SendTask B11/B15/B18 | ReceiveTask multi-entrante 02 | Décision (correction / rejet / accepté) |
| `MSG_CASIERJUD_RESUB` | XPortal → XFlow | SendTask 05 | ReceiveTask B12 | Resoumission après correction |

**Patterns appliqués :**
- **P2** : ReceiveTask multi-entrante côté XPortal (reçoit PAY_ORDER, RETURN et post-correction).
- **P3** : Notification AVANT SendMessage sur chaque retour XFlow vers XPortal.
- **P4** : Nœud de rejet DRY — tous les rejets (non-paiement, rejet agent, rejet chef, max corrections) convergent vers un seul bloc notify+send.
- **P5** : Pas de vérification Odoo/API — exception documentée (fichier non informatisé).
- **P6** : Boucle correction → retour direct à l'agent instructeur (pas de vérification système intermédiaire, conforme à P5).
- **P7** : EndEvents explicites : `End_P_Accepte`, `End_P_Rejete` (XPortal), `End_X_Success`, `End_X_Reject`, `End_X_Escalade` (XFlow).
- **P8** : 6 messages = 6 SendTask/ReceiveTask appariés (MSG_CASIERJUD_RETURN utilisé dans 3 chemins mais via une seule ReceiveTask multi-entrante côté XPortal — pattern valide).

### 3.4 Flux d'escalade temporelle

| Élément | Type | Timer | Déclencheur | Action | EndEvent |
|---------|------|-------|-------------|--------|----------|
| B09 — Instruction | Boundary non-interrompant | PT72H | SLA instructeur dépassé | Notification escalade chef de service (N07) | `End_X_Escalade` |
| B12 — Attente resoumission | Boundary non-interrompant | P15D | Citoyen ne resoumets pas | Clôture automatique → rejet | `End_X_Reject` |
| 05 — Correction XPortal | Boundary non-interrompant | P15D | Citoyen ne corrige pas | Clôture automatique → EndEvent rejet | `End_P_Rejete` |

---

## Section 4 — Règles métier

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|----|---|---|---|---|
| **RG-001** | **Pièce d'identité valide** | SI la pièce d'identité uploadée est expirée ALORS l'agent demande une correction (motif : pièce expirée). | HAUTE | B09 |
| **RG-002** | **Acte de naissance lisible** | SI l'acte de naissance est illisible ou incomplet ALORS l'agent demande une correction (motif : document illisible). | HAUTE | B09 |
| **RG-003** | **Paiement préalable obligatoire** | SI le paiement n'est pas confirmé par la plateforme e-Gov ALORS le dossier est automatiquement rejeté et le citoyen notifié. | HAUTE | B06 |
| **RG-004** | **Limite de corrections** | SI le nombre de tentatives de correction atteint 3 ALORS le dossier est automatiquement clôturé et rejeté. Le citoyen doit soumettre une nouvelle demande. | HAUTE | B12, 05 |
| **RG-005** | **Timer correction citoyen** | SI le citoyen ne resoumets pas son dossier corrigé dans un délai de 15 jours calendaires ALORS le dossier est automatiquement clôturé. | HAUTE | B12 |
| **RG-006** | **Verrouillage des champs e-ID** | SI un champ d'identité (`nom`, `prenom`, `eMail`, `numeroTelephone`) est pré-rempli via le Profil Citoyen ET non vide ALORS le champ est verrouillé dynamiquement (`logic` Form.io). | HAUTE | 01 |
| **RG-007** | **Motif autre obligatoire** | SI le champ `motifDemande` a la valeur `Autre` ALORS le champ `motifAutre` devient obligatoire (custom conditional). | MOYENNE | 01 (stepDemande) |
| **RG-008** | **Format téléphone togolais** | SI le numéro de téléphone est saisi manuellement ALORS il doit respecter le format `228XXXXXXXX` (9 chiffres après l'indicatif). | MOYENNE | 01 (stepIdentite) |
| **RG-009** | **Date de naissance antérieure** | SI la date de naissance saisie est postérieure ou égale à la date du jour ALORS la validation retourne une erreur. | HAUTE | 01 (stepIdentite) |
| **RG-010** | **Retrait physique obligatoire** | Le bulletin de casier judiciaire n°3 ne peut être remis qu'en main propre au guichet de la DACS, sur présentation du récépissé et de la pièce d'identité originale. Cette contrainte est d'ordre légal (Code de procédure pénale) et ne peut être levée que par une modification législative. | HAUTE | Étape retrait (hors BPMN) |
| **RG-011** | **Escalade SLA instructeur** | SI la tâche d'instruction n'est pas complétée dans 72 heures ALORS une notification d'escalade est envoyée au chef de service (jeton parallèle, non interrompant). | MOYENNE | B09 |
| **RG-012** | **Taille maximale des fichiers** | SI un fichier uploadé dépasse 2 MB ALORS le composant `file` Form.io bloque l'upload avec un message d'erreur explicite. | HAUTE | 01 (stepPieces) |
| **RG-013** | **Archivage du dossier** | APRÈS chaque décision finale (acceptation ou rejet), les données du dossier et les pièces jointes sont archivées dans le système XFlow et conservées selon les règles de rétention ATD. | BASSE | B16, B15 |

---

## Section 5 — Intégration avec des systèmes tiers

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| **Plateforme e-Gov (paiement)** | API REST externe — callback asynchrone | Montant (2 000 FCFA), référence dossier, statut paiement | À chaque demande (service payant systématiquement) | Actif |
| **Service SMS ATD** | ServiceTask `flow-notify` | Numéro de téléphone, template, variables | À chaque jalon : AR, correction, bulletin prêt, rejet | Actif |
| **Service Email ATD** | ServiceTask `flow-notify` | Adresse email, template, variables | À chaque jalon | Actif |
| **Notifications in-app** | ServiceTask `flow-notify` | Template in-app, `record_id` | À chaque jalon | Actif |
| **Fichier national des condamnations** | **Aucune** — consultation manuelle | N/A | N/A | Non informatisé — hors scope |
| **Odoo ERP** | **Aucune** | N/A | N/A | Non applicable (pas d'intégration back-office métier prévue à ce stade) |
| **Identité numérique e-ID** | Pré-remplissage via `config.users` | Nom, prénom, email, téléphone | Au chargement du formulaire | Actif |

---

## Section 6 — Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|------|-------------|-------|--------------|--------------|
| **N01** | Soumission initiale reçue (B03) | Email + SMS + In-App | Citoyen | "Votre demande de casier judiciaire [REF] a bien été reçue. Vous allez être redirigé vers le paiement (2 000 FCFA)." |
| **N02** | Paiement confirmé (B07) | Email + SMS + In-App | Citoyen | "Votre paiement de 2 000 FCFA a été confirmé. Votre dossier [REF] est en cours de traitement par la DACS." |
| **N03** | Correction demandée par l'agent (B10) | Email + SMS + In-App | Citoyen | "Votre dossier [REF] nécessite des corrections : [MOTIF]. Veuillez corriger votre dossier sur le portail dans un délai de 15 jours." |
| **N04** | Bulletin validé — prêt au retrait (B17) | Email + SMS + In-App | Citoyen | "Votre bulletin de casier judiciaire [REF] est prêt. Présentez-vous au guichet de la DACS, Prefecture de [PREFECTURE], avec votre récépissé et votre pièce d'identité originale." |
| **N05** | Rejet par non-paiement (B14) | Email + SMS + In-App | Citoyen | "Votre demande [REF] a été annulée faute de paiement. Vous pouvez soumettre une nouvelle demande à tout moment." |
| **N06** | Rejet par l'agent ou le chef de service (B14) | Email + SMS + In-App | Citoyen | "Votre dossier [REF] a été rejeté. Motif : [MOTIF]. Pour toute question, contactez la DACS ou le centre d'appel ATD." |
| **N07** | Escalade SLA instructeur (B09 boundary 72h) | Email | Chef de service DACS | "ALERTE : Le dossier [REF] n'a pas été traité dans le délai de 72h par l'agent instructeur. Merci d'intervenir." |
| **N08** | Dossier clôturé automatiquement (timer 15j) | Email + SMS | Citoyen | "Votre dossier [REF] a été clôturé automatiquement car aucune correction n'a été soumise dans le délai de 15 jours." |

**Variables disponibles dans les templates :**
- `[REF]` = `this.data.xref` (référence unique du dossier)
- `[MOTIF]` = `this.data.Activity_X_Agent.result.submissionData.motif`
- `[PREFECTURE]` = Localisation du guichet DACS concerné

---

## Section 7 — KPIs du service & engagements SLA

### KPIs de production

| Indicateur | Valeur AS-IS | Objectif TO-BE | Mesure |
|------------|-------------|----------------|--------|
| Délai moyen de délivrance | 3 jours ouvrables | 2–3 jours ouvrables (délai d'instruction inchangé) | Durée entre soumission et notification N04 |
| Taux de rejet au dépôt | 15% | < 1% | (Dossiers avec correction) / (Total dossiers) |
| Nombre de déplacements citoyen | 2 | 1 (retrait uniquement) | N/A (mesure qualitative) |
| Taux de paiement en ligne | 0% | > 90% | Paiements e-Gov / Total dossiers |
| Taux de notification reçue | 0% | > 95% | Notifications délivrées / Notifications émises |
| Satisfaction citoyen (NPS) | Non mesuré | > 70 | Enquête post-service J+1 |

### Engagements SLA par tâche humaine

| Tâche | Acteur | SLA | Escalade |
|-------|--------|-----|----------|
| Instruction du dossier (B09) | Agent instructeur DACS | 72 heures ouvrables | N07 au chef de service après 72h |
| Validation du bulletin (B13) | Chef de service DACS | 24 heures ouvrables | Remontée N+1 après 24h (à définir avec DACS) |
| Correction par le citoyen (05) | Citoyen | 15 jours calendaires | Clôture automatique du dossier |
| Resoumission XFlow (B12) | Citoyen | 15 jours calendaires | Clôture automatique + N08 |

---

## Section 8 — Interface e-service [FDS]

Aucune interface e-service dédiée n'est prévue. Le service est accessible exclusivement via XPortal (portail national des services publics du Togo). La DACS n'exploite pas de portail propre interfacé avec ce service.

**URL d'accès** : `https://services.gouv.tg/justice/casier-judiciaire` (à confirmer avec ATD)

**Authentification** : Via le système d'identité numérique national (e-ID). Le citoyen doit disposer d'un compte actif sur XPortal.

**Responsabilité design** : ATD — les maquettes, charte graphique et CSS du formulaire sont conformes aux standards P-Studio ATD.

---

## Section 9 — Validations & signatures

| Rôle | Nom | Structure | Date | Signature |
|------|-----|-----------|------|-----------|
| **Rédigé par** (Intégrateur) | À renseigner | ATD — Agence Togo Digital | 2026-03-24 | _____________ |
| **Validé par** (FDS) | À renseigner | Ministère de la Justice — DACS | À renseigner | _____________ |
| **Approuvé par** (ATD) | À renseigner | ATD — Direction Technique | À renseigner | _____________ |