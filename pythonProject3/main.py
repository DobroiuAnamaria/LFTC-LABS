from node import Node

symbols = {
    "var": 2,
    "int": 3,
    "char": 4,
    "float": 5,
    "bool": 6,
    "read": 7,
    "write": 8,
    "for": 9,
    "do": 10,
    "if": 11,
    "else": 12,
    "and": 13,
    "or": 14,
    "not": 15,
    ":": 16,
    ";": 17,
    ",": 18,
    ".": 19,
    "+": 20,
    "*": 21,
    "(": 22,
    ")": 23,
    "[": 24,
    "]": 25,
    "/": 26,
    "%": 27,
    "++": 28,
    "--": 29,
    "{": 30,
    "}": 31,
    ">=": 32,
    "\"": 33,
    "=": 34,
    "<=": 36
}
simpleSeparators = [";", ",", "{", "}", "[", "]", "(", ")", "=", ">", "<", "%", "+", "-", "*"]
complexSeparators = ["==", ">=", "<=", "++", "--", "~/", "!="]

tokens = []
fip = []
ts = None

currentLine = 1


def getFileContent(file_path):
    f = open(file_path, 'r')
    content = f.read()
    f.close()
    return content


def analyze(token):
    global ts
    if token in symbols:
        fip.append((symbols[token], -1))
    else:
        # remove newline characters
        if token == "":
            return

        if token[0] in ['"', "+", "-"] or token[0].isnumeric():  # constant
            # check if valid
            # number
            if token[0] != '"':
                if not token.isdecimal() or (token[0] == '0' and len(token) > 1):
                    raise Exception(f"Error on line {currentLine}: invalid numeric constant")
            # string
            else:
                if len(token) < 3:
                    raise Exception(f"Error on line {currentLine}: invalid empty string")
                for c in token[1:len(token) - 1]:
                    if not c.isalpha() and not c.isnumeric() and c not in [".", ",", ":", ";", "!", "?", " "]:
                        raise Exception(f"Error on line {currentLine}: unexpected character inside string constant")
                    if token[len(token) - 1] != "\"":
                        raise Exception(f"Error on line {currentLine}: unexpected end of file, '\"' expected")

            # add to ts and determine pozition in ts
            if ts is None:
                ts = Node(token)
            else:
                ts.insert(token)

            fip.append((1, token))
        else:  # identificator
            # check if valid variable name
            validateIdentificator(token)

            # add to ts
            if ts is not None:
                ts.insert(token)
            else:
                ts = Node(token)
            fip.append((0, token))


def validateIdentificator(token):
    if(len(token)) > 8:
        raise Exception(f"Error on line {currentLine}: max length for an identificator is 8")
    if token[0] != "_" and not token[0].isalpha():
        raise Exception(f"Error on line {currentLine}: unexpected character at the beginning of an identificator")
    if token[0] == "_" and not token[1].isalpha():
        raise Exception(f"Error on line {currentLine}: unexpected character after '_'")
    if token[len(token) - 1] == "_":
        raise Exception(f"Error on line {currentLine}: invalid last character")

    for i in range(len(token)):
        c = token[i]
        if not c.isalnum() and c != "_":
            raise Exception(f"Error on line {currentLine}: unexpected character")
        if i != len(token) - 1:
            if c == "_" and token[i + 1] == "_":
                raise Exception(f"Error on line {currentLine}: illegal double '_'")


def updateFip(sortedTs):
    for i in range(len(sortedTs)):
        for j in range(len(fip)):
            if fip[j][1] == sortedTs[i]:
                fip[j] = (fip[j][0], i + 1)


def main():
    # read file
    code = getFileContent("program.txt")
    # .replace("\n", " ")

    # read char by char and separate into tokens
    tokenStart = -1
    isString = False
    i = 0
    while i < len(code):
        # get new token starting index
        if tokenStart == -1:
            # if space go to next index
            if code[i] == " ":
                i += 1
                continue
            tokenStart = i

        # newline
        if code[i] == "\n":
            if tokenStart != -1:
                analyze(code[tokenStart:i])
            tokenStart = -1

            global currentLine
            currentLine += 1
            i += 1
            continue

        # "
        if code[i] == "\"":
            # entering the string realm
            if not isString:
                if tokenStart != -1:
                    analyze(code[tokenStart:i])
                tokenStart = i
            # exiting the string realm
            else:
                analyze(code[tokenStart:i + 1])
                tokenStart = -1
            isString = not isString
            i += 1
            continue

        # " i don't care what's inside... yet "
        if isString:
            i += 1
            continue

        # check for complex separators
        if code[i:i + 2] in complexSeparators:
            if tokenStart != -1:
                analyze(code[tokenStart:i])
            analyze(code[i:i + 2])
            i += 1
            tokenStart = -1
        # check for simple separators
        elif code[i] in simpleSeparators:
            # abc; -> ["abc", ";"]
            if tokenStart != -1:
                analyze(code[tokenStart:i])
            # fip.append(";")
            analyze(code[i])
            tokenStart = -1
        # check for the rest
        elif code[i] == " ":
            if tokenStart == -1:
                i += 1
                continue
            else:
                analyze(code[tokenStart:i])
                tokenStart = -1
        # hopefully aplhanumeric or "_"
        else:
            if tokenStart == -1:
                tokenStart = i

        if i == len(code) - 1 and tokenStart != -1:
            analyze(code[tokenStart:])

        i += 1

    updateFip(ts.printTree())
    print(f"TS: {ts.printTree()}")
    print("FIP:")
    for pair in fip:
        print(pair)


try:
    main()
except Exception as e:
    print(e)
