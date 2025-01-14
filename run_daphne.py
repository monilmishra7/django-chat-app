import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')
django.setup()

from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    cli = CommandLineInterface()
    cli.run(["-p", "8001", "chat_project.asgi:application"])