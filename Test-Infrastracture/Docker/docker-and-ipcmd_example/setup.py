import setuptools 

if __name__ == "__main__":
    setuptools.setup(
        name='link_dokcer-ns',
        version='0.0.1',
        description="This program links dokcer-namespace-id to host-namespace",
        author="shin-ch13",
        python_requires='>=3.6.9',
        packages=setuptools.find_packages(''),
        # 'console_scripts'はapp名(左辺)に'_'は使えない。package名(右辺)に'-'は使えない。
        entry_points={
            'console_scripts':[ 'link-dokcer-ns=link_docker_ns:main']
        },
        classifiers=[
            'Programming Language :: Python :: 3.6.9'
        ]
    )