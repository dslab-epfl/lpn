# We'll implement a Python equivalent of the provided C-based Groebner basis code.
# We will:
# 1) Represent monomials as integer lists/tuples.
# 2) Store polynomials with a dictionary { exponent_tuple: coefficient }.
# 3) Support ring with variable ordering (lex, grevlex) and a variable permutation.
# 4) Provide spoly, polynomial_rem, reduce_initial, etc.
# 5) For each new nonzero polynomial discovered, we'll track it with an incrementing ID.
#
# Disclaimer:
#  - This code ignores large integer issues (like the request). Coefficients are normal ints.
#  - This is a demonstration, not production-level code.

import itertools
from collections import defaultdict
import sympy
from sympy import groebner, symbols

# We define a global ID generator for polynomials:
def unique_pair_id(a: int, b: int) -> int:
    """Generate a unique ID for an unordered pair (a, b) using Cantor's pairing function."""
    a, b = min(a, b), max(a, b)  # Ensure (a, b) is always ordered
    return (a + b) * (a + b + 1) // 2 + b + 10000

class Ring:
    """A ring structure that contains ordering info and variable permutations."""
    def __init__(self, num_vars, order="lex", var_order=None):
        self.num_vars = num_vars  # dimension
        self.order_type = order   # 'lex' or 'grevlex'
        if var_order is None:
            # default variable order is [0, 1, 2, ...]
            self.var_order = list(range(num_vars))
        else:
            self.var_order = var_order
        self.poly_id_counter = itertools.count()


    def monomial_compare(self, a, b):
        """
        Compare two monomials a, b each a list/tuple of exponents.
        Return -1 if a < b, 0 if equal, 1 if a > b.
        We apply the variable permutation self.var_order first.
        Then apply lex or grevlex.
        """
        # Permute
        pa = tuple(a[i] for i in self.var_order)
        pb = tuple(b[i] for i in self.var_order)
        if self.order_type == "lex":
            # compare left to right
            if pa == pb:
                return 0
            for x, y in zip(pa, pb):
                if x > y:
                    return 1
                elif x < y:
                    return -1
            return 0
        elif self.order_type == "grevlex":
            # Compare total degree first (larger degree is smaller in grevlex)
            sa = sum(pa)
            sb = sum(pb)
            if sa > sb:
                return 1  # Bigger total degree => smaller in grevlex
            elif sa < sb:
                return -1  # Smaller total degree => bigger in grevlex

            # If total degrees are equal, compare from right to left
            for a, b in zip(reversed(pa), reversed(pb)):
                if a < b:
                    return 1  # Smaller exponent => bigger in grevlex
                elif a > b:
                    return -1  # Larger exponent => smaller in grevlex

            return 0  # Monomials are identical
        else:
            raise ValueError("Unknown order type: " + self.order_type)

class Polynomial:
    """
    A polynomial in ring. We store it as a dict {exptuple: coeff}, ignoring zero coeffs.
    We also track a unique ID for each polynomial.
    """
    def __init__(self, terms, ring, give_id = False):
        """
        terms: dict of exponent-tuple -> coefficient (int)
        ring: Ring object
        """
        self.ring = ring
        self.terms = {}
        for exp, coeff in terms.items():
            # convert QQ -> ZZ by taking int
            coeff = int(coeff) 
            if coeff != 0:
                self.terms[tuple(exp)] = coeff
        if give_id:
            self.id = next(ring.poly_id_counter)  # unique ID for this polynomial
            print("Assigning ID", self.id)
        else:
            self.id = None
        # optionally, we might want to keep them sorted, but we can do so on the fly.

    def assign_id(self, poly):
        self.id = poly.id

    def assign_new_id(self):
        self.id = next(self.ring.poly_id_counter)
        print("Assigning ID", self.id)

    def is_zero(self):
        return len(self.terms) == 0

    def copy(self):
        return Polynomial(self.terms.copy(), self.ring)

    def leading_term(self):
        """Return (exp, coeff) for the leading term under ring's ordering, or (None, 0)."""
        if not self.terms:
            return None, 0
        # find max under ring ordering
        best_exp = None
        for e in self.terms:
            if best_exp is None:
                best_exp = e
            else:
                c = self.ring.monomial_compare(e, best_exp)
                if c == 1:  # e > best_exp
                    best_exp = e
        return best_exp, self.terms[best_exp]

    def __len__(self):
        return len(self.terms)
    
    def __str__(self):
        if self.is_zero():
            return f"Poly#{self.id}: 0"
        parts = []
        for exp, coeff in self.terms.items():
            parts.append(f"{coeff}*x^{exp}")
        return f"Poly#{self.id}: " + " + ".join(parts)

    def __repr__(self):
        return self.__str__()
    

