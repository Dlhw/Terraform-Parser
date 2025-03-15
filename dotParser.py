from cloud_config import *
import argparse

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

def consolidate_allResource(nodelist):
    indexToRemove = []
    for d in AWS_CONSOLIDATED_NODES:
        count = 0 
        prefix = str(list(d.keys())[0])
        for i in range(len(nodelist)):
            # if nodelist[i].split('.')[0] == prefix:
            #     print(f'equal: {nodelist[i]}')
            #     continue
            # else:
            #     if nodelist[i].startswith(prefix):
            #         print(nodelist[i])
            #         indexToRemove.append(i)
            
            if nodelist[i].startswith("module"):
                resource_name_list = nodelist[i].split(".")
                # if resource_name_list[2].startswith(prefix):
                if prefix in resource_name_list[2]:
                    if d[prefix]["resource_name"] not in nodelist:
                        count += 1 
                        nodelist[i] = d[prefix]["resource_name"]
                    elif count > 0:
                        indexToRemove.append(i)
            else:
                # if nodelist[i].startswith(prefix):
                if prefix in nodelist[i]:
                    if d[prefix]["resource_name"] not in nodelist:
                        count += 1 
                        nodelist[i] = d[prefix]["resource_name"]
                    elif count > 0:
                        indexToRemove.append(i)
    nodelist = rmv_elements(nodelist,indexToRemove)
    return nodelist

def consolidate_edges(head,tail,indexToRemove):
    for i in range(len(head)):
        for d in AWS_CONSOLIDATED_NODES:
            prefix = str(list(d.keys())[0])
            # if head[i].startswith(prefix):
            #     if head[i].split('.')[0] != prefix:
            #         indexToRemove.append(i)
            #         continue
            # if tail[i].startswith(prefix):
            #     if tail[i].split('.')[0] != prefix:
            #         indexToRemove.append(i)
            #         continue
            if head[i].startswith('module'):
                head_list = head[i].split('.')
                # if head_list[2].startswith(prefix):
                if prefix in head_list[2]:
                    head[i] = d[prefix]["resource_name"]
            if tail[i].startswith('module'):
                tail_list = tail[i].split('.')
                # if tail_list[2].startswith(prefix):
                if prefix in tail_list[2]:
                    tail[i] = d[prefix]["resource_name"]
            # if head[i].startswith(prefix):
            if prefix in head[i]:
                head[i] = d[prefix]["resource_name"]
            # if tail[i].startswith(prefix):
            if prefix in tail[i]:
                tail[i] = d[prefix]["resource_name"]
        if head[i] == tail[i]:
            indexToRemove.append(i)

def auto_annotation(allResource,head,tail):
    for node in allResource:
        for d in AWS_AUTO_ANNOTATIONS:
            prefix = list(d.keys())[0]
            if not node.startswith(prefix):
                continue
            extraNodes = d[prefix]["link"]
            direction = d[prefix]['arrow']
            for extra in extraNodes:
                if extra not in allResource:
                    allResource.append(extra)
                if direction.startswith('r'):
                    head.append(extra+"(Implied)")
                    tail.append(node+"(Implied)")
                else:
                    head.append(node+"(Implied)")
                    tail.append(extra+"(Implied)")

def auto_link(allResource,head,tail):
    for node in allResource:
        for d in AWS_AUTO_LINKS:
            prefix = list(d.keys())[0]
            if not node.startswith(prefix):
                continue
            linkNodes= d[prefix]["link"]
            direction = d[prefix]['arrow']
            for link in linkNodes:
                for s in allResource:
                    if not s.startswith(link):
                        continue
                    if direction.startswith('n'):
                        head.append(node+"(none)")
                        tail.append(link)

def fix_arrow_direction(head,tail):
    for i in range(len(head)):
        reverse = False
        if "Implied" in head[i] or "Implied" in tail[i]:
            # if implied, don't reverse, and change the name back to normal
            if "Implied" in head[i]:
                head[i] = head[i].split('(')[0]
            if "Implied" in tail[i]:
                tail[i] = tail[i].split('(')[0]
            continue
        if any(head[i].startswith(s) for s in AWS_REVERSE_ARROW_LIST ):
            reverse = not reverse  
        if any(tail[i].startswith(s) for s in AWS_REVERSE_ARROW_LIST):
            reverse = not reverse
        if reverse:
            temp = tail[i]
            tail[i] = head[i]
            head[i] = temp
    

