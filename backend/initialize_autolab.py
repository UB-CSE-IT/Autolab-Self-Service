import os

from dotenv import load_dotenv

from backend.connections.autolab_api_connection import AutolabApiConnection

if __name__ == '__main__':
    load_dotenv()
    AutolabApiConnection(os.getenv("AUTOLAB_ROOT"), os.getenv("AUTOLAB_CLIENT_ID"),
                         os.getenv("AUTOLAB_CLIENT_SECRET"), os.getenv("AUTOLAB_CLIENT_CALLBACK"))
