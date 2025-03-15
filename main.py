from cloud_config import *
from helperFunctions import *
from drawFunctions import *
import argparse
import glob
import os
import ast
import re
import hcl2

def recursive_dict_processer(dictionary,tfStorage,path=[]):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # If the value is a dictionary, call the function recursively
            recursive_dict_processer(value,tfStorage,path.append(key))
        else:
            # If the value is not a dictionary
            newArgs = processArgs(value,tfStorage)
            update_nested_dict(tfStorage,path,newArgs)
        
def is_string_a_list(input_string):
    try:
        result = ast.literal_eval(input_string)
        if isinstance(result,list):
            return result
        else:
            return input_string
    except (SyntaxError, ValueError):
        
        return input_string

def processArgs(argument:str, tfStorage:dict):
    temp = argument.split("*")
    output = []
    for e in temp:
        e = e.split("=")
        if len(e) == 2:
            if not e[-1].strip().replace(",","").isdigit(): #not a digit/number
                if "\'" not in e[-1] and "\"" not in e[-1] and "." in e[-1]: # if there's inverted commas, it's a string, else it's a variable referencing another value if there's a '.'
                    keys = e[-1].strip().replace(',','comma' ).split('.')
                    comma = False
                    if "comma" in keys[-1]:
                        comma = True
                    if keys[0] == "local":
                        newkeys,index = processKeys(keys)
                        if index != None:
                            args = getArgs(newkeys,tfStorage)
                            if comma:
                                e[-1] = args[index]+','
                            else:
                                e[-1] = args[index]
                        else:
                            args = str(getArgs(newkeys,tfStorage))
                            if comma:
                                e[-1] = args + ','
                            else:
                                e[-1] = args
        e = "= ".join(e)
        output.append(e)
    output = "*".join(output)
    return output

def processMod(args,td):
    os.chdir(td)
    td = os.path.normpath(os.path.join(td,args['source'].strip().replace('\"','')))
    # print(td)
    modDict = create_tf_dict3(td)

    # argsToDict not good enough to handle all arguments 

    # print(keys)
    # new_keys = processKeys(keys,ModModified=True)
    # print(new_keys)
    # old_args = getArgs(new_keys[2:],modDict)
    # new_args = argsToDict(old_args)
    # update_nested_dict(modDict,new_keys,new_args)

    # trying recursion

    # if "module" in keylist:
    #     newkeys = processKeys(keys)
    #     args = getArgs(newkeys,modDict)
    #     newArgs = processArgs(args,modDict)
    #     newMod = processMod(newArgs,td)
    #     copy = newkeys.copy() # copy cause update_nested_dict changes the list
    #     update_nested_dict(tfStorage,copy,newMod)

    args.update(modDict)
    
    return args
            
def listToDict(tfStorage:dict):
    for k in tfStorage:
        if isinstance(tfStorage[k],list):
            if len(tfStorage[k]) != 1:
                temp ={}
                for element in tfStorage[k]:
                    temp = merge(temp,element)
                tfStorage[k] = temp
            else:
                tfStorage[k] = tfStorage[k][0]
    return tfStorage

def create_tf_dict3(td):
    os.chdir(td)
    oneLine = ''
    for tfFile in glob.glob("*.tf"):
        with open(tfFile, 'r') as f:
            for line in f:
                oneLine += line
    tfStorage =  hcl2.loads(oneLine)
    return tfStorage

