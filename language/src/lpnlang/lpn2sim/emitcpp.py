import inspect
import ast
from pathlib import Path
from lpnlang import *
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from textwrap import dedent, indent
from enum import IntEnum
from typing import List, Dict
from .emitcpp_const_str import *


INDENT = "    "
NEWLINE = "\n"
BACKSLASH = "\\"

def print_node_attributes(node):
    attributes = [attr for attr in dir(node) if not attr.startswith('__')]
    for attr in attributes:
        value = getattr(node, attr, None)
        print(f"{attr}: {value}")

def expr_to_cpp(expr):
    if isinstance(expr, ast.Name):
        return expr.id
    elif isinstance(expr, ast.Num):
        return str(expr.n)
    elif isinstance(expr, ast.Attribute):
        value = expr_to_cpp(expr.value)
        # print("debug ", value, expr.attr)
        # Check if it's a subscript access and the attribute is 'tokens'
        if isinstance(expr.value, ast.Subscript) or \
           (isinstance(expr.value, ast.Attribute) and expr.value.attr == 'tokens'):
            return f"{value}->{expr.attr}"
        else:
            return f"{value}.{expr.attr}"
    elif isinstance(expr, ast.Subscript):
        # Handling subscript access (like array or list indexing)
        value = expr_to_cpp(expr.value)
        index = expr_to_cpp(expr.slice)
        return f"{value}[{index}]"
    elif isinstance(expr, ast.Index):
        return expr_to_cpp(expr.value)
    elif isinstance(expr, ast.Constant):
        return str(expr.value)

    # Add more cases as needed
    assert(f"fault on {expr}" and 0)
    return ""

def binop_to_cpp(op, convert_to_double=False):
    if isinstance(op, ast.Add):
        return '+'
    elif isinstance(op, ast.Sub):
        return '-'
    elif isinstance(op, ast.Mult):
        return '*'
    elif isinstance(op, ast.Div):
        if convert_to_double:
            return '/(double)'
        else:
            return '/'
    elif isinstance(op, ast.FloorDiv):
        # Translate floor division to C++ division (for integers, C++ inherently floors the result)
        return '/'
    elif isinstance(op, ast.Mod):
        return '%'
    # ... (other operators)
    return '?'

