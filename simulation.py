# Network Software Modeling - Assignment 2
# Ezra Priya (16200091) and Ying Wang (1620700)

# Citation:
# Dataset: Hospital ward dynamic contact network
# A research by P. Vanhems et al., Estimating Potential Infection Transmission Routes in Hospital Wards Using Wearable Proximity Sensors, PLoS ONE 8(9): e73970 (2013).

# Acknowledgement to SocioPatterns collaboration  http://www.sociopatterns.org

import networkx as nx
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import collections
import operator
from matplotlib import pylab

# Initialize parameters
P_infectious         = 0.01    # Probability that the disease is contagious
P_pat_transmit       = 0.05    # Probability of patient transmitting infectious disease
P_oth_transmit       = 0.03    # Probability of non-patient transmitting disease
initial_infected     = 0       # Set the number of initially infected people
employee_check       = 7       # Each hospital worker will be checked for their condition every this interval days
P_recovery           = 0.6     # Probability of recovered/isolated hospital worker in every check-up
status_list_by_day   = {}      # A data structure for all days' status_list for the purpose of drawing graph
np.random.seed(123)

sterilized            = []

# Change above sterilized list to the sterilized list below to set 10% people of real-world graph (G1) to be immune
# sterilized            = ['1098', '1193', '1164', '1115', '1210', '1295', '1109']

# Sterilized list for the Erdos-Renyi graph (G2)
# sterilized            = [322, 874, 356, 75, 690, 649, 3, 669, 108, 863, 553, 237, 211, 7, 300, 4, 702, 147, 933, 837, 748, 236, 830, 998, 658, 552, 544, 173, 581, 624, 709, 180, 769, 318, 187, 819, 285, 632, 711, 304, 14, 97, 110, 212, 889, 36, 494, 722, 381, 906, 275, 927, 941, 165, 55, 720, 383, 715, 438, 404, 332, 148, 563, 86, 506, 181, 533, 238, 324, 429, 809, 680, 76, 232, 213, 17, 949, 1, 817, 554, 476, 315, 106, 564, 757, 967, 341, 56, 31, 705, 343, 183, 526, 992, 28, 504, 590, 280, 224, 305]

# Read the real-world graph from an edge-list file
G1 = nx.read_edgelist('G1_edgelist.txt')

# Read the title list of each person (patient, nurse, doctor, or administration staff)
people_df = pd.read_csv("Title_list.csv", sep = ";")

# Set the name and title of each person as a dataframe for further processing
person_list = people_df['index']
title_list = people_df['title']

# Define number of nodes and edges for the randomly generated graphs
dummy_graph_nodes    = 1000
dummy_graph_edges    = 15000

# Erdos-Renyi random graph generation
G2                   = nx.gnm_random_graph(dummy_graph_nodes, dummy_graph_edges)

# Watts-Strogatz random graph generation
G3                   = nx.watts_strogatz_graph(dummy_graph_nodes, int(len(G1.edges())/len(G1.nodes())), 0.2)

# Select graph to use: the original dataset graph (G) or randomly generated Erdos-Renyi graph (G2)
graph                = G1


# Registering the status and title of each person to dictionaries
def reset_status(graph):
    Title = {}
    Status = {}
    
    if graph == G1:                        # If the real-world graph is selected
        node_list = graph.nodes()          # List all persons to be evaluated
        c = 0                              # Dummy counter for index to person_list and title_list
        for node in person_list:           # Setting the initial status and title for every person
            Title[node] = title_list[c]    # Setting the title of each person according to people_df
            Status[node] = 0               # Setting every person as NOT INFECTED initially
            c += 1                         # Dummy counter to refer to the person_list and title_list
    else:                                  # If the selected graph is the Erdos-Renyi or Watts-Strogatz graph
        node_list = graph.nodes()
        for node in graph.nodes():
            Status[node] = 0
            if np.random.uniform() < 0.387:  # 0.387 is the proportion of patient in the original dataset
                Title[node] = 'PAT'          # Set 38.7% of all nodes as patient
            else:
                Title[node] = 'NON-PAT'      # Set the rest as non-patient (doesn't need to be specified for nurse/doctor/administration staff)

    return Title, Status, node_list
        
    
