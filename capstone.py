from ev3dev.ev3 import *
import threading
import random
from time import *
import math
myLock = threading.Lock()

mB = LargeMotor('outC') #Left Wheel for moving forward and back
mC = LargeMotor('outB') #Right Wheel for moving forward and back
mD = LargeMotor('outD') #Used for the launcher
potentialShot = False
foundline = False
direction = 1


# Put the IR sensor into distance mode.
irright = InfraredSensor('in1')
irright.mode = 'IR-PROX'
irleft = InfraredSensor('in2')
irleft.mode = 'IR-PROX'
#connect TouchSensor
ts = TouchSensor()
#connact ColorSensor
cl = ColorSensor()



# Record the initial separation of the sensor and the object
right = irright.value()
left = irleft.value()

#function that searches for the different color lines
def funcDrive():
	global foundline
	global direction
	while (True):
		myLock.acquire(True)
		mB.run_forever(speed_sp= 100)
		mC.run_forever(speed_sp= 100) 
		myLock.release()

		#if the robot runs into a wall it will backup and turn for 3 seconds
		if ts.value() == 1:
			myLock.acquire(True)
			mB.run_forever(speed_sp= -50)
			mC.run_forever(speed_sp= -50) 
			sleep(2)
			
			mB.stop(stop_action="brake")
			mC.stop(stop_action="brake")
			
			mB.run_forever(speed_sp= 50)
			mC.run_forever(speed_sp= -50)
			sleep(3)

			mB.stop(stop_action="brake")
			mC.stop(stop_action="brake")

			myLock.release()	

			#red == 5     blue == 2
			#when finding the red line it'll turn and print found red
		while cl.value() == 5 and foundline == False and direction == 1:
			myLock.acquire(True)
			mB.run_forever(speed_sp=100)
			mC.run_forever(speed_sp=0)
			print("found red")
			myLock.release()
			
			#when finding the blue line it'll turn and print found blue
		while cl.value() == 2 and foundline == False and direction == 1:
			myLock.acquire(True)
			mB.run_forever(speed_sp=0)
			mC.run_forever(speed_sp=100)
			print("found blue")
			myLock.release()

			#when finding the black line it'll break and set foundline equal to True
		if cl.value() == 1 and foundline == False:
			count = 0
			for i in range (5):
				if cl.value() == 1:
					count += 1
			if count == 5:
				myLock.acquire(True)
				mB.stop(stop_action="brake")
				mC.stop(stop_action="brake")
				sleep(0.1)
				print("found black")
				myLock.release()	
				foundline = True

			#red == 5     blue == 2
			#this does the same as earlier but with direction switched so it'll turn the other way
		while cl.value() == 5 and foundline == False and direction == -1:
			myLock.acquire(True)
			mB.run_forever(speed_sp=0)
			mC.run_forever(speed_sp=100)
			sleep(0.5)
			myLock.release()
			print("found red")
			
		while cl.value() == 2 and foundline == False and direction == -1:
			myLock.acquire(True)
			mB.run_forever(speed_sp=100)
			mC.run_forever(speed_sp=0)
			sleep(0.5)
			print("found blue")
			
			myLock.release()
		if cl.value() == 1 and foundline == False:
			
			myLock.acquire(True)
			mB.stop(stop_action="brake")
			mC.stop(stop_action="brake")
			sleep(0.1)
			print("found black")
			myLock.release()	
			foundline = True



def funcTurnBlock():
	global potentialShot
	global throwSpeed
	global foundline
	while (True):
		#this will make the robot turn while it has not seen the hoop yet but it has found the line.
		while (potentialShot == False and foundline == True):

			print("in turn block")
			myLock.acquire(True)
			mB.run_forever(speed_sp= 25)
			mC.run_forever(speed_sp= -75) 
			sleep(0.1)
			myLock.release()
			

			right = irright.value()
			left = irleft.value()

			currentPosition_left = left
			currentPosition_right = right
			
			#when the InfraredSensors read an object (the hoop) at distance 80 or less it will go to the potential shoot block
			if (currentPosition_left< 80 and currentPosition_right< 80):
				myLock.acquire(True)
				currentPosition = (left+right)/2

				#the math was found online to shoot the ball. http://www.legoengineering.com/ev3-projectile-launcher/
				a = .030*currentPosition
				#constant that we made up that gave us the most accurate shooting results
				b = 2.718
				power= math.pow(b,a)
				throwSpeed = round(9.0*8.838*power)
				potentialShot = True
				myLock.release()
				sleep(3)	
		sleep(.1)
		


def funcThrowBlock():
	global potentialShot
	global throwSpeed
	global foundline
	global direction
	while(True):
		#this block will throw the ball and then turn around and start searching for lines.
		while (potentialShot == True):
			print("potential shot")
			myLock.acquire(True)
			#sleep(.25)

			mB.stop(stop_action="brake")
			mC.stop(stop_action="brake")
			sleep(2)
			timeValue = time() + .18	
			while (time() < timeValue):
				mD.run_forever(speed_sp=throwSpeed) #Change the speed
			mD.stop(stop_action="brake")
			sleep(1)
			timeValue2 = time() + .18
			while (time() < timeValue2):	
				mD.run_forever(speed_sp=-throwSpeed) #Change the speed
			mD.stop(stop_action="brake")
			potentialShot = False
			foundline = False
			#here we set the direction so it goes the other way.
			direction = direction * -1

			mB.run_forever(speed_sp= -50)
			mC.run_forever(speed_sp= -50)
			sleep(2)
			mB.run_forever(speed_sp= 50)
			mC.run_forever(speed_sp= -50)
			sleep(2)

			myLock.release()
			sleep(1)

		sleep(.1)

threadDrive = threading.Thread(target=funcDrive)
threadTurnBlock = threading.Thread(target=funcTurnBlock)
threadThrowBlock = threading.Thread(target=funcThrowBlock)

# Start running them
threadDrive.start()
threadTurnBlock.start()
threadThrowBlock.start()

# Now wait for them to finish
threadDrive.join()
threadTurnBlock.join()
threadThrowBlock.join()