class CppFunctionGenerator(ast.NodeVisitor):
    def __init__(self):
        self.cpp_code = ""
        self.indent_level = 0
        self.declared_variables = {}
        self.string_literals = set()
        self.token_types = {}
        self.prev_context_return = None
        self.prev_capture_by_value = None
        self.set_of_token_types = {}
        self.enums = None
        self.last_left = None
        self.last_statement_start = None
        self.convert_to_double = False
        self.gen_klee_mode = False
        self.open_merge = False

    def generate_indent(self):
        return "    " * self.indent_level
    
    def visit_Break(self, node):
        self.cpp_code += f"{self.generate_indent()}break;\n"

    def visit_If(self, node):
        self.cpp_code += f"{self.generate_indent()}if ("
        self.visit(node.test)  # Visit the test expression of the if statement
        self.cpp_code += ") {\n"
        self.indent_level += 1

        for body_item in node.body:
            self.visit(body_item)

        self.indent_level -= 1
        self.cpp_code += f"{self.generate_indent()}}}" + "\n"

        if node.orelse:
            self.cpp_code += f"{self.generate_indent()}else {{" + "\n"
            self.indent_level += 1

            for body_item in node.orelse:
                self.visit(body_item)

            self.indent_level -= 1
            self.cpp_code += f"{self.generate_indent()}}}" + "\n"

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            self.cpp_code += f" {self.visit(op)} "
            self.visit(right)
    
    def visit_BoolOp(self, node):
        op = self.boolop_to_cpp(node.op)
        self.cpp_code += "("
        for idx, value in enumerate(node.values):
            if idx > 0:
                self.cpp_code += f" {op} "
            self.visit(value)
        self.cpp_code += ")"

    def boolop_to_cpp(self, boolop):

        if isinstance(boolop, ast.And):
            return "&&"
        elif isinstance(boolop, ast.Or):
            return "||"
        exit(" boolop not seen ", boolop)
        return ""
    
    def unaryop_to_cpp(self, unaryop):
        if isinstance(unaryop, ast.UAdd):
            return '+'
        elif isinstance(unaryop, ast.USub):
            return '-'
        elif isinstance(unaryop, ast.Not):
            return '!'
        exit("unaryop not seen ", unaryop)
        return ""

    def visit_Gt(self, node):
        return ">"
    
    def visit_Lt(self, node):
        return "<"

    def visit_Eq(self, node):
        return "=="
    
    def visit_NotEq(self, node):
        return "!="

    def visit_Return(self, node):
        self.cpp_code += f"{self.generate_indent()}return "
        self.last_left = "return"
        if node.value is not None:
            self.visit(node.value)
        self.cpp_code += ";\n"
        self.last_left = None

    def visit_UnaryOp(self, node):
        # print("UnaryOp", node.op)
        # print(f"{node.__class__.__name__}: {ast.dump(node, annotate_fields=True, include_attributes=False)}")
        op = self.unaryop_to_cpp(node.op)
        self.cpp_code += f"{op}("
        self.visit(node.operand)
        self.cpp_code += ")"

    def visit_Num(self, node):
        self.cpp_code += str(node.n)

    def visit_Name(self, node):
        if node.id == "binding":
            return
        self.cpp_code += node.id

    def visit_NameConstant(self, node):
        if node.value is True:
            self.cpp_code += "true"
        elif node.value is False:
            self.cpp_code += "false"
        elif node.value is None:
            # For other NameConstant values (like None)
            raise Exception(f"NameConstant value {node.value} not supported")
            self.visit(node.value)

    def visit_Attribute(self, node):
        '''
            Cautious about the attribute access,
            maybe something is wrong
        '''
        if isinstance(node.value, ast.Subscript) or \
           (isinstance(node.value, ast.Attribute) and node.value.attr == 'tokens'):
            self.visit(node.value)
            self.cpp_code += f"->{node.attr}"
        else:
            if isinstance(node.value, ast.Name) and node.value.id == 'CstStr':
                self.cpp_code += f"(int)CstStr::{node.attr.upper()}"
            elif isinstance(node.value, ast.Name) and node.attr == 'tokens':
                'all access to tokens is through place and place is a ptr in cpp'
                self.visit(node.value)
                self.cpp_code += f"->{node.attr}"
                # print("Attribute", node.value.id, node.attr)
                # assert(0)
            else:
                self.visit(node.value)
                self.cpp_code += f".{node.attr}"

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.cpp_code += "["
        self.visit(node.slice)
        self.cpp_code += "]"

    def visit_Index(self, node):
        self.visit(node.value)
    
    def visit_Assign(self, node):
        target_var = node.targets[0].id
        self.last_statement_start = len(self.cpp_code)
        if target_var not in self.declared_variables:
            self.cpp_code += f"{self.generate_indent()}auto "
            self.declared_variables[target_var] = 'auto'
        else:
            self.cpp_code += f"{self.generate_indent()}"

        self.visit(node.targets[0])
        self.cpp_code += " = "
        self.last_left = target_var
        self.visit(node.value)
        if self.cpp_code[-2:] == ";\n":
            return 
        self.cpp_code += ";\n"
        self.last_left = None
        self.last_statement_start = None
        if self.open_merge:
            self.cpp_code += "klee_close_merge();\n"
            self.open_merge = False
    def visit_BinOp(self, node):
        self.cpp_code += "("
        self.visit(node.left)
        self.cpp_code += f" {binop_to_cpp(node.op, self.convert_to_double)} "
        self.visit(node.right)
        self.cpp_code += ")"

    def visit_AnnAssign(self, node):
        assert(0)

    def visit_For(self, node):
        loop_var = node.target.id
        if isinstance(node.iter, ast.Call):
            #  the loop is of the form "for i in range(x, y)"
            #  the loop is of the form "for i in range(x)"
            if (node.iter.func.id != 'range'):
                raise Exception(f"Only range() function is supported in for loop")
            
            if len(node.iter.args) == 1:
                self.cpp_code += f"{self.generate_indent()}for (int {loop_var} = 0; {loop_var} < "
                self.visit(node.iter.args[0])
                self.cpp_code += """; ++{loop_var}) {{\n""".format(loop_var=loop_var)
            else:
                self.cpp_code += f"{self.generate_indent()}for (int {loop_var} = "
                self.visit(node.iter.args[0])
                self.cpp_code += f"; {loop_var} < "
                self.visit(node.iter.args[1])
                self.cpp_code += """; ++{loop_var}) {{\n""".format(loop_var=loop_var)
            # self.cpp_code += f"{self.generate_indent()}for (int {loop_var} = {start}; {loop_var} < {end}; ++{loop_var}) {{\n"
        else:
            self.cpp_code += f"{self.generate_indent()}for (auto {loop_var} : "
            self.visit(node.iter)
            self.cpp_code += ") {\n"

        self.indent_level += 1
        for body_item in node.body:
            self.visit(body_item)

        self.indent_level -= 1
        self.cpp_code += f"{self.generate_indent()}}}\n"
    
    def visit_Assert(self, node):
        
        self.cpp_code += f"{self.generate_indent()}assert("
        self.visit(node.test)
        self.cpp_code += ");\n"

    def visit_Call(self, node):
        # print("visiting a call", node.func)
        if isinstance(node.func, ast.Name):
            # print("=== func code === ", node.func.id)
            if node.func.id == 'prop_value':
                args = [expr_to_cpp(arg) for arg in node.args]
                assert(args[0]=="binding")
                place = args[1]
                nth_tk = args[2]
                prop_name = args[3]
                if nth_tk == "None":
                    if prop_name == "tk_len":
                        in_place_code= """{place}->tokensLen()""".format(place=place)
                    else:
                        raise Exception(f"(prop_value) property name {prop_name} not supported when idx is None")
                else:
                    in_place_code= """{place}->tokens[{nth_tk}]->{prop_name}""".format(place=place, nth_tk=nth_tk, prop_name=prop_name)
                # print(in_place_code)
                self.cpp_code += in_place_code
            
            elif node.func.id == 'get_token':
                bd = expr_to_cpp(node.args[0])
                assert(bd == "binding")
                place = expr_to_cpp(node.args[1])
                nth_tk = expr_to_cpp(node.args[2])
                # print(in_place_code)
                self.cpp_code += """{place}->tokens[{nth_tk}]""".format(place=place, nth_tk=nth_tk)

            elif node.func.id == 'Token':
                if not node.args:  # Check if Token() is called without arguments
                    self.cpp_code += f"{self.generate_indent()}NEW_TOKEN_WO_DECL(EmptyToken);\n"
                else:
                    token_type_name, set_token_fields = self.handle_token_args_key_only(node.args)
                    self.cpp_code += """NEW_TOKEN_WO_DECL({token_type_name});\n""".format(token_type_name=token_type_name)
                    if set_token_fields is not None:
                        for key, value in set_token_fields:
                            self.cpp_code += """{indent}{left_var}->{key} = """.format(indent=self.generate_indent(), left_var=self.last_left, key=key) 
                            self.visit(value)
                            self.cpp_code += ";\n"
            elif node.func.id == 'list':
                assert(self.last_statement_start is not None)
                var_declare = self.cpp_code[self.last_statement_start:]
                # print(var_declare)
                var_declare = var_declare.split("=")[0]
                var_declare = var_declare.split("auto")[1]
                self.cpp_code = self.cpp_code[:self.last_statement_start]
                self.cpp_code += f"std::vector<int> {var_declare};\n"
            elif node.func.id == 'len':
                if isinstance(node.args[0], ast.Name):
                    # print(node.args[0].id)
                    self.cpp_code += f"{node.args[0].id}.size()"
            else:
                func_name = node.func.id
                if func_name == "max" or func_name == "min":
                    func_name = "std::" + func_name
                if func_name == "lpn_int":
                    if not self.gen_klee_mode:
                        func_name = "int"
                    else:
                        before_assign = self.cpp_code[:self.last_statement_start]
                        before_assign += "klee_open_merge();\n"
                        self.cpp_code = before_assign + self.cpp_code[self.last_statement_start:]
                        self.open_merge = True
                        func_name = ""
                self.cpp_code += """{indent}{func_name}(""".format(indent=self.generate_indent(), func_name=func_name)
                for i, arg in enumerate(node.args):
                    old_len = len(self.cpp_code)
                    self.visit(arg)
                    if len(self.cpp_code) == old_len:
                        'nothing is added, so skip ',' '
                        continue
                    if i <= len(node.args) - 2:
                        self.cpp_code += ", "
                self.cpp_code += """)"""
                if self.last_left is None:
                    self.cpp_code += ";\n"
                    if self.open_merge:
                        self.cpp_code += "klee_close_merge();\n"

        elif isinstance(node.func, ast.Attribute):
            output_object = expr_to_cpp(node.func.value)
            # print(output_object, node.func.attr)
            if node.func.attr == 'push_token':
                # Special handling if the argument is a Token creation
                # print(output_object)
                if isinstance(node.args[0], ast.Call) and node.args[0].func.id == 'Token':
                    if not node.args[0].args:  # Check if Token() is called without arguments
                        self.cpp_code += f"{self.generate_indent()}NEW_TOKEN(EmptyToken, new_token);\n"
                        self.cpp_code += f"{self.generate_indent()}{output_object}->pushToken(new_token);\n"
                    else:
                        token_type_name, set_token_fields = self.handle_token_args_key_only(node.args[0].args)
                        self.cpp_code += """{indent}NEW_TOKEN({token_type_name}, new_token);\n""".format(indent=self.generate_indent(), token_type_name=token_type_name)
                        if set_token_fields is not None:
                            for key, value in set_token_fields:
                                self.cpp_code += """{indent}new_token->{key} = """.format(indent=self.generate_indent(), key=key) 
                                self.visit(value)
                                self.cpp_code += ";\n"
                                
                        self.cpp_code += """{indent}{output_object}->pushToken(new_token);\n""".format(indent=self.generate_indent(), output_object=output_object)
                else:
                    # Generic handling for other types of push_token
                    self.cpp_code += f"{self.generate_indent()}{output_object}->pushToken("
                    self.visit(node.args[0])
                    self.cpp_code += ");\n"
                    # argument = expr_to_cpp(node.args[0])
                    # self.cpp_code += f"{self.generate_indent()}{output_object}->pushToken({argument});\n"
            elif node.func.attr == 'append':
                # print(node.func.attr )
                self.cpp_code += """{indent}{output_object}.push_back(""".format(indent=self.generate_indent(), output_object=output_object)
                self.visit(node.args[0])
                self.cpp_code += ");\n"

            else:
                output_object = expr_to_cpp(node.func.value)
                if output_object == "math":
                    self.cpp_code += f"(int){node.func.attr}("
                    for arg in node.args:
                        self.visit(arg)
                    self.cpp_code += ")"
                    if self.last_left is None:
                        self.cpp_code += ";\n"
                else:
                    raise Exception(f"func.call_func Not implemented at {output_object}")
        else:
            "let everything else be handled by the not doing anything"
            if not isinstance(node.func, ast.Name):
                raise Exception(f"func.call_func Not implemented at {node.func}")
            func_name = node.func.id
            self.visit(node.func.id)
            self.cpp_code += "("
            for i, arg in enumerate(node.args):
                old_len = len(self.cpp_code)
                self.visit(arg)
                if len(self.cpp_code) == old_len:
                    'nothing is added, so skip ',' '
                    continue
                if i <= len(node.args) - 2:
                    self.cpp_code += ", "
            self.cpp_code += ")"
            if self.last_left is None:
                self.cpp_code += ";\n"
            "Check if the function call result is itself called (nested call)"

    def handle_token_args(self, args):
        # Function to handle arguments passed to Token constructor
        if len(args) == 1 and isinstance(args[0], ast.Dict):
            # Assuming a dictionary is passed to Token
            fields = []
            set_value = []
            for key, value in zip(args[0].keys, args[0].values):
                if isinstance(key, ast.Constant):
                    key_str = key.s 
                else:
                    assert(0)
                value_str = expr_to_cpp(value)
                fields.append(f"{key_str}")
                set_value.append((key_str, value_str))
            
            assert(tuple(fields) in self.set_of_token_types)
            token_type_name = self.set_of_token_types[tuple(fields)]
            self.token_types[token_type_name] = fields

            return token_type_name, set_value
        return "", None

    def handle_token_args_key_only(self, args):
        # Function to handle arguments passed to Token constructor
        if len(args) == 1 and isinstance(args[0], ast.Dict):
            # Assuming a dictionary is passed to Token
            fields = []
            set_value = []
            for key, value in zip(args[0].keys, args[0].values):
                if isinstance(key, ast.Constant):
                    key_str = key.s 
                else:
                    assert(0)
                fields.append(f"{key_str}")
                set_value.append((key_str, value))
            assert(tuple(fields) in self.set_of_token_types)
            token_type_name = self.set_of_token_types[tuple(fields)]
            self.token_types[token_type_name] = fields

            return token_type_name, set_value
        return "", None

