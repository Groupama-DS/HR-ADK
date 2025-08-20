import os
from dotenv import load_dotenv
load_dotenv()

MODEL="gemini-2.5-flash"
# AMI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/ami-main-docs_1750757232003"
# TRAINING_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/training_1754549769417"
# SALARIZARE_VANZARI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/salarizare-vanzari_1754549885702"
# RELATII_MUNCA_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/relatii-munca_1754549933330"
# LOGISTICA_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/logistica_1754549990935"
# BENEFICII_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/beneficii_1754550084766"
# EVALUAREA_PERFORMANTEI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/evaluarea-performantei_1754550133241"


PROJECT_ID = "prj-hackathon-team2"
LOCATION = "eu"
TEST_ENGINE_ID = "test-search_1754642633497"
AMI_ENGINE_ID = "asigurare-medicala_1755091622568"
SALARIZARE_VANZARI_ENGINNE_ID="salarizare-vanzari_1755155324183"
RELATII_MUNCA_ENGINE_ID="relatii-munca_1755155359529"
LOGISTICA_ENGINE_ID="logistica_1755155531609"
BENEFICII_ENGINE_ID="beneficii_1755155561616"
EVALUAREA_PERFORMANTEI_ENGINE_ID="evaluarea-performantei_1755155598201"
TRAINING_ENGINE_ID="training_1755091659945"