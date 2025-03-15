import os
import glob
import re
from helperFunctions import *
def not_within_range(reference_range, check_range):
    if check_range[0] > reference_range[1]:
        return True
    elif check_range[1] < reference_range[0]:
        return True
    else:
        return False

def create_tf_dict(td):
    os.chdir(td)
    oneLine=''
    for tfFile in glob.glob("*.tf"):
        with open(tfFile, 'r') as f:
            for line in f:
                line = line.strip()
                oneLine += "*"+line  #add "*" to handle comments in the code, doesn't handle curly brackets{} in comments
    print(oneLine)
    tfStorage = {}
    end = len(oneLine)
    pointer = 0 
    opened = 0 # for identifcation of subgroups
    run = True
    open_bracket = oneLine.find("{",pointer)
    close_bracket = oneLine.find("}",pointer)

    while run:
        if close_bracket == (end-1):  # end of the string/file, different from end of a resource
            run = False
            header = oneLine[pointer:open_bracket]
            startArgs = open_bracket
            header = header.split("*")[-1].strip().replace("\"","").split(" ")  # remove comments using "*" previously added
            args = oneLine[startArgs:close_bracket+1]
            depth = len(header)
            for i in range(depth-1,-1,-1):  
                args = {header[i]:args}
            tfStorage = merge(tfStorage,args)


        elif open_bracket<close_bracket and opened == 0: #maingroup
            header = oneLine[pointer:open_bracket]
            startArgs = open_bracket
            opened += 1
            pointer = open_bracket+1
            open_bracket = oneLine.find("{",pointer)
            close_bracket = oneLine.find("}",pointer)

        elif open_bracket<close_bracket and opened > 0: #subgroup
            opened += 1
            pointer = open_bracket+1
            open_bracket = oneLine.find("{",pointer)
            close_bracket = oneLine.find("}",pointer)

        elif open_bracket > close_bracket and opened-1 == 0: # last group to close
            opened -= 1
            pointer = close_bracket+1
            header = header.split("*")[-1].strip().replace("\"","").split(" ")  # remove comments using "*" previously added
            args = oneLine[startArgs:pointer+1]
            depth = len(header)
            for i in range(depth-1,-1,-1):  
                args = {header[i]:args}
            tfStorage = merge(tfStorage,args)

            # for next resource
            open_bracket = oneLine.find("{",pointer)
            close_bracket = oneLine.find("}",pointer)

        else: #there's group to close
            opened -= 1
            pointer = close_bracket+1
            open_bracket = oneLine.find("{",pointer)
            close_bracket = oneLine.find("}",pointer)

    if 'locals' in tfStorage:
        tfStorage['locals'] = argsToDict(tfStorage["locals"])

    current_directory = os.path.dirname(os.path.abspath(__file__)) # get directory where this script is located
    os.chdir(current_directory)


    return tfStorage