class ASTPrettyPrinter(ast.NodeVisitor):
    def __init__(self):
        self.indent_level = 0

    def generic_visit(self, node):
        indent = '    ' * self.indent_level
        print(f"{indent}{node.__class__.__name__}: {ast.dump(node, annotate_fields=True, include_attributes=False)}")
        
        self.indent_level += 1
        super().generic_visit(node)
        self.indent_level -= 1

def pretty_print_ast(source_code):
    tree = ast.parse(source_code)
    printer = ASTPrettyPrinter()
    printer.visit(tree)

def generate_token_classes_and_p_list_from_p_list(p_list, PATH_NAME):
    print(""" 
    Please run the simulation once, 
    because the type of places and tokens are inferred at runtime.
          """)
    token_classes = ""
    set_of_token_types = {}
    all_place = []
    for place in p_list:
        fields = place.type_annotations
        # Filter out empty strings (empty fields)
        if tuple(fields) in set_of_token_types:
            all_place.append((place.id, set_of_token_types[tuple(fields)]))
            continue
        if len(fields) == 0:
            all_place.append((place.id, 'EmptyToken'))
            continue
        if len(fields) > 0:
            # Create class name
            if len(fields) > 3:
                class_name_suffix = ''.join([field[0] for field in fields])
            else:
                class_name_suffix = '_'.join([field for field in fields])
            class_name = "token_class_" + class_name_suffix
            all_place.append((place.id, class_name))
            set_of_token_types[tuple(fields)] = class_name
            # Generate token class
            token_classes += "CREATE_TOKEN_TYPE(\n"
            token_classes += f"{class_name}," + "\n"
            for field in fields:
                token_classes += f"int {field};"+"\n"
            dict_fields = [f"    dict->operator[](\"{field}\")={field}" for field in fields]
            setup_dict = ";\n".join(dict_fields) +";"
            dictionary_func = AS_DICTIONARY.format(dict=setup_dict)
            token_classes += dictionary_func
            token_classes += ")\n\n"
    
    with open(f"{PATH_NAME}/token_types.hh", 'w') as f:
        include = TOKEN_TYPE_HH_INCLUDE
        common = ""
        enddefine = """#endif"""
        f.write(include + common + token_classes + enddefine)
        
    with open(f"{PATH_NAME}/places.hh", 'w') as f:
        place_declaration = PLACE_HH_INCLUDE
        defined = set()
        for p, p_type in all_place:
            if p in defined:
                continue
            p_type = p_type if p_type != 'EmptyToken' else ""
            place_declaration += """extern Place<{p_type}> {p};\n""".format(p=p, p_type=p_type)
            defined.add(p)
        f.write(place_declaration+"#endif")
    
    with open(f"{PATH_NAME}/places.cc", 'w') as f:
        place_definition = """#include "places.hh"\n"""
        defined = set()
        for p, p_type in all_place:
            if p in defined:
                continue
            p_type = p_type if p_type != 'EmptyToken' else ""
            place_definition += """Place<{p_type}> {p}(\"{p}\");\n""".format(p=p, p_type=p_type)
            defined.add(p)
        f.write(place_definition)
    
    place_type_dict = {}
    for p_id, p_type in all_place:
        place_type_dict[p_id] = p_type
    return set_of_token_types, place_type_dict