# Basic polynomial add
def polynomial_add(p1, p2):
    """Return p1 + p2."""
    assert p1.ring == p2.ring
    d = defaultdict(int)
    for e, c in p1.terms.items():
        d[e] += c
    for e, c in p2.terms.items():
        d[e] += c
    return Polynomial(d, p1.ring)

# Basic polynomial sub
def polynomial_sub(p1, p2):
    """Return p1 - p2."""
    assert p1.ring == p2.ring
    d = defaultdict(int)
    for e, c in p1.terms.items():
        d[e] += c
    for e, c in p2.terms.items():
        d[e] -= c
    return Polynomial(d, p1.ring)

# Multiply polynomial p by monomial m with coefficient c
def polynomial_mul_monom(p, m, c):
    """ m is exponent tuple, c is int."""
    d = defaultdict(int)
    for e, coeff in p.terms.items():
        new_exp = tuple(ei + mi for ei, mi in zip(e, m))
        d[new_exp] += coeff * c
    return Polynomial(d, p.ring)

# spoly
def spoly(p1, p2):
    """S = lcm(LM(p1), LM(p2))/LM(p1)*p1 - lcm(LM(p1), LM(p2))/LM(p2)*p2"""
    e1, c1 = p1.leading_term()
    e2, c2 = p2.leading_term()
    if e1 is None or e2 is None:
        # one is zero => s-poly is 0
        return Polynomial({}, p1.ring)
    # LCM of exponents
    lcm_exp = tuple(max(a, b) for a, b in zip(e1, e2))
    # multiply p1 by (lcm_exp - e1) and * c2
    diff1 = tuple(l - e for l, e in zip(lcm_exp, e1))
    part1 = polynomial_mul_monom(p1, diff1, c2)

    # multiply p2 by (lcm_exp - e2) and * c1
    diff2 = tuple(l - e for l, e in zip(lcm_exp, e2))
    part2 = polynomial_mul_monom(p2, diff2, c1)

    # subtract
    return polynomial_sub(part1, part2)

# polynomial_rem: p REM G
#   Repeatedly reduces p by the leading term of polynomials in G until no more reduction.

def polynomial_rem(p, G):
    # print(f"Reducing {p} by {len(G)} polynomials")
    p = p.copy()
    round = 0
    while True:
        changed = False
        if p.is_zero():
            return p, round
        e_p, c_p = p.leading_term()
        # print(f"EP = {e_p}, coeff = {c_p}")
        done = False
        for g in G:
            e_g, c_g = g.leading_term()
            if e_g is None:
                continue
            # check if e_p is >= e_g
            can_div = True
            for x, y in zip(e_p, e_g):
                if x < y:
                    can_div = False
                    break
            if can_div:
                # factor = e_p - e_g in exponents
                factor_exp = tuple(x - y for x, y in zip(e_p, e_g))
                # multiply g by that factor with 1/c_g? ignoring big integer issues, we'll do integer.
                # But c_g might not be 1.
                # We'll just do the naive approach ignoring fraction.
                # If we want to do it properly in rationals, we do factor = 1/c_g, but ignoring big number.
                
                # print(f"c_p = {c_p}, c_g = {c_g}")
                sub_poly = polynomial_mul_monom(g, factor_exp, c_p/c_g) # ignoring c_g for simplicity
                p = polynomial_sub(p, sub_poly)
                changed = True
                round += 1
                print(f"Round {round}")
                break
        if not changed:
            break
    return p, round

# reduce_initial
# does a naive pass of p.rem(...) for i in range(len(F))
def reduce_initial(F):
    # F is a list of polynomials.
    # We'll do a pass like in the C code.
    i = 0
    while i < len(F):
        # reduce F[i] with all F[:i]
        p, _ = polynomial_rem(F[i], F[:i])
        F[i] = p
        i += 1
    # remove any that is zero?
    # or keep them?

    # maybe remove zero polynomials
    F2 = [f for f in F if not f.is_zero()]
    return F2

