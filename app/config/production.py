"""app/config/production.py
"""
import os

DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', '')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
JSON_AS_ASCII = False
