#fragment start *

import calmLexer as lexer
from   calmSymbols import *
from   genericAstNode import Node

class ParserError(Exception): pass

def dq(s): return '"%s"' %s

token   = None
verbose = False
indent  = 0
numberOperator = ["+","-","/","*"]
equalityOperator = ["==", "<=", ">=", "!="]
iterateOperator = ["++", "--", "-=", "+="]
#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def getToken():
	global token 
	if verbose: 
		if token: 
			print(("  "*indent) + "   (" + token.show(align=False) + ")")
	token  = lexer.get()


#-------------------------------------------------------------------
#    push and pop
#-------------------------------------------------------------------
def push(s):
	global indent
	indent += 1
	if verbose: print(("  "*indent) + " " + s)

def pop(s):
	global indent
	if verbose: 
		pass
	indent -= 1

#-------------------------------------------------------------------
#  decorator track0
#-------------------------------------------------------------------
def track0(func):
	def newfunc():
		push(func.__name__)
		func()
		pop(func.__name__)
	return newfunc

#-------------------------------------------------------------------
#  decorator track
#-------------------------------------------------------------------
def track(func):
	def newfunc(node):
		push(func.__name__)
		func(node)
		pop(func.__name__)
	return newfunc

#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def error(msg):
	token.abort(msg)


#-------------------------------------------------------------------
#        foundOneOf
#-------------------------------------------------------------------
def foundOneOf(argTokenTypes):

	for argTokenType in argTokenTypes:
		if token.type == argTokenType:
			return True
	return False


#-------------------------------------------------------------------
#        found
#-------------------------------------------------------------------
def found(argTokenType):
	if token.type == argTokenType:
		return True
	return False

#-------------------------------------------------------------------
#       consume
#-------------------------------------------------------------------
def consume(argTokenType):
	"""
	Consume a token of a given type and get the next token.
	If the current token is NOT of the expected type, then
	raise an error.
	"""
	if token.type == argTokenType:
		getToken()
	else:
		error("I was expecting to find "
			  + dq(argTokenType)
			  + " but I found " 
			  + token.show(align=False)
			)

#-------------------------------------------------------------------
#    parse
#-------------------------------------------------------------------
def parse(sourceText, **kwargs):
	global lexer, verbose
	verbose = kwargs.get("verbose",False)
	# create a Lexer object & pass it the sourceText
	lexer.initialize(sourceText)
	getToken()
	program()
	if verbose:
		print "~"*80
		print "Successful parse!"
		print "~"*80
	return ast

#--------------------------------------------------------
#                   program
#--------------------------------------------------------
@track0
def program():

	global ast
	node = Node()

	statement(node)
	while not found(EOF):
		statement(node)

	consume(EOF)
	ast = node


#--------------------------------------------------------
#                   statement
#--------------------------------------------------------
@track
def statement(node):
	
	if found("pone"):
		printStatement(node)
	elif found("kung"):
		ifStatement(node)
	elif found("ginabuhat"):
		functionStatement(node)
	elif found("samtang"):
		whileLoop(node)
	elif found("para"):
		forLoop(node)
	else:  
		assignmentStatement(node)


#--------------------------------------------------------
#                   expression
#--------------------------------------------------------
@track
def expression(node):

	if found(STRING):
		stringLiteral(node)
		while found("||"):
			getToken()
			stringExpression(node)

	elif found(NUMBER):
		numberLiteral(node)
		while foundOneOf(numberOperator): 
			node.add(token)
			getToken()
			numberExpression(node)

	elif found(""):
		print "Empty statement inside IF"
		printStatement(node)
		
	else:
		node.add(token)
		consume(IDENTIFIER)

		if foundOneOf(numberOperator):
			while foundOneOf(numberOperator):
				node.add(token)
				getToken()
				numberExpression(node)
		elif foundOneOf(equalityOperator):
			while foundOneOf(equalityOperator) :
				node.add(token)
				getToken()
				numberExpression(node)
		elif foundOneOf(iterateOperator):
			while foundOneOf(iterateOperator):
				node.add(token)
				getToken()
				

#--------------------------------------------------------
#                   assignmentStatement
#--------------------------------------------------------
@track
def assignmentStatement(node):

	identifierNode = Node(token)
	consume(IDENTIFIER)

	operatorNode = Node(token)
	consume("=")
	node.addNode(operatorNode)

	operatorNode.addNode(identifierNode)

	expression(operatorNode)
	consume(";")

