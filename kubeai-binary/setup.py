from setuptools import setup, find_packages

setup(
    name='kubeai',
    version='1.0',
    py_modules=['kubeai'],
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        kubeai=kubeai:ask_chatgpt
    ''',
)
