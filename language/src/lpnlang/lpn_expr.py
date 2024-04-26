import typing

class EdgeExpr:
    def __init__(self, name, **kwargs):
        self.param_types = kwargs
        self.func = None
        self.extern_func = []
        self.name = name
    
    def install(self, func):
        self.func = func

    def register_external_func(self, list_func):
        [self.extern_func.append(func) for func in list_func]

    def __call__(self, *args):
        if len(args) != len(self.param_types.keys()):
            raise TypeError(f"Expected {len(self.param_types.keys())} parameters, got {len(args)}")
        for i, (key, expected_type) in enumerate(self.param_types.items()):
            expected_type = self.param_types.get(key)
            value = args[i]
            if value is None:
                continue
            if expected_type is None:
                raise TypeError(f"Unexpected parameter '{key}'")
            if isinstance(value, typing.List):
                if typing.get_origin(expected_type) is list:
                    first_arg = typing.get_args(expected_type)[0]
                    for v in value:
                        if not isinstance(v, first_arg):
                            raise TypeError(f"(list)Parameter '{key}' must be of type List{first_arg.__name__}")
                else:
                    raise TypeError(f"(list)Parameter '{key}' must be of type {expected_type.__name__}]")
            
            elif isinstance(value, typing.Dict):
                if typing.get_origin(expected_type) is dict:
                    first_arg, second_arg = typing.get_args(expected_type)
                    for k, v in value.items():
                        if not isinstance(k, first_arg):
                            raise TypeError(f"(dict)Parameter '{key}' must be of type Dict[{first_arg.__name__}, {second_arg.__name__}]")
                        if not isinstance(v, second_arg):
                            raise TypeError(f"(dict)Parameter '{key}' must be of type Dict[{first_arg.__name__}, {second_arg.__name__}]")
                else:
                    raise TypeError(f"(dict)Parameter '{key}' must be of type {expected_type.__name__}")
            else:
                if not isinstance(value, expected_type):
                    raise TypeError(f"(plain)Parameter '{key}' must be of type {expected_type.__name__}")
            
        return self.CallableEdgeExpr(self, args)

    class CallableEdgeExpr:
        def __init__(self, edge_expr, args):
            self.edge_expr = edge_expr
            self.args = args

        def __call__(self, binding):
            return self.edge_expr.func(binding, *self.args)

class DelayFunc(EdgeExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

class InWeightFunc(EdgeExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

class OutWeightFunc(EdgeExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    class CallableEdgeExpr:
        def __init__(self, edge_expr, args):
            self.edge_expr = edge_expr
            self.args = args

        def __call__(self, binding, output_place):
            return self.edge_expr.func(binding, output_place, *self.args)

class GuardFunc(EdgeExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

class ThresholdFunc(EdgeExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

class FuncExpr:
    def __init__(self, name, **kwargs):
        self.param_types = kwargs
        self.func = None
        self.name = name
    
    def install(self, func):
        self.func = func
    
    def __call__(self, binding, *args):
        if len(args) != len(self.param_types.keys()):
            raise TypeError(f"Expected {len(self.param_types.keys())} parameters, got {len(args)}")
        for i, (key, expected_type) in enumerate(self.param_types.items()):
            expected_type = self.param_types.get(key)
            value = args[i]
            if value is None:
                continue
            if expected_type is None:
                raise TypeError(f"Unexpected parameter '{key}'")
            if isinstance(value, typing.List):
                if typing.get_origin(expected_type) is list:
                    first_arg = typing.get_args(expected_type)[0]
                    for v in value:
                        if not isinstance(v, first_arg):
                            raise TypeError(f"(list)Parameter '{key}' must be of type List{first_arg.__name__}")
                else:
                    raise TypeError(f"(list)Parameter '{key}' must be of type {expected_type.__name__}]")
            
            elif isinstance(value, typing.Dict):
                if typing.get_origin(expected_type) is dict:
                    first_arg, second_arg = typing.get_args(expected_type)
                    for k, v in value.items():
                        if not isinstance(k, first_arg):
                            raise TypeError(f"(dict)Parameter '{key}' must be of type Dict[{first_arg.__name__}, {second_arg.__name__}]")
                        if not isinstance(v, second_arg):
                            raise TypeError(f"(dict)Parameter '{key}' must be of type Dict[{first_arg.__name__}, {second_arg.__name__}]")
                else:
                    raise TypeError(f"(dict)Parameter '{key}' must be of type {expected_type.__name__}")
            else:
                if not isinstance(value, expected_type):
                    raise TypeError(f"(plain)Parameter '{key}' must be of type {expected_type.__name__}")
    
        return self.func(binding, *args)
    
class IntFunc(FuncExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

class VoidFunc(FuncExpr):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
