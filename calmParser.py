#fragment start *
"""
A recursive descent parser for nxx1, 
as defined in nxx1ebnf.txt
"""
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
iterateOperator = ["++", "--"]
#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def getToken():
	global token 
	if verbose: 
		if token: 
			# print the current token, before we get the next one
			#print (" "*40 ) + token.show() 
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
		#print(("  "*indent) + " " + s + ".end")
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
	"""
	argTokenTypes should be a list of argTokenType
	"""
	for argTokenType in argTokenTypes:
		#print "foundOneOf", argTokenType, token.type
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
	"""
program = statement {statement} EOF.
	"""
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
	"""
statement = printStatement | assignmentStatement .
assignmentStatement = variable "=" expression ";".
printStatement      = "print" expression ";".
	"""
	if found("pone"):
		printStatement(node)
	elif found("kung"):
		ifStatement(node)
		if found ("kung_nd"):
			elseifStatement(node)
		if found("kung_nd_ngd"):
			elseStatement(node)
	elif found("ginabuhat"):
		functionStatement(node)
	elif found("samtang"):
		whileLoop(node)
	else:  
		assignmentStatement(node)


#--------------------------------------------------------
#                   expression
#--------------------------------------------------------
@track
def expression(node):
	"""
expression = stringExpression | numberExpression.

/* "||" is the concatenation operator, as in PL/I */
stringExpression =  (stringLiteral | variable) {"||"            stringExpression}.
numberExpression =  (numberLiteral | variable) { numberOperator numberExpression}.
numberOperator = "+" | "-" | "/" | "*" .
	"""

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

	elif found("pone"):
		printStatement(node)

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
				pass
		elif found("="):
			consume("=")
			node.add(token)
			consume(NUMBER)
			node.add(token)
			consume(";")
			node.add(token)


#--------------------------------------------------------
#                   assignmentStatement
#--------------------------------------------------------
@track
def assignmentStatement(node):
	"""
assignmentStatement = variable "=" expression ";".
	"""
	identifierNode = Node(token)
	consume(IDENTIFIER)

	operatorNode = Node(token)
	consume("=")
	node.addNode(operatorNode)

	operatorNode.addNode(identifierNode)

	expression(operatorNode)
	consume(";")

#--------------------------------------------------------
#                   printStatement
#--------------------------------------------------------
@track
def printStatement(node):
	"""
printStatement      = "print" expression ";".
	"""
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

	state = Node(token)
	consume("kung")
	consume("(")

	node.addNode(state)
	expression(state)


	consume(")")
	consume("{")

	
	node.addNode(state)
	expression(state)

	consume("}")
#--------------------------------------------------------
#                   Else If Statement (kung_nd)
#--------------------------------------------------------
@track
def elseifStatement(node):

	state = Node(token)
	consume("kung_nd")
	consume("(")

	node.addNode(state)
	expression(state)


	consume(")")
	consume("{")

	
	node.addNode(state)
	expression(state)

	consume("}")

#--------------------------------------------------------
#                   Else Statement (kung_nd_ngd)
#--------------------------------------------------------
@track
def elseStatement(node):

	state = Node(token)
	consume("kung_nd_ngd")
	consume("{")

	node.addNode(state)
	expression(state)

	consume("}")

#--------------------------------------------------------
#                   Function Statement (ginabuhat)
#--------------------------------------------------------
@track
def functionStatement(node):

	state = Node(token)
	consume("ginabuhat")

	if found(IDENTIFIER):
		node.addNode(state)
		stringLiteral(state)

	consume("(")
	node.addNode(state)
	expression(state)
	consume(")")


	consume("{")

	node.addNode(state)
	expression(state)

	consume("}")

#--------------------------------------------------------
#                   While Loop (samtang)
#--------------------------------------------------------
@track
def whileLoop(node):

	state = Node(token)
	consume("samtang")
	consume("(")

	node.addNode(state)
	expression(state)

	consume(")")
	consume("{")

	
	node.addNode(state)
	expression(state)

	consume("}")

#--------------------------------------------------------
#                   For Loop (para)
#--------------------------------------------------------
@track
def forLoop(node):

	state = Node(token)
	consume("para")
	consume("(")

	node.addNode(state)
	expression(state)

	consume(")")
	consume("{")

	
	node.addNode(state)
	expression(state)

	consume("}")
#--------------------------------------------------------
#                   stringExpression
#--------------------------------------------------------
@track
def stringExpression(node):
	"""
/* "||" is the concatenation operator, as in PL/I */
stringExpression =  (stringLiteral | variable) {"||" stringExpression}.
	"""

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
	"""
numberExpression =  (numberLiteral | variable) { numberOperator numberExpression}.
numberOperator = "+" | "-" | "/" | "*" .
	"""
	print "Found is a number expression"

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
