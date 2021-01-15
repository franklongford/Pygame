from setuptools import find_packages, setup


def main():
    """ Entry point for script execution. """
    setup(
        name='ants',
        version=0.1,
        install_requires=[
            'scikit-image',
            'pygame',
            'numpy'
        ],
        entry_points={
            "gui_scripts": [
                'run_game = ants.__main__:main'
            ]
        },
        packages=find_packages(),
        include_package_data = True
    )


if __name__ == '__main__':
    main()
