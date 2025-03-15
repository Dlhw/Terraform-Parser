from cloud_config import *

def keys_in_nested_dict(dictionary,keys, prefix=''):
    for key, value in dictionary.items():
        keys.append(key)
        if isinstance(value, dict):
            keys_in_nested_dict(value,keys, prefix=f"{prefix}{key}.")

def exclude(fin,allResource,head,tail,provider):
    for element in fin:
        if len(element) ==1: # A node
            resource_name = element[0].split()[1]
            for implied in AWS_IMPLIED_CONNECTIONS:
                if implied in resource_name:
                    resource_name = AWS_IMPLIED_CONNECTIONS[implied]
            if any(resource_name.startswith(s) for s in exclude):
                continue
            elif resource_name.startswith("module"):
                resource_name = resource_name.split('.')[2] +"."+ resource_name.split('.')[3]
                allResource.append(resource_name)
            elif resource_name.startswith('provider'):
                if provider == '':
                    provider = resource_name.split("/")[2].split('\\')[0]
            else:
                allResource.append(resource_name)
        else: # An edge
            head_name = element[0].split()[1]
            tail_name = element[1].split()[1]
            for implied in AWS_IMPLIED_CONNECTIONS:
                if implied in head_name:
                    head_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
                if implied in tail_name:
                    tail_name = AWS_IMPLIED_CONNECTIONS[implied]+"(Implied)"
            if any(head_name.startswith(s) for s in exclude) or any(tail_name.startswith(s) for s in exclude):
                continue
            elif head_name.startswith("provider"):
                if provider == '':
                    provider = head_name.split("/")[2].split('\\')[0]
            elif tail_name.startswith("provider"):
                if provider == '':
                    provider = tail_name.split("/")[2].split('\\')[0]
            elif head_name.startswith('module'):
                head_name_resource = head_name.split('.')
                if len(head_name_resource) == 2 or head_name_resource[2] in exclude: #skip module.module_name
                    continue
                if tail_name.startswith('module'): #both modules
                    tail_name_resource = tail_name.split('.')
                    if tail_name_resource[2] in exclude:
                        continue
                    head.append(head_name_resource[2]+'.'+head_name_resource[3])
                    tail.append(tail_name_resource[2]+'.'+tail_name_resource[3])
                else: #only head is module and tail is valid
                    head.append(head_name_resource[2]+'.'+head_name_resource[3])
                    tail.append(tail_name)
            elif tail_name.startswith('module'): ## head isn't a module
                tail_name_resource = tail_name.split('.')
                if len(tail_name_resource) ==2 or tail_name_resource[2] in exclude: #skip module.module_name
                    continue
                head.append(head_name)
                tail.append(tail_name_resource[2]+'.'+tail_name_resource[3])
            else: # not module, provider, and not in exclude list
                head.append(head_name)
                tail.append(tail_name)

def include(fin,allResource,head,tail,provider):
    for element in fin:
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
            if provider =='':
                if head_name.startswith("provider"):
                    provider = head_name.split("/")[2].split('\\')[0]
                    print(f'provider: {provider}\n')
                elif tail_name.startswith("provider"):
                    provider = tail_name.split("/")[2].split('\\')[0]
                    print(f'provider: {provider}\n')
            elif head_name.startswith('module'):
                head_name_resource = head_name.split('.')
                if len(head_name_resource) == 2 or (head_name_resource[2] not in INCLUDE and not any(n in head_name_resource[2] for n in SINGLE_NODES)): #skip module.acm (close)
                    continue
                if tail_name.startswith('module'): #both modules
                    tail_name_resource = tail_name.split('.')
                    if len(tail_name_resource) == 2 or (tail_name_resource[2] not in INCLUDE and not any(n in tail_name_resource[2] for n in SINGLE_NODES)): #skip module.acm (close)
                        continue
                    head.append(head_name)
                    tail.append(tail_name)
                else: #only head is module and tail is not
                    if tail_name not in INCLUDE and not any(n in tail_name for n in SINGLE_NODES) :
                        continue
                    head.append(head_name)
                    tail.append(tail_name)
                    

            elif tail_name.startswith('module'): ## head isn't a module
                tail_name_resource = tail_name.split('.')
                if len(tail_name_resource) ==2 or (tail_name_resource[2] not in INCLUDE and not any(n in tail_name_resource[2] for n in SINGLE_NODES)) or (head_name not in INCLUDE and not any(n in head_name for n in SINGLE_NODES)): #skip module.module_name
                    continue
                head.append(head_name)
                tail.append(tail_name)

            elif (head_type in INCLUDE or any(n in head_type for n in SINGLE_NODES)) and (tail_type in INCLUDE or any(n in tail_type for n in SINGLE_NODES)) :  # not module, provider, and in include list
                head.append(head_name)
                tail.append(tail_name)
    return provider

