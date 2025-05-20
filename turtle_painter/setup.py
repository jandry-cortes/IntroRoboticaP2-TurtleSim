from setuptools import find_packages, setup

package_name = 'turtle_painter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jandrito',
    maintainer_email='jandrito@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "my_second_node = turtle_painter.my_second_node:main",
            "draw_circle = turtle_painter.draw_circle:main",
            "pose_subscriber = turtle_painter.pose_subscriber:main",
            "turtle_controller = turtle_painter.turtle_controller:main",
            "turtle_painter = turtle_painter.turtle_painter:main"
        ],
    },
)