def create_tf_dict2(td):
    os.chdir(td)
    oneLine=''
    for tfFile in glob.glob("*.tf"):
        with open(tfFile, 'r') as f:
            for line in f:
                line = line.strip()
                oneLine += "*"+line  #add "*" to handle comments in the code, doesn't handle curly brackets{} in comments

    tfStorage = {}
    patterns = [
        r'(?P<blockType>terraform)\s{',
        r'(?P<blockType>locals)\s{',
        r'(?P<blockType>provider)\s[\'"](?P<label>\w+)[\'"]\s{',
        r'(?P<blockType>module)\s[\'"](?P<label>\w+)[\'"]\s{',
        r'(?P<blockType>variable)\s[\'"](?P<label>\w+)[\'"]\s{',
        r'(?P<blockType>output)\s[\'"](?P<label>\w+)[\'"]\s{',
        r'(?P<blockType>data)\s[\'"](?P<label1>\w+)[\'"]\s[\'"](?P<label2>\w+)[\'"]\s{',
        r'(?P<blockType>resource)\s[\'"](?P<label1>\w+)[\'"]\s[\'"](?P<label2>\w+)[\'"]\s{'
        ]
    count= 0
    for p in patterns:
        pattern = re.compile(p)
        matches = pattern.finditer(oneLine)
        for match in matches:
            # print(match)
            # print(match.groupdict())
            opened = 1
            startArgs = match.span()[1]-1
            pointer = match.span()[1]
            open_bracket = oneLine.find("{",pointer)
            close_bracket = oneLine.find("}",pointer)
            while opened != 0:
                if open_bracket == -1: #end of file, can't find another open_bracket
                    opened -= 1
                    pointer = close_bracket+1
                elif open_bracket > close_bracket: # there's group to close
                    opened -= 1
                    pointer = close_bracket+1
                    open_bracket = oneLine.find("{",pointer)
                    close_bracket = oneLine.find("}",pointer)
                elif open_bracket < close_bracket: # subgroup
                    opened += 1
                    pointer = open_bracket +1
                    open_bracket = oneLine.find("{",pointer)
                    close_bracket = oneLine.find("}",pointer)
            # all groups closed
            args = oneLine[startArgs:pointer]
            group = match.groupdict()
            depth =len(group)
            for i in range(depth,0,-1):  
                args = {match.group(i):args}
            tfStorage = merge(tfStorage,args)
            count +=1
    # print(count)

    # numbers = [4,2,5,6,17,4,3,3,11,6,8,5,10,14,7,3,7]
    

    if 'locals' in tfStorage:
        argsToDict2(tfStorage["locals"])
        tfStorage['locals'] = argsToDict(tfStorage["locals"])
        

    current_directory = os.path.dirname(os.path.abspath(__file__)) # get directory where this script is located
    os.chdir(current_directory)


    return tfStorage

def argsToDict(argument:str):
    # print(argument)
    output = {}
    pattern = re.compile(r'(\w+)\s*=\s*([^*]*)')
    matches = pattern.finditer(argument)
    searched_square_brackets = False
    searched_round_brackets = False
    indexToSkip :list[tuple[int, int]] = []
    for match in matches:
        # print(match)
        if len(indexToSkip) != 0:
            if indexToSkip[0][1]< match.span()[0]:
                indexToSkip.pop(0)
        if match.group(2).startswith('[') and not searched_square_brackets:
            searched_square_brackets = True
            newPattern = re.compile(r'(\w+)\s*=\s*(\[[^\]]*\])')
            newMatches = newPattern.finditer(argument)
            for new in newMatches:
                indexToSkip.append(new.span())
                temp = {new.group(1):new.group(2)}
                output = merge(output,temp)
        if match.group(2).startswith('(') and not searched_round_brackets:
            searched_round_brackets = True
            newPattern = re.compile(r'(\w+)\s*=\s*(\([^\)]*\))')
            newMatches = newPattern.finditer(argument)
            for new in newMatches:
                # print(new)
                indexToSkip.append(new.span())
                temp = {new.group(1):new.group(2)}
                output = merge(output,temp)
        if len(indexToSkip) != 0:
            check_range = indexToSkip[0]
            if not_within_range(match.span(), check_range):
                temp = {match.group(1):match.group(2)}
                output = merge(output,temp)
            else:
                continue
        else:
            temp = {match.group(1):match.group(2)}
            # print(f'output:{output}')
            # print(f'temp:{temp}')
            output = merge(output,temp)
            
    return output

def argsToDict2(argument:str):
    patterns = [
        # r'(?P<argumentName>\w+)\s*=\s*[\'"](?P<argumentValue>[^\'"]+)[\'"]', # handle inverted commas
        # r'(?P<argumentName>\w+)\s*=\s*(?P<argumentValue>[^"\'*\s\[\{\d]+)',    # handle variables
        # r'(?P<argumentName>\w+)\s*=\s*(?P<argumentValue>[\d]+)',             # handle digits
        # r'(?P<argumentName>\w+)\s*=\s*(?P<argumentValue>\[[^\]]+\])',        # handle square brackets
        # r'(?P<argumentName>\w+)\s*=\s*\{(?P<argumentValue>[^\}]+\})',        # handle block (curly brackets)
        ]
    count= 0
    # print(argument)
    for p in patterns:
        pattern = re.compile(p)
        matches = pattern.finditer(argument)
        for m in matches:
            print(m)

