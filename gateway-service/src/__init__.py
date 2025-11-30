"""
Gateway Service - Point d'entrée unique pour tous les services

Ce service gère le routage des requêtes, la validation JWT,
et le rate limiting. Il sert de proxy entre le frontend et
les services backend.
"""

__version__ = '1.0.0'
__author__ = 'Lucas PIRES, Soheil BENABIDA, Kevin CARTTIGUEANE'