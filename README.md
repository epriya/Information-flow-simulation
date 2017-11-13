This code is written as part of the Network Software Modelling assignment of UCD MSc Business Analytics course
The project topic is:
Information-flow-simulation

With a real-world graph case: contagion in a hospital

Acknowledgement
SocioPatterns for the real-world graph dataset

Implementation is in Python with networkx library


Background

A study by the US Centers for Disease Control and Prevention (2007) showed that one in 25 hospital patients carries at least one healthcare-associated infections (HAI). 
While receiving medical treatments, contact between patient and healthcare workers acts as a source of transmission of infections. 
Moreover, hospital workers are also vulnerable to infections when preventive measures are not sufficient.

This project discusses a case of HAI transmission in a hospital using a real-world graph of physical contacts between patients and hospital workers, as well as among the hospital workers (doctors, nurses, and administration staffs) taken from a geriatric unit of a university hospital in Lyon, France. 
Wearable sensors were used to count the close physical interaction between two persons which is considered as a contact.

Although the sensor was not designed to detect the presence of an infection, a graph representing contacts could be used to simulate the possibility of an outbreak when a HAI-carrier is not isolated and begins to transmit the infection to hospital workers and eventually to other patients. 

Each contagious disease has a different contagion rate. Through the simulation, we could see how severe the contagion is by assuming a transmission probability. 
By recognizing the potential outbreak and the vulnerability of hospital workers, prevention and mitigation measures can be enforced to protect hospital workers as part of the disease transmission.


Three different graph types will be used in the simulation:
1.	A real-world graph of contacts in a hospital in Lyon, France, which come as two data files:
o	An edge-list graph dataset of order 75 and size 1139
o	A dictionary file explaining the title of each node/person (patient, doctor, nurse, or administration staff)

2.	A randomly generated Erdos-Renyi graph
o	Roughly the same proportion of as in the real-world graph: 1000 nodes and 15000 edges
o	The same proportion of patient with the real-world graph: 38.7%

3.	A randomly generated Watts-Strogatz graph
o	The same order, size, and proportion of patient with the Erdos-Renyi graph
All three graphs have the same properties:
	Node represents a person (patient, doctor, nurse, or administration staff)
	Edge represents close physical interaction (contact)
	Non-directed
Although in reality one acts as a source of infection carrier and the other acts as a receiver, we assume an infection can be transmitted so long as a contact happens between the two persons regardless of the source
	Non-regular and non-complete

