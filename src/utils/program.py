
import os
import subprocess
from textwrap import wrap
from termcolor import colored

from utils.format_text import Prints

class Program:

    def __init__(self, name, init, commands):
        self.name = name
        
        self.commands = Program.completeCommands(name, commands)
        # Clear the terminal at the start, for nicies :3
        Program.clear()
        Program.printSuccess(f"Welcome to {self.name}!")
        init()

    def completeCommands(name, commands):
        fakeHelpCommand = Command.help(name, [])
        exitCommand = Command.exitCommand()
        ret = [fakeHelpCommand] + commands + [exitCommand]

        # circle back because help should know about the added commands...
        helpCommand = Command.help(name, ret)
        ret[0] = helpCommand
        return ret

    def clear():
        subprocess.Popen('clear', shell=True).wait()

    def parse(self, userInput):
        words = userInput.strip().split()
        if len(words) == 0: return
        command = Command.getMatch(words[0], self.commands)
        if command is None:
            Program.printError(f"Unrecognized command '{words[0]}'...")
            return
        try:
            command.run(words)
        except Exception as e:
            Program.printError(f"Error calling {command.name}: {e}")
    
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

class Command:

    def __init__(self, name, title, description, args, func):
        self.name = name
        self.title = title
        self.description = description
        self.args = args
        self.func = func
        self.signature = " ".join([name] + [arg.signature for arg in args])
        self.longSignature = " ".join([name] + [arg.longSignature for arg in args])

    def getMatch(name, commands):
        for command in commands:
            if command.name == name:
                return command
        return None
    
    def exitCommand():
        def exitFunction(args):
            Program.printSpecial("Bye Bye ^_^")
            exit()
        return Command("exit", "Exit", "Terminate the program.", [], exitFunction)

    def help(name, commands):
        def printGlossary(args):
            commandName = args["command"]
            command = None
            if commandName is None:
                Program.printWarning(
                    Prints.columns([
                        "\n".join([ command.signature for command in commands ]),
                        "\n".join([ command.title for command in commands ]),
                    ])
                )
                return

            command = Command.getMatch(commandName, commands)
            if command is None:
                Program.printError(f"No command called '{commandName}'.")
                return
            
            Program.printWarning(
                Prints.columns([
                    "\n".join([
                        command.title,
                        " ~ ",
                        command.longSignature
                    ]),
                    "\n".join(
                        wrap(command.description, 30)
                    ),
                ])
            )
        return Command(
            "help",
            "Help",
            "Get information on what commands there are, or what a specific command does.",
            [ Arg.stringType("command").optional() ],
            printGlossary,
        )
    
    def run(self, words):
        processedArgs = {}
        index = 1
        for arg in self.args:
            processedArg = arg.validate(words, index)
            processedArgs[arg.name] = processedArg
            if type(processedArg) is list:
                index += len(processedArg)
            elif processedArg is not None:
                index += 1
            # Else don't increment index.

        if index != len(words):
            Program.printError(f"Extra arguments...")
            return

        # Log EXACTLY what got called....
        niceArgs = ", ".join(
            [f"{name}={processedArgs[name]}" for name in processedArgs]
        )
        Program.printWarning(f"{self.name}({niceArgs})")
        
        self.func(processedArgs)

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
        
        niceValueType = valueType
        if valueType == 'enum':
            niceValueType = f"({",".join(enumValues)})"

        self.signature = f"${name}{suffix}" # ({valueType}{suffix})"
        self.longSignature = f"${name}:{niceValueType}{suffix}"

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
    
    def validate(self, words: list[str], index: int):
        if self.argType == 'variable':
            ret = []
            # Validate words until one is invalid.
            try:
                while True:
                    ret.append(self.validateOne(words[index]))
                    index += 1
            except:
                return ret
        
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

    def validateOne(self, word: str):
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