#--------------------------------------------------------
#     printStatement
#--------------------------------------------------------
@track
def printStatement(node):
	statementNode = Node(token)
	consume("pone")
	consume("(")

	node.addNode(statementNode)
	expression(statementNode)

	consume(")")
	consume(";")

#--------------------------------------------------------
#                   If Statement (kung)
#--------------------------------------------------------
@track
def ifStatement(node):

	kungNode = Node(token)
	node.addNode(kungNode)
	
	consume("kung")
	consume("(")

	expression(kungNode)

	consume(")")
	consume("{")

		
	while  not found("}"):
		if found("pone"):
			printStatement(kungNode)
		elif found("kung"):
			ifStatement(kungNode)
		elif found("kung_nd"):
			kung_ndNode = Node(token)
			kungNode.addNode(kung_ndNode)
			consume("kung_nd")
			elseifStatement(kung_ndNode)
		elif found(IDENTIFIER):
			assignmentStatement(kungNode)
		elif found("kung_nd_ngd"):
			elseStatement(kungNode)
			break

	consume("}")


#--------------------------------------------------------
#                   Else If Statement (kung_nd)
#--------------------------------------------------------
@track
def elseifStatement(node):

	consume("(")

	expression(node)

	consume(")")
	consume("{")

	while  not found("}"):
		statement(node)

	consume("}")


#--------------------------------------------------------
#                   Else Statement (kung_nd_ngd)
#--------------------------------------------------------
@track
def elseStatement(node):

	kung_nd_ngdNode = Node(token)
	node.addNode(kung_nd_ngdNode)
	consume("kung_nd_ngd")
	consume("{")

	while not found("}"):
		statement(kung_nd_ngdNode)


	consume("}")

#--------------------------------------------------------
#                   While Loop (samtang)
#--------------------------------------------------------
@track
def whileLoop(node):

	samtangNode = Node(token)
	node.addNode(samtangNode)

	consume("samtang")
	consume("(")

	expression(samtangNode)

	consume(")")
	consume("{")

	while not found("}"):
		statement(samtangNode)

	
	consume("}")
#--------------------------------------------------------
#            Function Statement (ginabuhat)
#--------------------------------------------------------
@track
def functionStatement(node):

	funNode = Node(token)
	consume("ginabuhat")

	node.addNode(funNode)
	stringLiteral(funNode)

	consume("(")
	expression(funNode)
	consume(")")

	consume("{")

	while not found("}"):
		statement(funNode)

	consume("}")

#--------------------------------------------------------
#                   For Loop (para)
#--------------------------------------------------------
@track
def forLoop(node):

	paraNode = Node(token)
	node.addNode(paraNode)

	consume("para")
	consume("(")

	expression(paraNode)

	consume(";")

	expression(paraNode)

	consume(";")
	paraNode.add(token)
	consume(IDENTIFIER)
	if foundOneOf(iterateOperator):
		while foundOneOf(iterateOperator):
			paraNode.add(token)
			getToken()

	consume(")")
	consume("{")

	while not found("}"):
		statement(paraNode)

	consume("}")


#--------------------------------------------------------
#                   stringExpression
#--------------------------------------------------------
@track
def stringExpression(node):

	if found(STRING):
		node.add(token)
		getToken()

		while found("||"):
			print a, "\n"
			getToken()
			numberExpression(node)
	else:
		node.add(token)
		consume(IDENTIFIER)

	while found("||"):
		getToken() 
		stringExpression(node)

#--------------------------------------------------------
#                   numberExpression
#--------------------------------------------------------
@track
def numberExpression(node):

	if found(NUMBER):
		numberLiteral(node)
	else:
		node.add(token)
		consume(IDENTIFIER)

	while foundOneOf(numberOperator): 
		node.add(token)
		getToken()
		numberExpression(node)

#--------------------------------------------------------
#                   stringLiteral
#--------------------------------------------------------
def stringLiteral(node): 
	node.add(token)
	getToken()

#--------------------------------------------------------
#                   numberLiteral
#--------------------------------------------------------
def numberLiteral(node): 
	node.add(token)
	getToken()
