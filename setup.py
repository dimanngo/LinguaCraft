import glob
from setuptools import setup, find_packages

setup(
    name='LinguaCraft',  # Project name
    version='0.1.3',    # Initial version
    author='Dmytro Golodiuk',  # Your name
    author_email='info@golodiuk.com',  # Your email
    description='A personalized companion for mastering foreign languages.',  # Short description
    long_description=open('README.md').read(),  # Ensure you have a README.md file
    long_description_content_type='text/markdown',
    url='https://github.com/dimanngo/LinguaCraft',  # Project URL
    packages=find_packages(where='src'),  # Automatically find packages in the src directory
    package_dir={'': 'src'},  # Specify that packages are in the src directory
    include_package_data=True,  # Include non-python files in the package
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change if using a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version
    install_requires=[
        'deep-translator',  # Required for translation functionality
        'langdetect',  # Required for language detection
        'nltk',  # Required for natural language processing
        'openai',  # Required for OpenAI API calls
        'python-dotenv',  # Required for environment variables
        'requests',  # Required for HTTP requests
        'rich',  # Required for rich text formatting
        'spacy',  # Required for lemmatization
        'textual',  # Required for the Textual library
    ],
    entry_points={
        'console_scripts': [
            'linguacraft=linguacraft.main:main',  # Entry point for the command line
        ],
    },
)