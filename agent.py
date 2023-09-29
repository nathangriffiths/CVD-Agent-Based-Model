import random
import math

class Agent:
	id_counter = 0

	def __init__(self, sex, age, risk_factors, initial_levels):

		#unique ID for agent
		self.id = type(self).id_counter
		type(self).id_counter += 1

		# initialising spouse as 'None' for single
		# NB the spouse relationship dominates other forms, and so a spouse not included in household etc. 
		self.spouse = None

		# lists of Agents for connections
		# NB an agent appears in at most one of these lists, based on the importance of the relationship, 
		# such that household > friends > workplace
		self.household = []
		self.friends = []

		# workplace is a list of (influential) work colleagues
		# initialise to empty
		self.assign_to_workplace = None
		self.workplace = []
		self.workplace_type = None

		# setting initial values for key attributes
		self.age = age
		self.sex = sex
		self.imd = None

		# setting risk values for each contributing factor
		self.smoking_level = initial_levels['smoking']
		self.inactivity_level = initial_levels['inactivity']
		self.alcohol_level = initial_levels['alcohol']
		self.diet_level = initial_levels['diet']

		# these are temporary stores for updated values
		self.smoking_level_temp = 0
		self.inactivity_level_temp = 0
		self.alcohol_level_temp = 0
		self.diet_level_temp = 0

		# setting chance of cardio-vascular incident
		self.cv_chance = 0

		# agent threshold currently uses a gaussian distribution with a mean of 1.0 and std of 0.05.
		# this is based on previous experience but can be adjusted / tuned empirically
		self.threshold = random.gauss(0.8, 0.05)

		# set the risk factors
		self.risk_factors = risk_factors


	# define string representation of main agent features (messy, but useful for debugging)
	def __str__(self):
		spouse_string = "["
		if self.spouse != None:
			spouse_string = spouse_string + str(self.spouse.id)
		spouse_string = spouse_string + "]"

		house_string = "["
		for i in self.household:
			house_string = house_string + str(i.id) + ","
		house_string = house_string + "]"

		friend_string = "["
		for i in self.friends:
			friend_string = friend_string + str(i.id) + ","
		friend_string = friend_string + "]"

		if self.workplace == None:
			work_string = 'None'
		else:
			work_string = "["
			for i in self.workplace:
				work_string = work_string + str(i.id) + ","
			work_string = work_string + "]"

		return str(self.id) + ":" + str(self.age) + self.sex + ":" + "q" + str(self.imd) + ":" + "S" + spouse_string + ":" + "H" + house_string + ":" + "F" + friend_string + ":" + "W" + work_string


	# increment age
	def age_up(self):
		self.age = self.age + 1


	# set threshold using a Gaussian distribution (can be tuned empirically) 
	def set_threshold(self):
		self.threshold = random.gauss(1, 0.05)


	# Calculate the base CVD chance for a female, based on age, bmi, cholesterol and blood pressure.
	# code adapted from algorithm provided by the QRISK3 team: https://www.qrisk.org
	# see paper: Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: prospective cohort study, BMJ 2017;357:j2099
	def base_cvd_female(self, bmi = 26.8, rati = 3.5, sbp = 123, sbps5 = 5):
		age = self.age
		dage = age/10.0
		age_1 = math.pow(dage,-2)
		age_2 = dage
		dbmi = bmi/10.0
		bmi_1 = math.pow(dbmi,-2)
		bmi_2 = math.pow(dbmi,-2) * math.log(dbmi)

		# Centring the continuous variables
		age_1 = age_1 - 0.053274843841791
		age_2 = age_2 - 4.332503318786621
		bmi_1 = bmi_1 - 0.154946178197861
		bmi_2 = bmi_2 - 0.144462317228317
		rati = rati - 3.476326465606690
		sbp = sbp - 123.130012512207030
		sbps5 = sbps5 - 9.002537727355957

		# Start of Sum
		a = 0

		# Sum from continuous values
		a += age_1 * -8.1388109247726188000000000
		a += age_2 * 0.7973337668969909800000000
		a += bmi_1 * 0.2923609227546005200000000
		a += bmi_2 * -4.1513300213837665000000000
		a += rati * 0.1533803582080255400000000
		a += sbp * 0.0131314884071034240000000
		a += sbps5 * 0.0078894541014586095000000

		# Sum from interaction terms
		a += age_1 * bmi_1 * 23.8026234121417420000000000
		a += age_1 * bmi_2 * -71.1849476920870070000000000
		a += age_1 * sbp * 0.0341318423386154850000000
		a += age_2 * bmi_1 * 0.5236995893366442900000000
		a += age_2 * bmi_2 * 0.0457441901223237590000000
		a += age_2 * sbp * -0.0015082501423272358000000

		# Calculate the score itself
		score = 100.0 * (1 - math.pow(0.988876402378082, math.exp(a)))
		self.cv_chance = score / 100.0


	# Calculate the base CVD chance for a male, based on age, bmi, cholesterol and blood pressure.
	# code adapted from algorithm provided by the QRISK3 team: https://www.qrisk.org
	# see paper: Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: prospective cohort study, BMJ 2017;357:j2099
	def base_cvd_male(self, bmi = 27.7, rati = 4.1, sbp = 130, sbps5 = 7):
		age = self.age
		dage=age/10.0
		age_1 = math.pow(dage,-1)
		age_2 = math.pow(dage,3)
		dbmi=bmi/10.0
		bmi_2 = math.pow(dbmi,-2)*math.log(dbmi)
		bmi_1 = math.pow(dbmi,-2)

		# Centring the continuous variables
		age_1 = age_1 - 0.234766781330109
		age_2 = age_2 - 77.284080505371094
		bmi_1 = bmi_1 - 0.149176135659218
		bmi_2 = bmi_2 - 0.141913309693336
		rati = rati - 4.300998687744141
		sbp = sbp - 128.571578979492190
		sbps5 = sbps5 - 8.756621360778809

		# Start of Sum
		a=0

		# Sum from continuous values
		a += age_1 * -17.8397816660055750000000000;
		a += age_2 * 0.0022964880605765492000000;
		a += bmi_1 * 2.4562776660536358000000000;
		a += bmi_2 * -8.3011122314711354000000000;
		a += rati * 0.1734019685632711100000000;
		a += sbp * 0.0129101265425533050000000;
		a += sbps5 * 0.0102519142912904560000000;

		# Sum from interaction terms
		a += age_1 * bmi_1 * 31.0049529560338860000000000
		a += age_1 * bmi_2 * -111.2915718439164300000000000
		a += age_1 * sbp * 0.0188585244698658530000000
		a += age_2 * bmi_1 * 0.0050380102356322029000000;
		a += age_2 * bmi_2 * -0.0130744830025243190000000;
		a += age_2 * sbp * -0.0000127187419158845700000;

		# Calculate the score itself
		score = 100.0 * (1 - math.pow(0.977268040180206, math.exp(a)))
		self.cv_chance = score / 100.0


	# Should be done after the update_risk_level method is called
	def test_for_cv(self):
		# First, we calculate the base chance based on sex of the agent
		if self.sex == 'M':
			self.base_cvd_male()
		else:
			self.base_cvd_female()

		# We test for age string each time, because agents can increase their age and may
		# end up in a different bracket
		if self.age < 35:
			age_str = '18-34'
		elif self.age < 65:
			age_str = '35-64'
		else:
			age_str = '65+'

		# Account for additional factors
		self.cv_chance = self.cv_chance * self.risk_factors[age_str]['Alcohol'][self.alcohol_level]
		self.cv_chance = self.cv_chance	* self.risk_factors[age_str]['Smoking'][self.smoking_level]
		self.cv_chance = self.cv_chance * self.risk_factors[age_str]['Inactivity'][self.inactivity_level]
		self.cv_chance = self.cv_chance * self.risk_factors[age_str]['Diet'][self.diet_level]

		# We have calculated the chance over ten years, so assume a uniform chance each year.
		# This means we need to divide our currently calculated chance by 10
		if self.cv_chance / 10.0 > random.random():
			return True
		
		return False


	# Calculating the smoking level for the next timestep in the simulation
	def next_smoking_level(self, inc_inf):
		# Agents can never be level 0 once going to level 1 or 2
		# However, they may have incoming influence for level 0
		# This influence, if the agent is at level 1 or 2, will be
		# added to contribute to level 1 influence. 
		if self.smoking_level != 0:
			inc_inf[1] = inc_inf[1] + inc_inf[0]
			inc_inf.pop(0, None)

		lvls_over_thresh = list()
		total = 0

		#G o through each level and see which influences exceed the threshold
		for i in inc_inf.keys():
			if inc_inf[i] >= self.threshold:
				lvls_over_thresh.append(i)
				total = total + inc_inf[i]

		# assign next time step level based on incoming influences
		# no levels of behaviour exceeding our influence threshold means
		# we maintain the current level
		if len(lvls_over_thresh) == 0:
			self.smoking_level_temp = self.smoking_level
		# other wise if we only have one level exceeding the threshold, we use that
		elif len(lvls_over_thresh) == 1:
			self.smoking_level_temp = lvls_over_thresh[0]
		# otherwise we pick one of the levels that exceed the threshold
		# using a weighted probability
		else:
			rangeCap = 0
			choice = random.random()
			for k in lvls_over_thresh:
				rangeCap = rangeCap + (inc_inf[k] / total)
				if choice < rangeCap:
					self.smoking_level_temp = k
					break


	# calculate the level of inactivity for the agent
	# in the next timestep
	def next_inactivity_level(self, inc_inf):
		lvls_over_thresh = list()
		total = 0
		for i in inc_inf.keys():
			if inc_inf[i] >= self.threshold:
				lvls_over_thresh.append(i)
				total = total + inc_inf[i]

		if len(lvls_over_thresh) == 0:
			self.inactivity_level_temp = self.inactivity_level
		elif len(lvls_over_thresh) == 1:
			self.inactivity_level_temp = lvls_over_thresh[0]
		else:
			rangeCap = 0
			choice = random.random()
			for k in lvls_over_thresh:
				rangeCap = rangeCap + (inc_inf[k] / total)
				if choice < rangeCap:
					self.inactivity_level_temp = k
					break


	# calculate the level of alcohol for the agent
	# in the next timestep
	def next_alcohol_level(self, inc_inf):
		lvls_over_thresh = list()
		total = 0

		for i in inc_inf.keys():
			if inc_inf[i] >= self.threshold:
				lvls_over_thresh.append(i)
				total = total + inc_inf[i]

		if len(lvls_over_thresh) == 0:
			self.alcohol_level_temp = self.alcohol_level
		elif len(lvls_over_thresh) == 1:
			self.alcohol_level_temp = lvls_over_thresh[0]
		else:
			rangeCap = 0
			choice = random.random()
			for k in lvls_over_thresh:
				rangeCap = rangeCap + (inc_inf[k] / total)
				if choice < rangeCap:
					self.alcohol_level_temp = k
					break


	# calculate the level of diet for the agent
	# in the next timestep
	def next_diet_level(self, inc_inf):
		lvls_over_thresh = list()
		total = 0

		for i in inc_inf.keys():
			if inc_inf[i] >= self.threshold:
				lvls_over_thresh.append(i)
				total = total + inc_inf[i]

		if len(lvls_over_thresh) == 0:
			self.diet_level_temp = self.diet_level
		elif len(lvls_over_thresh) == 1:
			self.diet_level_temp = lvls_over_thresh[0]
		else:
			rangeCap = 0
			choice = random.random()
			for k in lvls_over_thresh:
				rangeCap = rangeCap + (inc_inf[k] / total)
				if choice < rangeCap:
					self.diet_level_temp = k
					break


	# Separating out the update of levels so that all agents
	# can be updated at the same time without impacting the
	# process of new level calculation
	# This process should also adjust the CVD risk for the agent
	def update_risk_levels(self):
		self.smoking_level = self.smoking_level_temp
		self.inactivity_level = self.inactivity_level_temp
		self.alcohol_level = self.alcohol_level_temp
		self.diet_level = self.diet_level_temp

		




	