def parseDot(infile,outfile,td):
    text = []
    # open graph.dot file
    with open(infile,'r',encoding="utf-8") as fin: 
        for line in fin:
            line = line.strip()
            if line.startswith('\"[root]'):
                text.append(line.split('->',))

    allResource = []
    head = []
    tail = []
    provider =''

    # exclude(text,allResource,head,tail,provider)
    
    provider = include(text,allResource,head,tail,provider)

    #Add auto annotations
    auto_annotation(allResource,head,tail)

    #add auto links
    auto_link(allResource,head,tail)

    # consolidating nodes, not all resource block will appear on the diagram
    allResource = consolidate_allResource(allResource)
    
    #fix directions of arrows, removes "implied"
    fix_arrow_direction(head,tail)

    # consolidate edges
    indexToRemove = []
    consolidate_edges(head,tail,indexToRemove)

    # remove redundant connections doesnt remove duplicate connections, if rmv_elements inside consolidate_edges, error is thrown.
    head = rmv_elements(head,indexToRemove)
    tail = rmv_elements(tail,indexToRemove)
   
    grpResource = []
    outerResource = []
    edgeResource = []
    indivResource = []
    grping = dict()

    # sorting resources  
    sorting(allResource,grpResource,outerResource,edgeResource,grping,indivResource)

    indexToRemove = []
    grpedNodes = []
    subGroups = []

    # for connections that represent grouping, remove them from head and tail
    head, tail = rmvGrpNodesFromEdges(grpResource,grpedNodes,grping,subGroups,head,tail,indexToRemove)

    # use of dictionary(edges) to remove duplicate connections
    edges = dict()
    rmvDuplicateEdges(edges,head,tail)

    # remove group nodes from indiv
    indivResource = [indivResource[i] for i in range(len(indivResource)) if indivResource[i] not in grpedNodes]

    # draw dotGraph
    draw_dotGraph(outfile,outerResource,provider,edgeResource,indivResource,grping,subGroups,edges)

    # change outfile name to json
    outfile = outfile.split(".dot")
    outfile = outfile[0]+".json"

    #getting arguments

    resourceToSearch = []
    for resource in allResource:
        if "." in resource:
            resourceToSearch.append(resource)

    tfStorage = create_tf_dict3(td)
    tfStorage = listToDict(tfStorage)

    # print(tfStorage['locals'])
    # for k in tfStorage['locals']:
    #     print(k)
    

    # print(tfStorage['provider']['aws'])
    # for resource in resourceToSearch:
    #     keys = resource.split('.')
    #     copy = keys.copy()
    #     keys = processKeys(keys)
    #     print(keys)
    #     args = getArgs(keys,tfStorage)
    #     # newArgs = processArgs(args,tfStorage)
    #     if keys[0] == "module":
    #         args = processMod(args,td)
    #     print(args)
    #     update_nested_dict(tfStorage,keys,args)

    current_directory = os.path.dirname(os.path.abspath(__file__)) # get directory where this script is located
    os.chdir(current_directory)

    # draw reactflow json
    draw_reactJson(outfile,outerResource,provider,edgeResource,indivResource,grping,edges,tfStorage)

    
    
# if __name__ == '__main__':
#     parser=argparse.ArgumentParser(description='Convert Dot graph to diagram')
#     parser.add_argument('-i', dest='infile',help='input dot file',type=str, required=True)
#     parser.add_argument('-o', dest='outfile',help='output dot file',type=str, default="output.dot")
#     parser.add_argument('-td', dest='td',help='terraform directory',type=str, required=True)
#     args = parser.parse_args()
#     infile = args.infile
#     outfile = args.outfile
#     td = args.td
#     parseDot(infile,outfile,td)


#     ## dict = {
#     #           provider : provider_name :value,
#     #           terraform : args (1 string),
#     #           variables : variable_name1 :value,
#     #                       variable_name2 :value,
#     #                       .
#     #                       .
#     #           data: data_type : data_name: args (1 string),
#     #           locals : args (1 string) --> locals : local_var_name_1: value
#     #                                                 local_var_name_2: value
#     #                                                 .
#     #                                                 .
#     #                                                 . 
#     #           resource: resource_type: resource_name : args(1 string),
#     #           module : module_name : args(1 string) --> module: module_name: arg_name1 : value
#     #                                                                          .
#     #                                                                          .
#     #                                                                          .
#     #                                                                          arg_name_x: value
#     #                                                                          provider:
#     #                                                                          terraform:
#     #                                                                          variable:
#     #                                                                          data:
#     #                                                                          locals:
#     #                                                                          resource:
#     #                                                                          (if any) module: --> arg_name1 : value
#     #                                                                                              .
#     #                                                                                              .
#     #                                                                                              .
#     #                                                                                               arg_name_x: value
#     #                                                                                               provider:
#     #                                                                                               terraform:
#     #                                                                                               variable:
#     #                                                                                               data:
#     #                                                                                               locals:
#     #                                                                                               resource: 
#     #  
#     #
#     #
#     #
#     # }
# #

# #


    
