import random
import sys 
import parameters as theparams
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import os
import networkx as nx
import argparse
import csv
from pathlib import Path
import pickle
import parameters
from agent import Agent
from network import Network

class Spread_Model:
	def __init__(self, agents, inf_by_rel, base_filename):

		# get list of agents
		self.agents = agents

		# inf_by_rel is a dictionary of dictionaries with
		# following structure:
		# 	[spouse/household/friendship/workplace][smoking/alcohol/diet/inactivity][0/1/2]
		# if we want to access the amount of influence a friend will exert on an agent
		# to adopt level 2 inactivity, we would access that as such:
		# 	inf_by_rel['friendship']['inactivity'][2]
		# This would return a double between 0 and 1.

		# get list of influence relationships
		self.inf_by_rel = inf_by_rel

		# base filename for output
		self.base_filename = base_filename

		# storing the list of dead agents
		self.deceased = dict()

		self.avg_cvd = list()
		self.behaviour_prevalence = list()
		self.cvd_demographics = list()

		# dictionary to track number of cvd events to enable presentation in the form of Hippisley-Cox et al., 2017
		self.cvd_count = dict()

		self.cvd_count['M'] = {}
		self.cvd_count['F'] = {}

		self.cvd_count['M']['25-29'] = 0
		self.cvd_count['M']['30-34'] = 0
		self.cvd_count['M']['35-39'] = 0
		self.cvd_count['M']['40-44'] = 0
		self.cvd_count['M']['45-49'] = 0
		self.cvd_count['M']['50-54'] = 0
		self.cvd_count['M']['55-59'] = 0
		self.cvd_count['M']['60-64'] = 0
		self.cvd_count['M']['65-69'] = 0
		self.cvd_count['M']['70-74'] = 0
		self.cvd_count['M']['75-79'] = 0
		self.cvd_count['M']['80-84'] = 0

		self.cvd_count['F']['25-29'] = 0
		self.cvd_count['F']['30-34'] = 0
		self.cvd_count['F']['35-39'] = 0
		self.cvd_count['F']['40-44'] = 0
		self.cvd_count['F']['45-49'] = 0
		self.cvd_count['F']['50-54'] = 0
		self.cvd_count['F']['55-59'] = 0
		self.cvd_count['F']['60-64'] = 0
		self.cvd_count['F']['65-69'] = 0
		self.cvd_count['F']['70-74'] = 0
		self.cvd_count['F']['75-79'] = 0
		self.cvd_count['F']['80-84'] = 0

		# dictionary to track number of person years in simulation to enable presentation in the form of Hippisley-Cox et al., 2017
		self.person_years = dict()

		self.person_years['M'] = {}
		self.person_years['F'] = {}

		self.person_years['M']['25-29'] = 0
		self.person_years['M']['30-34'] = 0
		self.person_years['M']['35-39'] = 0
		self.person_years['M']['40-44'] = 0
		self.person_years['M']['45-49'] = 0
		self.person_years['M']['50-54'] = 0
		self.person_years['M']['55-59'] = 0
		self.person_years['M']['60-64'] = 0
		self.person_years['M']['65-69'] = 0
		self.person_years['M']['70-74'] = 0
		self.person_years['M']['75-79'] = 0
		self.person_years['M']['80-84'] = 0

		self.person_years['F']['25-29'] = 0
		self.person_years['F']['30-34'] = 0
		self.person_years['F']['35-39'] = 0
		self.person_years['F']['40-44'] = 0
		self.person_years['F']['45-49'] = 0
		self.person_years['F']['50-54'] = 0
		self.person_years['F']['55-59'] = 0
		self.person_years['F']['60-64'] = 0
		self.person_years['F']['65-69'] = 0
		self.person_years['F']['70-74'] = 0
		self.person_years['F']['75-79'] = 0
		self.person_years['F']['80-84'] = 0

		# dictionary of the Hippisley-Cox et al., 2017 data
		self.score_grid = dict()
		self.score_grid['M'] = {}
		self.score_grid['F'] = {}

		self.score_grid['M']['25-29'] = 4
		self.score_grid['M']['30-34'] = 9.9
		self.score_grid['M']['35-39'] = 21.2
		self.score_grid['M']['40-44'] = 39.9
		self.score_grid['M']['45-49'] = 66.5
		self.score_grid['M']['50-54'] = 98.6
		self.score_grid['M']['55-59'] = 141.8
		self.score_grid['M']['60-64'] = 196.9
		self.score_grid['M']['65-69'] = 265.5
		self.score_grid['M']['70-74'] = 354.8
		self.score_grid['M']['75-79'] = 451.6
		self.score_grid['M']['80-84'] = 582.9

		self.score_grid['F']['25-29'] = 2.4
		self.score_grid['F']['30-34'] = 4.9
		self.score_grid['F']['35-39'] = 10.2
		self.score_grid['F']['40-44'] = 19
		self.score_grid['F']['45-49'] = 32
		self.score_grid['F']['50-54'] = 48.3
		self.score_grid['F']['55-59'] = 74.7
		self.score_grid['F']['60-64'] = 113.6
		self.score_grid['F']['65-69'] = 171.3
		self.score_grid['F']['70-74'] = 250.8
		self.score_grid['F']['75-79'] = 351.1
		self.score_grid['F']['80-84'] = 480.2

	# Method will remove the agent from our simulation
	# we store the agent in a list, for use in analysis
	# we also record some information of the dead agent for later use
	def agent_death(self, agent, t, cvd_metrics):
		self.agents.remove(agent)
		self.deceased[t].append(agent)

		if agent.spouse is not None:
			agent.spouse.spouse = None

		for hm in agent.household:
			hm.household.remove(agent)

		for wm in agent.workplace:
			wm.workplace.remove(agent)

		for f in agent.friends:
			f.friends.remove(agent)

		cvd_metrics[agent.sex] = cvd_metrics[agent.sex] + 1

		imd_level = 'imd' + str(agent.imd)
		cvd_metrics[imd_level] = cvd_metrics[imd_level] + 1

		cvd_metrics['avg_age'] = cvd_metrics['avg_age'] + agent.age

		if agent.age >= 25:
			if agent.age <= 29:
				self.cvd_count[agent.sex]['25-29'] = self.cvd_count[agent.sex]['25-29'] + 1
			elif agent.age <= 34:
				self.cvd_count[agent.sex]['30-34'] = self.cvd_count[agent.sex]['30-34'] + 1
			elif agent.age <= 39:
				self.cvd_count[agent.sex]['35-39'] = self.cvd_count[agent.sex]['35-39'] + 1
			elif agent.age <= 44:
				self.cvd_count[agent.sex]['40-44'] = self.cvd_count[agent.sex]['40-44'] + 1
			elif agent.age <= 49:
				self.cvd_count[agent.sex]['45-49'] = self.cvd_count[agent.sex]['45-49'] + 1
			elif agent.age <= 54:
				self.cvd_count[agent.sex]['50-54'] = self.cvd_count[agent.sex]['50-54'] + 1
			elif agent.age <= 59:
				self.cvd_count[agent.sex]['55-59'] = self.cvd_count[agent.sex]['55-59'] + 1
			elif agent.age <= 64:
				self.cvd_count[agent.sex]['60-64'] = self.cvd_count[agent.sex]['60-64'] + 1
			elif agent.age <= 69:
				self.cvd_count[agent.sex]['65-69'] = self.cvd_count[agent.sex]['65-69'] + 1
			elif agent.age <= 74:
				self.cvd_count[agent.sex]['70-74'] = self.cvd_count[agent.sex]['70-74'] + 1
			elif agent.age <= 79:
				self.cvd_count[agent.sex]['75-79'] = self.cvd_count[agent.sex]['75-79'] + 1
			elif agent.age <= 84:
				self.cvd_count[agent.sex]['80-84'] = self.cvd_count[agent.sex]['80-84'] + 1


	def eval_params(self):
		modelScore = 0
		negScore = 0
		posScore = 0

		for g in self.cvd_count.keys():
			for a in self.cvd_count[g].keys():
				perThousandYear = (self.cvd_count[g][a] / self.person_years[g][a]) * 1000
				diff = perThousandYear - self.score_grid[g][a]
				modelScore = modelScore + abs(diff)
				if diff < 0:
					negScore = negScore + diff
				else:
					posScore = posScore + diff
					

		return [modelScore, negScore, posScore]

	# Method to calculate request metrics between each time step - can be
	# put into plots at the end of the simulation.
	def analytics(self, i):

		# average CVD risk for all currently living agents
		cvd_total = 0

		# tracking prevalence of specific behaviours in each time step
		behaviour_count = {'smoking': [0,0,0], 'inactivity':[0,0,0], 'diet':[0,0,0], 'alcohol': [0,0,0]}

		# track prevalence of each behaviour level
		print("Number of agents: " + str(len(self.agents)))
		for agent in self.agents:
			cvd_total = cvd_total + agent.cv_chance

			behaviour_count['smoking'][agent.smoking_level] = behaviour_count['smoking'][agent.smoking_level] + 1
			behaviour_count['inactivity'][agent.inactivity_level] = behaviour_count['inactivity'][agent.inactivity_level] + 1
			behaviour_count['diet'][agent.diet_level] = behaviour_count['diet'][agent.diet_level] + 1
			behaviour_count['alcohol'][agent.alcohol_level] = behaviour_count['alcohol'][agent.alcohol_level] + 1


		cvd_total = cvd_total / len(self.agents)
		self.avg_cvd.append(cvd_total)

		for i in range(3):
			behaviour_count['smoking'][i] = behaviour_count['smoking'][i] / len(self.agents)
			behaviour_count['inactivity'][i] = behaviour_count['inactivity'][i] / len(self.agents)
			behaviour_count['diet'][i] = behaviour_count['diet'][i] / len(self.agents)
			behaviour_count['alcohol'][i] = behaviour_count['alcohol'][i] / len(self.agents)

		self.behaviour_prevalence.append(behaviour_count)

	# 
	def print_cvd_incidence_rates(self):
		print("x")


	#record and save key metrics on behaviour prevalence for comparion to real world data
	def save_behaviour_metrics(self):

		lvl12_drink_lvl2_housemate = 0
		lvl0_drink_lvl2_housemate = 0
		lvl12_drink_lvl01_housemate = 0
		lvl0_drink_lvl01_housemate = 0

		ex_smoker_hm_quit = 0
		ex_smoker_hm_smokes = 0
		smoker_hm_quit = 0
		smoker_hm_smokes = 0

		lvl12_drink_lvl2_spouse = 0
		lvl0_drink_lvl2_spouse = 0
		lvl12_drink_lvl01_spouse = 0
		lvl0_drink_lvl01_spouse = 0

		ex_smoker_spouse_quit = 0
		ex_smoker_spouse_smokes = 0
		smoker_spouse_quit = 0
		smoker_spouse_smokes = 0

		ex_smoker_friend_quit = 0
		ex_smoker_friend_smokes = 0
		smoker_friend_quit = 0
		smoker_friend_smokes = 0

		active_spouse_exercises = 0
		inactive_spouse_exercises = 0
		active_spouse_inactive = 0
		inactive_spouse_inactive = 0

		active_friend_exercises = 0
		inactive_friend_exercises = 0
		active_friend_inactive = 0
		inactive_friend_inactive = 0
		
		for agent in self.agents:

			hm_lvl2_alc = False
			hm_lvl1_smo = False
			hm_lvl2_smo = False

			for hm in agent.household:
				if hm.alcohol_level == 2:
					hm_lvl2_alc = True 

				if hm.smoking_level == 1:
					hm_lvl1_smo = True
				elif hm.smoking_level == 2:
					hm_lvl2_smo = True

			if hm_lvl2_alc and agent.alcohol_level > 0:
				lvl12_drink_lvl2_housemate = lvl12_drink_lvl2_housemate + 1
			elif hm_lvl2_alc and agent.alcohol_level == 0:
				lvl0_drink_lvl2_housemate = lvl0_drink_lvl2_housemate + 1
			elif not hm_lvl2_alc and agent.alcohol_level > 0:
				lvl12_drink_lvl01_housemate = lvl12_drink_lvl01_housemate + 1
			else:
				lvl0_drink_lvl01_housemate = lvl0_drink_lvl01_housemate + 1

			if hm_lvl1_smo and agent.smoking_level == 1:
				ex_smoker_hm_quit = ex_smoker_hm_quit + 1
			elif hm_lvl1_smo and agent.smoking_level == 2:
				ex_smoker_hm_smokes = ex_smoker_hm_smokes + 1
			elif hm_lvl2_smo and agent.smoking_level == 1:
				smoker_hm_quit = smoker_hm_quit + 1
			elif hm_lvl2_smo and agent.smoking_level == 2:
				smoker_hm_smokes = smoker_hm_smokes + 1

			if agent.spouse is not None:
				if agent.spouse.alcohol_level == 2 and agent.alcohol_level > 0:
					lvl12_drink_lvl2_spouse = lvl12_drink_lvl2_spouse + 1
				elif agent.spouse.alcohol_level == 2 and agent.alcohol_level == 0:
					lvl0_drink_lvl2_spouse = lvl0_drink_lvl2_spouse + 1
				elif agent.spouse.alcohol_level < 2 and agent.alcohol_level > 0:
					lvl12_drink_lvl01_spouse = lvl12_drink_lvl01_spouse + 1
				else:
					lvl0_drink_lvl01_spouse = lvl0_drink_lvl01_spouse + 1

				if agent.spouse.smoking_level == 1 and agent.smoking_level == 1:
					ex_smoker_spouse_quit = ex_smoker_spouse_quit + 1
				elif agent.spouse.smoking_level == 2 and agent.smoking_level == 1:
					ex_smoker_spouse_smokes = ex_smoker_spouse_smokes + 1
				elif agent.spouse.smoking_level == 1 and agent.smoking_level == 2:
					smoker_spouse_quit = smoker_spouse_quit + 1
				elif agent.spouse.smoking_level == 2 and agent.smoking_level == 2:
					smoker_spouse_smokes = smoker_spouse_smokes + 1

				if agent.spouse.inactivity_level < 2 and agent.inactivity_level < 2:
					active_spouse_exercises = active_spouse_exercises + 1
				elif agent.spouse.inactivity_level == 2 and agent.inactivity_level < 2:
					active_spouse_inactive = active_spouse_inactive + 1
				elif agent.spouse.inactivity_level < 2 and agent.inactivity_level == 2:
					inactive_spouse_exercises = inactive_spouse_exercises + 1
				elif agent.spouse.inactivity_level == 2 and agent.inactivity_level == 2:
					inactive_spouse_exercises = inactive_spouse_inactive + 1
			
			friend_lvl1_smo = False
			friend_lvl2_smo = False
			friend_lvl2_act = False

			for f in agent.friends:
				if f.smoking_level == 1:
					friend_lvl1_smo = True
				elif f.smoking_level == 2:
					friend_lvl2_smo = True

				if f.inactivity_level == 2:
					friend_lvl2_act = True

			if friend_lvl1_smo and agent.smoking_level == 1:
				ex_smoker_friend_quit = ex_smoker_friend_quit + 1
			elif friend_lvl1_smo and agent.smoking_level == 2:
				ex_smoker_friend_smokes = ex_smoker_friend_smokes + 1
			elif friend_lvl2_smo and agent.smoking_level == 1:
				smoker_friend_quit = smoker_friend_quit + 1
			elif friend_lvl2_smo and agent.smoking_level == 2:
				smoker_friend_smokes = smoker_friend_smokes + 1

			if not friend_lvl2_act and agent.inactivity_level < 2:
				active_friend_exercises = active_friend_exercises + 1
			elif not friend_lvl2_act and agent.inactivity_level == 2:
				inactive_friend_exercises = inactive_friend_exercises + 1
			elif friend_lvl2_act and agent.inactivity_level < 2:
				active_friend_inactive = active_friend_inactive + 1
			elif friend_lvl2_act and agent.inactivity_level == 2:
				inactive_friend_inactive = inactive_friend_inactive + 1


		housemate_lvl2_drink_rate = lvl12_drink_lvl2_housemate / (lvl12_drink_lvl2_housemate + lvl0_drink_lvl2_housemate)
		housemate_lvl0_drink_rate = lvl12_drink_lvl01_housemate / (lvl12_drink_lvl01_housemate + lvl0_drink_lvl01_housemate)
		housemate_lvl2_abstain_rate = lvl0_drink_lvl2_housemate / (lvl12_drink_lvl2_housemate + lvl0_drink_lvl2_housemate)
		housemate_lvl0_abstain_rate = lvl0_drink_lvl01_housemate / (lvl12_drink_lvl01_housemate + lvl0_drink_lvl01_housemate)

		hm_quit_inf_quit = ex_smoker_hm_quit / (ex_smoker_hm_quit + ex_smoker_hm_smokes)
		hm_smoke_inf_quit = ex_smoker_hm_smokes / (ex_smoker_hm_quit + ex_smoker_hm_smokes)
		hm_quit_inf_smoke = smoker_hm_quit / (smoker_hm_quit + smoker_hm_smokes)
		hm_smoke_inf_smoke = smoker_hm_smokes / (smoker_hm_quit + smoker_hm_smokes)

		spouse_lvl2_drink_rate = lvl12_drink_lvl2_spouse / (lvl12_drink_lvl2_spouse + lvl0_drink_lvl2_spouse)
		spouse_lvl0_drink_rate = lvl12_drink_lvl01_spouse / (lvl12_drink_lvl01_spouse + lvl0_drink_lvl01_spouse)
		spouse_lvl2_abstain_rate = lvl0_drink_lvl2_spouse / (lvl12_drink_lvl2_spouse + lvl0_drink_lvl2_spouse)
		spouse_lvl0_abstain_rate = lvl0_drink_lvl01_spouse / (lvl12_drink_lvl01_spouse + lvl0_drink_lvl01_spouse)

		spouse_quit_inf_quit = ex_smoker_spouse_quit / (ex_smoker_spouse_quit + ex_smoker_spouse_smokes)
		spouse_smoke_inf_quit = ex_smoker_spouse_smokes / (ex_smoker_spouse_quit + ex_smoker_spouse_smokes)
		spouse_quit_inf_smoke = smoker_spouse_quit / (smoker_spouse_quit + smoker_spouse_smokes)
		spouse_smoke_inf_smoke = smoker_spouse_smokes / (smoker_spouse_quit + smoker_spouse_smokes)

		spouse_active_inf_active = active_spouse_exercises / (active_spouse_exercises + active_spouse_inactive)
		spouse_active_inf_inactive = inactive_spouse_exercises / (inactive_spouse_exercises + inactive_spouse_inactive)
		spouse_inactive_inf_active =  active_spouse_inactive / (active_spouse_exercises + active_spouse_inactive)
		spouse_inactive_inf_inactive = inactive_spouse_inactive / (inactive_spouse_exercises + inactive_spouse_inactive)

		friend_quit_inf_quit = ex_smoker_friend_quit / (ex_smoker_friend_quit + ex_smoker_friend_smokes)
		friend_smoke_inf_quit = ex_smoker_friend_smokes / (ex_smoker_friend_quit + ex_smoker_friend_smokes)
		friend_quit_inf_smoke = smoker_friend_quit / (smoker_friend_quit + smoker_friend_smokes)
		friend_smoke_inf_smoke = smoker_friend_smokes / (smoker_friend_quit + smoker_friend_smokes)

		friend_active_inf_active = active_friend_exercises / (active_friend_exercises + active_friend_inactive)
		friend_active_inf_inactive = inactive_friend_exercises / (inactive_friend_exercises + inactive_friend_inactive)
		friend_inactive_inf_active =  active_friend_inactive / (active_friend_exercises + active_friend_inactive)
		friend_inactive_inf_inactive = inactive_friend_inactive / (inactive_friend_exercises + inactive_friend_inactive)

		met_list = list()

		behaviour_metrics_file = "./results/" + self.base_filename + "_behaviour_metrics.txt"
		with open(behaviour_metrics_file, 'w', newline='') as file:
			file.write("Population:" + str(len(self.agents)) + "\n")
			met_list.append(len(self.agents))
			file.write("Average CVD risk:" + str(self.avg_cvd[-1]) + "\n")
			met_list.append(self.avg_cvd[-1])
			file.write("Proportion of lvl 2 smoking:" + str(self.behaviour_prevalence[-1]['smoking'][2]) + "\n")
			met_list.append(self.behaviour_prevalence[-1]['smoking'][2])
			file.write("Proportion of lvl 2 inactivity:" + str(self.behaviour_prevalence[-1]['inactivity'][2]) + "\n")
			met_list.append(self.behaviour_prevalence[-1]['inactivity'][2])
			file.write("Proportion of lvl 2 alcohol:" + str(self.behaviour_prevalence[-1]['alcohol'][2]) + "\n")
			met_list.append(self.behaviour_prevalence[-1]['alcohol'][2])
			file.write("Proportion of lvl 2 diet:" + str(self.behaviour_prevalence[-1]['diet'][2]) + "\n")
			met_list.append(self.behaviour_prevalence[-1]['diet'][2])

			file.write("Proportion of lvl1 or lvl2 alcohol with lvl2 housemates:" + str(housemate_lvl2_drink_rate) + "\n")
			met_list.append(housemate_lvl2_drink_rate)
			file.write("Proportion of lvl1 or lvl2 alcohol with lvl0 or lvl1 housemates:" + str(housemate_lvl0_drink_rate) + "\n")
			met_list.append(housemate_lvl0_drink_rate)
			file.write("Proportion of lvl0 alcohol with lvl2 housemates:" + str(housemate_lvl2_abstain_rate) + "\n")
			met_list.append(housemate_lvl2_abstain_rate)
			file.write("Proportion of lvl0 alcohol with lvl0 or lvl1 housemates:" + str(housemate_lvl0_abstain_rate) + "\n")
			met_list.append(housemate_lvl0_abstain_rate)

			file.write("Proportion of lvl1 or lvl2 alcohol with lvl2 spouse:" + str(spouse_lvl2_drink_rate) + "\n")
			met_list.append(spouse_lvl2_drink_rate)
			file.write("Proportion of lvl1 or lvl2 alcohol with lvl0 or lvl1 spouse:" + str(spouse_lvl0_drink_rate) + "\n")
			met_list.append(spouse_lvl0_drink_rate)
			file.write("Proportion of lvl0 alcohol with lvl2 spouse:" + str(spouse_lvl2_abstain_rate) + "\n")
			met_list.append(spouse_lvl2_abstain_rate)
			file.write("Proportion of lvl0 alcohol with lvl0 or lvl1 spouse:" + str(spouse_lvl0_abstain_rate) + "\n")
			met_list.append(spouse_lvl0_abstain_rate)

			file.write("Proportion of lvl1 smoking with lvl1 housemates:" + str(hm_quit_inf_quit) + "\n")
			met_list.append(hm_quit_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl1 housemates:" + str(hm_quit_inf_smoke) + "\n")
			met_list.append(hm_quit_inf_smoke)
			file.write("Proportion of lvl1 smoking with lvl2 housemates:" + str(hm_smoke_inf_quit) + "\n")
			met_list.append(hm_smoke_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl2 housemates:" + str(hm_smoke_inf_smoke) + "\n")
			met_list.append(hm_smoke_inf_smoke)

			file.write("Proportion of lvl1 smoking with lvl1 spouse:" + str(spouse_quit_inf_quit) + "\n")
			met_list.append(spouse_quit_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl1 spouse:" + str(spouse_quit_inf_smoke) + "\n")
			met_list.append(spouse_quit_inf_smoke)
			file.write("Proportion of lvl1 smoking with lvl2 spouse:" + str(spouse_smoke_inf_quit) + "\n")
			met_list.append(spouse_smoke_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl2 spouse:" + str(spouse_smoke_inf_smoke) + "\n")
			met_list.append(spouse_smoke_inf_smoke)

			file.write("Proportion of lvl1 smoking with lvl1 friend:" + str(friend_quit_inf_quit) + "\n")
			met_list.append(friend_quit_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl1 friend:" + str(friend_quit_inf_smoke) + "\n")
			met_list.append(friend_quit_inf_smoke)
			file.write("Proportion of lvl1 smoking with lvl2 friend:" + str(friend_smoke_inf_quit) + "\n")
			met_list.append(friend_smoke_inf_quit)
			file.write("Proportion of lvl2 smoking with lvl2 friend:" + str(friend_smoke_inf_smoke) + "\n")
			met_list.append(friend_smoke_inf_smoke)

			file.write("Proportion of lvl0 or lv1 activity with lvl0 or lvl1 spouse:" + str(spouse_active_inf_active) + "\n")
			met_list.append(spouse_active_inf_active)
			file.write("Proportion of lvl2 activity with lvl0 or lvl1 spouse:" + str(spouse_active_inf_inactive) + "\n")
			met_list.append(spouse_active_inf_inactive)
			file.write("Proportion of lvl0 or lv1 activity with lvl2 spouse:" + str(spouse_inactive_inf_active) + "\n")
			met_list.append(spouse_inactive_inf_active)
			file.write("Proportion of lvl2 activity with lvl2 spouse:" + str(spouse_inactive_inf_inactive) + "\n")
			met_list.append(spouse_inactive_inf_inactive)

			file.write("Proportion of lvl0 or lv1 activity with lvl0 or lvl1 friend:" + str(friend_active_inf_active) + "\n")
			met_list.append(friend_active_inf_active)
			file.write("Proportion of lvl2 activity with lvl0 or lvl1 friend:" + str(friend_active_inf_inactive) + "\n")
			met_list.append(friend_active_inf_inactive)
			file.write("Proportion of lvl0 or lv1 activity with lvl2 friend:" + str(friend_inactive_inf_active) + "\n")
			met_list.append(friend_inactive_inf_active)
			file.write("Proportion of lvl2 activity with lvl2 friend:" + str(friend_inactive_inf_inactive) + "\n")
			met_list.append(friend_inactive_inf_inactive)

		results_folder = Path("./results/")
		all_runs_file = results_folder / (self.base_filename + "behaviour_metrics_all.pkl")
		if not os.path.isfile(all_runs_file):
			result_list = list()
			result_list.append(met_list)
			with open(all_runs_file, 'wb') as pkl_file:
				pickle.dump(result_list, pkl_file, pickle.HIGHEST_PROTOCOL)
		else:
			with open(all_runs_file, 'rb') as pkl_file:
				result_list = pickle.load(pkl_file)
			result_list.append(met_list)
			with open(all_runs_file, 'wb') as pkl_file:
				pickle.dump(result_list, pkl_file, pickle.HIGHEST_PROTOCOL)


	# output summary of results
	def print_simulation_metrics(self):
		print("At the end of the simulation:")
		print("Population:", len(self.agents))
		print("Average CVD risk:", self.avg_cvd[-1])
		print("Proportion of level 2 smoking:", self.behaviour_prevalence[-1]['smoking'][2])
		print("Proportion of level 2 inactivity:", self.behaviour_prevalence[-1]['inactivity'][2])
		print("Proportion of level 2 alcohol:", self.behaviour_prevalence[-1]['alcohol'][2])
		print("Proportion of level 2 diet:", self.behaviour_prevalence[-1]['diet'][2])

		total = 0
		for d in self.deceased:
			total = total + len(self.deceased[d])

		print("Total deaths:", total)
		print("Death metrics in final year: " + str(self.cvd_demographics[-1]))

		print(self.cvd_count)
		print(self.person_years)

		age_bins = ['25-29', '30-34', '35-39', '40-44', '45-49', '50-54', \
	      '55-59', '60-64', '65-69', '70-74', '75-79', '80-84']
		
		print('Women:')		
		print('age group', '\t', 'incidents', '\t', 'person years', '\t', 'rate per 1000 person years')
		for age in age_bins:
			print(age, '\t\t', self.cvd_count['F'][age], '\t\t', self.person_years['F'][age], '\t\t', "{:.2f}".format((self.cvd_count['F'][age] / (self.person_years['F'][age] / 1000))))
		total_incidents_f = sum(self.cvd_count['F'].values())
		total_person_years_f = sum(self.person_years['F'].values())
		print('total', '\t\t', total_incidents_f, '\t\t', total_person_years_f, '\t\t', "{:.2f}".format((total_incidents_f / (total_person_years_f / 1000))))
		print()

		print('Men:')		
		print('age group', '\t', 'incidents', '\t', 'person years', '\t', 'rate per 1000 person years')
		for age in age_bins:
			print(age, '\t\t', self.cvd_count['M'][age], '\t\t', self.person_years['M'][age], '\t\t', "{:.2f}".format((self.cvd_count['M'][age] / (self.person_years['M'][age] / 1000))))
		total_incidents_m = sum(self.cvd_count['M'].values())
		total_person_years_m = sum(self.person_years['M'].values())
		print('total', '\t\t', total_incidents_m, '\t\t', total_person_years_m, '\t\t', "{:.2f}".format((total_incidents_m / (total_person_years_m / 1000))))
		print()


	# save summary of results
	def save_simulation_metrics(self):
		age_bins = ['25-29', '30-34', '35-39', '40-44', '45-49', '50-54', \
	      '55-59', '60-64', '65-69', '70-74', '75-79', '80-84']
		metrics = ['f_incidents', 'f_years', 'f_rate', 'm_incidents', 'm_years', 'm_rate']

		results_folder = Path("./results/")
		latest_run_file = results_folder / (self.base_filename + "_latest.csv")
		all_runs_file = results_folder / (self.base_filename + "_all.pkl")
		print("Output file (latest run): ", latest_run_file)
		print("Output file (all runs): ", all_runs_file)

		# if the all runs file does not exist, create an empty template file
		if not os.path.isfile(all_runs_file):
			print("Creating output file (all runs): ", all_runs_file)
			results = {}
			for age in age_bins:
				results[age] = {}
				for metric in metrics:
					results[age][metric] = []
			results['total'] = {}
			for metric in metrics:
				results['total'][metric] = []
			with open(all_runs_file, 'wb') as pkl_file:
				pickle.dump(results, pkl_file, pickle.HIGHEST_PROTOCOL)

		# append results to existing run results
		with open(all_runs_file, 'rb') as pkl_file:
			results = pickle.load(pkl_file)
		for age in age_bins:
			results[age]['f_incidents'].append(self.cvd_count['F'][age])
			results[age]['f_years'].append(self.person_years['F'][age])
			# results[age]['f_rate'].append("{:.2f}".format((self.cvd_count['F'][age] / (self.person_years['F'][age] / 1000))))
			results[age]['f_rate'].append((self.cvd_count['F'][age] / (self.person_years['F'][age] / 1000)))
			results[age]['m_incidents'].append(self.cvd_count['M'][age])
			results[age]['m_years'].append(self.person_years['M'][age])
			# results[age]['m_rate'].append("{:.2f}".format((self.cvd_count['M'][age] / (self.person_years['M'][age] / 1000))))
			results[age]['m_rate'].append((self.cvd_count['M'][age] / (self.person_years['M'][age] / 1000)))
		total_incidents_f = sum(self.cvd_count['F'].values())
		total_person_years_f = sum(self.person_years['F'].values())
		total_incidents_m = sum(self.cvd_count['M'].values())	
		total_person_years_m = sum(self.person_years['M'].values())
		results['total']['f_incidents'].append(total_incidents_f)
		results['total']['f_years'].append(total_person_years_f)
		# results['total']['f_rate'].append("{:.2f}".format((total_incidents_f / (total_person_years_f / 1000))))
		results['total']['f_rate'].append((total_incidents_f / (total_person_years_f / 1000)))
		results['total']['m_incidents'].append(total_incidents_m)
		results['total']['m_years'].append(total_person_years_m)
		# results['total']['m_rate'].append("{:.2f}".format((total_incidents_m / (total_person_years_m / 1000))))
		results['total']['m_rate'].append((total_incidents_m / (total_person_years_m / 1000)))
		with open(all_runs_file, 'wb') as pkl_file:
			pickle.dump(results, pkl_file, pickle.HIGHEST_PROTOCOL)

		# save (overwrite) the latest results to file
		with open(latest_run_file, 'w', newline='') as file:
			writer = csv.writer(file)
			fields = ['age group', 'incidents (w)', 'person years (w)', 'rate per 1000 person years (w)',
	     				'incidents (m)', 'person years (m)', 'rate per 1000 person years (m)']
			writer.writerow(fields)
			for age in age_bins:
				writer.writerow([age, self.cvd_count['F'][age], self.person_years['F'][age], (self.cvd_count['F'][age] / (self.person_years['F'][age] / 1000)), 
					self.cvd_count['M'][age], self.person_years['M'][age], (self.cvd_count['M'][age] / (self.person_years['M'][age] / 1000))])		
			total_incidents_f = sum(self.cvd_count['F'].values())
			total_person_years_f = sum(self.person_years['F'].values())
			total_incidents_m = sum(self.cvd_count['M'].values())	
			total_person_years_m = sum(self.person_years['M'].values())			
			writer.writerow(["total", total_incidents_f, total_person_years_f, (total_incidents_f / (total_person_years_f / 1000)),
		    	total_incidents_m, total_person_years_m, (total_incidents_m / (total_person_years_m / 1000))])

	# define the main simulation
	def simulation(self, maxLength):
		for i in range(maxLength):
			print("Beginning timestep : " + str(i))
			print("Current population size: " + str(len(self.agents)))

			for agent in self.agents:

				# set up data structure to store the incoming influence
				inc_inf = dict()
				inc_inf['smoking'] = {0: 0.0, 1: 0.0, 2: 0.0}
				inc_inf['alcohol'] = {0: 0.0, 1: 0.0, 2: 0.0}
				inc_inf['diet'] = {0: 0.0, 1: 0.0, 2: 0.0}
				inc_inf['inactivity'] = {0: 0.0, 1: 0.0, 2: 0.0}

				# check if agent has a spouse and include the
				# spouse's influence upon the agent
				if agent.spouse is not None:

					# determine input for smoking
					inc_inf['smoking'][agent.spouse.smoking_level] = \
					inc_inf['smoking'][agent.spouse.smoking_level] + \
					self.inf_by_rel['Spouse']['Smoking'][agent.spouse.smoking_level]

					# determine input for alcohol
					inc_inf['alcohol'][agent.spouse.alcohol_level] = \
					inc_inf['alcohol'][agent.spouse.alcohol_level] + \
					self.inf_by_rel['Spouse']['Alcohol'][agent.spouse.alcohol_level]

					# determine input for diets
					inc_inf['diet'][agent.spouse.diet_level] = \
					inc_inf['diet'][agent.spouse.diet_level] + \
					self.inf_by_rel['Spouse']['Diet'][agent.spouse.diet_level]

					# determine input for inactivity
					inc_inf['inactivity'][agent.spouse.inactivity_level] = \
					inc_inf['inactivity'][agent.spouse.inactivity_level] + \
					self.inf_by_rel['Spouse']['Inactivity'][agent.spouse.inactivity_level]

				# add household influence to incoming influence for agent
				for hm in agent.household:

					# determine input for smoking
					inc_inf['smoking'][hm.smoking_level] = \
					inc_inf['smoking'][hm.smoking_level] + \
					self.inf_by_rel['Household']['Smoking'][hm.smoking_level]

					# determine input for alcohol
					inc_inf['alcohol'][hm.alcohol_level] = \
					inc_inf['alcohol'][hm.alcohol_level] + \
					self.inf_by_rel['Household']['Alcohol'][hm.alcohol_level]

					# determine input for diets
					inc_inf['diet'][hm.diet_level] = \
					inc_inf['diet'][hm.diet_level] + \
					self.inf_by_rel['Household']['Diet'][hm.diet_level]

					# determine input for inactivity
					inc_inf['inactivity'][hm.inactivity_level] = \
					inc_inf['inactivity'][hm.inactivity_level] + \
					self.inf_by_rel['Household']['Inactivity'][hm.inactivity_level]

				# add household influence to incoming influence for agent
				for wm in agent.workplace:
					# determine input for smoking
					inc_inf['smoking'][wm.smoking_level] = \
					inc_inf['smoking'][wm.smoking_level] + \
					self.inf_by_rel['Workplace'][agent.workplace_type]['Smoking'][wm.smoking_level]

					# determine input for alcohol
					inc_inf['alcohol'][wm.alcohol_level] = \
					inc_inf['alcohol'][wm.alcohol_level] + \
					self.inf_by_rel['Workplace'][agent.workplace_type]['Alcohol'][wm.alcohol_level]

					# determine input for diets
					inc_inf['diet'][wm.diet_level] = \
					inc_inf['diet'][wm.diet_level] + \
					self.inf_by_rel['Workplace'][agent.workplace_type]['Diet'][wm.diet_level]

					# determine input for inactivity
					inc_inf['inactivity'][wm.inactivity_level] = \
					inc_inf['inactivity'][wm.inactivity_level] + \
					self.inf_by_rel['Workplace'][agent.workplace_type]['Inactivity'][wm.inactivity_level]

				# add incoming influence for friends in friendship network
				for friend in agent.friends:

					# determine input for smoking
					inc_inf['smoking'][friend.smoking_level] = \
					inc_inf['smoking'][friend.smoking_level] + \
					self.inf_by_rel['Friendship']['Smoking'][friend.smoking_level]

					# determine input for alcohol
					inc_inf['alcohol'][friend.alcohol_level] = \
					inc_inf['alcohol'][friend.alcohol_level] + \
					self.inf_by_rel['Friendship']['Alcohol'][friend.alcohol_level]

					# determine input for diets
					inc_inf['diet'][friend.diet_level] = \
					inc_inf['diet'][friend.diet_level] + \
					self.inf_by_rel['Friendship']['Diet'][friend.diet_level]

					# determine input for inactivity
					inc_inf['inactivity'][friend.inactivity_level] = \
					inc_inf['inactivity'][friend.inactivity_level] + \
					self.inf_by_rel['Friendship']['Inactivity'][friend.inactivity_level]
					
				# Calculate the new level for the agent based on the calculated incoming influence.
				# These new levels are stored in temporary variables.
				# We need to shift the levels of all agents at the same time, so save the temporary
				# values for now and swap them over later. 
				agent.next_smoking_level(inc_inf['smoking'])
				agent.next_alcohol_level(inc_inf['alcohol'])
				agent.next_diet_level(inc_inf['diet'])
				agent.next_inactivity_level(inc_inf['inactivity'])

			cvd_metrics = {'M': 0, 'F': 0, 'imd1': 0, 'imd2': 0, 'imd3': 0, 'imd4': 0, 'imd5': 0, 'avg_age': 0}
			# update agent risk levels and CVD risk.
			# Then, test for a CVD event and remove the agent in the event they have
			# suffered a CVD event.

			self.deceased[i] = list()
			for agent in self.agents:
				# update tracking of person years for calculating final results
				if agent.age >= 25:
					if agent.age <= 29:
						self.person_years[agent.sex]['25-29'] = self.person_years[agent.sex]['25-29'] + 1
					elif agent.age <= 34:
						self.person_years[agent.sex]['30-34'] = self.person_years[agent.sex]['30-34'] + 1
					elif agent.age <= 39:
						self.person_years[agent.sex]['35-39'] = self.person_years[agent.sex]['35-39'] + 1
					elif agent.age <= 44:
						self.person_years[agent.sex]['40-44'] = self.person_years[agent.sex]['40-44'] + 1
					elif agent.age <= 49:
						self.person_years[agent.sex]['45-49'] = self.person_years[agent.sex]['45-49'] + 1
					elif agent.age <= 54:
						self.person_years[agent.sex]['50-54'] = self.person_years[agent.sex]['50-54'] + 1
					elif agent.age <= 59:
						self.person_years[agent.sex]['55-59'] = self.person_years[agent.sex]['55-59'] + 1
					elif agent.age <= 64:
						self.person_years[agent.sex]['60-64'] = self.person_years[agent.sex]['60-64'] + 1
					elif agent.age <= 69:
						self.person_years[agent.sex]['65-69'] = self.person_years[agent.sex]['65-69'] + 1
					elif agent.age <= 74:
						self.person_years[agent.sex]['70-74'] = self.person_years[agent.sex]['70-74'] + 1
					elif agent.age <= 79:
						self.person_years[agent.sex]['75-79'] = self.person_years[agent.sex]['75-79'] + 1
					elif agent.age <= 84:
						self.person_years[agent.sex]['80-84'] = self.person_years[agent.sex]['80-84'] + 1

				# update cvd risk, check for cvd events, and increment age
				agent.update_risk_levels()

				if agent.test_for_cv():
					self.agent_death(agent, i, cvd_metrics)
				else:
					agent.age_up()

			cvd_metrics['avg_age'] = cvd_metrics['avg_age'] / len(self.deceased[i])
			cvd_metrics['total'] = len(self.deceased[i])
			self.cvd_demographics.append(cvd_metrics)

			print("Timestep " + str(i) + " finished. Calculating analytics.")
			self.analytics(i)
		print("Finished running simulation.")


def default_rels():
	inf_by_rel = dict()
	rKey = ['Spouse', 'Friendship', 'Household', 'Workplace']
	bKey = ['Inactivity', 'Diet', 'Smoking', 'Alcohol']

	for r in rKey:
		inf_by_rel[r] = dict()

		for b in bKey:
			inf_by_rel[r][b] = {0:0.1, 1:0.1, 2:0.1}

	return inf_by_rel


def main():
	parser = argparse.ArgumentParser(description="spread - create a network and run spread for CVD simulation.")
	# main simulation parameters
	parser.add_argument(dest='parameter_folder',
		help='folder of csv files with parameter specifications')

	parser.add_argument('-n', '--size', action='store',
		default=3500, type=int, help='target population size')

	parser.add_argument('-t', '--timestep', action='store', \
		default=10, type=int, help='select number of timesteps for simulation')
	
	parser.add_argument('-e', '--exp_id', default='None',
		     help='experiment ID for output file prefix')

	parser.add_argument('--metrics', dest='mets', action='store_true', help='store behaviour prevalence metrics')

	# parser.add_argument('--plots', dest='plots',
	# 	action='store_true', help='generate basic plots')
	# parser.set_defaults(plots=False)
	
	args = parser.parse_args()
	print("Using parameters from folder:", args.parameter_folder)
	target_size = args.size
	print("Target population size: ", target_size)
	exp_id = args.exp_id
	print("Experiment ID: ", exp_id)
	param = parameters.Parameters(args.parameter_folder)
	config_name = os.path.basename(os.path.normpath(args.parameter_folder))

	stats_base_filename = "n-" + str(args.size) + "_t-" + str(args.timestep) + "_config-" + config_name
	if exp_id != 'None':
		stats_base_filename = "expID-" + exp_id + "_" + stats_base_filename
	print("Statistics base filename: ", stats_base_filename)


	n = Network(param)

	agent_list = n.generate_agents(target_size)

	#makes an array of relationships with all values of 0.1
	inf_by_rel = param.get_inf_by_rel()

	# spreader = Spread_Model(agent_list, inf_by_rel, graph)
	spreader = Spread_Model(agent_list, inf_by_rel, stats_base_filename)

	print("Beginning simulation.")

	spreader.analytics(-1)
	spreader.cvd_demographics.append({'M': 0, 'F': 0, 'imd1': 0, 'imd2': 0, 'imd3': 0, 'imd4': 0, 'imd5': 0, 'avg_age': 0, 'total': 0})
	spreader.simulation(args.timestep)
	spreader.print_simulation_metrics()
	spreader.save_simulation_metrics()
	if args.mets:
		spreader.save_behaviour_metrics()


if __name__ == "__main__":
    main()

















			
			
			




		