def rmvGrpNodesFromEdges(grpResource,grpedNodes,grping,subGroups,head,tail,indexToRemove):
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
    return head,tail

def rmvDuplicateEdges(edges,head,tail):
    for i in range(len(tail)):
        if head[i] not in edges:
            edges[head[i]] = [tail[i]]
        else:
            if tail[i] not in edges[head[i]]:
                edges[head[i]].append(tail[i])

def sorting(allResource,grpResource,outerResource,edgeResource,grping,indivResource):
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
                grping["SS_Shared_Services"] = [element]
            else:
                grping["SS_Shared_Services"].append(element)
        else:
            indivResource.append(element)

def consolidate_allResource(nodelist):
    indexToRemove = []
    for d in AWS_CONSOLIDATED_NODES:
        count = 0 
        prefix = str(list(d.keys())[0])
        for i in range(len(nodelist)):
            if nodelist[i].startswith("module"):
                resource_name_list = nodelist[i].split(".")
                if prefix in resource_name_list[2]:
                    if d[prefix]["resource_name"] not in nodelist:
                        count += 1 
                        nodelist[i] = d[prefix]["resource_name"]
                    elif count > 0:
                        indexToRemove.append(i)
            else:
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
            if head[i].startswith('module'):
                head_list = head[i].split('.')
                if prefix in head_list[2]:
                    head[i] = d[prefix]["resource_name"]
            if tail[i].startswith('module'):
                tail_list = tail[i].split('.')
                if prefix in tail_list[2]:
                    tail[i] = d[prefix]["resource_name"]
            if prefix in head[i]:
                head[i] = d[prefix]["resource_name"]
            if prefix in tail[i]:
                tail[i] = d[prefix]["resource_name"]
        if head[i] == tail[i]:
            indexToRemove.append(i)

# This creates nodes to link 
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

# This searches for nodes in the resource list to draw links
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
    
def rmv_elements(input_ls, indexToRemove):
    return [input_ls[i] for i in range(len(input_ls)) if i not in indexToRemove]

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else: # same key different value
                raise Exception('Conflict at ' +'.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def processKeys(keys,ModModified=False):
    if keys[0] == "module":
        new_keys = processKeys(keys[2:])
        if not ModModified:
            while len(keys) >2:
                keys.pop()
        else:
            keys = keys[0:2] + new_keys
        return keys
    elif keys[0] == "data":
        while len(keys) >3:
            keys.pop()
        return keys
    elif keys[0] == "var":
        keys[0] = 'variable'
        while len(keys) >2:
            keys.pop()
        return keys
    elif keys[0] == 'local':
        index = None
        keys[0] = 'locals'
        if '[' in keys[-1]:  # '[' indicates a list in the value 
            ls = keys[-1].split('[')
            keys[-1] = ls[0]
            index = int(ls[1][0])
        while len(keys) >2:
            keys.pop()
        return keys , index
    else:
        keys.insert(0,"resource")
        while len(keys) >3:
            keys.pop()
        return keys

def getArgs(keys:list,tfStorage:dict):
    for key in keys:
        tfStorage = tfStorage[key]
    return tfStorage   

def update_nested_dict(d:dict, keys:list, new_value):
    if len(keys) == 1:
        d[keys[0]] = new_value
        return
    current_key = keys.pop(0)
    update_nested_dict(d[current_key], keys, new_value)

