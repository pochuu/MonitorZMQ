from setuptools import setup, find_packages

setup(
   name='monitor',
   version='1.0',
   description='Distributed monitor using ZMQ',
   author='pochuu',
   author_email='kasprzak226@gmail.com',
   packages=find_packages(),  #same as name
   install_requires=['pyzmq==23.2.0','zmq==0.0.0'], #external packages as dependencies
)