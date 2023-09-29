import random
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
import os
import gc
import networkx as nx
import argparse
from agent import Agent
import parameters

class Network:
    def __init__(self, parameters) -> None:
        self.param = parameters

    # generate the population of agents
    def generate_agents(self, target_size):
        agent_list = []
        # track how many agents are actually created
        numAgents = 0
        # create a list for agents who will need assigning to workplaces
        remaining_agents = []
        # create the agents and households
        while numAgents < target_size:
            debug = False
            # create a new agent with characteristics based on whole population distribution
            sex, age = self.param.pick_sex_age()
            risk_factors = self.param.pick_risk_factors(sex)
            initial_levels = self.param.pick_initial_levels(sex, age)
            agent_list.append(Agent(sex, age, risk_factors, initial_levels))
            # keep track of this agent
            firstInHousehold = agent_list[-1]
            # choose a size and index of deprivation for this agent's household
            imd = self.param.pick_household_imd(firstInHousehold.sex, firstInHousehold.age)
            firstInHousehold.imd = imd
            # pick whether this agent should be assigned a workplace
            if random.random() < self.param.work_probability(sex, age, imd):
                agent_list[-1].assign_to_workplace = True
                remaining_agents.append(agent_list[-1])
            # if the first agent is married, add their spouse
            if random.random() < self.param.p_married[sex][str(age)]:
                sex, age = self.param.pick_spouse_sex_age(firstInHousehold.sex, firstInHousehold.age)
                risk_factors = self.param.pick_risk_factors(sex)
                initial_levels = self.param.pick_initial_levels(sex, age)
                agent_list.append(Agent(sex, age, risk_factors, initial_levels))
                agent_list[-1].imd = imd
                agent_list[-1].spouse = firstInHousehold
                firstInHousehold.spouse = agent_list[-1]
                if (debug): print("added spouse")
            # pick household size
            h = self.param.pick_household_size(firstInHousehold.age, firstInHousehold.spouse != None)
            if (debug): print("first agent in household", firstInHousehold.id, "target household size", h, "imd", imd)
            # if added spouse temporarily decrement h
            if firstInHousehold.spouse != None:
                h -= 1
            # add the remaining agents in the household  
            for i in range(1, h):
                if (debug): print("hSize", h, "add additional agent number", i)
                sex, age = self.param.pick_house_member_sex_age(firstInHousehold.sex, firstInHousehold.age, firstInHousehold.spouse)
                risk_factors = self.param.pick_risk_factors(sex)
                initial_levels = self.param.pick_initial_levels(sex, age)
                agent_list.append(Agent(sex, age, risk_factors, initial_levels))
                agent_list[-1].imd = imd
                firstInHousehold.household.append(agent_list[-1])
                # pick whether the new agent should be assigned a workplace
                if random.random() < self.param.work_probability(sex, age, imd):
                    agent_list[-1].assign_to_workplace = True
                    remaining_agents.append(agent_list[-1])
            # if added spouse reset h
            if firstInHousehold.spouse != None:
                h += 1
                if (debug): print("spouse added, resetting h:", h)
            # update household lists for each new agent
            for i in range(1, h):
                if (debug): print("updating household of", agent_list[-i].id, end = '')
                # if this was the second agent in the household, check whether it's spouse of the first agent
                if i == h - 1 and agent_list[-i].spouse != None:
                    # if it is the spouse, don't add the first agent into this agent's household list
                    if (debug): print(" spouse of first", Network.str_agent_list(agent_list[-h+1:-i]), end = '')
                    agent_list[-i].household.extend(agent_list[-h+1:-i])
                # otherwise add all agents that were put in the household prior to this one 
                else:
                    if (debug): print(" not spouse of first", agent_list[-i], Network.str_agent_list(agent_list[-h:-i]), end = '')
                    agent_list[-i].household.extend(agent_list[-h:-i])
                # if this agent was not the last in the household, add the subsequent agents
                if i != 1:
                    if (debug): print(" ", agent_list[-i], Network.str_agent_list(agent_list[-i+1:]), end = '')
                    agent_list[-i].household.extend(agent_list[-i+1:])
                if (debug): print(".")

            if (debug):
                print("Added household with the following members:")
                for i in range(1, h + 1):
                    print(agent_list[-i])

            numAgents += h
            if (debug): print("target size: ", target_size, " actual size: ", numAgents)

        # agents and households now created
        print("Created agents and households. Target size: ", target_size, " actual size: ", numAgents)

        # create the friendship network
        fDebug = False
        friendNetworkSize = (int) (numAgents * (1.0 - self.param.graph_excluded))
        if (fDebug): print("Friendship network size: ", friendNetworkSize)
        # create the underlying graph for the friendship network
        if self.param.graph_type == 'Newman–Watts–Strogatz':
            if (fDebug): print("Creating friendship network using Newman–Watts–Strogatz, k=" + str(self.param.graph_k) + ", p=" + str(self.param.graph_p))
            graph = nx.newman_watts_strogatz_graph(friendNetworkSize, self.param.graph_k, self.param.graph_p, seed=None)
        # elif self.param.graph_type == 'Watts–Strogatz':
        #     if (fDebug): print("Creating friendship network using Watts–Strogatz, k=" + str(self.param.graph_k) + ", p=" + str(self.param.graph_p))
        #     graph = nx.watts_strogatz_graph(friendNetworkSize, self.param.graph_k, self.param.graph_p, seed=None)
        elif self.param.graph_type == 'Barabasi-Albert':
            if (fDebug): print("Creating friendship network using Barabasi-Albert, m=" + str(self.param.graph_m))
            graph = nx.barabasi_albert_graph(friendNetworkSize, self.param.graph_m, seed=None)
        else:
            print("Error: unknown graph type " + self.param.graph_type)
            exit(1)
        # determine which agents in the population to put into the friendship graph
        agentsWithCloseFriends = random.sample(agent_list, friendNetworkSize)
        # create the graph
        agent_map = dict(zip(range(0, friendNetworkSize), agentsWithCloseFriends))
        nx.relabel_nodes(graph, agent_map, copy=False)
        # remove spouse and agents in household from friends (since relationships hierarchical)
        for a in graph.nodes:
            if graph.has_node(a.spouse):
                if graph.has_edge(a, a.spouse):
                    graph.remove_edge(a, a.spouse)
            for h in a.household:
                if graph.has_node(h):
                    if graph.has_edge(a, h):
                        graph.remove_edge(a, h)

        
        # friendship relationships now defined
        print("Created friendship network.", graph)
        print("Average friendship degree (excluding spouse, household, workplace):", nx.number_of_edges(graph) / nx.number_of_nodes(graph))

        # create the workplaces 
        for a in remaining_agents:
            # create a new workplace with a
            wplace = [a]
            remaining_agents.remove(a) 
            # get a target workplace size
            workplace_size = self.param.pick_workplace_contacts_size()
            # if the number of agents remaining < target size, just add them to the workplace  
            if len(remaining_agents) < workplace_size:
                wplace = wplace + remaining_agents
                remaining_agents.clear()
            # otherwise create a workplace of the target size with randomly selected agents
            else:
                for i in range(workplace_size):
                    employee = random.choice(remaining_agents)
                    wplace.append(employee)
                    remaining_agents.remove(employee)
            wtype = self.param.pick_workplace_type()
            # set the workplace of each agent
            for employee in wplace:
                employee.workplace = wplace.copy()
                employee.workplace_type = wtype
                employee.assign_to_workplace = False
                # remove self from workplace record
                employee.workplace.remove(employee)
                # remove spouse from workplace record (since relationships hierarchical)
                if employee.spouse in employee.workplace:
                    employee.workplace.remove(employee.spouse)
                # remove agents in household from the workplace (since relationships hierarchical)
                for colleague in employee.workplace:
                    if colleague in employee.household:
                        employee.workplace.remove(colleague)

                # remove agents in friends from the workplace (since relationships hierarchical)
                if graph.has_node(employee):
                    for colleague in employee.workplace:
                        if graph.has_node(colleague):
                            if graph.has_edge(employee, colleague):
                                employee.workplace.remove(colleague)      

        # use the friendship network to set the friend list for each agent
        for a in agent_list:
            if graph.has_node(a):
                for n in graph.neighbors(a):
                    a.friends.append(n)
        # try to force garbage collection on the graph
        del graph
        gc.collect

        # uncomment the following to also return the friendship graph; also need to
        # comment out the garbage collection above
        # return agent_list, graph
        return agent_list


    # print a list of agents, can be useful for debugging
    def str_agent_list(agents):
        return_string = "["
        for i in agents:
            return_string = return_string + str(i.id) + ","
        return_string = return_string + "]"
        return return_string    


    # string representation of a graph node, again useful for debugging
    def node_to_string(g, agent):

        if agent.spouse == None:
            spouse_string = "[_]"
        else:
            spouse_string = "[" + str(agent.spouse.id) + "]"

        if len(agent.household) == 0:
            house_string = "[_]"
        else:
            house_string = "["
            house_string = house_string + str(agent.household[0].id)
            for i in agent.household[1:]:
                house_string = house_string + "," + str(i.id) 
            house_string = house_string + "]"

        friend_string = "["
        index = 0
        for i in g.neighbors(agent):
            if index != 0:
                friend_string = friend_string + ","
            friend_string = friend_string + str(i.id)
            index += 1
        friend_string = friend_string + "]"

        if len(agent.workplace) == 0:
            work_string = "[_]"
        else:
            work_string = "["
            work_string = work_string + str(agent.workplace[0].id)
            for i in agent.workplace[1:]:
                work_string = work_string + "," + str(i.id) 
            work_string = work_string + "]"
        return str(agent.id) + ":" + str(agent.age) + agent.sex + ":" + "q" \
            + str(agent.imd) + ":" + "S" + spouse_string + ":" + "H" + house_string \
                + ":" + "F" + str(nx.degree(g,agent)) + friend_string + ":" + "W" + work_string

 
