from src.models.psped import Foreas

for foreas in Foreas.objects():
    foreas.build_tree()