def open_group(grp,fout):
    fout.write(f'subgraph \"cluster_{grp}\"')
    fout.write("{\n")
    fout.write(f"label = \"{grp}\";\n")

def close_group(fout):
    fout.write("}\n")

def add_element(element,fout):
    fout.write(f"\"{element}\" [shape = \"box\"];\n")

def rmv_elements(input_ls, indexToRemove):
    return [input_ls[i] for i in range(len(input_ls)) if i not in indexToRemove]

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

def node_with_parent(fout, node_width, node_height, node_id, node_type, node_x, node_y, parentNode, counter):
    if counter != 0:
        fout.write(",\n\t  ")
    fout.write("{\n\t\t")
    fout.write("\"style\":{\"width\":")
    fout.write(f"{node_width},\"height\":{node_height}")
    fout.write('},\n\t\t')

    fout.write(f"\"id\":\"{node_id}\",\n\t\t")

    fout.write(f"\"type\":\"{node_type}\",\n\t\t")

    fout.write("\"data\":{\"label\":")
    fout.write(f'\"{node_id}\"')
    fout.write('},\n\t\t')

    fout.write("\"position\":{\"x\":")
    fout.write(f"{node_x},\"y\":{node_y}")
    fout.write('},\n\t\t')

    fout.write(f"\"parentNode\":\"{parentNode}\"\n\t  ")

    fout.write("}")
    return counter + 1

def node_without_parent(fout, node_width, node_height, node_id, node_type, node_x, node_y, counter):
    if counter != 0:
        fout.write(",\n\t  ")
    fout.write("{\n\t\t")
    fout.write("\"style\":{\"width\":")
    fout.write(f"{node_width},\"height\":{node_height}")
    fout.write('},\n\t\t')

    fout.write(f"\"id\":\"{node_id}\",\n\t\t")

    fout.write(f"\"type\":\"{node_type}\",\n\t\t")

    fout.write("\"data\":{\"label\":")
    fout.write(f'\"{node_id}\"')
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