# Set some patients to have contagious disease at day 0
def initial_infection():
    
    status_list = []                                # Used later for coloring the nodes when plotting the graph
    initial_infected = 0                            # Used later to calculate the proportion of people get infected
    
    for node in node_list:                          # Check every person in the hospital (we're looking for patients only)
        if Title[int(node)] == 'PAT':               # Check if the person is a patient (qualified to act as a source of disease transmittal)
            if np.random.uniform() < P_infectious:  # If the disease happens to be contagious by chance (20%) 
                Status[int(node)] = 1               # Set this patient to be infected and qualified as a source of disease spread
                initial_infected += 1               # Count the number of infected people (for calculating the proportion later)
                print("Patient %s " %node)
        status_list.append(Status[int(node)])       # Similar to Status dictionary, but this one is for coloring the nodes later
    
    return Status, Title, status_list, initial_infected

# Make sure we have at least one patient with infectious disease at the beginning to start the simulation 
print("Patient(s) below act as the initial HAI carrier:")

while initial_infected == 0:                        # Is there any patient with infected disease?
    day = 0                                         # Initialize day of first occurence
    Title, Status, node_list = reset_status(graph)  # Set the title and status of each person
    Status, Title, status_list, initial_infected = initial_infection()  # Repeat the initial_infection() function until we get at least 1 patient with infected disease
    status_list_by_day[day] = status_list           # Add day 0 status_list to the main data structure for keeping track of status_list

    
# Simulate for one time step
def one_day(day):
    
    status_list = []                            # Reset the status of everyone. Later we'll update again from the updated Status dictionary  
    infected = 0                               # Reset the number of infected people
    
    # Every day a hospital worker is considered as having a different immunity/fitness level
    def immunity_level():
        min_immunity = 0.5                              # Threshold for body fitness
        if np.random.uniform() <= min_immunity:         # Below the minimum body fitness, a worker is more exposed to infected disease
            return True
        else:
            return False
    
    # To determine if a neighbour happens to be the unlucky 5% who got infected from an infected patient
    def infected_from_patient():
        if np.random.uniform() <= P_pat_transmit:
            return True
        else:
            return False
   
    # To determine if a neighbour happens to be the unlucky 3% who got infected from an infected non-patient
    def infected_from_non_patient():
        if np.random.uniform() <= P_oth_transmit:
            return True
        else:
            return False
    
    # To reset state of persons who we determine to have immunity (not susceptible to infection)
    def reset_sterilized_persons(node):
        if node in sterilized:
            Status[int(node)] = 0
    
    for node in node_list:                                         # Check for every person in the hospital
        # Split the infected people by patient and non-patient because patient has a higher chance to transmit disease
       
        # If a patient becomes infected, he/she is a HIGH-RISK source for spreading the disease
        if Status[int(node)] == 1 and Title[int(node)] == 'PAT':   # If the person is infected and he/she is a patient (high-risk)
            neighbors = graph[node]                                # Collecting everyone that has interacted with this patient as neighbors
            for neig in neighbors:                                 # Check the neighbors of this 'high-risk' patient
                if  infected_from_patient() and immunity_level():  # If the neighbor happens to be the unlucky 5% who get infected from the patient
                    Status[int(neig)] = 1                          # Set this person's status as infected 
                    reset_sterilized_persons(neig)
    
        # If a non-patient becomes infected, he/she is a MEDIUM-RISK source for spreading the disease
        elif Status[int(node)] == 1 and Title[int(node)] != 'PAT': # This case is for a non-patient who is infected as becoming a source (medium-risk)
            neighbors = graph[node]                                    
            for neig in neighbors:
                if  infected_from_non_patient() and immunity_level():
                    Status[int(neig)] = 1 
                    reset_sterilized_persons(neig)
                    
        # If the person is not infected, he/she is a NO-RISK source
        else:
            pass                                                   # The person is not infected and hence will not cause his/her neighbors to get infected
    
    # If worker is being infected, he/she has some probability of getting recognized during the weekly check-up and hence can be isolated/recovered
    def recovered_non_patient():
        if np.random.uniform() <= P_recovery:                      # If the infected employee is recognized during the check up (only some employees will be detected)
            return True
        else:
            return False
    
    # Weekly check-up for hospital workers
    if day % employee_check == 0:                                       # Check if today is the check-up schedule. Periodic x-days check-up can be formulated with modulo function
        for node in node_list:                                          # Check-up is performed to all workers
            if Title[int(node)] != 'PAT' and Status[int(node)] == 1:    # Check if he/she is a hospital worker (non-patients) and infected
                if recovered_non_patient():                             # If this infected employee is detected to be infected
                    Status[int(node)] = 0                               # Set as recovered. In reality, this means he/she is isolated
    
    # Now we update again the status_list and the number of infected people from the Status dictionary (Status dictionary was not reset)
    for s in Status:                                               # S dictionary is the main reference for each person's status
        status_list.append(Status[s])                              # We add again the status_list based on the updated Status of each person
        if Status[s] == 1:                                         # Count the number of infected people on this day
            infected += 1
    
    infected_proportion = infected/len(Status)                     # Calculate the proportion of infected people
    status_list_by_day[day] = status_list                          # Update the status_list data structure for plotting purpose
    
    return Status, status_list, infected_proportion


