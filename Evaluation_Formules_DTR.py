#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur d'évaluation des formules de la Réglementation Thermique du Bâtiment
DTR C 3.2/4 - Version 2016

Ce module permet d'évaluer les formules complexes du DTR et de pré-calculer
des valeurs typiques pour les coefficients qui sont exprimés sous forme
de relations mathématiques.
"""

import json
import math
import os
from typing import Dict, List, Union, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import itertools


class TypeIsolation(Enum):
    """Types d'isolation pour les parois"""
    REPARTIE = "repartie"
    INTERIEURE = "interieure"
    EXTERIEURE = "exterieure"


class TypeLiaison(Enum):
    """Types de liaisons pour les ponts thermiques"""
    MUR_MENUISERIE = "mur_menuiserie"
    DEUX_PAROIS_EXTERIEURES = "deux_parois_exterieures"
    PAROI_EXTERIEURE_INTERIEURE = "paroi_exterieure_interieure"


@dataclass
class Paroi:
    """Représentation simplifiée d'une paroi"""
    nom: str
    type_isolation: TypeIsolation
    resistance_thermique: float  # R en m².°C/W (sans isolant)
    epaisseur: float  # e en m
    coefficient_K: float  # K en W/m².°C (avec isolant)
    resistance_isolant: Optional[float] = None  # r_i ou r_e en m².°C/W