def generate_lpn_setup(p_list, set_of_token_types, PATH_NAME):
    place_declaration = SETUP_PLACE_HH_INCLUDE
    setup_place_code = """void lpn_init() {\n\n"""
    defined = set()
    for place in p_list:
        if len(place.tokens_init) != 0:
            if len(place.type_annotations) == 0:
                setup_place_code += """{indent}for (int i = 0; i < {tk_len}; ++i){{\n{indent2}NEW_TOKEN(EmptyToken, new_token);\n{indent2}{pid}.pushToken(new_token);\n{indent}}}\n""".format(tk_len=len(place.tokens_init), pid=place.id, indent=INDENT, indent2=INDENT*2)
                setup_place_code += "\n"
                continue
            
            'use for loop to condense the code if the value are all the same'
            value_tuple = tuple(place.tokens_init[0].prop(key) for key in place.type_annotations)
            unified_value = True
            for ith, tk in enumerate(place.tokens_init):
                value_tuple_tmp = tuple(tk.prop(key) for key in place.type_annotations)
                if value_tuple_tmp != value_tuple:
                    unified_value = False
                    break
            if unified_value:
                tk = place.tokens_init[0]
                init_token_code = ""
                tk_name = f"{place.id}_tk"
                token_type_str = set_of_token_types[tuple(place.type_annotations)]
                init_token_code += """{indent2}NEW_TOKEN({token_type_str}, {token_name});\n""".format(indent2=INDENT*2, token_type_str=token_type_str, token_name=tk_name)
                for key in place.type_annotations:
                    init_token_code += """{indent2}{tk_name}->{key} = {value};\n""".format(indent2=INDENT*2, tk_name=tk_name, key=key, value=tk.prop(key))

                setup_place_code += """{indent}for (int i = 0; i < {tk_len}; ++i){{\n{init_token}{indent2}{pid}.pushToken({tk_name});\n{indent}}}\n""".format(
                    tk_len=len(place.tokens_init), 
                    tk_name=tk_name,
                    init_token=init_token_code, 
                    pid=place.id, 
                    indent=INDENT, 
                    indent2=INDENT*2)
                setup_place_code += "\n"
                continue
            
            setup_place_code += """\n{indent}for (int i = 0; i < {tk_len}; ++i){{\n""".format(tk_len=1, indent=INDENT)
            for ith, tk in enumerate(place.tokens_init):
                tk_name = f"{place.id}_{ith}_tk"
                token_type_str = set_of_token_types[tuple(place.type_annotations)]
                setup_place_code += """{indent}NEW_TOKEN({token_type_str}, {token_name});\n""".format(indent=INDENT, token_type_str=token_type_str, token_name=tk_name)
                for key in place.type_annotations:
                    setup_place_code += """{indent}{tk_name}->{key} = {value};\n""".format(indent=INDENT, tk_name=tk_name, key=key, value=tk.prop(key))
                setup_place_code += """{indent}{pid}.pushToken({tk_name});\n""".format(indent=INDENT, pid=place.id, tk_name=tk_name)
            setup_place_code += "\n"
            setup_place_code += """{indent}}}\n""".format(indent=INDENT)
    setup_place_code += "}\n"
    endif = """#endif"""
    
    with open(f"{PATH_NAME}/lpn_init.hh", 'w') as f:
        f.write(place_declaration + setup_place_code + endif)


