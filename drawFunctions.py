from helperFunctions import *

def drawArgs(keys:list,fout,tfStorage):
    for k in keys:
        if k !=keys[-1]:
            fout.write(f'\"{k}\":\"{tfStorage[k]}\",\n\t\t\t\t')
        else:
            fout.write(f'\"{k}\":\"{tfStorage[k]}\"\n\t\t\t\t')


def draw_subGrp(grping,fout,subGrp, subGrps, drawn,count):
    open_group(subGrp,fout)
    if len(grping[subGrp]) != 0:
        for node in grping[subGrp]:
            if node in subGrps:
                draw_subGrp(grping,fout,node,subGrps,drawn,count)
            else:
                fout.write(f"\"{node}\" [shape = box];\n")
    else:
        fout.write(f"invis_node{len(count)} [style =invis]\n")
        count.append(1)
    close_group(fout)
    drawn.append(subGrp)

def open_group(grp,fout):
    fout.write(f'subgraph \"cluster_{grp}\"')
    fout.write("{\n")
    fout.write(f"label = \"{grp}\";\n")

def close_group(fout):
    fout.write("}\n")

def add_element(element,fout):
    fout.write(f"\"{element}\" [shape = \"box\"];\n")

def draw_from_list(ls,fout):
    if len(ls) != 0:
        for element in ls:
            fout.write(f"\"{element}\" [shape = \"box\"];\n")

def mvNodeDown(node_height, node_y):
    node_y += node_height
    return node_y

def mvNodeUp(node_height, node_y):
    node_y -= node_height
    return node_y

def mvNodeRight(node_width, node_x):
    node_x += node_width
    return node_x

def mvNodeLeft(node_width, node_x):
    node_x -= node_width
    return node_x

def node_with_parent(fout, node_width, node_height, node_id, node_type, node_x, node_y, parentNode, counter,tfStorage):
    if counter != 0:
        fout.write(",\n\t  ")
    fout.write("{\n\t\t")
    fout.write("\"style\":{\"width\":")
    fout.write(f"{node_width},\"height\":{node_height}")
    fout.write('},\n\t\t')

    fout.write(f"\"id\":\"{node_id}\",\n\t\t")

    fout.write(f"\"type\":\"{node_type}\",\n\t\t")

    fout.write("\"data\":{\"label\":")
    nested_keys = []
    if "." in node_id:
        fout.write(f'"{node_id}",\n\t\t\t\t')
        keys = node_id.split('.')
        newkeys = processKeys(keys)
        args = getArgs(newkeys,tfStorage)
        keys_in_nested_dict(args,nested_keys)
        drawArgs(nested_keys,fout,args)
    else:
        fout.write(f'"{node_id}"')
    fout.write('},\n\t\t')

    fout.write("\"position\":{\"x\":")
    fout.write(f"{node_x},\"y\":{node_y}")
    fout.write('},\n\t\t')

    fout.write(f"\"parentNode\":\"{parentNode}\"\n\t  ")

    fout.write("}")
    return counter + 1

def node_without_parent(fout, node_width, node_height, node_id, node_type, node_x, node_y, counter,tfStorage,provider=False):
    if counter != 0:
        fout.write(",\n\t  ")
    fout.write("{\n\t\t")
    fout.write("\"style\":{\"width\":")
    fout.write(f"{node_width},\"height\":{node_height}")
    fout.write('},\n\t\t')

    fout.write(f"\"id\":\"{node_id}\",\n\t\t")

    fout.write(f"\"type\":\"{node_type}\",\n\t\t")

    fout.write("\"data\":{\"label\":")
    nested_keys =[]
    if provider:
        fout.write(f'"{node_id}",\n\t\t\t\t')
        keys_in_nested_dict(tfStorage["provider"][node_id],nested_keys)
        drawArgs(nested_keys,fout,tfStorage["provider"][node_id])
    elif "." in node_id:
        fout.write(f'"{node_id}",\n\t\t\t\t')
        keys = node_id.split('.')
        newkeys = processKeys(keys)
        args = getArgs(newkeys,tfStorage)
        keys_in_nested_dict(args,nested_keys)
        drawArgs(nested_keys,fout,args)

    else:
        fout.write(f'"{node_id}"')
    fout.write('},\n\t\t')

    fout.write("\"position\":{\"x\":")
    fout.write(f"{node_x},\"y\":{node_y}")
    fout.write('}\n\t  ')

    fout.write("}")
    return counter + 1

def drawEdges(fout, source, target, edgeCounter):
    if edgeCounter != 0:
        fout.write(",\n\t  ")
    if "none" in source:
        source = source.split("(")[0]
    fout.write("{\n\t\t")
    fout.write(f"\"id\":\"{source}-{target}\",\n\t\t")

    fout.write(f"\"source\":\"{source}\",\n\t\t")

    fout.write(f"\"target\":\"{target}\"\n\t  ")
    fout.write("}")
    return edgeCounter + 1

