# Cartographie AS-IS : Demande de Carte Nationale d'Identité (CNI)

## Identification du service

| Champ | Valeur |
|---|---|
| **Nom du service** | Demande et délivrance de la Carte Nationale d'Identité (CNI) |
| **Organisme** | Ministère de la Sécurité et de la Protection Civile |
| **Direction** | Direction Générale de la Documentation Nationale (DGDN) |
| **Base légale** | Loi n°98-004 du 11 février 1998 ; Décret n°2010-091 du 16 juillet 2010 ; Arrêté n°014/MSP du 12 mars 2015 |

---

## Description fonctionnelle

La Carte Nationale d'Identité biométrique est le document officiel permettant à tout citoyen togolais d'attester de son identité sur le territoire national et dans les pays de la CEDEAO. Elle est obligatoire pour l'exercice du droit de vote, l'ouverture d'un compte bancaire et de nombreuses démarches administratives. La DGDN produit et personnalise les CNI sur une chaîne sécurisée centralisée à Lomé. Les dossiers sont collectés dans les préfectures via les 35 Centres de Documentation (CD).

---

## Public cible et éligibilité

| Critère | Valeur |
|---|---|
| **Bénéficiaires** | Tout citoyen togolais âgé de 15 ans et plus |
| **Conditions** | Nationalité togolaise, âge ≥ 15 ans, état civil justifié |
| **Volume annuel** | ~250 000 CNI (1ères demandes + renouvellements + duplicatas) |

---

## Types de demande et coûts

| Type | Coût | Documents requis |
|---|---|---|
| **1ère demande (majeur)** | 4 000 FCFA | Formulaire + acte de naissance + CNI des parents + justificatif domicile + 2 photos |
| **Renouvellement** | 4 000 FCFA | Ancienne CNI (même expirée) + formulaire |
| **Duplicata (perte/vol)** | 8 000 FCFA | Déclaration police/gendarmerie + formulaire + acte de naissance + 2 photos |
| **Procédure d'urgence** | 20 000 FCFA | Mêmes docs + justification urgence |
| **Mineur (15–17 ans)** | 4 000 FCFA | Formulaire signé représentant légal + acte de naissance + CNI représentant |

---

## Processus AS-IS (côté citoyen)

### Étape 1 — Déplacement au Centre de Documentation
Le citoyen se rend physiquement au CD de sa préfecture ou à la DGDN à Lomé avec toutes les pièces requises. Aucune démarche en ligne n'est possible pour la CNI biométrique à ce jour.

### Étape 2 — Dépôt du dossier et paiement
- Dépôt du dossier papier complet au guichet du CD
- Paiement en espèces à la caisse
- Remise d'un récépissé avec numéro de dossier et date estimée de retrait

### Étape 3 — Capture biométrique (en présentiel)
- Photo numérique
- Relevé des empreintes digitales (10 doigts)
- Signature numérique
- Saisie et vérification des données biographiques par l'agent

### Étape 4 — Transmission à la DGDN
Le dossier numérique (données biographiques + biométriques) est transmis par lot à la DGDN à Lomé via VPN. En cas de coupure réseau, cette transmission peut être retardée de plusieurs jours.

### Étape 5 — Personnalisation et impression à la DGDN
- Impression sécurisée du titre
- Intégration de la puce électronique et des données biométriques
- Contrôle qualité visuel et électronique
- **Délai standard** : 15 à 30 jours ouvrables
- **Procédure d'urgence** : 48h

### Étape 6 — Retour au Centre de Documentation
- La CNI produite est retournée au CD d'origine
- Notification par SMS (partielle — certains CD seulement)

### Étape 7 — Retrait au guichet
- Le citoyen se présente une 2e fois au CD
- Présentation du récépissé + vérification identité
- Signature du registre de délivrance
- **Problème** : de nombreux citoyens se déplacent sans certitude que la CNI est prête (notification SMS non systématique)

---

## Processus AS-IS (côté agents)

| Acteur | Rôle | Tâches |
|---|---|---|
| **Agent de réception CD** | Guichet dépôt | Vérification complétude, encaissement, enregistrement dans le système local |
| **Opérateur biométrique** | Capture | Photo, empreintes, signature, saisie données biographiques |
| **Superviseur CD** | Contrôle qualité | Contrôle données saisies, validation par lot avant transmission DGDN |
| **Agents DGDN (personnalisation)** | Production | Réception fichiers CD, personnalisation et impression sur chaîne sécurisée |
| **Agents DGDN (contrôle qualité)** | QC | Vérification visuelle et électronique avant envoi aux CD |
| **Agent de distribution CD** | Distribution | Réception des CNI retournées, notification, délivrance au guichet |

---

## Outils actuels

| Outil | Description |
|---|---|
| **Logiciel DGDN** | Application biométrique sur mesure. Interface web locale dans les CD connectée par VPN |
| **VPN DGDN ↔ CD** | Transmission sécurisée des fichiers biométriques par lot |
| **SMS** | Partiellement déployé — certains CD envoient des SMS manuels, d'autres non |
| **Base biométrique centrale** | Serveur centralisé à la DGDN — l'une des rares administrations togolaises avec une base nationale biométrique |
| **Archives** | Papier dans les CD + serveur central DGDN pour les données biométriques |

---

## Goulots d'étranglement identifiés

| # | Problème | Impact |
|---|---|---|
| G1 | Délai de production 15–30 jours jugé excessif | Frustration citoyens, perte de temps |
| G2 | 2 déplacements obligatoires (dépôt + retrait) | Contraignant pour les populations rurales ou à mobilité réduite |
| G3 | Ruptures de stock de cartes vierges (2021, 2023) | Arrêt temporaire de production dans les CD |
| G4 | Notification SMS non systématique | Déplacements inutiles des citoyens |
| G5 | Fragilité réseau VPN entre CD et DGDN | Transmissions retardées de plusieurs jours |
| G6 | CNI non réclamées dans les CD | Mobilisation d'espace + ressources de gestion |
| G7 | 15 % de dossiers incomplets au 1er dépôt | File d'attente + retravail agent |

---

## Statistiques clés

| Indicateur | Valeur |
|---|---|
| Demandes par an | ~250 000 |
| CNI produites / jour (nominale) | ~1 000 (pic : 1 500 en période électorale) |
| Taux dossiers rejetés / incomplets | ~15 % au 1er dépôt |
| Délai moyen standard | 15 à 30 jours ouvrables |
| Délai procédure d'urgence | 48h |
| Nombre de Centres de Documentation | 35 (1 par préfecture + plusieurs à Lomé) |
| Agents impliqués | ~200 |
| Durée de validité CNI | 10 ans (majeur) / 5 ans (mineur) |

---

## Parties non digitalisables (contraintes légales)

| Élément | Justification |
|---|---|
| **Capture biométrique** | Doit être réalisée obligatoirement en présence physique du demandeur dans un CD agréé |
| **Remise du titre physique** | La CNI est un titre sécurisé physique — pas de dématérialisation possible sans réforme légale |