# main method for testing the network
def main():
    parser = argparse.ArgumentParser(description="network - create a network for CVD simulation.")
    # main simulation parameters
    parser.add_argument(dest='parameter_folder', 
        help='folder of csv files with parameter specifications')
    parser.add_argument('-n', '--size', action='store',
        default=3500, type=int, help='target population size')
    parser.add_argument('--plots', dest='plots', \
                        action='store_true', help='generate basic plots')
    parser.set_defaults(plots=False)
    args = parser.parse_args()
    print("Using parameters from folder:", args.parameter_folder)
    target_size = args.size
    print("Target population size: ", target_size)
 
    param = parameters.Parameters(args.parameter_folder)
    config_name = os.path.basename(os.path.normpath(args.parameter_folder))
    n = Network(param)

    plots = args.plots    
    if not plots:
        mpl.use('PDF')

    agent_list = n.generate_agents(target_size)
    print("Number of agents in population:", len(agent_list))
    # to use the following need to return agent_list and graph from generate_agents()
    # which uses significantly more memory
    # print("Number of edges in the friendship network:", nx.number_of_edges(graph))
    # print("Average friendship degree (excluding spouse, household, workplace):", nx.number_of_edges(graph) / nx.number_of_nodes(graph))

    # Uncomment the following to print details of some random agents
    # print("Example agents:")
    # random_sample = random.sample(agent_list, 10)
    # for a in random_sample:
    #     print(a)

    # Uncomment the following to print all agents
    # for a in agent_list:
    #     if graph.has_node(a):
    #         print(Network.node_to_string(graph, a), "workplace_type:", a.workplace_type)    
    #     else:
    #         print(a)
    # for i in graph.nodes():
    #     print(Network.node_to_string(graph, i), "workplace_type:", i.workplace_type)
        
    # Uncomment the following to plot the friendship network (for SMALL networks only!)
    # options = {"node_color": "black", "node_size": 2, "linewidths": 0, "width": 0.1}
    # seed = 42 
    # pos = nx.spring_layout(G, seed=seed)  # Seed for reproducible layout
    # nx.draw(G, pos=pos, **options)
    # plt.show()

    # plot the age distribution
    if plots:
        plot_folder = Path("./plots")
        print("outputting plots to:", str(plot_folder /config_name))

        age_dist = dict()
        for i in range(param.min_age, param.max_age + 1):
            age_dist[i] = 0
        for i in agent_list:
            age_dist[i.age] = age_dist[i.age] + 1
        fig = plt.figure()
        plt.ylabel('Frequency')
        plt.xlabel('Age')
        plt.title('Age distribution')
        xpoints = age_dist.keys()
        ypoints = age_dist.values()
        plt.bar(xpoints, ypoints, color='#6699ff')
        filename = plot_folder / config_name / ("n" + str(target_size) + "_age_distribution.pdf")
        plt.savefig(filename)
        plt.close(fig)

        # plot the friendship degree distribution
        # for this will need to return agent_list and graph from generate_agents()
        # which uses significantly more memory
        # degree_dist = nx.degree_histogram(graph)
        # fig = plt.figure()
        # plt.ylabel('Frequency')
        # plt.xlabel('Degree')
        # plt.title('Friendship degree distribution')
        # xpoints = range(0,len(degree_dist))
        # ypoints = degree_dist
        # plt.bar(xpoints, ypoints, color='#6699ff')
        # filename = plot_folder / config_name / ("n" + str(target_size) + "_friendship_degree_distribution.pdf")
        # plt.savefig(filename)
        # plt.close(fig)

if __name__ == "__main__":
    main()