def draw_dotGraph(outfile,outerResource,provider,edgeResource,indivResource,grping,subGroups,edges):
    drawn =[]
    count = []
    with open(outfile,'w', encoding='utf-8') as fout:
        fout.write("digraph {\ncompound = true;\n") #header
        # drawing outerNodes #
        draw_from_list(outerResource,fout) 
        # draw connections #
        for element in edges:
            size = len(edges[element])
            if "none" not in element:
                draw_directedEdge(fout,size,edges,element)
            else:
                draw_nonDirectedEdges(fout,size,edges,element)

        # drawing provider #
        open_group(provider,fout)
        fout.write("labeljust=l;\n")

        # drawing edgeNode #
        draw_from_list(edgeResource,fout)

        # drawing nodes without grps 
        draw_from_list(indivResource,fout)
        
        # drawing groupsNodes #
        for grp in grping:
            if grp not in drawn:
                draw_subGrp(grping,fout,grp,subGroups,drawn,count)

        # close provider #
        close_group(fout)
        # close digraph #
        close_group(fout)

def draw_nonDirectedEdges(fout,size, edges,element):
    updatedElement = element.split("(")[0]
    if size >1: # there's more than 1 link from the same node
        fout.write(f'\"{updatedElement}\"->')
        fout.write('{')
        for i in range(size):
            if i != size-1:
                fout.write(f'\"{edges[element][i]}\",')
            else:
                fout.write(f'\"{edges[element][i]}\"[dir=none]')
                fout.write('};\n')
    else:
        fout.write(f'\"{updatedElement}\"->\"{edges[element][0]}\"[dir=none];\n')

def draw_directedEdge(fout,size,edges,element):
    if size >1: # there's more than 1 link from the same node
        fout.write(f'\"{element}\"->')
        fout.write('{')
        for i in range(size):
            if i != size-1:
                fout.write(f'\"{edges[element][i]}\",')
            else:
                fout.write(f'\"{edges[element][i]}\"')
                fout.write('};\n')
    else:
        fout.write(f'\"{element}\"->\"{edges[element][0]}\";\n')

def draw_reactJson(outfile,outerResource,provider,edgeResource,indivResource,grping,edges,tfStorage):
    #set some reactflow json params
    initial_x = 50
    initial_y = 50
    node_width = 150
    node_height = 36
    node_x=initial_x
    node_y=initial_y
    node_type = "default"
    group_width = 200
    group_height = 200
    counter = 0
    # making json file
    with open(outfile,'w', encoding='utf-8') as fout:
        fout.write("{\n\t\"nodes\":[\n\t  ")

        # draw outerNodes #
        for outerNode in outerResource:
            print(outerNode)
            counter = node_without_parent(fout,node_width,node_height,outerNode,node_type,node_x,node_y,counter,tfStorage)
            node_x = mvNodeRight(node_width,node_x)

        # drawing provider #
        x = initial_x
        y = mvNodeDown(node_height,initial_y) 
        counter = node_without_parent(fout,group_width,group_height,provider,node_type,x,y,counter,tfStorage,True)

        # drawing edgeNode #
        x = 0
        y = node_height
        for edgeNode in edgeResource:
            counter = node_with_parent(fout,node_width,node_height,edgeNode,node_type,x,y,provider,counter,tfStorage)
            y = mvNodeDown(node_height,y)

        # drawing nodes without grp inside aws #
        for indivNode in indivResource:
            counter = node_with_parent(fout,node_width,node_height,indivNode,node_type,x,y,provider,counter,tfStorage)
            y = mvNodeDown(node_height,y)

        drawn =[]

        # drawing groupsNodes #
        group_x = group_width
        group_y = 0
        for grp in grping:
            if grp not in drawn:
                counter = node_with_parent(fout,group_width,group_height,grp,node_type,group_x,group_y,provider,counter,tfStorage)
                group_x = mvNodeRight(group_width,group_x)
                if len(grping[grp]) != 0:
                    x = 0
                    y = node_height
                    for node in grping[grp]:
                        counter = node_with_parent(fout,node_width,node_height,node,node_type,x,y,grp,counter,tfStorage)
                        drawn.append(node)
                        y = mvNodeDown(node_height,y)
            else:
                if len(grping[grp]) != 0:
                    x = node_width
                    y = 0
                    for node in grping[grp]:
                        counter = node_with_parent(fout,node_width,node_height,node,node_type,x,y,grp,counter,tfStorage)
                        drawn.append(node)
                        x = mvNodeRight(node_width,x)
        fout.write("\n\t]")
        
        # drawing edges #        
        if len(edges) != 0:
            edgeCounter = 0
            fout.write(',\n\t')
            fout.write("\"edges\":[\n\t  ")
            for source in edges:
                for target in edges[source]:
                    edgeCounter = drawEdges(fout, source, target, edgeCounter)
            fout.write("\n\t]")
            # insert viewport #
            fout.write(",\n\t\"viewport\":{\n\t  ")
            fout.write(f"\"x\":0,\n\t  ") 

            fout.write(f"\"y\":0,\n\t  ")

            fout.write(f"\"zoom\":1\n\t")
            fout.write("}")
        fout.write('\n}')
