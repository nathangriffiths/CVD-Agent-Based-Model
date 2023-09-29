import random
import math
import numpy as np
import csv
import os

class Parameters:
    def __init__(self, parameter_folder) -> None:
        # relative location of parameter files
        self.parameter_folder = parameter_folder

        # filenames
        sex_file = os.path.join(os.path.curdir, self.parameter_folder, 'sex.csv')
        age_file = os.path.join(os.path.curdir, self.parameter_folder, 'age_distribution.csv')
        married_file = os.path.join(os.path.curdir, self.parameter_folder, 'married.csv')
        same_sex_marriage_file = os.path.join(os.path.curdir, self.parameter_folder, 'same_sex_marriage.csv')
        male_spouse_age_file = os.path.join(os.path.curdir, self.parameter_folder, 'male_spouse_age.csv')
        female_spouse_age_file = os.path.join(os.path.curdir, self.parameter_folder, 'female_spouse_age.csv')
        quintiles_file = os.path.join(os.path.curdir, self.parameter_folder, 'quintiles.csv')
        employed_file = os.path.join(os.path.curdir, self.parameter_folder, 'employed.csv')
        household_file = os.path.join(os.path.curdir, self.parameter_folder, 'household_size.csv')
        workplaces_file = os.path.join(os.path.curdir, self.parameter_folder, 'workplace_size.csv')
        workplace_contacts_file = os.path.join(os.path.curdir, self.parameter_folder, 'workplace_contacts.csv')
        workplace_type_distribution_file = os.path.join(os.path.curdir, self.parameter_folder, 'workplace_type_distribution.csv')
        behaviour_cvd_risk_file = os.path.join(os.path.curdir, self.parameter_folder, 'behaviour_cvd_risk.csv')
        behaviour_prevalence_file = os.path.join(os.path.curdir, self.parameter_folder, 'behaviour_cvd_prevalence.csv')
        relationship_inf_file = os.path.join(os.path.curdir, self.parameter_folder, 'relationship_influence.csv')
        workplace_types_file = os.path.join(os.path.curdir, self.parameter_folder, 'workplace_types.csv')
        # tolerance for error checking probabilities
        tol=1e-05

        # probability that an individual is male
        with open(sex_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] == 'Male':
                    self.p_male = float(row['Probability'])

        # create dictionaries mapping for age probabilities for male and female
        self.p_male_age = {}
        self.p_female_age = {}
        self.ages = []
        with open(age_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            self.min_age = int(csv_reader.fieldnames[1])
            self.max_age = int(csv_reader.fieldnames[-1])
            for a in csv_reader.fieldnames[1:]:
                self.ages.append(a)
            for row in csv_reader:
                if row['Sex'] == 'Male':
                    for i in range(self.min_age, self.max_age + 1):
                        self.p_male_age[i] = float(row[str(i)])
                elif row['Sex'] == 'Female':
                    for i in range(self.min_age, self.max_age + 1):
                        self.p_female_age[i] = float(row[str(i)])
                else:
                    print("Error reading in age distribution: unknown sex")
            # check probabilities sum to 1
            if not math.isclose(sum(self.p_male_age.values()), 1, rel_tol=tol):
                print("Error: probabilities for Male ages do not sum to 1. Parameter file:", age_file)
                exit(1)
            if not math.isclose(sum(self.p_female_age.values()), 1, rel_tol=tol):
                print("Error: probabilities for Female ages do not sum to 1. Parameter file:", age_file)
                exit(1)

        # create dictionary for spouse ages for male agents
        self.p_male_spouse_age = {}
        with open(male_spouse_age_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            if csv_reader.fieldnames[1] != str(self.min_age):
                print("Error: minimum spouse age should equal the minimum in age distribution. Parameter file:", male_spouse_age_file)
                exit(1)
            if csv_reader.fieldnames[-1] != str(self.max_age):
                print("Error: maximum spouse age should equal the maximum in age distribution. Parameter file:", male_spouse_age_file)
                exit(1)
            for row in csv_reader:
                self.p_male_spouse_age[int(row['Male_Age'])] = {}
                for i in self.ages:
                    value = 0.0 if row[i] == '' else float(row[i])
                    self.p_male_spouse_age[int(row['Male_Age'])][i] = value
        for i in self.p_male_spouse_age.keys():
            if not math.isclose(sum(self.p_male_spouse_age[i].values()), 1, rel_tol=tol):
                print("Error: probabilities for spouse age do not sum to 1. Parameter file:", male_spouse_age_file)
                print("Row", i)
                exit(1)

        # create dictionary for spouse ages for female agents
        self.p_female_spouse_age = {}
        with open(female_spouse_age_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            if csv_reader.fieldnames[1] != str(self.min_age):
                print("Error: minimum spouse age should equal the minimum in age distribution. Parameter file:", female_spouse_age_file)
                exit(1)
            if csv_reader.fieldnames[-1] != str(self.max_age):
                print("Error: maximum spouse age should equal the maximum in age distribution. Parameter file:", female_spouse_age_file)
                exit(1)
            for row in csv_reader:
                self.p_female_spouse_age[int(row['Female_Age'])] = {}
                for i in self.ages:
                    value = 0.0 if row[i] == '' else float(row[i])
                    self.p_female_spouse_age[int(row['Female_Age'])][i] = value
        for i in self.p_female_spouse_age.keys():
            if not math.isclose(sum(self.p_female_spouse_age[i].values()), 1, rel_tol=tol):
                print("Error: probabilities for spouse age do not sum to 1. Parameter file:", female_spouse_age_file)
                print("Row", i)
                exit(1)

        # probability that an individual is married, indexed by age and sex
        self.p_married = dict.fromkeys(['M', 'F'])
        self.p_married['M'] = dict.fromkeys(self.ages)
        self.p_married['F'] = dict.fromkeys(self.ages)
        with open(married_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] == 'Male':
                    self.p_married['M'][row['Age']] = float(row['Probability'])
                elif row['Sex'] == 'Female':
                    self.p_married['F'][row['Age']] = float(row['Probability'])

        # probability that a couple is same-sex
        with open(same_sex_marriage_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Same sex'] == 'TRUE':
                    self.p_same_sex = float(row['Probability'])

        # create dictionaries mapping sex and age to quintile probabilities
        self.p_male_quintile = {}
        self.p_female_quintile = {}
        with open(quintiles_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] == 'Male':
                    self.p_male_quintile[row['Age']] = {"IMD-1" : row['IMD-1'], "IMD-2" : row['IMD-2'], "IMD-3" : row['IMD-3'], \
                        "IMD-4" : row['IMD-4'], "IMD-5" : row['IMD-5']}
                elif row['Sex'] == 'Female':
                    self.p_female_quintile[row['Age']] = {"IMD-1" : row['IMD-1'], "IMD-2" : row['IMD-2'], "IMD-3" : row['IMD-3'], \
                        "IMD-4" : row['IMD-4'], "IMD-5" : row['IMD-5']}
            if list(self.p_male_quintile.keys()) != self.ages:
                print("Error: males ages in quintiles csv do not match age distribution. Parameter files:", \
                    age_file, quintiles_file)
                exit(1)
            for age in self.p_male_quintile.keys():
                if not math.isclose(float(self.p_male_quintile[age]['IMD-1']) + float(self.p_male_quintile[age]['IMD-2']) \
                    + float(self.p_male_quintile[age]['IMD-3']) + float(self.p_male_quintile[age]['IMD-4'])
                    + float(self.p_male_quintile[age]['IMD-5']), 1, rel_tol=tol):
                    print("Error: quintile probabilities for male age", age, "do not sum to 1. Parameter file:", \
                        quintiles_file)
                    exit(1)
            if list(self.p_female_quintile.keys()) != self.ages:
                print("Error: females ages in quintiles csv do not match age distribution. Parameter files:", \
                    age_file, quintiles_file)
                exit(1)
            for age in self.p_female_quintile.keys():
                if not math.isclose(float(self.p_female_quintile[age]['IMD-1']) + float(self.p_female_quintile[age]['IMD-2']) \
                    + float(self.p_female_quintile[age]['IMD-3']) + float(self.p_female_quintile[age]['IMD-4'])
                    + float(self.p_female_quintile[age]['IMD-5']), 1, rel_tol=tol):
                    print("Error: quintile probabilities for female age", age, "do not sum to 1. Parameter file:", \
                        quintiles_file)
                    exit(1)

        # create dictionaries mapping sex, IMD and age to employment probability
        self.p_male_employed = {}
        self.p_female_employed = {}
        with open(employed_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] == 'Male':
                    self.p_male_employed[row['IMD']] = {}
                    for i in csv_reader.fieldnames[2:]:
                        self.p_male_employed[row['IMD']][i] = row[i]
                if row['Sex'] == 'Female':
                    self.p_female_employed[row['IMD']] = {}
                    for i in csv_reader.fieldnames[2:]:
                        self.p_female_employed[row['IMD']][i] = row[i]

            if csv_reader.fieldnames[2:] != self.ages:
                print("Error: ages in IMD csv does not match agent distribution. Parameter files:", \
                    age_file, employed_file)
                exit(1)
            if list(self.p_male_employed.keys()) != ['IMD-1', 'IMD-2', 'IMD-3', 'IMD-4', 'IMD-5']:
                print("Error: male IMD indices out of expected range ('IMD-1', 'IMD-2', 'IMD-3', 'IMD-4', 'IMD-5'). Parameter file:", \
                    employed_file)
                exit(1)
            if list(self.p_female_employed.keys()) != ['IMD-1', 'IMD-2', 'IMD-3', 'IMD-4', 'IMD-5']:
                print("Error: female IMD indices out of expected range ('IMD-1', 'IMD-2', 'IMD-3', 'IMD-4', 'IMD-5'). Parameter file:", \
                    employed_file)
                exit(1)

        # create dictionaries mapping sex, IMD and age to employment probability
        self.p_household_married = {}
        self.p_household_unmarried = {}
        with open(household_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Married'] == 'Yes':
                    self.p_household_married[row['Age']] = {}
                    for i in csv_reader.fieldnames[2:]:
                        self.p_household_married[row['Age']][i] = row[i]
                if row['Married'] == 'No':
                    self.p_household_unmarried[row['Age']] = {}
                    for i in csv_reader.fieldnames[2:]:
                        self.p_household_unmarried[row['Age']][i] = row[i]
            if list(self.p_household_married.keys()) != self.ages:
                print("Error: married age IMD indices out of expected range (should match age_distribution.csv). Parameter file:", \
                    household_file)
                exit(1)
            if list(self.p_household_unmarried.keys()) != self.ages:
                print("Error: unmarried age IMD indices out of expected range (should match age_distribution.csv). Parameter file:", \
                    household_file)
                exit(1)
            for age in self.ages:
                if float(self.p_household_married[age][str(1)]) != 0.0:
                    print("Error: married household size cannot be <2. Parameter file:", household_file)
                    exit(1)
                if not math.isclose(sum(float(a) for a in self.p_household_married[age].values()), 1, rel_tol=tol):
                    print("Error: married household size probabilities do not sum to 1. Parameter file, age:", household_file, age)
                    exit(1)
                if not math.isclose(sum(float(a) for a in self.p_household_unmarried[age].values()), 1, rel_tol=tol):
                    print("Error: unmarried household size probabilities do not sum to 1. Parameter file, age:", household_file, age)
                    exit(1)

        # create dictionary of workplace size probabilities
        self.p_workplace_size = {}
        with open(workplaces_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.p_workplace_size[row['Size']] = row['Probability']
            if list(self.p_workplace_size.keys()) != ['<10', '<50', '<250', '250+']:
                print("Error: workplaces sizes do not match expected categories ('<10', '<50', '<250', '250+'). Parameter file:", \
                    workplaces_file)
                exit(1)
            if not math.isclose(math.fsum([float(i) for i in self.p_workplace_size.values()]), 1, rel_tol=tol):
                print("Error: workplaces probabilities do not sum to 1. Parameter file:", \
                    workplaces_file)
                exit(1)

        # create dictionary of workplace size probabilities
        self.p_workplace_contacts_size = {}
        with open(workplace_contacts_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.p_workplace_contacts_size[row['Size']] = row['Contacts']
            if list(self.p_workplace_contacts_size.keys()) != ['<10', '<50', '<250', '250+']:
                print(self.p_workplace_contacts_size.keys())
                print("Error: x workplaces sizes do not match expected categories ('<10', '<50', '<250', '250+'). Parameter file:", \
                    workplace_contacts_file)
                exit(1)
        self.p_workplace_contacts_size_spread = np.std([int(x) for x in list(self.p_workplace_contacts_size.values())])

        # create dictionary of how behaviours modify the risk of CVD
        self.behaviour_cvd_risk = {}
        with open(behaviour_cvd_risk_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] not in self.behaviour_cvd_risk.keys():
                    self.behaviour_cvd_risk[row['Sex']] = {}
                if row['Age'] not in self.behaviour_cvd_risk[row['Sex']].keys():
                    self.behaviour_cvd_risk[row['Sex']][row['Age']] = {}
                if row['Behaviour'] not in self.behaviour_cvd_risk[row['Sex']][row['Age']].keys():
                    self.behaviour_cvd_risk[row['Sex']][row['Age']][row['Behaviour']] = {}
                
                self.behaviour_cvd_risk[row['Sex']][row['Age']][row['Behaviour']][int(row['Level'])] = float(row['CVD_Risk'])

        # create dictionary of initial prevalence of the risk factor levels
        self.behaviour_prevalence = {}
        with open(behaviour_prevalence_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Sex'] not in self.behaviour_prevalence.keys():
                    self.behaviour_prevalence[row['Sex']] = {}
                if row['Age'] not in self.behaviour_prevalence[row['Sex']].keys():
                    self.behaviour_prevalence[row['Sex']][row['Age']] = {}
                if row['Behaviour'] not in self.behaviour_prevalence[row['Sex']][row['Age']].keys():
                    self.behaviour_prevalence[row['Sex']][row['Age']][row['Behaviour']] = {}
                
                self.behaviour_prevalence[row['Sex']][row['Age']][row['Behaviour']][int(row['Level'])] = float(row['Prevalence'])

        # create dictionary of the influence exerted on each behaviour and risk level by each relationship
        self.inf_by_rel = {}
        with open(relationship_inf_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                self.inf_by_rel[row['Relationship']] = {}

                for header in csv_reader.fieldnames:
                    if header != 'Relationship':
                        bhvr, lvl = header.split("-")

                        if bhvr not in self.inf_by_rel[row['Relationship']].keys():
                            self.inf_by_rel[row['Relationship']][bhvr] = {}

                        self.inf_by_rel[row['Relationship']][bhvr][int(lvl)] = float(row[header])

        #include workplace types and their influences into inf_by_rel:
        with open(workplace_types_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            self.inf_by_rel['Workplace'] = {}

            for row in csv_reader:
                self.inf_by_rel['Workplace'][int(row['Type'])] = {}
                for header in csv_reader.fieldnames:
                    if header != 'Type':
                        bhvr, lvl = header.split("-")

                        if bhvr not in self.inf_by_rel['Workplace'][int(row['Type'])].keys():
                            self.inf_by_rel['Workplace'][int(row['Type'])][bhvr] = {}

                        self.inf_by_rel['Workplace'][int(row['Type'])][bhvr][int(lvl)] = float(row[header])

        # create dictionary of workplace type probabilities
        self.p_workplace_type_distribution = {}
        with open(workplace_type_distribution_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.p_workplace_type_distribution[int(row['Type'])] = row['Probability']
            if list(self.p_workplace_type_distribution.keys()) != list(self.inf_by_rel['Workplace'].keys()):
                print("Error: types in workplace type distribution do not match workplace types (", \
                    list(self.inf_by_rel['Workplace'].keys()), "). Parameter file:", workplace_type_distribution_file)
                exit(1)
            if not math.isclose(math.fsum([float(i) for i in self.p_workplace_type_distribution.values()]), 1, rel_tol=tol):
                print("Error: workplace type probabilities do not sum to 1. Parameter file:", \
                    workplace_type_distribution_file)
                exit(1)


        # read the network parameters
        network_file = os.path.join(os.path.curdir, self.parameter_folder, 'network.csv')
        with open(network_file, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if row['Topology'] == 'Newman–Watts–Strogatz':
                    # Newman-Watts–Strogatz: small world graph created from initial ring topology, with new edges added on rewiring
                    self.graph_type = 'Newman–Watts–Strogatz'
                    # graph_k: each node is joined to k nearest neighbours in the ring
                    self.graph_k = int(row['k'])
                    # graph_p: probability of rewiring each edge
                    self.graph_p = float(row['p'])
                    # graph_excluded: proportion of population with no close friends
                    self.graph_excluded = float(row['excluded'])
                elif row['Topology'] == 'Barabasi-Albert':
                    # Barabasi-Albert: random graph grown through preferential attachment
                    self.graph_type = 'Barabasi-Albert'
                    # graph_m: number of edges to attach from a new node to existing nodes
                    self.graph_m = int(row['m'])
                    # graph_excluded: proportion of population with no close friends
                    self.graph_excluded = float(row['excluded'])
                else:
                    print("Error reading in network parameters: unknown topology (" + row['Topology'] + "). Parameter file:", network_file)
                    exit(1)


    # pick sex and age for a new agent (i.e., first agent in a household)
    def pick_sex_age(self):
        index = 0
        r = random.uniform(0,1)
        if random.random() < self.p_male:
            sex = 'M'
            threshold = self.p_male_age[self.min_age]
            while r > threshold:
                index += 1
                threshold += self.p_male_age[self.min_age + index]
        else:
            sex = 'F'
            threshold = self.p_female_age[self.min_age]
            while r > threshold:
                index += 1
                threshold += self.p_female_age[self.min_age + index] 
        return sex, self.min_age + index


    # pick the age for a spouse
    def pick_spouse_sex_age(self, spouse_sex, spouse_age):
        if random.random() < self.p_same_sex:
            sex = spouse_sex
        elif spouse_sex == 'F':
            sex = 'M'
        else:
            sex = 'F'
        index = 0
        r = random.uniform(0,1)
        if sex == 'M':
            threshold = self.p_male_spouse_age[spouse_age][str(self.min_age)]
            while r > threshold:
                index += 1
                threshold += self.p_male_spouse_age[spouse_age][str(self.min_age + index)]
        else:
            threshold = self.p_female_spouse_age[spouse_age][str(self.min_age)]
            while r > threshold:
                index += 1
                threshold += self.p_female_spouse_age[spouse_age][str(self.min_age + index)]
        return sex, self.min_age + index


    # this is separated to make it easier to read from data if such data can be found
    def pick_house_member_sex_age(self, first_member_sex, first_member_age, first_member_spouse):
        return self.pick_sex_age()


    # pick a household size
    def pick_household_size(self, first_member_age, first_member_married):
        index = 1
        r = random.uniform(0,1)
        if first_member_married == True:
            threshold = float(self.p_household_married[str(first_member_age)][str(index)])
            while r > threshold:
                index += 1
                threshold += float(self.p_household_married[str(first_member_age)][str(index)])
        else:
            threshold = float(self.p_household_unmarried[str(first_member_age)][str(index)])
            while r > threshold:
                index += 1
                threshold += float(self.p_household_unmarried[str(first_member_age)][str(index)])
        return index


    # pick the IMD for a household based on the initial household member
    def pick_household_imd(self, first_member_sex, first_member_age):
        r = random.uniform(0,1)
        index = 1
        if first_member_sex == 'M':
            threshold = float(self.p_male_quintile[str(first_member_age)]['IMD-1'])
            while r > threshold:
                index += 1
                threshold += float(self.p_male_quintile[str(first_member_age)][('IMD-' + str(index))])
        else:
            threshold = float(self.p_female_quintile[str(first_member_age)]['IMD-1'])
            while r > threshold:
                index += 1
                threshold += float(self.p_female_quintile[str(first_member_age)][('IMD-' + str(index))])
        return index    


    # return the probability of being employed based on sex, age, and imd
    def work_probability(self, sex, age, imd):
        if sex == 'M':
            return float(self.p_male_employed[('IMD-' + str(imd))][str(age)])
        else:
            return float(self.p_female_employed[('IMD-' + str(imd))][str(age)])


    # pick a workplace size according to defined bins
    def pick_workplace_size(self):
        max_size = 999
        sizes = list(self.p_workplace_size.keys())
        if sizes != ['<10', '<50', '<250', '250+']:
            print("Error in pick_workplace_size(): workplaces sizes do not match expected categories ('<10', '<50', '<250', '250+').")
            exit(1)
        index = 0
        r = random.uniform(0,1)
        threshold = float(self.p_workplace_size[sizes[index]])
        while r > threshold:
            index += 1
            threshold += float(self.p_workplace_size[sizes[index]])
        if index == 0:
            size = random.randint(1,9)
        elif index == 1: 
            size = random.randint(10,49)
        elif index == 2: 
            size = random.randint(50,249)
        else:
            size = random.randint(250,max_size)
        return size


    # Old version with different bin sizes (corresponding to bins used in https://online.olivet.edu/news/research-friends-work)
    # def pick_workplace_contacts_size(self):
    #     workplace_size = self.pick_workplace_size()
    #     friends_sizes = list(self.p_workplace_contacts_size.keys())
    #     if friends_sizes != ['<10', '<50', '<100', '<250', '<500', '500+']:
    #         print("Error in pick_workplace_contacts_size(): workplace contacts sizes do not match expected categories ('<10', '<50', '<100', '<250', '<500', '500+').")
    #         exit(1)
    #     if workplace_size < 10:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<10']), scale=self.p_workplace_contacts_size_spread))
    #     elif workplace_size < 50:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<50']), scale=self.p_workplace_contacts_size_spread))
    #     elif workplace_size < 100:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<100']), scale=self.p_workplace_contacts_size_spread))
    #     elif workplace_size < 250:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<250']), scale=self.p_workplace_contacts_size_spread))
    #     elif workplace_size < 500:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<500']), scale=self.p_workplace_contacts_size_spread))
    #     else:
    #         size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['500+']), scale=self.p_workplace_contacts_size_spread))
    #     if size < 0:
    #         size = 0
    #     return size


    # use the workplace size to determine number of workplace contacts
    def pick_workplace_contacts_size(self):
        workplace_size = self.pick_workplace_size()
        bins = list(self.p_workplace_contacts_size.keys())
        if bins != ['<10', '<50', '<250', '250+']:
            print("Error in pick_workplace_contacts_size(): workplace contacts sizes do not match expected categories ('<10', '<50', '<250', '250+').")
            exit(1)
        if workplace_size < 10:
            size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<10']), scale=self.p_workplace_contacts_size_spread))
        elif workplace_size < 50:
            size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<50']), scale=self.p_workplace_contacts_size_spread))
        elif workplace_size < 250:
            size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['<250']), scale=self.p_workplace_contacts_size_spread))
        else:
            size = int(np.random.normal(loc=int(self.p_workplace_contacts_size['250+']), scale=self.p_workplace_contacts_size_spread))
        if size < 0:
            size = 0
        return size


    # pick the workplace type
    def pick_workplace_type(self):
        r = random.uniform(0,1)
        index = 1
        threshold = float(self.p_workplace_type_distribution[1])
        while r > threshold:
            index += 1
            threshold += float(self.p_workplace_type_distribution[index])
        return index


    # pick risk factors depending on sex
    def pick_risk_factors(self, sex):
        if sex == 'M':
            return self.behaviour_cvd_risk['Male']
        else:
            return self.behaviour_cvd_risk['Female']


    # generic level picker, which takes a dict of three indices along 
    # with their probability and returns a level picked uniformly at random
    def pick_level(self, levels):
        r = random.uniform(0,1)

        if r <= levels[0]:
            return 0
        elif r <= levels[0] + levels[1]:
            return 1
        else:
            return 2


    # pick the initial risk levels for an agent
    def pick_initial_levels(self, sex, age):
        
        if age < 35:
            age_str = '18-34'
        elif age < 65:
            age_str = '35-64'
        else:
            age_str = '65+'

        if sex == 'M':
            gen = 'Male'
        else:
            gen = 'Female'

        initial_levels = dict()
        initial_levels['smoking'] = self.pick_level(self.behaviour_prevalence[gen][age_str]['Smoking'])
        initial_levels['alcohol'] = self.pick_level(self.behaviour_prevalence[gen][age_str]['Alcohol'])
        initial_levels['diet'] = self.pick_level(self.behaviour_prevalence[gen][age_str]['Diet'])
        initial_levels['inactivity'] = self.pick_level(self.behaviour_prevalence[gen][age_str]['Inactivity'])

        return initial_levels

    def get_inf_by_rel(self):
        return self.inf_by_rel









