# SERVICE REQUIREMENT SHEET (SRS)
## Demande de Casier Judiciaire — Bulletin n°3
### Direction des Affaires Civiles et du Sceau (DACS) — Ministère de la Justice — Togo

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Ministère de la Justice — Direction des Affaires Civiles et du Sceau (DACS) |
| **Service parent** | Ministère de la Justice |
| **Intégrateur en charge** | À renseigner |
| **Chef de projet ATD** | À renseigner |
| **Point focal FDS** | À renseigner |
| **Date de création** | 22 mars 2026 |
| **Date de dernière révision** | 22 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 22/03/2026 | ATD / IA | Version initiale |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service](#8-interface-e-service)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

Le casier judiciaire (bulletin n°3) est un document officiel délivré par la Direction des Affaires Civiles et du Sceau (DACS) du Ministère de la Justice, attestant des condamnations pénales définitives inscrites au nom d'une personne. Ce bulletin est fréquemment exigé lors d'une embauche dans la fonction publique, d'une inscription en établissement d'enseignement supérieur, d'une demande de visa ou de l'obtention d'une licence professionnelle. Sa délivrance est encadrée par le Code de procédure pénale togolais, qui impose que le document porte une signature manuscrite et un cachet humide d'un agent habilité.

La digitalisation permet au citoyen de soumettre sa demande en ligne via Xportal, de payer les frais (2 000 FCFA) sur la plateforme de paiement e-Gov externe, et de suivre en temps réel l'avancement de son dossier grâce aux notifications SMS/Email automatiques. Le traitement back-office (vérification de conformité, instruction, validation) est orchestré par Xflow. Le retrait physique du bulletin signé et cacheté reste obligatoire (contrainte légale), mais le citoyen ne se déplace qu'une seule fois, lorsqu'il est notifié que le document est prêt.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DACS-2026-001 |
| **Nom complet** | Demande de Casier Judiciaire — Bulletin n°3 |
| **Catégorie** | Justice / Actes judiciaires |
| **Bénéficiaires** | Tout citoyen togolais ou ressortissant étranger né au Togo, majeur ou mineur représenté par un tuteur légal |
| **Fréquence estimée** | ~15 000 bulletins/an (~50/jour à Lomé, ~10/jour par tribunal régional) |
| **Délai standard de traitement** | 3 jours ouvrables |
| **Délai réglementaire maximum** | 5 jours ouvrables |
| **Coût du service** | Payant — 2 000 FCFA (montant fixe) |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Demandeur** | Personne physique majeure (ou tuteur légal) | Soumet la demande en ligne, paie sur plateforme externe, reçoit les notifications, se présente une seule fois pour retirer le bulletin | Xportal (lecture seule) | Évaluateur du service |
| **Agent de réception DACS** | Agent DACS (N1 métier) | Vérifie la conformité du dossier numérique (pièces justificatives, identité) | Back-office Xflow | Délai : ≤ 24h ouvrables |
| **Agent instructeur DACS** | Agent DACS (N1 métier spécialisé) | Consulte le fichier des condamnations (papier), saisit le résultat (néant/mentions), prépare et signe le bulletin physique | Back-office Xflow | Délai : 1-3 jours ouvrables |
| **Chef de service DACS** | Responsable administratif DACS | Valide le bulletin instruit, contrôle la conformité | Back-office Xflow — accès complet | Délai : ≤ 4h ouvrables |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, escalades temporelles | Infrastructure ATD | Disponibilité 99,5 % |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance usagers en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de 3 formulaires Form.io distincts orchestrés par Xflow :

- **Formulaire principal (4 onglets wizard)** : parcours commun à tous les demandeurs.
- **Formulaire de paiement (1 page, conditionnel)** : déclenché automatiquement après soumission du formulaire principal, redirige vers la plateforme de paiement e-Gov externe.
- **Formulaire de correction (2 onglets wizard, conditionnel)** : activé uniquement si l'agent demande une correction, entre l'étape de vérification et la resoumission.

#### Formulaire principal — 4 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Bienvenue | Landing page Premium — présentation du service, prérequis, étapes |
| Onglet 2 | Informations personnelles | Données e-ID pré-remplies + informations complémentaires |
| Onglet 3 | Pièces justificatives | Upload des documents requis |
| Onglet 4 | Récapitulatif et soumission | Résumé + confirmation + CAPTCHA |

#### Formulaire de paiement — Conditionnel (service payant)

Ce formulaire est un composant Form.io indépendant, déclenché par Xflow via une User Task après la soumission du formulaire principal. Il redirige le citoyen vers la plateforme de paiement e-Gov externe (Flooz / TMoney / Visa / Mastercard).

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Paiement | Paiement des frais — 2 000 FCFA | Toujours — service payant à montant fixe |

#### Formulaire de correction — Conditionnel (boucle de correction)

Ce formulaire est un composant Form.io indépendant, déclenché par Xflow lorsque l'agent demande une correction. Le citoyen corrige et resoumets via son dossier existant.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Correction | Correction du dossier | `decision == 'correction'` — déclenché par Xflow (étape B04) |

### 2.2. Détail des champs

#### Onglet 1 — Bienvenue

Landing page Premium utilisant le système de grille Bootstrap (columns 8/4) avec Info Pills pour les avantages du service (soumission 24h/7j, paiement en ligne, suivi en temps réel, un seul déplacement), une Sidebar avec les informations DACS, et un guide pas à pas numéroté (4 étapes).

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlIntroContent` | N/A | HTML | N/A | Grille Bootstrap 8/4 | Système | Contenu statique Premium |
| `htmlInfoPills` | N/A | HTML | N/A | Info Pills stylisées | Système | Avantages du service |
| `htmlSidebar` | N/A | HTML | N/A | Sidebar informative | Système | Coordonnées DACS, horaires |
| `htmlEtapes` | N/A | HTML | N/A | Guide pas à pas numéroté | Système | 4 étapes du parcours |

#### Onglet 2 — Informations personnelles

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom de famille | Texte | Oui | Lecture seule dynamique (bloc logic) | Profil Citoyen (`config.users.lastName`) | RG-001 — Verrouillage e-ID |
| `prenom` | Prénom(s) | Texte | Oui | Lecture seule dynamique (bloc logic) | Profil Citoyen (`config.users.firstName`) | RG-001 |
| `dateNaissance` | Date de naissance | Date | Oui | Format JJ/MM/AAAA | Profil Citoyen (`config.users.birthDate`) | RG-001 |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | Min 2, max 100 caractères | Saisie | — |
| `nationalite` | Nationalité | Select | Oui | Liste dynamique | API (`config.apiBaseUrl/references/nationalities`) | RG-002 |
| `telephone` | Numéro de téléphone | Téléphone | Oui | Format international +228XXXXXXXX | Profil Citoyen (`config.users.phone`) | RG-001 |
| `email` | Adresse email | Email | Oui | Validation format email | Profil Citoyen (`config.users.email`) | RG-001 |
| `adresse` | Adresse de résidence | Texte | Oui | Min 5, max 200 caractères | Saisie | — |
| `nomPere` | Nom du père | Texte | Non | Max 100 caractères | Saisie | Facultatif — aide à la recherche (homonymes) |
| `nomMere` | Nom de la mère | Texte | Non | Max 100 caractères | Saisie | Facultatif — aide à la recherche (homonymes) |

#### Onglet 3 — Pièces justificatives

Les fichiers sont uploadés directement dans Xportal et transmis à Xflow. Formats acceptés : PDF, JPG, PNG.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pieceIdentite` | Copie de la pièce d'identité nationale ou du passeport | Fichier | Oui | PDF/JPG/PNG < 2 Mo — en cours de validité | Upload | RG-009 |
| `acteDeNaissance` | Copie de l'acte de naissance | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | RG-009 |

#### Formulaire de paiement — Détail des champs

Le formulaire de paiement affiche le montant fixe et déclenche la redirection vers la plateforme de paiement e-Gov externe.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `serviceTitle` | Paiement — Casier Judiciaire | HTML (h2) | N/A | Statique | Système | Titre du service |
| `htmlExplication` | Vous allez être redirigé vers la plateforme de paiement... | HTML (h4) | N/A | Statique | Système | Texte explicatif |
| `montantAPayer` | Montant à payer | Texte | N/A | Lecture seule — rempli par Calculate Costs | Système | 2 000 FCFA |
| `dynamicCost` | N/A | Texte | N/A | Hidden, clearOnHide: false | Système | Variable technique Calculate Costs |
| `dejaPaye` | N/A | Texte | N/A | Hidden, clearOnHide: false, defaultValue: "OUI" | Système | Flag de paiement |

**Propriétés techniques :**

| Propriété technique | Valeur |
|---|---|
| **Slug du formulaire** | `paiement-casier-judiciaire` |
| **Déclencheur processus** | User Task Xportal — étape P2 |
| **Action post-traitement** | Confirmation paiement → Send Task vers Xflow (MSG_CJ_START) |

#### Formulaire de correction — Détail des champs

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `motifAgent` | Motif de la correction demandée | HTML | N/A | Lecture seule — injecté par Xflow | Système | Affiché en alerte rouge |
| `numeroDossier` | Numéro de dossier | Texte | N/A | Hidden — injecté par Xflow | Système | Référence interne |
| `nbCorrections` | Nombre de corrections effectuées | Texte | N/A | Hidden — injecté par Xflow | Système | Compteur pour limite (max 3) |
| `htmlCompteur` | Tentatives restantes | HTML | N/A | Calcul `3 - nbCorrections`, rouge si dernière | Système | RG-007 |
| `piecesCorrigees` | Pièces corrigées | Fichier | Oui | PDF/JPG/PNG < 2 Mo, multiple | Upload | RG-009 |
| `commentaire` | Commentaire (optionnel) | Textarea | Non | Max 500 caractères | Saisie | — |
| `htmlRecapCorrection` | Récapitulatif | HTML | N/A | Script Parseur Formulaire | Système | Récapitulatif Intelligent |
| `luEtApprouve` | Je certifie que les corrections apportées sont exactes | Checkbox | Oui | Doit être coché | Saisie | Exclu du récap via excludeKeys |

#### Onglet 4 — Récapitulatif et soumission

L'onglet 4 affiche un résumé de toutes les données saisies via le script d'analyse natif ATD. L'usager coche une case de confirmation. P-Studio gère nativement le bouton « Soumettre » sur le dernier panel du wizard.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur Formulaire | Système | Injection du composant `recap_form.json` |
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations fournies sont exactes et complètes | Checkbox | Oui | Doit être coché | Saisie | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

Les actions suivantes sont pré-configurées sur la soumission du formulaire P-Studio :

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Formulaire de paiement uniquement | Prix fixe : 2 000 FCFA (`fixedPrice: 2000`, `pricingMode: "fixed"`) |
| **Publish to RabbitMQ** | Toujours actif (formulaire principal) | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

Le processus complet est modélisé sur P-Studio (Camunda Web Modeler). Le diagramme BPMN est joint en annexe (fichier `.bpmn`).

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_CasierJudiciaire_v1` |
| **Événement déclencheur** | Soumission du formulaire par l'usager sur Xportal + paiement confirmé sur plateforme externe |
| **Événement de fin (succès)** | Notification SMS/Email de disponibilité du bulletin + retrait physique au guichet DACS |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé à l'usager |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL (citoyen) + Pool XFLOW (back-office) — deux pools exécutables communiquant via Kafka |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumission de la demande | Le citoyen remplit le formulaire wizard (informations personnelles + pièces justificatives). Les données e-ID sont pré-remplies. Validation Form.io au fil de la saisie. | Citoyen | Immédiat | → 02 |
| 02 | Paiement des frais | Le citoyen est redirigé vers la plateforme de paiement e-Gov externe (Flooz / TMoney / Visa / Mastercard). Montant fixe : 2 000 FCFA. | Citoyen / Plateforme externe | Immédiat | → 03 |
| 03 | Envoi du dossier au back-office | Send Task : le dossier complet (formulaire + pièces + preuve de paiement) est transmis à Xflow via Kafka (MSG_CJ_START). | Système | < 1 min | → 04 |
| 04 | Attente du retour Xflow | Receive Task central unique. Reçoit tous les retours Xflow via MSG_CJ_RETURN. La gateway route selon `result.action`. | Système | Variable | Si `correction` → 05 / Si `accepte` ou `rejete` → 06 |
| 05 | Correction du dossier | Le citoyen corrige les pièces demandées via le formulaire de correction. Resoumission vers Xflow via MSG_CJ_RESUB. Retour à l'étape 04. | Citoyen | ≤ 15 jours | → 04 (boucle) |
| 06 | Fin du processus portail | EndEvent — le citoyen consulte le statut final (accepté ou rejeté) sur Xportal. | Système | Immédiat | → FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Réception du dossier | Xflow reçoit le message de démarrage MSG_CJ_START depuis Xportal. Les données du formulaire et la preuve de paiement sont chargées. | Système | Immédiat | → B02 |
| B02 | Marquer dossier soumis | Step Notification : statut du dossier mis à jour (`Submitted`). | Système | < 1 min | → B03 |
| B03 | Accusé de réception | Send Notification : SMS + Email au citoyen avec numéro de suivi, liste des pièces reçues, délai estimé (3 jours ouvrables). | Système | < 5 min | → B04 |
| B04 | Vérification de conformité | User Task : l'agent de réception vérifie la conformité du dossier numérique (authenticité des pièces, validité de l'identité, présence de l'acte de naissance). | Agent de réception DACS | ≤ 24h ouvrables | Si conforme → B07 / Si correction → B05 / Si rejet → B10 |
| B05 | Notification correction | Step Notification + Send Notification SMS/Email au citoyen avec motif de correction. Send Task MSG_CJ_RETURN (`action: "correction"`) vers Xportal. | Système | < 5 min | → B06 |
| B06 | Attente resoumission | Receive Task : attente du message MSG_CJ_RESUB (resoumission citoyen). Timer : clôture automatique après 15 jours. | Système | ≤ 15 jours | → B04 (retour vérification) |
| B07 | Instruction du bulletin | User Task : l'agent instructeur consulte le fichier national des condamnations (fichier papier), saisit le résultat (néant ou mentions), prépare le bulletin physique (signature manuscrite + cachet humide). | Agent instructeur DACS | 1-3 jours ouvrables | → B08 |
| B08 | Validation chef de service | User Task : le chef de service contrôle le bulletin instruit (données, signature, cachet). | Chef de service DACS | ≤ 4h ouvrables | Si validé → B09 / Si correction → B07 / Si rejet → B10 |
| B09 | Archivage + notification disponibilité | Archivage GED Odoo + Step Notification (statut `Success`) + Send Notification SMS/Email au citoyen (bulletin prêt, lieu de retrait). Send Task MSG_CJ_RETURN (`action: "accepte"`) vers Xportal. | Système | < 5 min | → FIN (succès) |
| B10 | Rejet définitif | Step Notification (statut `Fail`) + Send Notification SMS/Email au citoyen avec motif de rejet. Send Task MSG_CJ_RETURN (`action: "rejete"`) vers Xportal. | Système | < 5 min | → FIN (rejet) |

### 3.3. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai vérification conformité dépassé (24h) | Email + Dashboard | Rappel automatique à l'agent de réception |
| Délai vérification conformité dépassé (48h) | Email + Dashboard | Escalade automatique vers le chef de service DACS |
| Délai correction citoyen dépassé (15 jours) | SMS + Email | Clôture automatique du dossier avec notification |
| Délai instruction bulletin dépassé (3 jours) | Email + Dashboard | Rappel automatique à l'agent instructeur |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Verrouillage données e-ID | Si `config.users.XXX` non vide → champ verrouillé (disabled via bloc logic dynamique). Le citoyen ne ressaisit pas les données déjà connues. | HAUTE | Onglet 2 formulaire |
| RG-002 | Liste nationalités dynamique | La liste des nationalités est requêtée via `config.apiBaseUrl/references/nationalities`. Aucune donnée en dur. | MOYENNE | Onglet 2 formulaire |
| RG-003 | Paiement préalable obligatoire | Le dossier n'est transmis à Xflow (MSG_CJ_START) qu'après confirmation effective du paiement sur la plateforme e-Gov externe. | HAUTE | Étapes 02-03, P2 |
| RG-004 | Pièce d'identité en cours de validité | La pièce d'identité uploadée doit être en cours de validité. Vérification visuelle par l'agent de réception. Si expirée → correction ou rejet. | HAUTE | Onglet 3, Étape B04 |
| RG-005 | Unicité de la demande | Un citoyen identifié par son numéro e-ID ne peut avoir qu'une seule demande de casier judiciaire en cours. Si une demande est active, blocage de la nouvelle soumission. | HAUTE | Étape 01 |
| RG-006 | Limite de corrections | Maximum 3 tentatives de correction. Si `nbCorrections > 3` → rejet automatique avec notification au citoyen. | HAUTE | Étapes 05, B06 |
| RG-007 | Délai de correction citoyen | Le citoyen dispose de 15 jours pour soumettre un dossier corrigé. Au-delà, le dossier est clôturé automatiquement avec statut « Rejeté — délai dépassé ». | HAUTE | Étapes 05, B06 |
| RG-008 | Retrait physique obligatoire | Le bulletin n°3 doit être retiré physiquement au guichet DACS. Le citoyen présente son récépissé de dossier + pièce d'identité originale. Contrainte légale : signature manuscrite + cachet humide. | HAUTE | Post-B09 |
| RG-009 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 2 Mo par fichier. Tout fichier non conforme est rejeté avec message explicite. | MOYENNE | Onglet 3, Étape B04 |
| RG-010 | Archivage 10 ans | Tous les dossiers (acceptés et rejetés) doivent être archivés dans la GED Odoo pendant 10 ans minimum conformément aux obligations légales togolaises. | HAUTE | Post-décision |
| RG-011 | Validité du bulletin | Le bulletin de casier judiciaire n°3 a une durée de validité de 3 mois à compter de la date de délivrance. | MOYENNE | Information citoyen |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Plateforme de paiement e-Gov | Plateforme externe (redirection) | Montant (2 000 FCFA), référence dossier, statut paiement | Étape P2 — Paiement obligatoire | Disponible |
| Plateforme SMS | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut | Disponible |
| Plateforme Email | API REST (envoi) | Adresse email, template, réf. dossier | À chaque changement de statut | Disponible |
| GED Odoo (archivage ATD) | API interne | Dossier complet (formulaire + pièces + résultat instruction) | Post-validation — Archivage automatique (étape B09) | Disponible |
| Identité numérique (e-ID) | API REST (lecture) | Nom, prénom, date naissance, téléphone, email | Pré-remplissage formulaire (étape 01) | Disponible |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission + paiement confirmé (Étape B03) | SMS + Email | Citoyen | *Votre demande de casier judiciaire (réf. [DOSSIER]) a bien été reçue. Délai de traitement : 3 jours ouvrables.* |
| N02 | Correction demandée (Étape B05) | SMS + Email | Citoyen | *Votre dossier (réf. [DOSSIER]) nécessite des corrections : [motif]. Vous disposez de 15 jours pour resoummettre. Tentatives restantes : [N].* |
| N03 | Bulletin disponible (Étape B09) | SMS + Email | Citoyen | *Votre bulletin de casier judiciaire (réf. [DOSSIER]) est prêt. Présentez-vous au guichet DACS avec votre récépissé et votre pièce d'identité originale.* |
| N04 | Rejet définitif (Étape B10) | SMS + Email | Citoyen | *Votre demande de casier judiciaire (réf. [DOSSIER]) a été rejetée. Motif : [motif_rejet]. Vous pouvez soumettre une nouvelle demande.* |
| N05 | Confirmation de paiement (Étape P2) | SMS + Email | Citoyen | *Votre paiement de 2 000 FCFA pour la demande de casier judiciaire a été confirmé. Reçu : [RECU].* |
| N06 | Rappel agent — 24h dépassées (Étape B04) | Email + Dashboard | Agent de réception DACS | *Rappel : Le dossier [DOSSIER] doit être vérifié avant [date_heure_limite].* |
| N07 | Escalade superviseur — 48h dépassées (Étape B04) | Email + Dashboard | Chef de service DACS | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai de vérification. Action requise.* |
| N08 | Invitation évaluation (J+1 retrait) | SMS + Email | Citoyen | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 90 % (dossiers soumis / formulaires initiés) — objectif vs 85 % AS-IS grâce à la validation Form.io |
| **Taux d'abandon** | ≤ 10 % |
| **Délai standard de traitement** | 3 jours ouvrables |
| **Délai réglementaire maximum** | 5 jours ouvrables |
| **Taux de rejet** | ≤ 10 % |
| **Taux de dossiers incomplets** | ≤ 5 % (vs 15 % AS-IS) |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80 % |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5 % mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Nombre de déplacements citoyen** | 1 seul (retrait uniquement) — vs 2 AS-IS |

---

## 8. Interface e-service

Aucune interface e-service dédiée n'est prévue. Le service est accessible exclusivement via Xportal.

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux de la DACS. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe | Point focal DACS | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande de Casier Judiciaire (Bulletin n°3) | v1.0 | ATD*