def run_simulation(days):
                                   
    f1 = plt.figure(1)
    day_list = [0]                                           # Day 1 is when the initial patients got infected initially - this is for the x-axis of the plot
    proportion_list = [(initial_infected/len(node_list))]    # Initial proportion of infected people - this is for the y-axis of the plot
    
    for day in range(1, days+1):                             # Simulate for day 1 to day x
        Status, status_list, proportion = one_day(day)       # Run the simulation one_day() function
        day_list.append(day)                                 # Append the day_list for the purpose of contamination plot
        proportion_list.append(proportion)                   # Append the proportion_list for the purpose of contamination plot
 
    plt.plot(day_list, proportion_list, linestyle='-', color='red')             # Draw the contamination plot
    plt.xlabel('Days')
    plt.ylabel('Proportion of infected population')
    plt.title('Real-world graph')
    ax = plt.axes()
    ax.yaxis.grid()
    ax.xaxis.grid()                                            
    
    return Status, day_list, proportion_list, f1

# Determine how many days of simulation to run inside run_simulation()
Status, day_list, proportion_list, f1 = run_simulation(30)


# Calculation of basic reproductive number
def repro_num():
    gd = graph.degree()
    gdv = list(gd.values())
    d_bar = float(np.mean(gdv))
    r = (0.05*0.387)+(0.03*0.613)
    R0 = r*((d_bar*d_bar)-d_bar)/d_bar
    print("The reproductive number of the selected graph is %.2f" %R0)
    print()
    
repro_num()


# Centrality analysis
def centrality_analysis():

    # Betweenness centrality
    betw_cent = nx.betweenness_centrality(graph)
    sort_betw_cent = sorted(betw_cent.items(), key=operator.itemgetter(1), reverse=True)

    # Degree centrality
    deg_cent = nx.degree_centrality(graph)
    sort_deg_cent = sorted(deg_cent.items(), key=operator.itemgetter(1), reverse=True)

    # Closeness centrality
    clos_cent = nx.closeness_centrality(graph)
    sort_clos_cent = sorted(clos_cent.items(), key=operator.itemgetter(1), reverse=True)

    # Eigenvector centrality 
    eiv_cent = nx.eigenvector_centrality(graph)
    sort_eiv_cent = sorted(eiv_cent.items(), key=operator.itemgetter(1), reverse=True)

    # Convert centrality (from library form) to pandas data frames
    Bet_df = pd.DataFrame.from_records(sort_betw_cent, columns = ['Name by Betweenness', 'Betweeness Centrality'])
    Deg_df = pd.DataFrame.from_records(sort_deg_cent, columns = ['Name by Degree', 'Degree Centrality'])
    Clos_df = pd.DataFrame.from_records(sort_clos_cent, columns = ['Name by Closeness', 'Closeness Centrality'])
    Eiv_df = pd.DataFrame.from_records(sort_eiv_cent, columns = ['Name by Eigenvector', 'Eigenvector Centrality'])

    # Merge the four data frames for a single data frame for display
    result1 = Bet_df.join(Deg_df)
    result2 = result1.join(Clos_df)
    result = result2.join(Eiv_df)

    print("Some nodes with the highest centrality measures:")
    print(result.head())
    # To export the list to csv, uncomment below code
    #result.to_csv("rw_centrality.xls", sep="\t")
    
    return betw_cent, deg_cent, clos_cent, eiv_cent

