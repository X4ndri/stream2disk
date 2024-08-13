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
            'your_command=app:archx', 
        ],
    },
    description='a GUI wrapper for ffmpeg stream to disk functionality',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ahmad Abdal Qader',
    url='https://qader.dev',  # Optional
)