def reduce(F):
    # We'll do a naive pass of p.rem(...) for i in range(len(F))
    i = 0
    G = []
    while i < len(F):
        # reduce F[i] with all F[:i]
        p, _ = polynomial_rem(F[i], F[:i] + F[i+1:])
        # F[i] = p
        G.append(p)
        i += 1

    G2 = [f for f in G if not f.is_zero()]
    return G2

# check zero
def polynomial_is_zero(p):
    return p.is_zero()


# We'll implement a function for Buchberger's algorithm that also logs newly added polynomials.
def buchberger(F, ring):
    from collections import deque
    """Compute the Groebner basis using a FIFO queue to track polynomial pairs efficiently."""
    
    # Initialize polynomial set with unique IDs
    G = {i: poly for i, poly in enumerate(F)}  # Indexed polynomials
    fifo = deque([(i, 0) for i in range(len(F))])  # Generator queue: (my_poly_id, pair_poly_id)
    print("Initial FIFO:", fifo)
    new_polys_log = {}  # Log of new polynomials added
    new_polys_log["get_id"] = {}
    new_polys_log["poly_stats"] = {}
    new_polys_log["spoly_stats"] = {}

    for id, g in G.items():
        new_polys_log["poly_stats"][id] = {"len": len(g), "nonzero": True}
   
    while fifo:
        my_poly_id, pair_poly_id = fifo.popleft()
        assert(my_poly_id in G)
        if(pair_poly_id not in G):
            if pair_poly_id + 1 != my_poly_id:
                fifo.append((my_poly_id, pair_poly_id + 1))
            continue
        # Avoid recomputing trivial (i, i) pairs
        if my_poly_id == pair_poly_id:
            continue

        # Compute S-polynomial
        s = spoly(G[my_poly_id], G[pair_poly_id])
        s.assign_new_id()  # Assign unique ID to new S-poly

        # Reduce polynomial
        r, round = polynomial_rem(s, list(G.values()))  # Reduce modulo current basis
        r.assign_id(s)  # Maintain ID consistency
        new_polys_log["get_id"][unique_pair_id(my_poly_id, pair_poly_id)] = r.id
        # new_polys_log["poly_stats"][r.id] = {"nonzero":False}
        new_polys_log["poly_stats"][r.id] = {"nonzero":False}
        # new_polys_log["poly_stats"][r.id] = 0 #{"nonzero":False}
        new_polys_log["spoly_stats"][r.id] = {"round": round}

        if not r.is_zero():
            new_polys_log["poly_stats"][r.id]["nonzero"] = True
            # new_polys_log["poly_stats"][r.id] = 1
            # Add new polynomial to the Groebner basis set
            # new_poly_id = len(G)
            G[r.id] = r
            # G[new_poly_id] = r

            # Add new generator to FIFO queue
            fifo.append((r.id, 0))

        # Continue advancing the generator in FIFO queue if possible
        if pair_poly_id + 1 != my_poly_id:
            fifo.append((my_poly_id, pair_poly_id + 1))

    # for id, g in G.items():
    #     new_polys_log["poly_stats"][id]["len"] = len(g) 

    return list(G.values()), new_polys_log


# def buchberger(F, ring):
#     # optionally do initial reduce
#     F = reduce_initial(F)

#     # pairs
#     G = list(F)  # copy
#     new_polys_log = []  # store new polynomials that appear

#     done = False
#     while not done:
#         done = True
#         pairs = []
#         for i in range(len(G)):
#             for j in range(i+1, len(G)):
#                 pairs.append((i,j))
#         for (i,j) in pairs:
#             s = spoly(G[i], G[j])
#             s.assign_new_id()
#             r = polynomial_rem(s, G)
#             r.assign_id(s)
#             new_polys_log.append(r)
#             if not r.is_zero():
#                 # add new polynomial
#                 G.append(r)
#                 done = False
#                 break  # must recompute pairs
#         # if we found something new, we'll break outer loop and redo
#     G = reduce(G)  # final reduction
#     return G, new_polys_log

########################################################################
# 2) Conversion Routines: from Sympy -> Our Polynomial, and vice versa
########################################################################