import typing 
def translate_transitions(t_list, place_type_dict, PATH_NAME):
    list_cnt = 0
    dict_cnt = 0
    top_level_list_value_dec = ""
    top_level_dict_value_dec = ""
    def create_const_named_list(list_, first_value):
        nonlocal list_cnt
        nonlocal top_level_list_value_dec
        var_name = f"list_{list_cnt}"
        list_cnt += 1
        if isinstance(first_value, int):
            top_level_list_value_dec += """std::vector<int> {var_name} = {{{list_value}}};\n""".format(var_name=var_name, list_value=", ".join([str(v) for v in list_]))
        elif isinstance(first_value, Place):
            token_class = place_type_dict[first_value.id]
            top_level_list_value_dec += """std::vector<Place<{token_class}>*> {var_name} = {{{list_value}}};\n""".format(token_class=token_class, var_name=var_name, list_value=", ".join([f"&{p.id}"for p in list_]))
        
        return var_name
    
    def create_const_named_dict(dict_, key_type, value_type):
        nonlocal dict_cnt
        nonlocal top_level_dict_value_dec
        var_name = f"dict_{dict_cnt}"
        dict_cnt += 1
        if key_type != int or value_type != int:
            raise Exception("Dictionary key and value should be int")
        dict_value = "\n"
        for key, value in dict_.items():
            dict_value += """{{{key}, {value}}}, \n""".format(key=key, value=value)
        top_level_dict_value_dec += """std::map<int, int> {var_name} = {{{dict_value}}};\n""".format(var_name=var_name, dict_value=dict_value)
        
        return var_name

    def prep_args(args, types):
        list_of_str = []
        for arg, (k, expected_type) in zip(args, types.items()):
            if isinstance(arg, int):
                arg_str = str(arg)
                if "CstStr" in arg_str:
                    enum_name = arg_str.split(".")[1]
                    list_of_str.append(f"(int)CstStr::{enum_name.upper()}")
                else:
                    list_of_str.append(str(arg))
                
            elif isinstance(arg, Place):
                list_of_str.append(f"&{arg.id}")
        
            elif isinstance(arg, typing.List):
                v = arg[0]
                if isinstance(v, int):
                    var_name = create_const_named_list(arg, v)
                    list_of_str.append(var_name)
                elif isinstance(v, Place):
                    var_name = create_const_named_list(arg, v)
                    list_of_str.append(var_name)
                else:
                    raise TypeError(f"(list)Parameter must be of type List[int] or List[Place]")
            
            elif isinstance(arg, typing.Dict):
                first_arg, second_arg = typing.get_args(expected_type)
                if first_arg != int or second_arg != int:
                    raise Exception("Dictionary key and value should be int")
                var_name = create_const_named_dict(arg, first_arg, second_arg)
                list_of_str.append(var_name)
            else:
                raise Exception("Arguments to functions should be either int or Place")
        return ', '.join(list_of_str)
    def prep_edge_func(func):
        return """{func_name}({args})""".format(func_name=func.edge_expr.name, args=prep_args(func.args, func.edge_expr.param_types))
    
    trans_code = ""
    for t in t_list:
        t_id = t.id
        delay_f = prep_edge_func(t.delay_f)
        p_input = """{{{p_list}}}""".format(p_list=",".join([f"&{p.id}" for p in t.p_input]))
        p_output = """{{{p_list}}}""".format(p_list=",".join([f"&{p.id}" for p in t.p_output]))
        pi_w = """{{{func_list}}}""".format(func_list=",".join([ prep_edge_func(func) for func in t.pi_w]))
        po_w = """{{{func_list}}}""".format(func_list=",".join([ prep_edge_func(func) for func in t.po_w]))
        if len(t.pi_w_threshold) != 0:
            pi_w_threshold = """{{{func_list}}}""".format(func_list=", ".join([ prep_edge_func(func) for func in t.pi_w_threshold])) 
        else:
            pi_w_threshold = """{{{func_list}}}""".format(func_list=", ".join("NULL" for _ in t.p_input))
        if len(t.pi_guard) != 0:
            pi_guard = """{{{func_list}}}""".format(func_list=", ".join([ prep_edge_func(func) for func in t.pi_guard]))
        else:
            pi_guard = """{{{func_list}}}""".format(func_list=", ".join("NULL" for _ in t.p_input))
        if t.pip != None:
            pip = prep_edge_func(t.pip)
        else:
            pip = "NULL"
        trans_code += DEF_TRANS.format(t_id=t_id, delay_f=delay_f, p_input=p_input, p_output=p_output, pi_w=pi_w, po_w=po_w, pi_w_threshold=pi_w_threshold, pi_guard=pi_guard, pip=pip)
        # break
    ifndef = "#ifndef __TRANSITIONS__\n#define __TRANSITIONS__\n"
    header = TRANS_HH_INCLUDE
    endif = "#endif"
    with open(f"{PATH_NAME}/transitions.hh", 'w') as f:
        f.write(
            ifndef + 
            header + 
            top_level_list_value_dec + 
            top_level_dict_value_dec + 
            trans_code + 
            endif)