betw_cent, deg_cent, clos_cent, eiv_cent = centrality_analysis()


# To find people with highest centrality measures
def find_top_central():
    
    import operator
    
    centrality_dict = {}
    nodes_key = []
    sterilized = []

    # Register each node with its averaged centrality measure to the centrality dictionary
    for node in graph.nodes():
        cent = (betw_cent[node] + deg_cent[node] + clos_cent[node] + eiv_cent[node])/4    # Take average of the 4 centrality measures
        centrality_dict[node] = cent                                                      # Register each node to centrality dictionary

    # Sort the centrality dictionary based on highest averaged centrality
    sort_cent = sorted(centrality_dict.items(), key=operator.itemgetter(1), reverse=True)

    # Take all nodes (the key of dictionary) to a new list with order starting with the highest centrality
    for key, value in sort_cent:
        nodes_key.append(key)
    
    # Calculate the number of people for the top 10% most central people
    # Change the coefficient for different percentage
    no_of_immune = int(0.1*len(graph.nodes()))
    
    # Register these top 10% people to the sterilized list
    for m in range(no_of_immune):
        sterilized.append(nodes_key[m])
    
    print()
    print("One of the possible solutions is to set set some persons (10%) with highest centrality to be immune.")
    print("List of sterilized people:")
    print(sterilized)
    print()
    
find_top_central()

# Visualize graph to see the proportion of infected persons
def draw_graph(graph, day):
    
    # Figure initialization
    f2 = plt.figure(num=None, figsize=(25, 20))
    plt.title("Contagion on day %d" %day)
    plt.axis('off')
    pos = nx.spring_layout(graph, k = 0.3)
    
    # Draw graph using networkx. Specified date is used in status_list_by_day to see the contagion on that day. 
    nx.draw_networkx_nodes(graph, pos, node_color = status_list_by_day[day], node_size = 900, font_size = 20, alpha=0.9, with_labels=True, cmap=plt.cm.Oranges, vmin=0.2, vmax=0.3)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)

    cut = 1
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)
    
    return f2

# Type the day which we want to visualize (this case is day-10)
f2 = draw_graph(graph, 10)


# Codes below are for plotting purpose. These are not run unless we want to create a plot for the report
def compare_plots():
    rw_proportion_list = proportion_list
    rw_prop = pd.DataFrame(rw_proportion_list)
    rw_prop.to_csv('GraphX_case-1.csv', sep=',')

    prop_def = pd.read_csv('GraphX_default.csv', header=0, names=['a', 'b'])
    prop_case = pd.read_csv('GraphX_case-1.csv', header=0, names=['a', 'b'])

    f3 = plt.figure()
    plt.plot(day_list, prop_def['b'], linestyle='-', color='red')
    plt.plot(day_list, prop_70['b'], linestyle='--', color='blue')

    plt.xlabel('Days')
    plt.ylabel('Proportion of infected population')
    plt.title('Real-world graph: 70% check-up detection rate vs. default 60% ')
    ax = plt.axes()
    ax.yaxis.grid()
    ax.xaxis.grid()
    plt.savefig('G1 70% detection rate.png')
    
plt.show()

