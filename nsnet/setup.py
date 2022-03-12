import setuptools 

with open('requirements.txt') as requirements_file:
  install_requirements = requirements_file.read().splitlines()

with open('README.md', 'r', encoding='utf-8') as fh:
  long_description = fh.read()

if __name__ == '__main__':
  setuptools.setup(
  name='nsnet',
  version='0.0.1',
  author='shin-ch13',
  description='Nsnet creat docker container with flexible network',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/shin-ch13/network-lab/nsnet',
  python_requires='>=3.6.9',
  install_requires=install_requirements,
  package_dir={'': 'src'},
  packages=setuptools.find_packages(where="src"),
  entry_points={
      'console_scripts':[
          'link-dokcer-ns=link_docker_ns:main',
          'nsnet=nsnet:main',
        ]
  },
  classifiers=[
    'Programming Language :: Python :: 3.6.9'
    ]
  )