def generate_all_edge_func(all_edge_func, set_of_token_types, enums, int_only):
    list_of_template_names = ["T", "U", "V", "W", "K", "M", "N", "O", "P", "Q", "R", "S", "X", "Y", "Z"]
    all_edge_func_code = ""
    def prep_outter_arg_list(edge_expr):
        list_of_str = []
        place_temp_cnt = 0
        for i, (arg_name, type_) in enumerate(edge_expr.param_types.items()):
            if type_ == Place:
                list_of_str.append(f"Place<{list_of_template_names[place_temp_cnt]}>* {arg_name}")
                place_temp_cnt += 1
            elif type_ == int:
                list_of_str.append(f"int {arg_name}")
            elif type_ == List[int]:
                list_of_str.append(f"std::vector<int>& {arg_name}")
                # return None
            elif type_ == List[Place]:
                list_of_str.append(f"std::vector<Place<{list_of_template_names[place_temp_cnt]}>*>& {arg_name}")
                place_temp_cnt += 1
                # return None
            elif type_ == Dict[int, int]:
                list_of_str.append(f"std::map<int, int>& {arg_name}")
                # return None
            else:
                return None
        return ', '.join(list_of_str)
    
    def prep_int_place_arg_list(edge_expr):
        list_of_str = []
        for i, (arg_name, type_) in enumerate(edge_expr.param_types.items()):
            if type_ == int:
                list_of_str.append(f"{arg_name}")
            if type_ == Place:
                'because Place<T>* ptr, this var needs to be captured by value, otherwise its lost'
                list_of_str.append(f"{arg_name}")
        if len(list_of_str) == 0:
            return ""
        else:
            return ', '+' ,'.join(list_of_str)
    
    def cnt_num_place_templates(edge_expr):
        cnt = 0
        for type_ in edge_expr.param_types.values():
            if type_ == Place:
                cnt += 1
            elif type_ == List[Place]:
                cnt += 1
        return cnt 
    
    def get_return_type(edge_expr):
        if isinstance(edge_expr, OutWeightFunc):
            return "void", "BasePlace*", "out_weight"
        elif isinstance(edge_expr, InWeightFunc):
            return "int", "", "inp_weight"
        elif isinstance(edge_expr, DelayFunc):
            return "uint64_t", "", "delay"
        elif isinstance(edge_expr, GuardFunc):
            return "bool", "", "guard" 
        elif isinstance(edge_expr, ThresholdFunc):
            return "int", "", "threshold"
        else:
            assert(0)
    func_processed = set()
    for edge_func in all_edge_func:
        if edge_func.edge_expr.name in func_processed:
            continue
        # print(" ====== processing edge func ==== ", edge_func.edge_expr.name)
        func_processed.add(edge_func.edge_expr.name)
        num_template = cnt_num_place_templates(edge_func.edge_expr)
        func_outter = ""
        outter_name = edge_func.edge_expr.name
        outter_types_dict = edge_func.edge_expr.param_types
        return_type, arg_list, inner_func_name = get_return_type(edge_func.edge_expr)
        outter_arg_list = prep_outter_arg_list(edge_func.edge_expr)
        if outter_arg_list is None:
            print("skipping because lpn2sim can't handle, please mannual rewrite this edge func : ", edge_func.edge_expr.name)
            continue
        if num_template > 0:
            func_outter += """template<{list_symb}>\n""".format(list_symb=", ".join([ f"typename {t_name}" for t_name in list_of_template_names[:num_template]]))
        func_outter += """std::function<{return_type}({arg_list})> {outter_name}({outter_arg_list})""".format(
                    return_type=return_type,
                    outter_name=outter_name, 
                    arg_list=arg_list, 
                    outter_arg_list=outter_arg_list)
        func_outter += " {\n"
        arg_list_with_name = arg_list
        if arg_list == "BasePlace*":
            arg_list_with_name = "BasePlace* output_place"
        func_outter += """{indent}auto {inner_func_name} = [&{outter_int_arg_list}]({arg_list_with_name}) -> {return_type} {{\n""".format(
            indent=INDENT,
            inner_func_name=inner_func_name, 
            outter_int_arg_list=prep_int_place_arg_list(edge_func.edge_expr),
            return_type=return_type, 
            arg_list_with_name=arg_list_with_name)
        inner_souce_with_install = inspect.getsource(edge_func.edge_expr.func)
        inner_body = dedent("\n".join(inner_souce_with_install.split('\n')[2:]))
        # print("inner_body", inner_body)
        tree = ast.parse(inner_body)
        emitter = CppFunctionGenerator()
        emitter.set_of_token_types = set_of_token_types
        emitter.enums = enums
        emitter.convert_to_double = not int_only
        if int_only:
            emitter.gen_klee_mode = True
        emitter.visit(tree)
        body_code = indent(emitter.cpp_code, f"{INDENT}"*2)
        func_outter += body_code+"""{indent}}};\n""".format(indent=INDENT)
        func_outter += """{indent}return {inner_func_name};\n}};\n""".format(indent=INDENT, inner_func_name=inner_func_name)
        # print(func_outter)
        all_edge_func_code += func_outter
    return all_edge_func_code

