"""# lucidium.setup

# Lucidium setup utility.
"""

from setuptools import find_packages, setup

setup(
    name =              "lucidium",
    version =           "0.0.0",
    author =            "Gabriel C. Trahan",
    author_email =      "gabrieltrahan777@hotmail.com",
    description =       """Experiments in neuro-symbolic reinforcement learning in the pursuit of 
                        developing agents/methods to aid in organic reasoning, inference, and 
                        logic.""",
    license =           "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007",
    license_files =     ("LICENSE"),
    url =               "https://github.com/theokoles7/lucidium",
    packages =          find_packages(),
    python_requires =   ">=3.10",
    install_requires =  [
                            
                        ]
)