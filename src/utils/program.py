
import os
import subprocess
from termcolor import colored

class Program:

    def __init__(self, name, init, commands):
        self.name = name
        self.commands = commands

        # Clear the terminal at the start, for nicies :3
        Program.clear()
        Program.printSuccess(f"Welcome to {self.name}!")
        init()

    def clear():
        subprocess.Popen('clear', shell=True).wait()

    def parse(self, userInput):
        words = userInput.strip().split()
        if len(words) > 0 and words[0] == 'exit':
            Program.printSpecial("Bye Bye ^_^")
            exit()
        for command in self.commands:
            if command.matches(words):
                try:
                    command.run(words)
                except Exception as e:
                    Program.printError(f"Error calling {command.name}: {e}")
                return
        # fall through:
        self.printGlossary()
        return None
    
    def printError(message):
        print(colored(message, "red"))

    def printSuccess(message):
        print(colored(message, "green"))

    def printWarning(message):
        print(colored(message, "blue"))

    def printSpecial(message):
        print(colored(message, "magenta"))
    
    def run(self):
        while True:
            self.parse(input(" ~> "))
    
    def printGlossary(self):
        out = ""

        maxNameLen = 0
        maxDescriptionLen = 0
        for command in self.commands:
            if maxNameLen < len(command.signature):
                maxNameLen = len(command.signature)
            if maxDescriptionLen < len(command.description):
                maxDescriptionLen = len(command.description)

        spacer = "|" + " "*(maxNameLen + 2) + "|" + " "*(maxDescriptionLen + 2) + "|\n"
        bumper = "+" + "-"*(maxNameLen+2) + "+" + "-"*(maxDescriptionLen+2) + "+"
        out += f"{bumper}\n"
        out += spacer
        for command in self.commands:
            out += f"| {command.title.ljust(maxNameLen)} | {' ' * maxDescriptionLen} |\n"
            out += f"| {command.signature.ljust(maxNameLen)} | {command.description.ljust(maxDescriptionLen)} |\n"
            out += spacer
        out += bumper
        Program.printWarning(f" ~{self.name} Commands~ \n{out}")

class Command:

    def __init__(self, name, title, description, args, func):
        self.name = name
        self.title = title
        self.description = description
        self.args = args
        self.func = func
        self.signature = " ".join([name] + [arg.signature for arg in args])

    def matches(self, words):
        if len(words) == 0:
            return False
        return words[0] == self.name
    
    def run(self, words):
        compiledArgs = {}
        index = 1
        for arg in self.args:
            compiledArgs[arg.name] = arg.validate(words, index)
            index += 1

        # Log EXACTLY what got called....
        niceArgs = ", ".join(
            [f"{name}={compiledArgs[name]}" for name in compiledArgs]
        )
        Program.printWarning(f"{self.name}({niceArgs})")
        
        self.func(compiledArgs)

class Arg:

    def __init__(self, name, valueType, argType=None, enumValues=None):
        self.name = name
        self.valueType = valueType
        self.argType = argType
        self.enumValues = enumValues

        if self.valueType == 'enum' and enumValues == None:
            raise AssertionError('Enums must include a list of accepted values.')

        suffix = ''
        if argType == 'variable': suffix = '[]'
        elif argType == 'optional': suffix = '?'
        self.signature = f"${name}{suffix}" # ({valueType}{suffix})"

    def intType(name):
        return Arg(name, "int")
    
    def stringType(name):
        return Arg(name, "string")
    
    def enumType(name, enumValues):
        return Arg(name, "enum", enumValues = enumValues)
    
    def variable(self):
        return Arg(
            self.name, 
            self.valueType, 
            argType="variable",
            enumValues=self.enumValues,
        )
    
    def optional(self):
        return Arg(
            self.name,
            self.valueType,
            argType="optional",
            enumValues=self.enumValues,
        )
    
    def validate(self, words, index):
        if self.argType == 'variable':
            return [
                self.validateOne(word)
                for word in words[index:]
            ]
        
        elif self.argType == 'optional':
            if len(words) <= index:
                return None
            try:
                return self.validateOne(words[index])
            except:
                return None
            
        else: # normal argument type
            if len(words) <= index:
                raise IndexError(f"Missing argument {self.name}.")
            return self.validateOne(words[index])

    def validateOne(self, word):
        if self.valueType == "string":
            return word
        if self.valueType == "int":
            try:
                intValue = int(word)
            except:
                raise TypeError(f"{self.name} must be an integer.")
            return intValue
        if self.valueType == "enum":
            if word not in self.enumValues:
                quotedValues = [
                    f"'{value}'" for value in self.enumValues
                ]
                oxfordComma = ',' if len(quotedValues) > 2 else ''
                valuesString = ", ".join(quotedValues[:-1]) + oxfordComma + " or " + quotedValues[-1]
                raise TypeError(f"{self.name} must be {valuesString}")
            return word