'''
    GML2LGF converter - Converts traditional gml files into Lemon Graph Format
    Copyright (C) 2013  Levente Csikor

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    For more information send an email to: csikor@tmit.bme.hu
'''
# -*- encoding: utf-8 -*-
#for copying a variable normally not just referencing to that from other variables
import copy
import sys

#for generating random costs if needed
import random

#it is for escaping characters
import re

#this will be helpful to get the file's basename
import os.path
class Converter:
    
    #global error msg
    error_msg = ''
    
    #the input file
    file_name = ''
    path_only = ''
    #storing all the nodes
    nodes = list()
    #storing nodes parameters
    node_params = dict()
    #number of nodes
    number_of_nodes = 0
    #storing all the edges
    edges = list()
    #storing edge parameters
    edge_params = dict()
    #number of edges
    number_of_edges = 0
    
    f = None
    
    text_area = None
    
    #the miscellaneous header part, which is not regarding to the final lgf file
    header = ''
    def __init__(self,file_name):
#         print('constructor...param1= {}'.format(file_name))
        self.file_name = file_name
        basename = os.path.basename(self.file_name) 
#         print basename
        path = os.path.abspath((self.file_name))
#         print "PATH: ",os.path.abspath((self.file_name))
        
#         print str(os.path.splitext(self.file_name))
        self.path_only = path[:(len(path)-len(basename))]
#         print "PATH_ONLY",path_only
        #resetting global variables
        self.number_of_edges = 0
        self.number_of_nodes = 0
        self.nodes = list()
        self.edges = list()
        self.node_params.clear()
        self.edge_params.clear()
        self.error_msg = ''
    
    def set_reference(self,text_area):
        self.text_area = text_area
    
    def log(self,txt):
        if(self.text_area != None):
            self.text_area.text +=txt + "\n"
       
    def read_file(self):
        
        try:
            self.f = open(self.file_name,'r')
            
        except IOError as ioe:
            self.error_msg = "Cannot open file: {}".format(ioe)
            print("Cannot open file: {}".format(ioe))
            return False
        except TypeError as te:
            self.error_msg = "There is no file to open/read {}".format(te)
            print("File variable is empty {}".format(te))
            return False
        except:
            self.error_msg = "Unexpected error:",sys.exc_info()[0]
            print("Unexpected error:",sys.exc_info()[0])
            return False
            
            
        
        isNode = False
        isEdge = False
        #storing a node and its properties
        one_node = dict() 
        #storing an edge and its properties
        one_edge = dict()

        
        for line in self.f:
               
            splitted_line = line.split()
            #looking for the first node and its params
            if(splitted_line[0] == "node" and splitted_line[1] == "["):
#                 self.log('Node element recognized')
                isNode = True
                isEdge = False
                continue
            #we found a node -> we are reading node params
            elif(isNode):
                if(splitted_line[0] != "]"):
#                     self.log("-----node line----")
#                     self.log("{}, {}".format(splitted_line[0],splitted_line[1]))
                    value = ''
                    for i in range(1,len(splitted_line)):
                        value += " "
                        value += splitted_line[i]
                    one_node[splitted_line[0]] = value
                    
                    
#                     print("a node prop: {}".format(self.one_node))
#                     print(line)
                elif(splitted_line[0] == "]"):
#                     self.log("==== node element closed ====")
                    isNode = False
                    
#                     self.nodes[self.iterator] = copy.deepcopy(one_node)
                    self.nodes.append(copy.deepcopy(one_node))
                    one_node.clear()
                continue
            #we are reading the edges and its details
            elif(splitted_line[0] == "edge" and splitted_line[1] == "["):
#                 self.log('Edge element recognized')
                isEdge = True
                isNode = False
                continue
            elif(isEdge):
                if(splitted_line[0] != "]"):
#                     self.log("---edge line ---")
#                     self.log("{},{}".format(splitted_line[0], splitted_line[1]))
                    
                    one_edge[splitted_line[0]] = splitted_line[1]