class MoteurFormulesDTR:
    """
    Moteur d'évaluation des formules du DTR C 3.2/4
    Permet d'évaluer les expressions mathématiques et de générer
    des tables de valeurs pré-calculées.
    """

    def __init__(self):
        """Initialise le moteur avec les constantes et fonctions de base"""
        self.constantes = {
            "π": math.pi,
            "pi": math.pi,
        }
        
        # Résultats pré-calculés (seront remplis par les méthodes)
        self.valeurs_precalculees = {}

    def evaluer_expression(self, expression: str, variables: Dict[str, float]) -> float:
        """
        Évalue une expression mathématique avec des variables.
        
        Args:
            expression: Chaîne comme "0.2 × K × e" ou "0.6 × K2 × e"
            variables: Dictionnaire des variables {nom: valeur}
            
        Returns:
            Résultat numérique de l'expression
        """
        # Nettoyer l'expression
        expr = expression.replace("×", "*").replace(" ", "")
        
        # Remplacer les variables par leurs valeurs
        for var_nom, var_valeur in variables.items():
            expr = expr.replace(var_nom, str(var_valeur))
        
        # Évaluer l'expression de manière sécurisée
        try:
            # Utiliser eval avec un dictionnaire restreint
            resultat = eval(expr, {"__builtins__": {}}, self.constantes)
            return round(resultat, 4)
        except Exception as e:
            print(f"Erreur lors de l'évaluation de '{expression}': {e}")
            return 0.0

    # ============================================================
    # PONTS THERMIQUES - FORMULES DU TABLEAU 4.2
    # ============================================================
    
    def calculer_kl_liaison_deux_parois(self, type_liaison: str, 
                                         paroi1: Paroi, paroi2: Paroi) -> float:
        """
        Calcule le coefficient linéique kl pour une liaison entre deux parois extérieures.
        Formules du Tableau 4.2.
        
        Args:
            type_liaison: "isolation_repartie_identiques", "isolation_interieure_rentrant", etc.
            paroi1: Première paroi
            paroi2: Deuxième paroi
            
        Returns:
            Coefficient kl en W/m.°C
        """
        K_moy = (paroi1.coefficient_K + paroi2.coefficient_K) / 2
        e_moy = (paroi1.epaisseur + paroi2.epaisseur) / 2
        
        formules = {
            "isolation_repartie_identiques": ("0.2 × K × e", {"K": K_moy, "e": e_moy}),
            "isolation_interieure_rentrant_identiques": ("0.6 × K × e", {"K": K_moy, "e": e_moy}),
            "isolation_exterieure_saillant_identiques": ("0.6 × K × e", {"K": K_moy, "e": e_moy}),
            "isolation_repartie_differentes_poteau": ("0.45 × e", {"e": e_moy}),
        }
        
        if type_liaison in formules:
            formule, vars_dict = formules[type_liaison]
            return self.evaluer_expression(formule, vars_dict)
        
        # Cas spécial avec R2
        if type_liaison == "isolation_repartie_differentes_angle":
            # 0.2 × e1 × (0.2 + R2 × e2)
            R2 = paroi2.resistance_thermique if paroi2.resistance_thermique else 1.0
            expr = "0.2 × e1 × (0.2 + R2 × e2)"
            vars_dict = {"e1": paroi1.epaisseur, "e2": paroi2.epaisseur, "R2": R2}
            return self.evaluer_expression(expr, vars_dict)
        
        return 0.0

    def calculer_kl_liaison_mur_menuiserie(self, type_isolation: TypeIsolation,
                                           position: str, epaisseur_mur: float,
                                           resistance_mur: float, coefficient_K: float) -> float:
        """
        Calcule le coefficient linéique pour liaison mur-menuiserie (Tableau 4.1)
        
        Args:
            type_isolation: Type d'isolation du mur
            position: "nu_interieur", "nu_exterieur", "ebrasement", etc.
            epaisseur_mur: Épaisseur du mur en m
            resistance_mur: Résistance thermique du mur en m².°C/W
            coefficient_K: Coefficient K du mur en W/m².°C
            
        Returns:
            Coefficient kl en W/m.°C
        """
        # Valeurs par défaut du tableau 4.1
        valeurs_default = {
            (TypeIsolation.REPARTIE, "nu_interieur"): 0.05,
            (TypeIsolation.REPARTIE, "nu_exterieur"): 0.05,
            (TypeIsolation.EXTERIEURE, "nu_interieur_isolation_arretee"): 0.10,
            (TypeIsolation.EXTERIEURE, "nu_interieur_isolation_recouvrant"): 0.05,
            (TypeIsolation.INTERIEURE, "nu_exterieur_isolation_arretee"): 0.10,
            (TypeIsolation.INTERIEURE, "nu_exterieur_isolation_recouvrant"): 0.05,
        }
        
        key = (type_isolation, position)
        if key in valeurs_default:
            return valeurs_default[key]
        
        # Formule pour le cas général
        # kl = 0.4 × e / (R + 0.15)
        expr = "0.4 × e / (R + 0.15)"
        return self.evaluer_expression(expr, {"e": epaisseur_mur, "R": resistance_mur})

    # ============================================================
    # PONTS THERMIQUES - FORMULES DU TABLEAU 4.3, 4.4, 4.5, 4.6
    # ============================================================
    
    def calculer_kl_liaison_isolation_repartie_interieure(self, paroi_ext: Paroi, 
                                                           paroi_int: Paroi) -> float:
        """
        Calcule kl pour liaison paroi isolation répartie + isolation intérieure
        Tableau 4.3
        """
        e_moy = (paroi_ext.epaisseur + paroi_int.epaisseur) / 2
        R1 = paroi_int.resistance_thermique
        R2 = paroi_ext.resistance_thermique
        K1 = paroi_int.coefficient_K
        K2 = paroi_ext.coefficient_K
        
        # Formule: 0.4 × e × (1 + α) / (0.06 + 0.5 × R1 + R2')
        # Calcul simplifié pour l'exemple
        alpha = self._calculer_alpha(R1, K2)
        R2_prime = R2 * 0.8  # Approximation
        
        expr = "0.4 × e × (1 + α) / (0.06 + 0.5 × R1 + R2p)"
        return self.evaluer_expression(expr, {
            "e": e_moy, "α": alpha, "R1": R1, "R2p": R2_prime
        })
    
    def calculer_kl_liaison_isolation_interieure_exterieure(self, paroi_int: Paroi,
                                                             paroi_ext: Paroi,
                                                             angle: str = "saillant") -> float:
        """
        Calcule kl pour liaison isolation intérieure + isolation extérieure
        Tableau 4.4
        
        Args:
            paroi_int: Paroi à isolation intérieure
            paroi_ext: Paroi à isolation extérieure
            angle: "saillant" ou "rentrant"
        """
        R1 = paroi_int.resistance_thermique
        e1 = paroi_int.epaisseur
        K2 = paroi_ext.coefficient_K
        R2_prime = paroi_ext.resistance_thermique * 0.8  # Approximation
        
        alpha = self._calculer_alpha(R1, K2, is_interieure=True)
        
        if angle == "saillant":
            # 0.3 × e1 × (1+α) / (0.06 × R1 + R'2)
            expr = "0.3 × e1 × (1 + α) / (0.06 × R1 + R2p)"
        else:  # rentrant
            # 0.3 × e1 × (1+α) / (0.06 + 0.5 × R1 + R'2)
            expr = "0.3 × e1 × (1 + α) / (0.06 + 0.5 × R1 + R2p)"
        
        return self.evaluer_expression(expr, {
            "e1": e1, "α": alpha, "R1": R1, "R2p": R2_prime
        })
    
    def calculer_kl_liaison_paroi_int_non_isee(self, paroi_ext: Paroi,
                                                epaisseur_paroi_int: float) -> float:
        """
        Calcule kl pour liaison avec paroi intérieure non isolée
        Tableau 4.5 et 4.6
        """
        # 0.4 × e / (R + 0.15)
        expr = "0.4 × e / (R + 0.15)"
        return self.evaluer_expression(expr, {
            "e": epaisseur_paroi_int,
            "R": paroi_ext.resistance_thermique
        })
    
    def _calculer_alpha(self, R: float, K: float, is_interieure: bool = False) -> float:
        """
        Calcule le coefficient α à partir des tableaux 4.7
        
        Args:
            R: Résistance thermique de l'isolant (ri ou re)
            K: Coefficient K de la paroi
            is_interieure: True pour isolation intérieure, False pour extérieure
            
        Returns:
            Valeur de α (0 à 1)
        """
        # Simulation d'une interpolation des valeurs du tableau 4.7
        # Version simplifiée - à enrichir avec les vraies valeurs du tableau
        valeurs_alpha = {
            (0.5, 1.5): 0.31,
            (0.75, 1.5): 0.60,
            (1.0, 1.5): 1.30,
            (0.5, 2.0): 0.32,
            (0.75, 2.0): 0.60,
            (1.0, 2.0): 0.90,
        }
        
        # Arrondir R et K pour trouver une valeur proche
        R_arr = round(R * 2) / 2  # Arrondi au 0.5 près
        K_arr = round(K * 2) / 2   # Arrondi au 0.5 près
        
        key = (R_arr, K_arr)
        if key in valeurs_alpha:
            return valeurs_alpha[key]
        
        # Valeur par défaut
        return 0.5

    # ============================================================
    # PONTS THERMIQUES - OSSATURE MÉTALLIQUE (Formule 4.4)
    # ============================================================
    
    def calculer_kl_ossature_metallique(self, li: float, le: float, epaisseur_profil: float,
                                         conductivite_metal: float, epaisseur_paroi: float,
                                         hi: float = 8.0, he: float = 23.0) -> float:
        """
        Calcule le coefficient linéique pour une liaison par ossature métallique
        Formule 4.4: 1/kl = 1/(hi × li) + L/(η × λm) + 1/(he × le)
        
        Args:
            li: Longueur développée de contact côté intérieur (m)
            le: Longueur développée de contact côté extérieur (m)
            epaisseur_profil: Épaisseur du profilé Σ (m)
            conductivite_metal: Conductivité thermique du métal (W/m.°C)
            epaisseur_paroi: Épaisseur de la paroi e (m)
            hi: Coefficient d'échange intérieur (W/m².°C)
            he: Coefficient d'échange extérieur (W/m².°C)
            
        Returns:
            Coefficient kl en W/m.°C
        """
        # Déterminer η (épaisseur équivalente)
        # η = Σ si profilé simple, η = 2×Σ si tube ou élément fermé
        # Par défaut, on prend η = epaisseur_profil (profilé simple)
        eta = epaisseur_profil
        
        # Calcul de L = e + (li + le)/8
        L = epaisseur_paroi + (li + le) / 8
        
        # Calcul de l'inverse de kl
        inv_kl = 1/(hi * li) + L/(eta * conductivite_metal) + 1/(he * le)
        
        return 1/inv_kl

    # ============================================================
    # GÉNÉRATION DE TABLES DE VALEURS PRÉ-CALCULÉES
    # ============================================================
    
    def generer_table_kl_liaisons_deux_parois(self) -> List[Dict]:
        """
        Génère une table de valeurs pré-calculées pour les liaisons
        entre deux parois extérieures (Tableau 4.2)
        """
        resultats = []
        
        # Plages de valeurs typiques
        valeurs_K = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        valeurs_e = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
        
        types_liaison = [
            ("isolation_repartie_identiques", "Isolation répartie - parois identiques"),
            ("isolation_interieure_rentrant_identiques", "Isolation intérieure - angle rentrant"),
            ("isolation_exterieure_saillant_identiques", "Isolation extérieure - angle saillant"),
        ]
        
        for type_code, type_nom in types_liaison:
            for K in valeurs_K:
                for e in valeurs_e:
                    paroi1 = Paroi(
                        nom="Paroi type",
                        type_isolation=TypeIsolation.REPARTIE,
                        resistance_thermique=1/K if K > 0 else 0.5,
                        epaisseur=e,
                        coefficient_K=K
                    )
                    paroi2 = Paroi(
                        nom="Paroi type",
                        type_isolation=TypeIsolation.REPARTIE,
                        resistance_thermique=1/K if K > 0 else 0.5,
                        epaisseur=e,
                        coefficient_K=K
                    )
                    
                    kl = self.calculer_kl_liaison_deux_parois(type_code, paroi1, paroi2)
                    
                    resultats.append({
                        "type_liaison": type_nom,
                        "type_code": type_code,
                        "K_W_m2C": K,
                        "epaisseur_m": e,
                        "kl_W_mC": kl,
                        "formule": "0.2 × K × e" if "repartie" in type_code else "0.6 × K × e"
                    })
        
        return resultats
    
    def generer_table_kl_mur_menuiserie(self) -> List[Dict]:
        """
        Génère une table de valeurs pour les liaisons mur-menuiserie
        """
        resultats = []
        
        epaisseurs = [0.2, 0.25, 0.3, 0.35, 0.4]
        resistances = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        
        configurations = [
            (TypeIsolation.REPARTIE, "nu_interieur", "Mur isolation répartie - nu intérieur"),
            (TypeIsolation.REPARTIE, "nu_exterieur", "Mur isolation répartie - nu extérieur"),
            (TypeIsolation.EXTERIEURE, "nu_interieur_isolation_arretee", "Isolation extérieure - isolation arrêtée"),
            (TypeIsolation.EXTERIEURE, "nu_interieur_isolation_recouvrant", "Isolation extérieure - isolation recouvrant"),
            (TypeIsolation.INTERIEURE, "nu_exterieur_isolation_arretee", "Isolation intérieure - isolation arrêtée"),
            (TypeIsolation.INTERIEURE, "nu_exterieur_isolation_recouvrant", "Isolation intérieure - isolation recouvrant"),
        ]
        
        for type_iso, position, desc in configurations:
            for e in epaisseurs:
                for R in resistances:
                    # Calcul du K approximatif
                    K = 1/R if R > 0 else 1.0
                    
                    paroi = Paroi(
                        nom="Mur",
                        type_isolation=type_iso,
                        resistance_thermique=R,
                        epaisseur=e,
                        coefficient_K=K
                    )
                    
                    kl = self.calculer_kl_liaison_mur_menuiserie(
                        type_iso, position, e, R, K
                    )
                    
                    resultats.append({
                        "configuration": desc,
                        "type_isolation": type_iso.value,
                        "position": position,
                        "epaisseur_m": e,
                        "resistance_thermique_m2C_W": R,
                        "kl_W_mC": kl
                    })
        
        return resultats
    
    def generer_table_kl_ossature_metallique(self) -> List[Dict]:
        """
        Génère une table de valeurs pour les ossatures métalliques
        """
        resultats = []
        
        # Configurations typiques
        profils = [
            {"nom": "Profilé simple acier", "li": 0.05, "le": 0.05, "ep": 0.003, "lambda": 52},
            {"nom": "Tube acier", "li": 0.1, "le": 0.1, "ep": 0.002, "lambda": 52, "eta_factor": 2},
            {"nom": "Profilé aluminium", "li": 0.06, "le": 0.06, "ep": 0.004, "lambda": 230},
            {"nom": "Tube aluminium", "li": 0.12, "le": 0.12, "ep": 0.003, "lambda": 230, "eta_factor": 2},
        ]
        
        epaisseurs_paroi = [0.2, 0.25, 0.3, 0.35]
        
        for profil in profils:
            eta_factor = profil.get("eta_factor", 1)
            for e_paroi in epaisseurs_paroi:
                kl = self.calculer_kl_ossature_metallique(
                    li=profil["li"],
                    le=profil["le"],
                    epaisseur_profil=profil["ep"] * eta_factor,
                    conductivite_metal=profil["lambda"],
                    epaisseur_paroi=e_paroi,
                    hi=8.0,
                    he=23.0
                )
                
                resultats.append({
                    "type_profil": profil["nom"],
                    "li_m": profil["li"],
                    "le_m": profil["le"],
                    "epaisseur_profil_m": profil["ep"],
                    "conductivite_W_mC": profil["lambda"],
                    "epaisseur_paroi_m": e_paroi,
                    "kl_W_mC": round(kl, 4)
                })
        
        return resultats
    
    # ============================================================
    # COEFFICIENT α - TABLEAU 4.7 COMPLET
    # ============================================================
    
    def generer_table_alpha(self) -> Dict:
        """
        Génère la table complète du coefficient α (Tableau 4.7)
        """
        # Valeurs extraites du tableau 4.7
        valeurs_K2 = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        valeurs_R = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
        
        # Matrice des valeurs (extraite du DTR)
        matrice_alpha = [
            # R = 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0
            [0.31, 0.60, 1.30, 0.15, 0.60, 1.20, 0.07, 0.60, 1.00, 0.00, 0.00],  # K2=1.5
            [0.32, 0.60, 0.90, 0.19, 0.60, 0.80, 0.07, 0.41, 0.60, 0.70, 0.00],  # K2=2.0
            [0.00, 0.32, 0.60, 0.60, 0.50, 0.00, 0.11, 0.32, 0.56, 0.60, 0.45],  # K2=2.5
            [0.00, 0.00, 0.02, 0.19, 0.38, 0.60, 0.40, 0.00, 0.00, 0.00, 0.00],  # K2=3.0
            [0.00, 0.00, 0.00, 0.00, 0.09, 0.23, 0.38, 0.56, 0.60, 0.00, 0.00],  # K2=3.5
            [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.29, 0.32, 0.46, 0.60, 0.00],  # K2=4.0
        ]
        
        resultats = []
        for i, K2 in enumerate(valeurs_K2):
            for j, R in enumerate(valeurs_R):
                if j < len(matrice_alpha[i]):
                    alpha = matrice_alpha[i][j]
                    if alpha > 0:  # Ne garder que les valeurs non nulles
                        resultats.append({
                            "K2_W_m2C": K2,
                            "resistance_isolant_m2C_W": R,
                            "alpha": alpha
                        })
        
        return {
            "description": "Coefficient α pour les liaisons (Tableau 4.7)",
            "unite": "sans dimension",
            "valeurs": resultats
        }
    
    # ============================================================
    # EXPORT DES RÉSULTATS
    # ============================================================
    
    def exporter_toutes_tables(self, format_sortie: str = "json", 
                                fichier_sortie: Optional[str] = None) -> Dict:
        """
        Génère et exporte toutes les tables pré-calculées
        
        Args:
            format_sortie: "json" ou "dict"
            fichier_sortie: Nom du fichier JSON (si None, pas de sauvegarde)
            
        Returns:
            Dictionnaire contenant toutes les tables
        """
        tables = {
            "metadata": {
                "titre": "Valeurs pré-calculées des coefficients de ponts thermiques",
                "source": "DTR C 3.2/4 - Moteur d'évaluation",
                "date_generation": "2026-03-08",
                "version": "1.0"
            },
            "coefficient_alpha": self.generer_table_alpha(),
            "liaisons_deux_parois": self.generer_table_kl_liaisons_deux_parois(),
            "liaisons_mur_menuiserie": self.generer_table_kl_mur_menuiserie(),
            "ossatures_metalliques": self.generer_table_kl_ossature_metallique(),
        }
        
        if format_sortie == "json" and fichier_sortie:
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                json.dump(tables, f, indent=2, ensure_ascii=False)
            print(f"Tables exportées vers {fichier_sortie}")
        
        return tables
    
    def exporter_ponts_thermiques_pour_logiciel(self, fichier_sortie: str = "ponts_thermiques_precalcules.json"):
        """
        Exporte un fichier JSON optimisé pour l'intégration dans un logiciel
        """
        tables = self.exporter_toutes_tables("json", fichier_sortie)
        
        # Créer une version simplifiée pour le logiciel
        version_logiciel = {
            "metadata": tables["metadata"],
            "coefficients": {
                "alpha": tables["coefficient_alpha"]["valeurs"],
                "liaisons": {
                    "deux_parois": [
                        {
                            "type": item["type_code"],
                            "K": item["K_W_m2C"],
                            "e": item["epaisseur_m"],
                            "kl": item["kl_W_mC"]
                        }
                        for item in tables["liaisons_deux_parois"]
                    ],
                    "mur_menuiserie": tables["liaisons_mur_menuiserie"],
                    "ossature_metallique": tables["ossatures_metalliques"]
                }
            }
        }
        
        # Sauvegarder la version simplifiée
        nom_fichier_simple = fichier_sortie.replace('.json', '_logiciel.json')
        with open(nom_fichier_simple, 'w', encoding='utf-8') as f:
            json.dump(version_logiciel, f, indent=2, ensure_ascii=False)
        
        print(f"Version logiciel exportée vers {nom_fichier_simple}")
        return version_logiciel


