from subprocess import Popen
import sys

p1 = Popen(["python", "client1.py"])
p2 = Popen(["python", "client2.py"])

p1.wait(); p2.wait(); 