def scraping_terraform_reg():
    string = "---\nsubcategory: \"ACM (Certificate Manager)\"\nlayout: \"aws\"\npage_title: \"AWS: aws_acm_certificate\"\ndescription: |-\n  Get information on a Amazon Certificate Manager (ACM) Certificate\n---\n\n# Data Source: aws_acm_certificate\n\nUse this data source to get the ARN of a certificate in AWS Certificate\nManager (ACM), you can reference\nit by domain without having to hard code the ARNs as input.\n\n## Example Usage\n\n```terraform\n# Find a certificate that is issued\ndata \"aws_acm_certificate\" \"issued\" {\n  domain   = \"tf.example.com\"\n  statuses = [\"ISSUED\"]\n}\n\n# Find a certificate issued by (not imported into) ACM\ndata \"aws_acm_certificate\" \"amazon_issued\" {\n  domain      = \"tf.example.com\"\n  types       = [\"AMAZON_ISSUED\"]\n  most_recent = true\n}\n\n# Find a RSA 4096 bit certificate\ndata \"aws_acm_certificate\" \"rsa_4096\" {\n  domain    = \"tf.example.com\"\n  key_types = [\"RSA_4096\"]\n}\n```\n\n## Argument Reference\n\n* `domain` - (Required) Domain of the certificate to look up. If no certificate is found with this name, an error will be returned.\n* `key_types` - (Optional) List of key algorithms to filter certificates. By default, ACM does not return all certificate types when searching. See the [ACM API Reference](https://docs.aws.amazon.com/acm/latest/APIReference/API_CertificateDetail.html#ACM-Type-CertificateDetail-KeyAlgorithm) for supported key algorithms.\n* `statuses` - (Optional) List of statuses on which to filter the returned list. Valid values are `PENDING_VALIDATION`, `ISSUED`,\n   `INACTIVE`, `EXPIRED`, `VALIDATION_TIMED_OUT`, `REVOKED` and `FAILED`. If no value is specified, only certificates in the `ISSUED` state\n   are returned.\n* `types` - (Optional) List of types on which to filter the returned list. Valid values are `AMAZON_ISSUED`, `PRIVATE`, and `IMPORTED`.\n* `most_recent` - (Optional) If set to true, it sorts the certificates matched by previous criteria by the NotBefore field, returning only the most recent one. If set to false, it returns an error if more than one certificate is found. Defaults to false.\n\n## Attribute Reference\n\nThis data source exports the following attributes in addition to the arguments above:\n\n* `arn` - ARN of the found certificate, suitable for referencing in other resources that support ACM certificates.\n* `id` - ARN of the found certificate, suitable for referencing in other resources that support ACM certificates.\n* `status` - Status of the found certificate.\n* `certificate` - ACM-issued certificate.\n* `certificate_chain` - Certificates forming the requested ACM-issued certificate's chain of trust. The chain consists of the certificate of the issuing CA and the intermediate certificates of any other subordinate CAs.\n* `tags` - Mapping of tags for the resource.\n"

    pattern = [
        r'Argument Reference(?P<Argument>[^#]+)',
        r'Attribute Reference(?P<Attribute>[^#]+)'
        ]
    for p in pattern:
        pattern = re.compile(p,flags=re.DOTALL)
        matches = pattern.finditer(string)
        for match in matches:
            dictionary = match.groupdict()

        # print(dictionary)
        final = {}
        pattern = r'`([^*]+)` - ([^*]+)'
        pattern = re.compile(pattern)
        for k,v in dictionary.items():
            matches = pattern.finditer(v)
            for match in matches:
                temp = {match.group(1):match.group(2)}
                final.update(temp)
            dictionary[k] = final


    for a in dictionary:
        print(a)
        for b in dictionary[a]:
            print(b)
            print(dictionary[a][b])
        print()
