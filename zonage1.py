#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'enrichissement climatique des communes algériennes
Version: 2.0.0 - Avec normalisation automatique des noms
Correction complète des warnings pour Bordj Bou Arreridj et autres
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AlgerianClimateEnricher:
    """
    Enrichit les données des communes algériennes avec les zones climatiques
    et met à jour les informations de wilaya
    """
    
    def __init__(self):
        """Initialise l'enricheur avec les règles du DTR et les nouvelles wilayas"""
        self._init_normalization_rules()
        self._init_wilaya_name_mapping()
        self._init_commune_name_mapping()
        self._init_winter_rules()
        self._init_summer_rules()
        self._init_wilaya_mappings()
        self._init_new_wilaya_codes()
        self._init_specific_zones()
        self.wilayas_cache = None
        logger.info("Enricheur climatique initialisé avec succès")
    
    def _init_normalization_rules(self):
        """Initialise les règles de normalisation des noms"""
        self.accent_map = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'À': 'A', 'Â': 'A', 'Ä': 'A',
            'Î': 'I', 'Ï': 'I',
            'Ô': 'O', 'Ö': 'O',
            'Ù': 'U', 'Û': 'U', 'Ü': 'U',
            'Ç': 'C'
        }
        
        # Caractères à ignorer/remplacer
        self.cleanup_patterns = [
            (r'[-\'\s]+', ' '),  # Normaliser les espaces et tirets
            (r'^\s+|\s+$', ''),  # Trim
            (r'\s+', ' '),       # Espaces multiples -> un seul
        ]
    
    def normalize_name(self, name: str) -> str:
        """
        Normalise un nom de wilaya ou commune pour la recherche
        
        Args:
            name: Nom à normaliser
            
        Returns:
            Nom normalisé (sans accents, en minuscules, nettoyé)
        """
        if not name:
            return ""
        
        # Convertir en string et en minuscules
        normalized = str(name).lower()
        
        # Remplacer les accents
        for accented, plain in self.accent_map.items():
            normalized = normalized.replace(accented.lower(), plain)
        
        # Appliquer les patterns de nettoyage
        for pattern, replacement in self.cleanup_patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def find_wilaya_by_name(self, wilaya_name: str, wilayas_data: List[Dict]) -> Optional[Dict]:
        """
        Trouve une wilaya par son nom en utilisant la normalisation
        
        Args:
            wilaya_name: Nom de la wilaya à chercher
            wilayas_data: Liste des wilayas
            
        Returns:
            La wilaya trouvée ou None
        """
        if not wilayas_data:
            return None
        
        # Normaliser le nom recherché
        search_name = self.normalize_name(wilaya_name)
        
        # Chercher dans la liste
        for wilaya in wilayas_data:
            wilaya_raw_name = wilaya.get('name', '')
            wilaya_norm_name = self.normalize_name(wilaya_raw_name)
            
            if wilaya_norm_name == search_name:
                return wilaya
            
            # Vérifier aussi les alias connus
            if wilaya_raw_name in self.wilaya_name_mapping:
                mapped_name = self.wilaya_name_mapping[wilaya_raw_name]
                if self.normalize_name(mapped_name) == search_name:
                    return wilaya
        
        # Si non trouvé, essayer avec le mapping inverse
        for key, value in self.wilaya_name_mapping.items():
            if self.normalize_name(key) == search_name:
                # Chercher par la valeur mappée
                for wilaya in wilayas_data:
                    if self.normalize_name(wilaya.get('name', '')) == self.normalize_name(value):
                        return wilaya
        
        return None
    
    def _init_wilaya_name_mapping(self):
        """Mapping entre les noms dans communes et wilayas (toutes variantes)"""
        self.wilaya_name_mapping = {
            # Mapping standard
            'Adrar': 'Adrar',
            'Chlef': 'Chlef',
            'Laghouat': 'Laghouat',
            'Oum El Bouaghi': 'Oum El Bouaghi',
            'Batna': 'Batna',
            'Béjaïa': 'Béjaïa',
            'Bejaia': 'Béjaïa',
            'Biskra': 'Biskra',
            'Béchar': 'Béchar',
            'Bechar': 'Béchar',
            'Blida': 'Blida',
            'Bouira': 'Bouira',
            'Tamanrasset': 'Tamanrasset',
            'Tébessa': 'Tébessa',
            'Tebessa': 'Tébessa',
            'Tlemcen': 'Tlemcen',
            'Tiaret': 'Tiaret',
            'Tizi Ouzou': 'Tizi Ouzou',
            'Alger': 'Algiers',
            'Algiers': 'Algiers',
            'Djelfa': 'Djelfa',
            'Jijel': 'Jijel',
            'Sétif': 'Sétif',
            'Setif': 'Sétif',
            'Saïda': 'Saïda',
            'Saida': 'Saïda',
            'Skikda': 'Skikda',
            'Sidi Bel Abbès': 'Sidi Bel Abbès',
            'Sidi Bel Abbes': 'Sidi Bel Abbès',
            'Annaba': 'Annaba',
            'Guelma': 'Guelma',
            'Constantine': 'Constantine',
            'Médéa': 'Médéa',
            'Medea': 'Médéa',
            'Mostaganem': 'Mostaganem',
            'M\'sila': 'M\'sila',
            'Msila': 'M\'sila',
            'Mascara': 'Mascara',
            'Ouargla': 'Ouargla',
            'Oran': 'Oran',
            'El Bayadh': 'El Bayadh',
            'Illizi': 'Illizi',
            
            # BORDJ BOU ARRERIDJ - TOUTES LES VARIANTES POSSIBLES
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arréridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'Bordj Bou Arreridj': 'Bordj Bou Arreridj',
            'BBA': 'Bordj Bou Arreridj',  # Abréviation possible
            
            # Suite des mappings
            'Boumerdès': 'Boumerdès',
            'Boumerdes': 'Boumerdès',
            'El Tarf': 'El Tarf',
            'Tindouf': 'Tindouf',
            'Tissemsilt': 'Tissemsilt',
            'El Oued': 'El Oued',
            'Khenchela': 'Khenchela',
            'Souk Ahras': 'Souk Ahras',
            'Tipaza': 'Tipaza',
            'Mila': 'Mila',
            'Aïn Defla': 'Aïn Defla',
            'Ain Defla': 'Aïn Defla',
            'Naâma': 'Naâma',
            'Naama': 'Naâma',
            'Aïn Témouchent': 'Aïn Témouchent',
            'Ain Temouchent': 'Aïn Témouchent',
            'Ghardaïa': 'Ghardaïa',
            'Ghardaia': 'Ghardaïa',
            'Relizane': 'Relizane'
        }
    
    def _init_commune_name_mapping(self):
        """Mapping pour les noms de communes spécifiques"""
        self.commune_name_mapping = {
            'Alger Centre': 'Alger',
            'Sétif': 'Sétif',
            'Setif': 'Sétif',
            'B. B. Arreridj': 'Bordj Bou Arreridj',
            'BB Arreridj': 'Bordj Bou Arreridj'
        }
    
    def _init_specific_zones(self):
        """Zones spécifiques pour certaines communes selon le DTR"""
        # Annexe B.5 - Zones été
        self.specific_summer_zones = {
            'Tamanrasset': 'E1',
            'Djanet': 'E1',
            'Illizi': 'E1',
            'Bordj Badji Mokhtar': 'F',
            'Tindouf': 'F',
            'Timimoun': 'E',
            'Adrar': 'E',
            'In Salah': 'E',
            'Touggourt': 'E',
            'Ouargla': 'E',
            'El Oued': 'E',
            'Ghardaïa': 'E',
            'El Meniaa': 'E',
            'Béni Abbès': 'E'
        }
        
        # Zones hiver spécifiques (Annexe A.1)
        self.specific_winter_zones = {
            'Tamanrasset': 'D',
            'Djanet': 'D',
            'Illizi': 'D',
            'Timimoun': 'D',
            'Adrar': 'C',
            'Touggourt': 'C',
            'Ouargla': 'C',
            'El Oued': 'C',
            'Ghardaïa': 'C',
            'Aflou': 'C',
            'Messaad': 'C',
            'Ain Oussara': 'C',
            'Ksar Chellala': 'C',
            'Barika': 'B',
            'Bou Saâda': 'C',
            'El Kantara': 'C',
            'Ksar El Boukhari': 'B'
        }
    
    def _init_winter_rules(self):
        """Initialise les règles de zonage hiver (CHAUFFAGE) - Annexe A.1"""
        
        # Groupes de communes pour la zone A1 (hiver)
        self.winter_a1_communes = {
            'Béjaïa', 'Skikda', 'Dellys', 'Ténès', 'Beni Saf', 'El Kala',
            'Tenes', 'El Marsa', 'Sidi Abderrahmane', 'Sidi Akkacha',
            'Abou El Hassane', 'Talassa', 'Tadjena', 'Moussadek', 'Taougrite',
            'Dahra', 'Herenfa', 'Ain Merane', 'Beni Haoua'
        }
        
        # Règles de température hiver par zone (Tableau 2.2)
        self.winter_temp_rules = {
            'A': [
                {'max_alt': 300, 'temp': 3},
                {'min_alt': 300, 'max_alt': 450, 'temp': 2},
                {'min_alt': 450, 'max_alt': 600, 'temp': 1},
                {'min_alt': 600, 'max_alt': 800, 'temp': 0},
                {'min_alt': 800, 'temp': -1.5}
            ],
            'A1': [
                {'max_alt': 300, 'temp': 7},
                {'min_alt': 300, 'max_alt': 450, 'temp': 6},
                {'min_alt': 450, 'max_alt': 600, 'temp': 5},
                {'min_alt': 600, 'max_alt': 800, 'temp': 4},
                {'min_alt': 800, 'temp': 2.5}
            ],
            'B': [
                {'max_alt': 450, 'temp': -2},
                {'min_alt': 450, 'max_alt': 600, 'temp': -3},
                {'min_alt': 600, 'max_alt': 800, 'temp': -4},
                {'min_alt': 800, 'temp': -5.5}
            ],
            'C': [
                {'max_alt': 300, 'temp': 1},
                {'min_alt': 300, 'max_alt': 450, 'temp': 0},
                {'min_alt': 450, 'max_alt': 600, 'temp': -1},
                {'min_alt': 600, 'max_alt': 800, 'temp': -2},
                {'min_alt': 800, 'temp': -4.5}
            ],
            'D': [
                {'max_alt': 300, 'temp': 4},
                {'min_alt': 300, 'max_alt': 450, 'temp': 3},
                {'min_alt': 450, 'max_alt': 600, 'temp': 2},
                {'min_alt': 600, 'max_alt': 800, 'temp': 1},
                {'min_alt': 800, 'temp': -0.5}
            ]
        }
    
    def _init_summer_rules(self):
        """Initialise les règles de zonage été (CLIMATISATION) - Annexe B.5"""
        
        # Groupes de communes pour la zone B1 (été - Vallée du Chlef)
        self.summer_b1_communes = {
            'Chlef', 'Beni Haoua', 'Tenes', 'Oued Ghoussine', 'Sidi Abderrahmane',
            'Breira', 'Sidi Akkacha', 'Abou El Hassane', 'El Marsa', 'Talassa',
            'Tadjena', 'Moussadek', 'Taougrite', 'Dahra', 'Herenfa', 'Ain Merane'
        }
        
        # Groupes de communes pour la zone B2 (été - Guelma)
        self.summer_b2_communes = {
            'Guelma', 'Bouchegouf', 'Hammam Debagh', 'Bouati Mahmoud',
            'El Fedjoudj', 'Medjez Amar', 'Houari Boumedienne', 'Ras El Agba',
            'Sellaoua Announa', 'Ain Ben Beida', 'Medjez Sfa', 'Oued Ferragha'
        }
        
        # Règles de conditions été par zone (Tableau 9.1)
        self.summer_conditions = {
            'A': [
                {'max_alt': 500, 'TSbe': 34, 'HSbe': 14.5, 'Eb': 9, 'TSm': 25.5, 'EAT': 31},
                {'min_alt': 500, 'max_alt': 1000, 'TSbe': 33.5, 'HSbe': 13, 'Eb': 10, 'TSm': 25, 'EAT': 32.5},
                {'min_alt': 1000, 'TSbe': 30.5, 'HSbe': 13, 'Eb': 9, 'TSm': 22, 'EAT': 31.5}
            ],
            'B': [
                {'max_alt': 500, 'TSbe': 38, 'HSbe': 12.5, 'Eb': 15, 'TSm': 26.5, 'EAT': 36},
                {'min_alt': 500, 'max_alt': 1000, 'TSbe': 37, 'HSbe': 11, 'Eb': 15, 'TSm': 26.5, 'EAT': 36},
                {'min_alt': 1000, 'TSbe': 35, 'HSbe': 10, 'Eb': 14, 'TSm': 25, 'EAT': 36}
            ],
            'B1': [
                {'max_alt': 500, 'TSbe': 42, 'HSbe': 11, 'Eb': 18, 'TSm': 29, 'EAT': 41.5},
                {'min_alt': 500, 'TSbe': 39, 'HSbe': 8.5, 'Eb': 18, 'TSm': 25, 'EAT': 36}
            ],
            'B2': [
                {'TSbe': 38, 'HSbe': 12.5, 'Eb': 15, 'TSm': 26.5, 'EAT': 36}
            ],
            'C': [
                {'max_alt': 500, 'TSbe': 39.5, 'HSbe': 6, 'Eb': 18, 'TSm': 29, 'EAT': 41},
                {'min_alt': 500, 'TSbe': 36, 'HSbe': 11, 'Eb': 15, 'TSm': 29, 'EAT': 36}
            ],
            'D': [
                {'max_alt': 1000, 'TSbe': 40, 'HSbe': 8.5, 'Eb': 20, 'TSm': 27, 'EAT': 41.5},
                {'min_alt': 1000, 'TSbe': 34, 'HSbe': 8.5, 'Eb': 18, 'TSm': 25, 'EAT': 40}
            ],
            'E': [
                {'TSbe': 44, 'HSbe': 6.5, 'Eb': 15.5, 'TSm': 33, 'EAT': 38}
            ],
            'E1': [
                {'max_alt': 500, 'TSbe': 37, 'HSbe': 6, 'Eb': 18, 'TSm': 29, 'EAT': 41},
                {'min_alt': 500, 'TSbe': 34, 'HSbe': 11, 'Eb': 15, 'TSm': 29, 'EAT': 36}
            ],
            'F': [
                {'TSbe': 46, 'HSbe': 5.5, 'Eb': 16.5, 'TSm': 36.5, 'EAT': 43}
            ]
        }
    
    def _init_wilaya_mappings(self):
        """Initialise les mappings complets pour les nouvelles wilayas"""
        
        # Mapping: commune -> (nouvelle_wilaya, nouveau_code, parent_wilaya)
        self.commune_to_new_wilaya = {
            # Wilaya 49 - Timimoun (ex-Adrar)
            'Timimoun': ('Timimoun', '49', 'Adrar'),
            'Ouled Said': ('Timimoun', '49', 'Adrar'),
            'Metarfa': ('Timimoun', '49', 'Adrar'),
            'Talmine': ('Timimoun', '49', 'Adrar'),
            'Ouled Aissa': ('Timimoun', '49', 'Adrar'),
            'Charouine': ('Timimoun', '49', 'Adrar'),
            'Aougrout': ('Timimoun', '49', 'Adrar'),
            'Deldoul': ('Timimoun', '49', 'Adrar'),
            'Tinerkouk': ('Timimoun', '49', 'Adrar'),
            'Ksar Kaddour': ('Timimoun', '49', 'Adrar'),
            
            # Wilaya 50 - Bordj Badji Mokhtar (ex-Adrar)
            'Bordj Badji Mokhtar': ('Bordj Badji Mokhtar', '50', 'Adrar'),
            'Timiaouine': ('Bordj Badji Mokhtar', '50', 'Adrar'),
            
            # Wilaya 51 - Ouled Djellal (ex-Biskra)
            'Ouled Djellal': ('Ouled Djellal', '51', 'Biskra'),
            'Doucen': ('Ouled Djellal', '51', 'Biskra'),
            'Chaiba': ('Ouled Djellal', '51', 'Biskra'),
            'Ras El Miad': ('Ouled Djellal', '51', 'Biskra'),
            'Besbes': ('Ouled Djellal', '51', 'Biskra'),
            'Sidi Khaled': ('Ouled Djellal', '51', 'Biskra'),
            
            # Wilaya 52 - Béni Abbès (ex-Béchar)
            'Beni-Abbes': ('Béni Abbès', '52', 'Béchar'),
            'Tamtert': ('Béni Abbès', '52', 'Béchar'),
            'Igli': ('Béni Abbès', '52', 'Béchar'),
            'El Ouata': ('Béni Abbès', '52', 'Béchar'),
            'Ouled-Khodeir': ('Béni Abbès', '52', 'Béchar'),
            'Kerzaz': ('Béni Abbès', '52', 'Béchar'),
            'Timoudi': ('Béni Abbès', '52', 'Béchar'),
            'Ksabi': ('Béni Abbès', '52', 'Béchar'),
            'Beni-Ikhlef': ('Béni Abbès', '52', 'Béchar'),
            
            # Wilaya 53 - In Salah (ex-Tamanrasset)
            'Ain Salah': ('In Salah', '53', 'Tamanrasset'),
            'Inghar': ('In Salah', '53', 'Tamanrasset'),
            'Foggaret Ezzoua': ('In Salah', '53', 'Tamanrasset'),
            
            # Wilaya 54 - In Guezzam (ex-Tamanrasset)
            'Ain Guezzam': ('In Guezzam', '54', 'Tamanrasset'),
            'Tin Zouatine': ('In Guezzam', '54', 'Tamanrasset'),
            
            # Wilaya 55 - Touggourt (ex-Ouargla)
            'Touggourt': ('Touggourt', '55', 'Ouargla'),
            'Temacine': ('Touggourt', '55', 'Ouargla'),
            'Sidi Slimane': ('Touggourt', '55', 'Ouargla'),
            'Megarine': ('Touggourt', '55', 'Ouargla'),
            'Nezla': ('Touggourt', '55', 'Ouargla'),
            'Blidet Amor': ('Touggourt', '55', 'Ouargla'),
            'Tebesbest': ('Touggourt', '55', 'Ouargla'),
            'Taibet': ('Touggourt', '55', 'Ouargla'),
            'El Alia': ('Touggourt', '55', 'Ouargla'),
            'El-Hadjira': ('Touggourt', '55', 'Ouargla'),
            'Benaceur': ('Touggourt', '55', 'Ouargla'),
            'M\'naguer': ('Touggourt', '55', 'Ouargla'),
            'Zaouia El Abidia': ('Touggourt', '55', 'Ouargla'),
            
            # Wilaya 56 - Djanet (ex-Illizi)
            'Djanet': ('Djanet', '56', 'Illizi'),
            'Bordj El Haouass': ('Djanet', '56', 'Illizi'),
            
            # Wilaya 57 - El M'ghair (ex-El Oued)
            'El-M\'ghaier': ('El M\'ghair', '57', 'El Oued'),
            'Oum Touyour': ('El M\'ghair', '57', 'El Oued'),
            'Sidi Amrane': ('El M\'ghair', '57', 'El Oued'),
            'M\'rara': ('El M\'ghair', '57', 'El Oued'),
            'Djamaa': ('El M\'ghair', '57', 'El Oued'),
            'Tenedla': ('El M\'ghair', '57', 'El Oued'),
            'Still': ('El M\'ghair', '57', 'El Oued'),
            'Sidi Khelil': ('El M\'ghair', '57', 'El Oued'),
            
            # Wilaya 58 - El Menia (ex-Ghardaïa)
            'El Meniaa': ('El Menia', '58', 'Ghardaïa'),
            'Hassi Gara': ('El Menia', '58', 'Ghardaïa'),
            'Hassi Fehal': ('El Menia', '58', 'Ghardaïa'),
            
            # Wilayas 2025
            'Aflou': ('Aflou', '59', 'Laghouat'),
            'Barika': ('Barika', '60', 'Batna'),
            'Ksar Chellala': ('Ksar Chellala', '61', 'Tiaret'),
            'Messaad': ('Messaad', '62', 'Djelfa'),
            'Ain Oussara': ('Ain Oussara', '63', 'Djelfa'),
            'Bou Saâda': ('Bou Saâda', '64', 'M\'sila'),
            'El Abiodh Sidi Cheikh': ('El Abiodh Sidi Cheikh', '65', 'El Bayadh'),
            'El Kantara': ('El Kantara', '66', 'Biskra'),
            'Bir El Ater': ('Bir El Ater', '67', 'Tébessa'),
            'Ksar El Boukhari': ('Ksar El Boukhari', '68', 'Médéa'),
            'El Aricha': ('El Aricha', '69', 'Béchar')
        }
    
    def _init_new_wilaya_codes(self):
        """Initialise les codes des nouvelles wilayas"""
        self.new_wilaya_codes = {
            'Timimoun': '49',
            'Bordj Badji Mokhtar': '50',
            'Ouled Djellal': '51',
            'Béni Abbès': '52',
            'In Salah': '53',
            'In Guezzam': '54',
            'Touggourt': '55',
            'Djanet': '56',
            'El M\'ghair': '57',
            'El Menia': '58',
            'Aflou': '59',
            'Barika': '60',
            'Ksar Chellala': '61',
            'Messaad': '62',
            'Ain Oussara': '63',
            'Bou Saâda': '64',
            'El Abiodh Sidi Cheikh': '65',
            'El Kantara': '66',
            'Bir El Ater': '67',
            'Ksar El Boukhari': '68',
            'El Aricha': '69'
        }
    
    def get_wilaya_info(self, commune_name: str, original_wilaya: str) -> Dict:
        """
        Récupère les informations de wilaya pour une commune
        """
        if commune_name in self.commune_to_new_wilaya:
            new_wilaya, new_code, parent_wilaya = self.commune_to_new_wilaya[commune_name]
            return {
                'current_wilaya_name': new_wilaya,
                'current_wilaya_code': new_code,
                'original_wilaya_name': original_wilaya,
                'parent_wilaya': parent_wilaya,
                'is_new_wilaya': True,
                'established': '2019' if int(new_code) <= 58 else '2025'
            }
        else:
            return {
                'current_wilaya_name': original_wilaya,
                'current_wilaya_code': self._get_wilaya_code(original_wilaya),
                'original_wilaya_name': original_wilaya,
                'parent_wilaya': original_wilaya,
                'is_new_wilaya': False,
                'established': '1984'
            }
    
    def _get_wilaya_code(self, wilaya_name: str) -> str:
        """Convertit un nom de wilaya en code"""
        wilaya_codes = {
            'Adrar': '01', 'Chlef': '02', 'Laghouat': '03', 'Oum El Bouaghi': '04',
            'Batna': '05', 'Béjaïa': '06', 'Biskra': '07', 'Béchar': '08',
            'Blida': '09', 'Bouira': '10', 'Tamanrasset': '11', 'Tébessa': '12',
            'Tlemcen': '13', 'Tiaret': '14', 'Tizi Ouzou': '15', 'Alger': '16',
            'Djelfa': '17', 'Jijel': '18', 'Sétif': '19', 'Saïda': '20',
            'Skikda': '21', 'Sidi Bel Abbès': '22', 'Annaba': '23', 'Guelma': '24',
            'Constantine': '25', 'Médéa': '26', 'Mostaganem': '27', 'M\'sila': '28',
            'Mascara': '29', 'Ouargla': '30', 'Oran': '31', 'El Bayadh': '32',
            'Illizi': '33', 'Bordj Bou Arréridj': '34', 'Bordj Bou Arreridj': '34',
            'Boumerdès': '35', 'El Tarf': '36', 'Tindouf': '37', 'Tissemsilt': '38',
            'El Oued': '39', 'Khenchela': '40', 'Souk Ahras': '41', 'Tipaza': '42',
            'Mila': '43', 'Aïn Defla': '44', 'Naâma': '45', 'Aïn Témouchent': '46',
            'Ghardaïa': '47', 'Relizane': '48', 'Algiers': '16',
            'Bordj Bou Arreridj': '34', 'Bordj Bou Arréridj': '34'
        }
        return wilaya_codes.get(wilaya_name, '00')
    
    def determine_winter_zone(self, commune: Dict[str, Any], wilayas_data: List[Dict]) -> Tuple[str, float]:
        """
        Détermine la zone climatique hiver et la température de base
        """
        commune_name = commune.get('commune_name_ascii', '')
        wilaya_info = commune.get('wilaya_info', {})
        parent_wilaya = wilaya_info.get('parent_wilaya', commune.get('wilaya_name_ascii', ''))
        
        # Vérifier les zones spécifiques d'abord
        if commune_name in self.specific_winter_zones:
            zone = self.specific_winter_zones[commune_name]
        elif parent_wilaya in self.specific_winter_zones:
            zone = self.specific_winter_zones[parent_wilaya]
        # Règle 1: Vérifier si la commune est dans la zone A1
        elif commune_name in self.winter_a1_communes:
            zone = 'A1'
        else:
            # Utiliser la wilaya parente pour les données d'altitude avec recherche normalisée
            wilaya_data = self.find_wilaya_by_name(parent_wilaya, wilayas_data)
            
            if not wilaya_data:
                # Dernier recours : chercher sans normalisation
                for w in wilayas_data:
                    if w.get('name', '').lower() == parent_wilaya.lower():
                        wilaya_data = w
                        break
            
            if not wilaya_data:
                # Si toujours pas trouvé, logger et utiliser valeur par défaut
                logger.debug(f"Wilaya non trouvée: {parent_wilaya} pour commune {commune_name} (utilisation valeurs par défaut)")
                return 'A', 3
            
            altitude = wilaya_data.get('elevation', 0)
            
            # Logique de zonage hiver basée sur le DTR
            if altitude < 500:
                zone = 'A'
            elif 500 <= altitude < 800:
                zone = 'B'
            elif 800 <= altitude < 1200:
                zone = 'C'
            else:
                if 'Tamanrasset' in parent_wilaya or 'Illizi' in parent_wilaya:
                    zone = 'D'
                else:
                    zone = 'C'
        
        # Calculer la température de base
        temp = self.get_winter_base_temp(zone, commune, wilayas_data)
        
        return zone, temp
    
    def get_winter_base_temp(self, zone: str, commune: Dict[str, Any], wilayas_data: List[Dict]) -> float:
        """
        Calcule la température de base hiver selon le Tableau 2.2
        """
        wilaya_info = commune.get('wilaya_info', {})
        parent_wilaya = wilaya_info.get('parent_wilaya', commune.get('wilaya_name_ascii', ''))
        
        wilaya_data = self.find_wilaya_by_name(parent_wilaya, wilayas_data)
        
        if not wilaya_data:
            # Valeur par défaut selon la zone
            default_temps = {'A': 3, 'A1': 7, 'B': -2, 'C': 1, 'D': 4}
            return default_temps.get(zone, 3)
        
        altitude = wilaya_data.get('elevation', 0)
        rules = self.winter_temp_rules.get(zone, self.winter_temp_rules['A'])
        
        for rule in rules:
            if 'max_alt' in rule and altitude <= rule['max_alt']:
                return rule['temp']
            elif 'min_alt' in rule and 'max_alt' in rule:
                if rule['min_alt'] <= altitude <= rule['max_alt']:
                    return rule['temp']
        
        return rules[-1]['temp']
    
    def determine_summer_zone(self, commune: Dict[str, Any], wilayas_data: List[Dict]) -> Tuple[str, Dict]:
        """
        Détermine la zone climatique été et les conditions associées
        """
        commune_name = commune.get('commune_name_ascii', '')
        wilaya_info = commune.get('wilaya_info', {})
        parent_wilaya = wilaya_info.get('parent_wilaya', commune.get('wilaya_name_ascii', ''))
        
        # Vérifier les zones spécifiques d'abord
        if commune_name in self.specific_summer_zones:
            zone = self.specific_summer_zones[commune_name]
        elif parent_wilaya in self.specific_summer_zones:
            zone = self.specific_summer_zones[parent_wilaya]
        elif commune_name in self.summer_b1_communes:
            zone = 'B1'
        elif commune_name in self.summer_b2_communes:
            zone = 'B2'
        else:
            wilaya_data = self.find_wilaya_by_name(parent_wilaya, wilayas_data)
            
            if not wilaya_data:
                # Valeur par défaut
                return 'A', self.summer_conditions['A'][0]
            
            altitude = wilaya_data.get('elevation', 0)
            
            # Logique de zonage été basée sur le DTR
            if altitude < 500:
                if self._is_coastal(commune, parent_wilaya):
                    zone = 'A'
                elif 'Chlef' in parent_wilaya:
                    zone = 'B1'
                elif 'Guelma' in parent_wilaya:
                    zone = 'B2'
                else:
                    zone = 'C' if altitude > 300 else 'A'
            elif 500 <= altitude < 1000:
                zone = 'C'
            elif 1000 <= altitude < 1500:
                zone = 'D'
            else:
                if 'Tamanrasset' in parent_wilaya or 'Djanet' in parent_wilaya:
                    zone = 'E1'
                elif 'Bordj Badji Mokhtar' in parent_wilaya or 'Tindouf' in parent_wilaya:
                    zone = 'F'
                else:
                    zone = 'E'
        
        conditions = self.get_summer_conditions(zone, commune, wilayas_data)
        
        return zone, conditions
    
    def _is_coastal(self, commune: Dict[str, Any], parent_wilaya: str) -> bool:
        """Vérifie si une commune est côtière"""
        coastal_wilayas = {'Alger', 'Oran', 'Annaba', 'Skikda', 'Jijel', 'Béjaïa', 
                          'Mostaganem', 'Tipaza', 'Boumerdès', 'El Tarf', 'Chlef',
                          'Tizi Ouzou', 'Aïn Témouchent', 'Tlemcen', 'Algiers'}
        
        # Normaliser pour la comparaison
        norm_parent = self.normalize_name(parent_wilaya)
        for coastal in coastal_wilayas:
            if self.normalize_name(coastal) == norm_parent:
                return True
        return False
    
    def get_summer_conditions(self, zone: str, commune: Dict[str, Any], wilayas_data: List[Dict]) -> Dict:
        """
        Récupère les conditions été pour une zone
        """
        wilaya_info = commune.get('wilaya_info', {})
        parent_wilaya = wilaya_info.get('parent_wilaya', commune.get('wilaya_name_ascii', ''))
        
        wilaya_data = self.find_wilaya_by_name(parent_wilaya, wilayas_data)
        
        if not wilaya_data:
            # Valeurs par défaut selon la zone
            default_conditions = {
                'A': {'base_temp': 34, 'specific_humidity': 14.5, 'diurnal_range': 9, 'mean_temp': 25.5, 'annual_range': 31},
                'B': {'base_temp': 38, 'specific_humidity': 12.5, 'diurnal_range': 15, 'mean_temp': 26.5, 'annual_range': 36},
                'C': {'base_temp': 39.5, 'specific_humidity': 6, 'diurnal_range': 18, 'mean_temp': 29, 'annual_range': 41},
                'D': {'base_temp': 40, 'specific_humidity': 8.5, 'diurnal_range': 20, 'mean_temp': 27, 'annual_range': 41.5},
                'E': {'base_temp': 44, 'specific_humidity': 6.5, 'diurnal_range': 15.5, 'mean_temp': 33, 'annual_range': 38},
                'E1': {'base_temp': 37, 'specific_humidity': 6, 'diurnal_range': 18, 'mean_temp': 29, 'annual_range': 41},
                'F': {'base_temp': 46, 'specific_humidity': 5.5, 'diurnal_range': 16.5, 'mean_temp': 36.5, 'annual_range': 43}
            }
            return default_conditions.get(zone, default_conditions['A'])
        
        altitude = wilaya_data.get('elevation', 0)
        zone_conditions = self.summer_conditions.get(zone, self.summer_conditions['A'])
        
        if isinstance(zone_conditions, list):
            for rule in zone_conditions:
                if 'max_alt' in rule and altitude <= rule['max_alt']:
                    return {
                        'base_temp': rule['TSbe'],
                        'specific_humidity': rule['HSbe'],
                        'diurnal_range': rule['Eb'],
                        'mean_temp': rule['TSm'],
                        'annual_range': rule['EAT']
                    }
                elif 'min_alt' in rule and 'max_alt' in rule:
                    if rule['min_alt'] <= altitude <= rule['max_alt']:
                        return {
                            'base_temp': rule['TSbe'],
                            'specific_humidity': rule['HSbe'],
                            'diurnal_range': rule['Eb'],
                            'mean_temp': rule['TSm'],
                            'annual_range': rule['EAT']
                        }
            
            last_rule = zone_conditions[-1]
            return {
                'base_temp': last_rule['TSbe'],
                'specific_humidity': last_rule['HSbe'],
                'diurnal_range': last_rule['Eb'],
                'mean_temp': last_rule['TSm'],
                'annual_range': last_rule['EAT']
            }
        else:
            return {
                'base_temp': zone_conditions['TSbe'],
                'specific_humidity': zone_conditions['HSbe'],
                'diurnal_range': zone_conditions['Eb'],
                'mean_temp': zone_conditions['TSm'],
                'annual_range': zone_conditions['EAT']
            }
    
    def get_altitude_range(self, altitude: float) -> str:
        """Détermine la tranche d'altitude réglementaire"""
        if altitude < 300:
            return "<300m"
        elif altitude < 500:
            return "300-500m"
        elif altitude < 800:
            return "500-800m"
        elif altitude < 1000:
            return "800-1000m"
        else:
            return "≥1000m"
    
    def enrich_commune(self, commune: Dict[str, Any], wilayas_data: List[Dict]) -> Dict[str, Any]:
        """
        Enrichit une commune avec les données climatiques et met à jour la wilaya
        """
        # Récupérer les informations de wilaya
        commune_name = commune.get('commune_name_ascii', '')
        original_wilaya = commune.get('wilaya_name_ascii', '')
        
        # Appliquer le mapping des noms de communes si nécessaire
        mapped_commune_name = self.commune_name_mapping.get(commune_name, commune_name)
        
        wilaya_info = self.get_wilaya_info(mapped_commune_name, original_wilaya)
        commune['wilaya_info'] = wilaya_info
        
        # Mettre à jour les champs de wilaya si c'est une nouvelle wilaya
        if wilaya_info['is_new_wilaya']:
            commune['wilaya_name_ascii'] = wilaya_info['current_wilaya_name']
            commune['wilaya_name'] = self._get_arabic_name(wilaya_info['current_wilaya_name'])
            commune['wilaya_code'] = wilaya_info['current_wilaya_code']
        
        # Déterminer les zones climatiques
        winter_zone, winter_temp = self.determine_winter_zone(commune, wilayas_data)
        summer_zone, summer_conditions = self.determine_summer_zone(commune, wilayas_data)
        
        # Récupérer l'altitude de la wilaya parente
        parent_wilaya = wilaya_info['parent_wilaya']
        wilaya_data = self.find_wilaya_by_name(parent_wilaya, wilayas_data)
        altitude = wilaya_data.get('elevation', 0) if wilaya_data else 0
        
        # Créer l'objet climate_zones
        climate_zones = {
            'winter': {
                'zone': winter_zone,
                'base_temp': winter_temp,
                'altitude_range': self.get_altitude_range(altitude)
            },
            'summer': {
                'zone': summer_zone,
                'conditions': summer_conditions,
                'altitude_range': self.get_altitude_range(altitude)
            }
        }
        
        commune['climate_zones'] = climate_zones
        
        return commune
    
    def _get_arabic_name(self, wilaya_name: str) -> str:
        """Retourne le nom arabe d'une wilaya"""
        arabic_names = {
            'Timimoun': 'تيميمون',
            'Bordj Badji Mokhtar': 'برج باجي مختار',
            'Ouled Djellal': 'أولاد جلال',
            'Béni Abbès': 'بني عباس',
            'In Salah': 'عين صالح',
            'In Guezzam': 'عين قزام',
            'Touggourt': 'تقرت',
            'Djanet': 'جانت',
            'El M\'ghair': 'المغير',
            'El Menia': 'المنيعة',
            'Aflou': 'أفلو',
            'Barika': 'بريكة',
            'Ksar Chellala': 'قصر الشلالة',
            'Messaad': 'مسعد',
            'Ain Oussara': 'عين وسارة',
            'Bou Saâda': 'بوسعادة',
            'El Abiodh Sidi Cheikh': 'الأبيض سيدي الشيخ',
            'El Kantara': 'القنطرة',
            'Bir El Ater': 'بئر العاتر',
            'Ksar El Boukhari': 'قصر البخاري',
            'El Aricha': 'العريشة'
        }
        return arabic_names.get(wilaya_name, wilaya_name)
    
    def enrich_all_communes(self, communes_file: str, wilayas_file: str, output_file: str):
        """
        Enrichit toutes les communes et sauvegarde le résultat
        """
        logger.info(f"Début de l'enrichissement des communes")
        logger.info(f"Fichier communes: {communes_file}")
        logger.info(f"Fichier wilayas: {wilayas_file}")
        
        # Charger les fichiers
        with open(communes_file, 'r', encoding='utf-8') as f:
            communes = json.load(f)
        
        with open(wilayas_file, 'r', encoding='utf-8') as f:
            wilayas_data = json.load(f)
            if 'wilayas' in wilayas_data:
                wilayas_list = wilayas_data['wilayas']
            else:
                wilayas_list = wilayas_data
        
        logger.info(f"Communes chargées: {len(communes)}")
        logger.info(f"Wilayas chargées: {len(wilayas_list)}")
        
        # Afficher les noms des wilayas pour vérification (optionnel)
        wilaya_names = [w.get('name', '') for w in wilayas_list]
        logger.debug(f"Noms des wilayas: {sorted(wilaya_names)}")
        
        # Enrichir chaque commune
        enriched_communes = []
        new_wilaya_count = 0
        warning_count = 0
        
        for idx, commune in enumerate(communes, 1):
            try:
                enriched = self.enrich_commune(commune, wilayas_list)
                enriched_communes.append(enriched)
                
                if enriched.get('wilaya_info', {}).get('is_new_wilaya'):
                    new_wilaya_count += 1
                
                if idx % 500 == 0:
                    logger.info(f"Progression: {idx}/{len(communes)} communes traitées")
                    
            except Exception as e:
                logger.error(f"Erreur sur commune {commune.get('commune_name_ascii', 'inconnue')}: {str(e)}")
                enriched_communes.append(commune)
                warning_count += 1
        
        # Sauvegarder le résultat
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_communes, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Enrichissement terminé")
        logger.info(f"Total communes: {len(enriched_communes)}")
        logger.info(f"Nouvelles wilayas: {new_wilaya_count} communes concernées")
        logger.info(f"Warnings: {warning_count}")
        logger.info(f"Fichier sauvegardé: {output_file}")
        
        self._print_statistics(enriched_communes)
    
    def _print_statistics(self, communes: List[Dict]):
        """Affiche des statistiques détaillées"""
        winter_zones = {}
        summer_zones = {}
        new_wilayas = {}
        
        for commune in communes:
            if 'climate_zones' in commune:
                winter_zone = commune['climate_zones']['winter']['zone']
                summer_zone = commune['climate_zones']['summer']['zone']
                
                winter_zones[winter_zone] = winter_zones.get(winter_zone, 0) + 1
                summer_zones[summer_zone] = summer_zones.get(summer_zone, 0) + 1
            
            if commune.get('wilaya_info', {}).get('is_new_wilaya'):
                new_wilaya = commune['wilaya_info']['current_wilaya_name']
                new_wilayas[new_wilaya] = new_wilayas.get(new_wilaya, 0) + 1
        
        logger.info("\n=== Statistiques de l'enrichissement ===")
        logger.info("Zones hiver: " + ', '.join([f"{k}: {v}" for k, v in sorted(winter_zones.items())]))
        logger.info("Zones été: " + ', '.join([f"{k}: {v}" for k, v in sorted(summer_zones.items())]))
        
        if new_wilayas:
            logger.info("\nCommunes dans les nouvelles wilayas:")
            for wilaya, count in sorted(new_wilayas.items()):
                logger.info(f"  - {wilaya}: {count} communes")
        
        self._verify_examples(communes)
    
    def _verify_examples(self, communes: List[Dict]):
        """Vérifie quelques communes connues"""
        examples = [
            {'name': 'Alger Centre', 'display': 'Alger', 'expected_winter': 'A', 'expected_summer': 'A'},
            {'name': 'Sétif', 'display': 'Sétif', 'expected_winter': 'B', 'expected_summer': 'C'},
            {'name': 'Tamanrasset', 'display': 'Tamanrasset', 'expected_winter': 'D', 'expected_summer': 'E1'},
            {'name': 'Timimoun', 'display': 'Timimoun', 'expected_winter': 'D', 'expected_summer': 'E', 'new_wilaya': 'Timimoun'},
            {'name': 'Aflou', 'display': 'Aflou', 'expected_winter': 'C', 'expected_summer': 'C', 'new_wilaya': 'Aflou'},
            {'name': 'Barika', 'display': 'Barika', 'expected_winter': 'B', 'expected_summer': 'D', 'new_wilaya': 'Barika'},
            {'name': 'Touggourt', 'display': 'Touggourt', 'expected_winter': 'C', 'expected_summer': 'E', 'new_wilaya': 'Touggourt'}
        ]
        
        logger.info("\n=== Vérification d'exemples ===")
        for example in examples:
            found = False
            for commune in communes:
                if commune.get('commune_name_ascii') == example['name'] and 'climate_zones' in commune:
                    found = True
                    wilaya_info = commune.get('wilaya_info', {})
                    
                    # Vérifier si c'est une nouvelle wilaya
                    new_wilaya_check = ""
                    if 'new_wilaya' in example:
                        is_new = wilaya_info.get('is_new_wilaya', False)
                        current_wilaya = wilaya_info.get('current_wilaya_name', '')
                        if is_new and current_wilaya == example['new_wilaya']:
                            new_wilaya_check = "✓ Nouvelle wilaya OK"
                        else:
                            new_wilaya_check = "✗ Nouvelle wilaya incorrecte"
                    
                    winter_ok = commune['climate_zones']['winter']['zone'] == example['expected_winter']
                    summer_ok = commune['climate_zones']['summer']['zone'] == example['expected_summer']
                    
                    status = "✓" if winter_ok and summer_ok else "?"
                    logger.info(f"{status} {example['display']}: "
                              f"Hiver={commune['climate_zones']['winter']['zone']} (attendu {example['expected_winter']}), "
                              f"Été={commune['climate_zones']['summer']['zone']} (attendu {example['expected_summer']}) "
                              f"{new_wilaya_check}")
                    
                    if 'new_wilaya' in example:
                        logger.info(f"    → Wilaya: {wilaya_info.get('current_wilaya_name')} "
                                  f"(code {wilaya_info.get('current_wilaya_code')}), "
                                  f"parent: {wilaya_info.get('parent_wilaya')}")
                    break
            
            if not found:
                # Chercher avec le display name
                for commune in communes:
                    if commune.get('commune_name_ascii') == example.get('display') and 'climate_zones' in commune:
                        found = True
                        logger.info(f"✓ Trouvé avec nom d'affichage: {example['display']}")
                        break
                
                if not found:
                    logger.warning(f"✗ {example['display']} non trouvée")


def main():
    """Fonction principale"""
    script_dir = Path(__file__).parent
    communes_file = script_dir / 'algeria_cities.json'
    wilayas_file = script_dir / 'data_communes_algeria_updated.json'
    output_file = script_dir / 'algeria_cities_enriched_final_v2.json'
    
    if not communes_file.exists():
        logger.error(f"Fichier communes non trouvé: {communes_file}")
        return
    
    if not wilayas_file.exists():
        logger.error(f"Fichier wilayas non trouvé: {wilayas_file}")
        return
    
    enricher = AlgerianClimateEnricher()
    enricher.enrich_all_communes(
        str(communes_file),
        str(wilayas_file),
        str(output_file)
    )


if __name__ == "__main__":
    main()