#                     print(line)
                elif(splitted_line[0] == "]"):
#                     self.log("===== edge element closed =====")
                    isEdge = False
                    self.edges.append(copy.deepcopy(one_edge))
                    one_edge.clear()
                    
                continue
            
             
            else:
                self.header+=line

                
        self.analyze_nodes_and_edges()
        
    #this function checks that how many different node/edge parameters are present, and its number of occurrence
    def analyze_nodes_and_edges(self):
        
        self.number_of_nodes = len(self.nodes)
        for i in range(self.number_of_nodes):
#             print(self.nodes[i])
            for j in self.nodes[i]:             
                if(i == 0):
                    self.node_params[j] = 1
                else:
                    try:
                        self.node_params[j] += 1
                    except KeyError:
                        self.node_params[j] = 1
        
        
        self.number_of_edges = len(self.edges)
        for i in range(self.number_of_edges):
            for j in self.edges[i]:
                if(i == 0):
                    self.edge_params[j] = 1
                else:
                    try:
                        self.edge_params[j] += 1
                    except KeyError:
                        self.edge_params[j] = 1
                        
        
        
#         print(g)            
        self.log("#nodes: {}".format(self.number_of_nodes))
        self.log("Found node params: {}".format(len(self.node_params)))
        for i in self.node_params:
            
            self.log("\t" + str(i) + ":" + str(self.node_params[i]) + "\t\t for instance:" + self.find_node_with_param(str(i)))
            
                
        
        self.log("#edges: {}".format(self.number_of_edges))
        self.log("Found edge params: {}".format(len(self.edge_params)))
        for i in self.edge_params:       
            self.log("\t" + str(i) + ":" + str(self.edge_params[i]) + "\t\t for instance:" + self.find_edge_with_param(str(i)))
     
    
    def find_node_with_param(self,param):
        '''This function will find an example for a particular param
        It is used to show in the GUI's console that how a property looks like
        '''
        retVal = None
        nodes_range = range(len(self.nodes))
        for i in nodes_range:
            try:
                retVal = self.nodes[i][param]
            except:
                continue
        if retVal != None:
            return str(retVal)
        else:
            print ("Somehow no example was found with the given param:", param)

    def find_edge_with_param(self,param):
        '''Same as find_node_with_param, but it is used for links
        '''
        retVal = None
        nodes_range = range(len(self.edges))
        for i in nodes_range:
            try:
                retVal = self.edges[i][param]
            except:
                continue
        if retVal != None:
            return str(retVal)
        else:
            print ("Somehow no example was found with the given param:", param)

    
    
           
    def write_out_results(self,link_options, node_params_to_write, edge_params_to_write):
        '''
        This method will do actually the THING.
        First it writes out the header of the GML file into a separate nfo file for lemon lgf,
        and then the nodes and edges - according to the settings, given by the user - will be written out in a lemon specific format/
        The lemon file name will be the same as the gml file's name, without .gml
        '''
        
        #get the network name from the file's base name
        basename = str(os.path.splitext(os.path.basename(self.file_name))[0])
        lgf_name = self.path_only + basename  + ".lgf"
        lgf_nfo = self.path_only + basename + ".nfo"

        
        output_file = open(lgf_name, 'w')
        #writing out the nfo from the header of the gml file
        output_nfo = open(lgf_nfo, 'w')
        output_nfo.write(self.header)
        
        #printing out nodes
        output_file.write("@nodes\n")
        
        
        #first column is label, which is usually stored as 'id' in GML, 
        #then we write out nodes' names
        output_file.write(node_params_to_write["id"] + 
                          "\t" +
                          node_params_to_write["label"] +
                          "\t")
        #OK we write out other params
        for i in node_params_to_write:
            #we ignore the previous two property
            if(i != "id" and i !="label"):
                output_file.write(node_params_to_write[i] + "\t")
        output_file.write("\n")
        
  
        #OK write out the nodes' particular data
        length = len(self.nodes)
        for i in range(length):
