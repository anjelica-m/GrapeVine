"""
Module containing the app configuration

Authors:
    James Schaefer-Pham
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.apps import AppConfig


class ProjectConfig(AppConfig):
    """App configuration for the project app."""
    name = 'project'

    def ready(self) -> None:
        from . import signals