def generate_all_normal_func(all_edge_func, set_of_token_types, enums, int_only):
    list_of_template_names = ["T", "U", "V", "W", "K", "M", "N", "O", "P", "Q", "R", "S", "X", "Y", "Z"]
    all_edge_func_code = ""
    def prep_arg_list(edge_expr):
        list_of_str = []
        place_template_cnt = 0
        for i, (arg_name, type_) in enumerate(edge_expr.param_types.items()):
            if type_ == Place:
                list_of_str.append(f"Place<{list_of_template_names[place_template_cnt]}>* {arg_name}")
                place_template_cnt += 1
            elif type_ == int:
                list_of_str.append(f"int {arg_name}")
        return ', '.join(list_of_str)
    
    def cnt_num_place_templates(edge_expr):
        cnt = 0
        for type_ in edge_expr.param_types.values():
            if type_ == Place:
                cnt += 1
        return cnt 
    
    def get_return_type(edge_expr):
        if isinstance(edge_expr, IntFunc):
            return "int"
        elif isinstance(edge_expr, VoidFunc):
            return "void"
        else:
            raise Exception("Function type not supported")
        
    func_processed = set()
    for edge_func in all_edge_func:
        func_code = ""
        if edge_func.name in func_processed:
            continue
        func_processed.add(edge_func.name)
        num_template = cnt_num_place_templates(edge_func)
        func_name = edge_func.name
        return_type = get_return_type(edge_func)
        arg_list = prep_arg_list(edge_func)
        if num_template > 0:
            func_code += """template<{list_symb}>\n""".format(list_symb=", ".join([ f"typename {t_name}" for t_name in list_of_template_names[:num_template]]))
        func_code += """{return_type} {func_name}({arg_list})""".format(
                    return_type=return_type,
                    func_name=func_name, 
                    arg_list=arg_list)
        func_code += " {\n"
        inner_souce_with_install = inspect.getsource(edge_func.func)
        inner_body = dedent("\n".join(inner_souce_with_install.split('\n')[2:]))
        tree = ast.parse(inner_body)
        emitter = CppFunctionGenerator()
        emitter.set_of_token_types = set_of_token_types
        emitter.enums = enums
        emitter.convert_to_double = not int_only
        if int_only:
            emitter.gen_klee_mode = True

        emitter.visit(tree)
        body_code = indent(emitter.cpp_code, f"{INDENT}"*2)
        func_code += body_code+"""}};\n""".format(indent=INDENT)
        all_edge_func_code += func_code
    return all_edge_func_code

