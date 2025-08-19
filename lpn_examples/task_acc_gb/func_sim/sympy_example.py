from sympy import symbols, Poly, ZZ

# Define variables
x, y = symbols('x y')

# Define polynomials
p1 = Poly(x**2 * y, x, y, domain=ZZ)  # Dividend
p2 = Poly(4 * x * y, x, y, domain=ZZ) # Divisor

# Compute remainder
remainder = p1.rem(p2)

print(remainder)

