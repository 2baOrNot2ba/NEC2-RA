from setuptools import setup, find_packages

setup(name='',
      version='0.1',
      description='Antenna pattern tools.',
      author='Tobia D. Carozzi',
      author_email='tobia.carozzi@chalmers.se',
      packages=find_packages(exclude=('tests', 'docs')),
      license='MIT',
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Telecommunications Industry',
          'License :: OSI Approved :: ISC License',
          'Programming Language :: Python :: 3.8',
          'Topic :: Communications :: Ham Radio',
          'Topic :: Scientific/Engineering :: Mathematics'
      ],
      install_requires=[
          'numpy>=1.10',
          'PyNEC==1.7.3.4',
          'matplotlib'
      ],
      #scripts=[]
      )