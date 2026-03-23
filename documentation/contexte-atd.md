# Synthèse Contextuelle : Programme de Digitalisation ATD (Agence Togo Digital)

Ce document constitue la référence stratégique et opérationnelle pour les intégrateurs participant au **Plan d'Accélération de la Digitalisation (PAD)** du Togo (TDR août 2024).

---

## 1. Vision et Objectifs Stratégiques (Indicateurs 2025/2026)
Le gouvernement togolais vise une nation moderne avec une croissance inclusive via la digitalisation massive des services publics :
- **Niveau 1 (Description)** : 100% des démarches décrites en ligne d'ici fin 2025.
- **Niveau 2 (Saisie)** : 100% des formulaires disponibles en ligne d'ici fin 2025.
- **Niveau 3 (Interaction)** : 75% des démarches administratives digitalisées (workflow complet).
- **Niveau 4 (Automatique)** : 20 parcours de vie (Life Paths) totalement digitalisés et automatisés.

**Objectif opérationnel global** : Digitaliser l'ensemble des démarches d'ici fin 2026, avec un traitement back-office systématique.

---

## 2. Niveaux de Digitalisation et Fonctionnalités
| Niveau | Définition | Fonctionnalités Clés |
| :--- | :--- | :--- |
| **1 : Information** | Description en ligne | Objectifs, Délais, Prix, Pièces, Base légale, Points de contact. |
| **2 : Saisie** | Soumission en ligne | Formulaire digitalisé, Paiement (Trésor), Prise de RDV, Notifications. |
| **3 : Gestion** | Traitement digital | Workflow BPMN, Affectation auto, Archivage, Signature électronique. |
| **4 : Automatisation** | Interopérabilité | Appels API inter-systèmes, IA pour interactions, Synchronisation auto. |

---

## 3. Architecture et Gouvernance Technique
- **XPortal** : Guichet national (Front-office), interface citoyenne unique.
- **XFlow** : Orchestrateur de processus (Middle-office) gérant transitions et statuts.
- **Back-Office** : Traitement via **Odoo Traitement** ou système métier fournisseur interconnecté via API.
- **P-Studio** : Environnement de conception Forms (Form.io) + BPMN (Camunda).

---

## 4. Méthodologie et Tâches de l'Intégrateur
La mission type dure **6 semaines** (hors préparation) et se divise en 4 phases :

### A. Analyse & Conception (S1)
- **Description exhaustive** : Répondre aux 4Q (Quoi, Pourquoi, Comment, à Qui).
- **KPIs (Indicateurs)** : Définir des indicateurs de production (ex: -20% délai) et de résultat (ex: satisfaction NPS).
- **Cartographies AS-IS & TO-BE** : Modélisation BPMN2 obligatoire pour identifier les optimisations.
- **Livrable** : Document d'Initialisation du Projet (DIP), SRS validé.

### B. Développement & Intégration (S2)
- Implémentation dans l'environnement de TEST.
- Création des formulaires et des règles métier.
- Configuration des notifications (SMS/Email) et du paiement électronique.

### C. Test et Validation (S3)
- Élaboration du plan de test (cas nominaux, limites et erreurs).
- Rapports d'anomalies et corrections.
- **Livrable** : PV de Recette fonctionnelle signé.

### D. Formation & Accompagnement (S4-S6)
- Formation des agents administratifs (Back-office).
- Formation de la DSI sur la conception de cartographies N2.
- Préparation de la communication (Tutoriels, Communiqué de Presse).
- Passage en production (S6).

---

## 5. Dimensionnement de l'Équipe Type (Pool d'Intégrateurs)
Une équipe minimale de **7 personnes** est requise pour assurer la numérisation d'environ 15 services :
1. **Chef de Projet (PMP/Scrum)** : Coordination, interactions ATD/Administration.
2. **Analystes Fonctionnels (x2)** : Cartographie, SRS, formation.
3. **Développeurs/Intégrateurs (x2)** : Configuration, Odoo integration.
4. **Testeur QA (x1)** : Exécution des tests et suivi des anomalies.
5. **Formateur / Change Manager (x1)** : Supports pédagogiques et conduite du changement.

---

## 6. Outils de l'Écosystème
- **KoboToolbox** : Collecte d'informations terrain.
- **Nextcloud** : Gestion documentaire centralisée.
- **Zentao** : Suivi des tests et bugs.
- **Odoo Project** : Gestion de projet obligatoire (Saisie des tâches, KPIs).

---
*Référence mise à jour : TDR Août 2024 - Agence Togo Digital.*