#             for j in self.nodes[i]:
#                 print j, self.nodes[i][j]
            #WE write out the id and the label first
            output_file.write(self.nodes[i]["id"] + "\t")
            output_file.write(self.nodes[i]["label"] + "\t")
            
            for k in node_params_to_write:
                if(k != "id" and k != "label"):
                    try: 
    #                         print k, self.nodes[i][k]
                        output_file.write(self.nodes[i][k])
                    except:# if corresponding property is not found then print N/A
    #                         print "KEY NOT FOUND"
                        output_file.write("N/A")
                    output_file.write("\t")
            output_file.write("\n")
# #                 print j, self.nodes[i][j]
#                 
        output_file.write("\n")
        ######## OK WE DID WRITE OUT THE NODES #########
        #---- here comes the edges ------
        output_file.write("@arcs")
        output_file.write("\n")
        output_file.write(" \t")
        output_file.write(" \t")
        output_file.write("label")
        output_file.write("\t")
        
        
            
        #writing out other properties
        for n in edge_params_to_write:
            output_file.write(edge_params_to_write[n])
            output_file.write("\t")
        
        
        #if costs are set differently than in gml, we add cost column
        if(link_options["cost"] == "unit" or link_options["cost"] == "random"):
            output_file.write("cost")
            output_file.write("\t")
         
        output_file.write("\n")   
        #since in LGF the edges are labeled with an autoincremented value
        #we create a variable for this
        edge_label = 0
        
        
        length = range(len(self.edges))
        for i in length:
            output_file.write(self.edges[i]["source"])
            output_file.write("\t")
            output_file.write(self.edges[i]["target"])
            output_file.write("\t")
            output_file.write(str(edge_label))
            output_file.write("\t")
            
            
            #we use remaining gml properties that may were set to other name
            for n in edge_params_to_write:
                try:
                    param = str(self.edges[i][n])
                    param = param.replace("'", "")
                    param = param.replace('"','')
                    output_file.write(param)
                except:#if corresponding property is not found then print N/A
                    output_file.write("N/A")
                output_file.write("\t")    
        
            #we writing out costs if they were set to be written
            cost = None
            #checking cost type
            if(link_options["cost"] == "random"):
                cost = random.randrange(1,100)
                output_file.write(str(cost))
                output_file.write("\t")
            elif(link_options["cost"] == "unit"):
                cost = 1
                output_file.write(str(cost))
                output_file.write("\t")
            
            #checking whether symmetric or asymmetric costs were set
            if(link_options["symmetric"]):
                output_file.write("\n")
                #in this case costs are symmetric
                output_file.write(self.edges[i]["target"])
                output_file.write("\t")
                output_file.write(self.edges[i]["source"])
                output_file.write("\t")
                #here we also need to increase edge_label since in this case,
                #a new link was added
                edge_label += 1
                output_file.write(str(edge_label))
                output_file.write("\t")
                    
                #we add the same remaining properties again
                for n in edge_params_to_write:
                    try:
                        param = str(self.edges[i][n])
                        param = param.replace("'", "")
                        param = param.replace('"','')
                        output_file.write(param)
                        
                    except:#if corresponding property is not found then print N/A
                        output_file.write("N/A")
                    output_file.write("\t")
                
                #finally, if we use random or unit costs then we need to add them again
                if(link_options["cost"] == "random" or link_options["cost"] == "unit"):
                    output_file.write(str(cost))
                    output_file.write("\t")
                    
            edge_label += 1
            
            #adding a new line
            output_file.write("\n")
            
        
        #closing file with a new line
        output_file.write("\n")
        
        
    

        
        print ("The new .lgf and .nfo file is created\n",str(lgf_name),"\n",str(lgf_nfo))    
        #open the nfo file for header
