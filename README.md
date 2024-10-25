# Rule-Engine-with-AST

Table of Contents : 

* Project Overview
* Technologies Used
* Features
* Installation
* Usage
* Code Structure
* Testing
* Visualization

 Project Overview :
 
This project implements a simple rule engine that determines user eligibility based on various attributes such as age, department, income, and experience. The engine uses an Abstract Syntax Tree (AST) to represent conditional rules and allows for dynamic creation, combination, and modification of these rules.

Technologies Used :
* Python 3.x
* Graphviz (for AST visualization)
* Regular expressions (re module)

Features :

- Rule Creation: Users can create rules based on logical conditions.
- Rule Combination: Multiple rules can be combined into a single AST using logical operators (AND, OR).
- Rule Evaluation: The engine can evaluate user attributes against the combined rules.
- Dynamic Rule Modification: Users can update, add, or remove conditions from existing rules.
- Error Handling: The engine includes error handling for invalid rule strings and data formats.
-Visualization: The AST is visualized and saved as a PNG file for easier understanding.

Testing : 

The code includes various test cases to ensure functionality:
- Creating individual rules and verifying their AST representation.
- Combining rules and ensuring the resulting AST reflects combined logic.
- Evaluating rules against different user attributes.

Visualization : 

The AST is visualized using Graphviz. Upon running the script, an image file named ast_visualization.png will be generated in the same directory. This file provides a graphical representation of the rule engine's logic.  
  