def sympy_poly_to_our(expr, ring, var_list):
    """
    Convert a Sympy polynomial 'expr' in x,y,z,... to our Polynomial format.
    var_list is the list of Sympy Symbols [x, y, z] in the EXACT order x>y>z.
    """
    # We'll parse expr.as_expr().expand() and look at each term.
    from sympy import Poly
    poly_expr = sympy.expand(expr)
    spoly = Poly(poly_expr, var_list, domain=sympy.ZZ)  # or QQ if you want rationals
    terms_dict = {}

    # Alternatively, iterate over monomials with Poly(...)
    terms_dict = {}
    for monom, coeff in spoly.as_dict().items():
        # monom is a tuple of exponents in the order of var_list
        # example: monom = (2, 1, 0) => x^2 y^1 z^0
        # We'll store it in our format: {(2,1,0): coeff}
        terms_dict[monom] = coeff

    poly = Polynomial(terms_dict, ring, give_id=True)
    return poly

def our_poly_to_sympy(p, var_list):
    """
    Convert one of our Polynomials to a Sympy expression in x,y,z.
    var_list: [x, y, z] symbolic
    """
    from sympy import Integer
    expr = 0
    for exp_tuple, coeff in p.terms.items():
        # Build x^exp_tuple[0] * y^exp_tuple[1] * z^exp_tuple[2], etc.
        mon_expr = 1
        for var, e in zip(var_list, exp_tuple):
            mon_expr *= var**e
        expr += coeff * mon_expr
    return sympy.expand(expr)

########################################################################
# 3) The Actual Test
########################################################################

def create_example_per_ring(var_order):
    # 3 variables in order x>y>z, with grevlex in our code
    num_vars = 5
    x, y, z, w, v = symbols('x y z w v', integer=True)
    # We'll define ring with 3 variables, grevlex, and var_order = [0,1,2] -> x>y>z
    order = 'grevlex'
    ring = Ring(num_vars=num_vars, order=order, var_order=var_order)

    # Example polynomials in sympy
    # f1 = x^2 + y, f2 = x*y - 1
    F_sym = []
    F_sym.append(x**3 + y**2 + w)       # Asymmetry: different degrees for x, y, w
    F_sym.append(y*z**3 - x**4 + v)     # Asymmetry: mix of high exponents and different variables
    F_sym.append(x*z - y**2 + w**2)     # Asymmetry: different variable interactions
    F_sym.append(y**2 + z**3 - 1 + v**4) # Asymmetry: mix of quadratic, cubic, and quartic terms
    F_sym.append(x**5 - y**3*z + w*v)   # Asymmetry: strong dominance of x and interaction terms
    F_sym.append(w**3 - x**2*y + z)     # Asymmetry: w has a high exponent, mix of interactions
    F_sym.append(z**2*x - w*v**2 + y)   # Asymmetry: variable v enters in squared form
    F_sym.append(x**2 + y**3*w - z*v)   # Asymmetry: y is raised higher than x
    F_sym.append(y*z*w - x**2*v**2 + 1) # Asymmetry: mix of all variables in complex ways
    F_sym.append(v**5 - w*x*y + z**2)   # Asymmetry: v has a dominant exponent

    F = []
    for f in F_sym:
        F.append(sympy_poly_to_our(f, ring, [x,y,z,v,w]))

    G_sym = groebner(F_sym, x, y, z, v, w, order=order, domain=sympy.ZZ)
    print(G_sym)
    exit(1)

    return (F, ring)

def gb_example():
    
    initial_num_polys = 10
    ordering_list = [[0,1,2,3,4], [1,0,2,3,4], [2,1,0,3,4], [3,2,1,0,4], [4,3,2,1,0], [0,4,3,2,1], [1,0,4,3,2], [2,1,0,4,3], [3,2,1,0,4], [4,3,2,1,0]]
    ordering_list = [[0,1,2,3,4]]
    path_list = []
    simplified_path_list = []
    for i, order in enumerate(ordering_list):
        path_list.append(create_example_per_ring(order))
        simplified_path_list.append((i, initial_num_polys))

    trace_list = {}
    for i, (F, ring) in enumerate(path_list):
        print(f'Ring order: {ring.var_order}')
        G_our, poly_log = buchberger(F, ring)
        for p in poly_log:
            print(f'PATH {i} LOG: {p}')

        trace_list[i] = poly_log

    # We might see that Sympy's basis and ours differ in shape but still generate the same ideal.
    print('\nDone!')
    return simplified_path_list, trace_list

# __main__ = gb_example()