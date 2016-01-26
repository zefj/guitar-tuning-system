#The recipe gives simple implementation of a Discrete Proportional-Integral-Derivative (PID) controller. PID controller gives output value for error between desired reference input and measurement feedback to minimize error value.
#More information: http://en.wikipedia.org/wiki/PID_controller
#
#cnr437@gmail.com
#
#######	Example	#########
#
#p=PID(3.0,0.4,1.2)
#p.setPoint(5.0)
#while True:
#     pid = p.update(measurement_value)
#
#


class PID:
	"""
	Discrete PID control
	"""

	def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min
		self.integral_thresh = 6
		self.min_output = -50
		self.max_output = 50
		
		#self.deadband = 0.3

		self.set_point=0.0
		self.error=0.0

	def update(self,current_value):
		"""
		Calculate PID output value for given reference input and feedback
		"""

		self.error = self.set_point - current_value

		#if abs(self.error) < self.deadband: ## przetestowac czy to dziala
		#	return 0

		self.P_value = self.Kp * self.error


		self.D_value = self.Kd * ( self.error - self.Derivator)
		#self.D_value = (self.Derivator - current_value) * self.Kd

		self.Derivator = self.error
		#self.Derivator = current_value
		
		if abs(self.error) < self.integral_thresh:
			if self.Integrator > 0 and self.Integrator + self.error < self.Integrator:
				self.Integrator = 0	
			elif self.Integrator < 0 and self.Integrator + self.error > self.Integrator:
				self.Integrator = 0
			else:	
				self.Integrator = self.Integrator + self.error
		else:
			self.Integrator = 0

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki
		
		# print "error: %s" % self.error
		# print "P: %s" % self.P_value		
		# print "I: %s" % self.I_value		
		# print "D: %s" % self.D_value

		PID = self.P_value + self.I_value + self.D_value

		if PID > self.max_output:
			PID = self.max_output
		elif PID < self.min_output:
			PID = self.min_output
		#print "PID = %s, error = %s, Integrator = %s, P_value = %s" % (PID, self.error, self.Integrator, self.P_value)
		return PID

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0
