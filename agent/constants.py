import os
from dotenv import load_dotenv
load_dotenv()

ENV = os.getenv("ENV")

if ENV == "local":
    MODEL="gemini-2.5-flash"
    AMI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/asigurare-medicala_1754643254301"
    TRAINING_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/training_1754549769417"
    SALARIZARE_VANZARI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/salarizare-vanzari_1754549885702"
    RELATII_MUNCA_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/relatii-munca_1754549933330"
    LOGISTICA_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/logistica_1754549990935"
    BENEFICII_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/beneficii-2_1757671228699"
    EVALUAREA_PERFORMANTEI_DATASTORE="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/evaluarea-performantei_1754550133241"

    PROJECT_ID = "prj-hackathon-team2"
    LOCATION = "eu"
    FULL_ENGINE_ID = "test-search_1754642633497"
else:
    MODEL="gemini-2.5-flash"
    AMI_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/asigurare-medicala_1757922951189"
    TRAINING_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/training_1757923333158"
    SALARIZARE_VANZARI_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/salarizare-vanzari_1757923300096"
    RELATII_MUNCA_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/relatii-munca_1757923263530"
    LOGISTICA_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/logistica_1757923216644"
    BENEFICII_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/beneficii_1757923086197"
    EVALUAREA_PERFORMANTEI_DATASTORE="projects/prj-test-hrminds/locations/eu/collections/default_collection/dataStores/evaluarea-performantei_1757923174511"

    PROJECT_ID = "prj-test-hrminds"
    LOCATION = "eu"
    FULL_ENGINE_ID = "app-search-test-hrminds_1757923593830"