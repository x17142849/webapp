from grovepi import *



buzzer_pin = 2
ultrasonic_range = 8

pinMode(buzzer_pin,"OUTPUT")
pinMode(ultrasonic_range,"INPUT")



first = True
while True:
	try:
		distance = ultrasonicRead(ultrasonic_range)
	
		if first:
			initial_distance = distance
			first = False
			time.sleep(10)
		if initial_distance - distance > 10:
			digitalWrite(buzzer_pin,1)
		else:
			digitalWrite(buzzer_pin,0)
		
	except KeyboardInterrupt:
		digitalWrite(buzzer_pin,0)
		print("KeyboardInterrupt")
		break
	except (TypeError,IOError) as e:
		print('Error')

