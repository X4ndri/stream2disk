from setuptools import setup, find_packages

setup(
    name='stream2disk',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'dearpygui', 'pathlib'
    ],
    entry_points={
        'console_scripts': [
            'your_command=your_script:main',  # Replace 'main' with the function to run
        ],
    },
    description='A brief description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://yourprojecthomepage.com',  # Optional
)