def retrieve_normal_func(edge_f):
    # print(edge_f.edge_expr.extern_func)
    return edge_f.edge_expr.extern_func

def generate_func_code(func_code, PATH_NAME):
    with open(f"{PATH_NAME}/lpn_funcs.hh", 'w') as f:
        header = FUNCS_HH_INCLUDE
        endif = "#endif"
        f.write(header+func_code+endif)

def generate_enums(enums):
    if enums is None:
        return ""
    enum_code = "\nenum class CstStr {\n"
    for name, member in enums.__members__.items():
        enum_code += f"    {name.upper()}={member.value},\n"
    return enum_code + "};\n\n"


def generate_simulator_based_on_t_list(t_list, PATH_NAME):
        t_list_str = ', '.join([ f"&{_t.id}" for _t in t_list ])
        t_size = len(t_list)
        t_list_def = """Transition* t_list[T_SIZE] = {{ {t_list_str} }};""".format(t_list_str=t_list_str)
        sim_code = SIM_CC.format(indent=INDENT, t_list_def=t_list_def, T_SIZE=t_size)
        with open(f"{PATH_NAME}/sim.cc", "w") as f:
            f.write(sim_code)



def pylpn2cpp_no_sim(p_list: List[Place], t_list: List[Transition], enums: IntEnum, PATH_NAME="LPNCPP", int_only=False):
    dir_path = Path(PATH_NAME)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)

    set_of_token_types, place_type_dict = generate_token_classes_and_p_list_from_p_list(p_list, PATH_NAME)
    translate_transitions(t_list, place_type_dict, PATH_NAME)

    all_edge_func = []
    all_normal_func = []
    for t in t_list:
        for edge_f in t.pi_w:
            all_edge_func.append(edge_f)
            all_normal_func.extend(retrieve_normal_func(edge_f))
    for t in t_list:
        for edge_f in t.po_w:
            all_edge_func.append(edge_f)
            all_normal_func.extend(retrieve_normal_func(edge_f))
    for t in t_list:
        if t.pi_w_threshold != None:
            for edge_f in t.pi_w_threshold:
                if edge_f != None:
                    all_edge_func.append(edge_f)
                    all_normal_func.extend(retrieve_normal_func(edge_f))
    for t in t_list: 
        if t.pi_guard != None:
            for edge_f in t.pi_guard:
                if edge_f != None:
                    all_edge_func.append(edge_f)
                    all_normal_func.extend(retrieve_normal_func(edge_f))
    for t in t_list:
        if t.pip != None:
            all_edge_func.append(t.pip)
            all_normal_func.extend(retrieve_normal_func(t.pip))

    for t in t_list:
        if t.delay_f != None:
            all_edge_func.append(t.delay_f)
            all_normal_func.extend(retrieve_normal_func(t.delay_f))

    all_normal_func_code = generate_all_normal_func(all_normal_func, set_of_token_types, enums, int_only)
    all_edge_func_code = generate_all_edge_func(all_edge_func, set_of_token_types, enums, int_only)
    enum_code = generate_enums(enums)
    generate_func_code(enum_code+all_normal_func_code+all_edge_func_code, PATH_NAME)  
    return set_of_token_types

def pylpn2cpp(p_list: List[Place], t_list: List[Transition], enums: IntEnum, PATH_NAME="LPNCPP"):
    set_of_token_types = pylpn2cpp_no_sim(p_list, t_list, enums, PATH_NAME, int_only=False)
    generate_simulator_based_on_t_list(t_list, PATH_NAME)
    generate_lpn_setup(p_list, set_of_token_types, PATH_NAME)