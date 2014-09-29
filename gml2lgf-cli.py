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
from converter import Converter

import sys, getopt

def print_help():
    """This function prints out how the CLI works"""
    print 'Usage:'
    print 'gml2lgf-cli.py -f <inputfile> -c <found,unit,random> -s <yes,no>'
    print '-f:'
    print '\t input gml file'
    print '-c:'
    print '\t found  -> nothing special is set for edges'
    print '\t random -> generates random costs for the edges between (1,100) and stores it as "cost" in lgf'
    print '\t unit   -> similar to random, but it creates unit costs for the edges'
    print '-s:'
    print '\t yes    -> uses symmetric edges'
    print '\t no     -> edges are just like they were found in the gml file'
    print '!!!All arguments are necessary!!!'
    sys.exit()

def main(argv):
    """The main function of the CLI interface"""
    inputfile = ''
    cost = ''
    symmetric = ''
    len = None
    try:
        opts, args = getopt.getopt(argv,"hf:c:s:",["gml_file=","cost=","symmetric="])
    except getopt.GetoptError:
        print 'gml2lgf-cli.py -f <inputfile> -c <found,unit,random> -s <yes,no>' 
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
        elif opt in ("-f", "--gmlfile"):
            inputfile = arg            
        elif opt in ("-c", "--cost"):
            cost = arg
        elif opt in ("-s", "--symmetric"):
         symmetric = arg
         
    if inputfile == '' or cost == '' or symmetric == '':
        print_help()
    else:
        #input file check
        if not inputfile.endswith(".gml"):
            print "This program need gml files!"
            print "Read help by executing gml2lgf-cli.py -h"
            sys.exit(2)
        else:

            #checking cost
            if ((cost != "found") and (cost != "unit") and (cost != "random")):
                print "Cost can only be 'found', 'unit' or 'random'"
                print "Read help by executing gml2lgf-cli.py -h"
                sys.exit(2)
            else: #almost done :)
                #checking the last param
                if((symmetric != "yes") and (symmetric != "no")):
                    print "Symmetric argument can only be 'yes' or 'no'"
                    print "Read help by executing gml2lgf-cli.py -h"
                    sys.exit(2)
                else:
                    print 'Input file is', inputfile
                    print 'Costs are set as', cost
                    print 'Symmetric link are used:',symmetric
                    print '\t Converting...'
                    #OK, everything is set properly
                    converter = Converter(inputfile)
                    converter.read_file()
                    status = dict()
                      
                    if(cost == "found"):
                        status["cost"] = "found"
                    elif(cost == "random"):
                        status["cost"] = "random"   
                    else:
                        status["cost"] = "unit"
                    
                    status["symmetric"] = False
                    if(symmetric == "yes"):
                        status["symmetric"] = True
                     
                    #converting node params as LEMON requires
                    node_params = dict()
                    for i in converter.node_params:
                        if(i == "id"):
                            node_params["label"] = str(converter.node_params[i])
                        if(i == "label"):
                            node_params["name"] = str(converter.node_params[i])
                        else:
                            node_params[i] = str(i)
                                                 
                            
                    #converting edge params as LEMON requires
                    edge_params = dict()
                    for i in converter.edge_params:
                        if((i == "source") or (i == "target")):
                            pass
                        else:
                            edge_params[i] = str(i)   

                    converter.write_out_results(status, node_params,edge_params)
                    print "\t\t\t [DONE]"
                    print "check",inputfile[0:-4]+".lgf"
                    
       
if __name__ == "__main__":
   main(sys.argv[1:])
