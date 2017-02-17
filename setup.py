from setuptools import setup, find_packages

setup(name='tsa',
      version='0.0',
      description='Topological Sensitivity Analysis',
      url='http://github.com/ananth-pallaseni/TSA',
      author='Ananth Pallaseni',
      author_email='ananth.pallaseni@gmail.com',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'scipy'
      ],
      zip_safe=False)