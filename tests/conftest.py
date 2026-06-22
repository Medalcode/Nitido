import sys
import os

# Agregar la carpeta 'backend' al path para que los tests encuentren el módulo 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
