import geopandas as gp
import networkx.readwrite
import numpy

from rundmcmc.chain import MarkovChain
from rundmcmc.make_graph import get_assignment_dict, add_data_to_graph
from rundmcmc.partition import Partition, propose_random_flip
from rundmcmc.updaters import statistic_factory, cut_edges
from rundmcmc.validity import Validator, contiguous

import csv

#def mean_median2(partition):
    
def mean_median2(partition, data_column1='d_votes', data_column2='r_votes'):  
    data1 = list(partition[data_column1].values())
    data2 = list(partition[data_column2].values())  
    data=[]
    for i in range(len(data1)):
        data.append(data1[i]/(data1[i]+data2[i]))
    return numpy.mean(data) - numpy.median(data)


def mean_thirdian2(partition, data_column1='d_votes', data_column2='r_votes'):
    data1 = list(partition[data_column1].values())
    data2 = list(partition[data_column2].values())
    data=[]
    for i in range(len(data1)):
        data.append(data1[i]/(data1[i]+data2[i]))
    return numpy.mean(data) - numpy.percentile(data, 33)

def main():
    # Sketch:
    #   1. Load dataframe.
    #   2. Construct neighbor information.
    #   3. Make a graph from this.
    #   4. Throw attributes into graph.
    df = gp.read_file("./testData/mo_cleaned_vtds.shp")
    graph = networkx.readwrite.read_gpickle('example_graph.gpickle')
    
    add_data_to_graph(df, graph, ["PR_DV08", "PR_RV08", "P_08"], "GEOID10")
    
    assignment = get_assignment_dict(df, "GEOID10", "CD")

    updaters = {'d_votes': statistic_factory('PR_DV08', alias='d_votes'), 
                'r_votes': statistic_factory('PR_RV08', alias='r_votes'),
                'cut_edges': cut_edges}
    initial_partition = Partition(graph, assignment, updaters)

    validator = Validator([contiguous])
    accept = lambda x: True

    chain = MarkovChain(propose_random_flip, validator, accept,
                        initial_partition, total_steps=100)
    
    
    
    mm=[]
    mt=[]
    #eg=[]
    
    for state in chain:
        mm.append(mean_median2(state, data_column1='d_votes',data_column2='r_votes'))
        mt.append(mean_thirdian2(state, data_column1='d_votes',data_column2='r_votes'))
        #eg.append(efficiency_gap(state, data_column1='d_votes',data_column2='r_votes))

    #print(graph.nodes(data=True))
    mm_outs=[mm]#,eg]
    mt_outs=[mt]
    #eg_outs=[eg]
    
    with open('mm_chain_out', "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(mm_outs)
        
    with open('mt_chain_out', "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(mt_outs)
        
        
if __name__ == "__main__":
    main()
