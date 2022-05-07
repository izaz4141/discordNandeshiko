from setuptools import setup

with open("data/requirements/release.txt", mode='r', encoding='utf-8') as req:
    packages = req.read().splitlines()

setup(
   name='discordNandeshiko',
   version='0.0.3',
   description='discord bot with python 3.10.2',
   author='Glicole',
   author_email='atranzryou@gmail.com',
   url='https://github.com/izaz4141/discordNandeshiko/',
   packages=['discordNandeshiko'],  # would be the same as name
   classifiers=[
       'Programming Language :: Python :: 3.10.2',
       'Natural Language :: Indonesia'
   ],
   python_requires='==3.10.2',
   install_requires=packages,
   project_urls={
       'Bug Reports': 'https://github.com/izaz4141/discordNandeshiko/issues/',
       'Source': 'https://github.com/izaz4141/discordNandeshiko/'
   },
   keywords="discord discordbot"
)