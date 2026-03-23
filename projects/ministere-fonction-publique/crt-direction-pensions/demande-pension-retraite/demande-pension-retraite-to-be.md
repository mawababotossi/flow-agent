# Cartographie TO-BE : Demande de mise à la retraite et de liquidation de pension

## Vision Générale
Digitalisation complète du processus de liquidation de pension. L'agent initie sa demande en ligne via un portail dédié. L'interconnexion avec le SIRH National (ANTILOPE) et l'État Civil permet de pré-remplir le dossier et de limiter les fraudes. Le suivi est transparent et les notifications sont automatiques (SMS/Email).

## Architecture Technique
- **Frontend (XPortal)** : Formulaire Wizard Form.io avec pré-remplissage e-ID.
- **Moteur de workflow (XFlow/Camunda 7)** : Orchestration du traitement back-office.
- **Intégrations (Kafka/API)** :
    - **ANTILOPE (SIRH)** : Récupération des états de services et calcul automatique.
    - **État Civil** : Vérification de l'identité et détection des décès.
    - **Notification Service** : Envoi de SMS/Email.
    - **PDF Service** : Génération du titre de pension avec QR Code.

## Acteurs et Systèmes
| Acteur / Système | Rôle |
|------------------|------|
| Citoyen (Futur Retraité) | Soumet la demande en ligne et suit l'avancement. |
| XPortal (Citoyen) | Interface de saisie et de suivi utilisateur. |
| XFlow (Back-Office) | Orchestrateur métier du traitement. |
| Liquidateur CRT | Valide les données consolidées par le système. |
| DG CRT | Valide numériquement le titre de pension. |
| Système ANTILOPE | Fournit les données de carrière et le calcul théorique. |

## Étapes Digitalisées

1.  **Pré-constitution et Soumission** (Citoyen → XPortal)
    - Authentification e-ID.
    - Pré-remplissage automatique des données personnelles et de carrière.
    - Upload des pièces complémentaires non disponibles numériquement.
    - Accusé de réception immédiat.

2.  **Validation Carrière et Calcul** (Système + Liquidateur)
    - Récupération automatique des états de services via ANTILOPE.
    - Calcul automatique de la pension.
    - Validation par le liquidateur CRT via tableau de bord XFlow.
    - **Boucle de correction** si des incohérences sont détectées (XPortal).

3.  **Approbation Finalisée** (Contrôleur + DG CRT)
    - Validation de la liquidation.
    - Génération du Titre de Pension PDF avec QR Code unique.
    - Signature électronique/numérique (selon faisabilité technique).

4.  **Mise à disposition et Notification** (Système)
    - Notification SMS/Email au retraité.
    - Titre de pension disponible en téléchargement sur XPortal.
    - Transmission automatique au service comptable pour ordonnancement.

5.  **Contrôle d'existence digitalisé** (Pensionné)
    - Preuve de vie via reconnaissance biométrique mobile ou passage en mairie (interconnectée).
    - Alerte automatique en cas de non-réalisation.

## Gains Attendus
- **Délai de traitement** : Réduction de 6 mois à moins de 30 jours.
- **Zéro papier** : Suppression des dossiers physiques et des déplacements.
- **Exactitude** : Calcul automatique basé sur les données sources SIRH.
- **Sécurité** : Réduction drastique des fraudes aux décès (interconnexion État Civil).
- **Confort** : Plus de déplacement physique annuel pour le contrôle d'existence.