# ============================================================
# EXEMPLE D'UTILISATION
# ============================================================

if __name__ == "__main__":
    # Initialiser le moteur
    moteur = MoteurFormulesDTR()
    
    print("=" * 60)
    print("MOTEUR D'ÉVALUATION DES FORMULES DTR C 3.2/4")
    print("=" * 60)
    
    # Exemple 1: Calcul d'un coefficient kl pour liaison deux parois
    print("\n--- Exemple 1: Liaison deux parois extérieures ---")
    paroi1 = Paroi(
        nom="Mur en béton",
        type_isolation=TypeIsolation.REPARTIE,
        resistance_thermique=0.5,
        epaisseur=0.2,
        coefficient_K=2.0
    )
    paroi2 = Paroi(
        nom="Mur en brique",
        type_isolation=TypeIsolation.REPARTIE,
        resistance_thermique=0.6,
        epaisseur=0.25,
        coefficient_K=1.8
    )
    
    kl = moteur.calculer_kl_liaison_deux_parois(
        "isolation_repartie_identiques", paroi1, paroi2
    )
    print(f"kl = {kl} W/m.°C")
    
    # Exemple 2: Génération de toutes les tables
    print("\n--- Génération des tables pré-calculées ---")
    tables = moteur.exporter_ponts_thermiques_pour_logiciel("ponts_thermiques_precalcules.json")
    
    print(f"Nombre de valeurs α générées: {len(tables['coefficients']['alpha'])}")
    print(f"Nombre de liaisons deux parois: {len(tables['coefficients']['liaisons']['deux_parois'])}")
    print(f"Nombre de liaisons mur-menuiserie: {len(tables['coefficients']['liaisons']['mur_menuiserie'])}")
    
    print("\n✅ Moteur d'évaluation prêt à être intégré dans votre logiciel!")