def parseDot(infile,outfile):
    text = []
    with open(infile,'r',encoding="utf-8") as fin: 
        for line in fin:
            line = line.strip()
            if line.startswith('\"[root]'):
                text.append(line.split('->',))
    allResource = []
    head = []
    tail = []
    provider =''
    # exclude = [ 
    #             'var',
    #             'root',
    #             'output',
    #             'data',
    #             'local',
    #             "aws_iam",
    #             "aws_route_table",
    #             "aws_network_acl",
    #             'aws_alb_target_group',
    #             "aws_key_pair",
    #             "aws_autoscaling",
    #             "aws_launch_configuration",
    #             "aws_db_instance",
    #             "aws_db_parameter_group",
    #             "aws_db_subnet_group",
    #             "aws_security_group",
    #             "aws_ec2_transit_gateway_route_table",
    #             "aws_cloudfront_origin_access_identity",
    #             "aws_route53_resolver_rule_association",
    #             "aws_route53_zone",
    #             "aws_eip",
    #             "aws_api_gateway_deployment",
    #             "aws_api_gateway_resource",
    #             "aws_api_gateway_stage",
    #             "aws_ec2_transit_gateway_vpc_ttachment_accepter",
    #             "aws_acm_certificate_validation"
    #         ]
    # for element in text:
    #     print(element)
    #     if len(element) ==1: # A node
    #         resource_name = element[0].split()[1]
    #         print(f'resource_name: {resource_name}\n')
    #         for implied in AWS_IMPLIED_CONNECTIONS:
    #             if implied in resource_name:
    #                 resource_name = AWS_IMPLIED_CONNECTIONS[implied]
    #         if any(resource_name.startswith(s) for s in exclude):
    #             continue
    #         elif resource_name.startswith("module"):
    #             resource_name = resource_name.split('.')[2] +"."+ resource_name.split('.')[3]
    #             allResource.append(resource_name)
    #         elif resource_name.startswith('provider'):
    #             if provider == '':
    #                 provider = resource_name.split("/")[2].split('\\')[0]
    #         else:
    #             allResource.append(resource_name)
    #     else: # An edge
    #         head_name = element[0].split()[1]
    #         tail_name = element[1].split()[1]
            
    #         for implied in AWS_IMPLIED_CONNECTIONS:
    #             if implied in head_name:
    #                 print(f'head_name: {head_name}\n')
    #                 head_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
    #             if implied in tail_name:
    #                 print(f'tail_name: {tail_name}\n')
    #                 tail_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
    #         if any(head_name.startswith(s) for s in exclude) or any(tail_name.startswith(s) for s in exclude):
    #             continue
    #         elif head_name.startswith("provider"):
    #             if provider == '':
    #                 provider = head_name.split("/")[2].split('\\')[0]
    #                 print(f'provider: {provider}\n')
    #         elif tail_name.startswith("provider"):
    #             if provider == '':
    #                 provider = tail_name.split("/")[2].split('\\')[0]
    #                 print(f'provider: {provider}\n')
    #         elif head_name.startswith('module'):
    #             head_name_resource = head_name.split('.')
    #             if len(head_name_resource) == 2 or head_name_resource[2] in exclude: #skip module.module_name
    #                 continue
    #             if tail_name.startswith('module'): #both modules
    #                 tail_name_resource = tail_name.split('.')
    #                 if tail_name_resource[2] in exclude:
    #                     continue
    #                 head.append(head_name_resource[2]+'.'+head_name_resource[3])
    #                 tail.append(tail_name_resource[2]+'.'+tail_name_resource[3])
    #             else: #only head is module and tail is valid
    #                 head.append(head_name_resource[2]+'.'+head_name_resource[3])
    #                 tail.append(tail_name)

    #         elif tail_name.startswith('module'): ## head isn't a module
    #             tail_name_resource = tail_name.split('.')
    #             if len(tail_name_resource) ==2 or tail_name_resource[2] in exclude: #skip module.module_name
    #                 continue
    #             head.append(head_name)
    #             tail.append(tail_name_resource[2]+'.'+tail_name_resource[3])
    #         else: # not module, provider, and not in exclude list
    #             head.append(head_name)
    #             tail.append(tail_name)

    for element in text:
        print(element)
        if len(element) ==1: # A node
            resource_name = element[0].split()[1]
            resource_type = resource_name.split('.')[0]
            for implied in AWS_IMPLIED_CONNECTIONS:
                if implied in resource_name:
                    resource_name = AWS_IMPLIED_CONNECTIONS[implied]
            if resource_name.startswith("module"):
                resource_name_ls = resource_name.split('.')
                resource_type = resource_name_ls[2]
                if resource_type in INCLUDE or any(n in resource_type for n in SINGLE_NODES):
                    allResource.append(resource_name)
            elif resource_name.startswith('provider'):
                if provider == '':
                    temp = resource_name.split("/")[2].split('\\')[0]
                    if temp in INCLUDE:
                        provider = temp
            elif resource_type in INCLUDE or any(n in resource_type for n in SINGLE_NODES):
                allResource.append(resource_name)
        else: # An edge
            head_name = element[0].split()[1]
            tail_name = element[1].split()[1]
            for implied in AWS_IMPLIED_CONNECTIONS:
                if implied in head_name:
                    head_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
                    print(f'head_name: {head_name}\n')
                if implied in tail_name:
                    tail_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
                    print(f'tail_name: {tail_name}\n')
            head_type = head_name.split('.')[0]
            tail_type = tail_name.split('.')[0]
            if head_name.startswith("provider"):
                if provider == '':
                    provider = head_name.split("/")[2].split('\\')[0]
                    print(f'provider: {provider}\n')
            elif tail_name.startswith("provider"):
                if provider == '':
                    provider = tail_name.split("/")[2].split('\\')[0]
                    print(f'provider: {provider}\n')
            elif head_name.startswith('module'):
                head_name_resource = head_name.split('.')
                # print(head_name)
                if len(head_name_resource) == 2 or (head_name_resource[2] not in INCLUDE and not any(n in head_name_resource[2] for n in SINGLE_NODES)): #skip module.acm (close)
                    continue
                if tail_name.startswith('module'): #both modules
                    tail_name_resource = tail_name.split('.')
                    if len(tail_name_resource) == 2 or (tail_name_resource[2] not in INCLUDE and not any(n in tail_name_resource[2] for n in SINGLE_NODES)): #skip module.acm (close)
                        continue
                    head.append(head_name)
                    tail.append(tail_name)
                else: #only head is module and tail is not
                    # print(f'look here: {tail_name}')
                    if tail_name not in INCLUDE and not any(n in tail_name for n in SINGLE_NODES) :
                        continue
                    head.append(head_name)
                    tail.append(tail_name)
                    

            elif tail_name.startswith('module'): ## head isn't a module
                tail_name_resource = tail_name.split('.')
                if len(tail_name_resource) ==2 or (tail_name_resource[2] not in INCLUDE and not any(n in tail_name_resource[2] for n in SINGLE_NODES)) or (head_name not in INCLUDE and not any(n in head_name for n in SINGLE_NODES)): #skip module.module_name
                    continue
                # print(f'here head: {head_name}')
                # print(f'here tail: {tail_name}')
                head.append(head_name)
                tail.append(tail_name)

            elif (head_type in INCLUDE or any(n in head_type for n in SINGLE_NODES)) and (tail_type in INCLUDE or any(n in tail_type for n in SINGLE_NODES)) :  # not module, provider, and in include list
                print()
                print('elif')
                head.append(head_name)
                tail.append(tail_name)
                print(f'headd: {head_name}')
                print(f'taill: {tail_name}')
                print()

                

    # print(f'\nallResources1: {allResource}\n')
    print(f'head1: {head}\n')
    print(f'tail1: {tail}\n')

    #Add auto annotations
    auto_annotation(allResource,head,tail)
    print(f'\nallResources2: {allResource}\n')
    print(f'head2: {head}\n')
    print(f'tail2: {tail}\n')

    #add auto links
    auto_link(allResource,head,tail)

    # consolidating nodes, not all resource block will appear on the diagram
    allResource = consolidate_allResource(allResource)
    print(f'\nallResources3: {allResource}\n')
    
    #fix directions of arrows, removes "implied"
    fix_arrow_direction(head,tail)
    print(f'head3: {head}\n')
    print(f'tail3: {tail}\n')

    # consolidate edges
    indexToRemove = []
    consolidate_edges(head,tail,indexToRemove)
    # remove redundant connections doesnt remove duplicate connections
    head = rmv_elements(head,indexToRemove)
    tail = rmv_elements(tail,indexToRemove)

    print(f'head4: {head}\n')
    print(f'tail4: {tail}\n')



    grpResource = []
    outerResource = []
    edgeResource = []
    indivResource = []
    grping = dict()

    # sorting resources         
    for element in allResource:
        element_check = element
        if element.startswith("module"):
            element_check = element.split('.')[2]
        if any(element_check == s for s in AWS_GROUP_NODES):
            grpResource.append(element)
        elif any(element_check.startswith(s) for s in AWS_OUTER_NODES):
            outerResource.append(element)
        elif any(element_check.startswith(s) for s in AWS_EDGE_NODES):
            edgeResource.append(element)
        #Add group shared services 
        elif any(element_check.startswith(s) for s in AWS_SHARED_SERVICES):
            if len(grping) == 0:
                grping["SS.Shared_Services"] = [element]
            else:
                grping["SS.Shared_Services"].append(element)
        else:
            indivResource.append(element)

    print(f'grp: {grpResource}\n')
    print(f'outer: {outerResource}\n')
    print(f'edge: {edgeResource}\n')
    print(f'indiv: {indivResource}\n')
    print(f'allResources: {allResource}\n')
    indexToRemove = []
    grpedNodes = []
    subGroups = []

    # for connections that represent grouping, remove them from head and tail
    for prefix in AWS_GROUP_NODES:
        for grp in grpResource:
            grp_check = grp
            if grp.startswith('module'):
                grp_check = grp.split('.')[2]
            if grp_check.startswith(prefix):
                grping[grp]=[]
                if len(head) != 0:
                    for i in range(len(tail)):
                        if tail[i] == grp:
                            if head[i] not in grpedNodes:
                                if head[i] in grpResource:
                                    subGroups.append(head[i])
                                grping[grp].append(head[i])
                                grpedNodes.append(head[i])
                                indexToRemove.append(i)
                                continue
                            else:
                                indexToRemove.append(i)
                                continue

                    tail = rmv_elements(tail,indexToRemove)
                    head = rmv_elements(head,indexToRemove)
                    indexToRemove = []

    print(f'subgraph: {subGroups}\n')
    print(f'grping: {grping}\n')
    # print(f"grpedNodes: {grpedNodes}\n")
    # print(f'Processed head: {head}\n')
    # print(f'Processed tail: {tail}\n')
    
    # use of dictionary(edges) to remove duplicate connections
    edges = dict()
    for i in range(len(tail)):
        if head[i] not in edges:
            edges[head[i]] = [tail[i]]
        else:
            if tail[i] not in edges[head[i]]:
                edges[head[i]].append(tail[i])

    # print(f'head5: {head}\n')
    # print(f'tail5: {tail}\n')




    

    #remove group nodes from indiv
    indivResource = [indivResource[i] for i in range(len(indivResource)) if indivResource[i] not in grpedNodes]  
    print(f'indiv after removal of group nodes: {indivResource}\n')
    print(f'connections: {edges}\n')

    drawn =[]
    count = []

    #drawing dot file
    with open(outfile,'w', encoding='utf-8') as fout:
        fout.write("digraph {\ncompound = true;\n") #header
        # drawing outerNodes #
        if len(outerResource) != 0:
            for element in outerResource:
                fout.write(f"\"{element}\" [shape = \"box\"];\n")
        # draw connections #
        for element in edges:
            size = len(edges[element])
            if "none" not in element:
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
            else:
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
        # drawing provider #
        open_group(provider,fout)
        fout.write("labeljust=l;\n")
        # drawing edgeNode #
        for element in edgeResource:
            add_element(element,fout)
        # drawing nodes without grps #
        if len(indivResource) != 0: 
            for element in indivResource:
                add_element(element,fout)
        # drawing groupsNodes #
        for grp in grping:
            if grp not in drawn:
                draw_subGrp(grping,fout,grp,subGroups,drawn,count)
        # close provider #
        close_group(fout)
        # close digraph #
        close_group(fout)

    #change outfile name to json
    outfile = outfile.split(".dot")
    outfile = outfile[0]+".json"

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
            counter = node_without_parent(fout,node_width,node_height,outerNode,node_type,node_x,node_y,counter)
            node_x = mvNodeRight(node_width,node_x)
        # drawing provider #
        x = initial_x
        y = mvNodeDown(node_height,initial_y) 
        counter = node_without_parent(fout,group_width,group_height,provider,node_type,x,y,counter)
        # drawing edgeNode #
        x = 0
        y = node_height
        for edgeNode in edgeResource:
            counter = node_with_parent(fout,node_width,node_height,edgeNode,node_type,x,y,provider,counter)
            y = mvNodeDown(node_height,y)
        # drawing nodes without grp inside aws #
        for indivNode in indivResource:
            counter = node_with_parent(fout,node_width,node_height,indivNode,node_type,x,y,provider,counter)
            y = mvNodeDown(node_height,y)
        drawn =[]
        # drawing groupsNodes #
        group_x = group_width
        group_y = 0
        for grp in grping:
            if grp not in drawn:
                counter = node_with_parent(fout,group_width,group_height,grp,node_type,group_x,group_y,provider,counter)
                group_x = mvNodeRight(group_width,group_x)
                if len(grping[grp]) != 0:
                    x = 0
                    y = node_height
                    for node in grping[grp]:
                        counter = node_with_parent(fout,node_width,node_height,node,node_type,x,y,grp,counter)
                        drawn.append(node)
                        y = mvNodeDown(node_height,y)
            else:
                if len(grping[grp]) != 0:
                    x = node_width
                    y = 0
                    for node in grping[grp]:
                        counter = node_with_parent(fout,node_width,node_height,node,node_type,x,y,grp,counter)
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

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Convert Dot graph to diagram')
    parser.add_argument('-i', dest='infile',help='input file',type=str, required=True)
    parser.add_argument('-o', dest='outfile',help='output file',type=str, default="output.dot")
    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile
    parseDot(infile,outfile)