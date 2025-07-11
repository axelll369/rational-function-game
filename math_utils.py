import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Union
import sympy as sp

class RationalFunction:
    """Represents a rational function and provides analysis methods"""
    
    def __init__(self, numerator: List[float], denominator: List[float]):
        """
        Initialize rational function with coefficient lists
        numerator: coefficients from highest to lowest degree
        denominator: coefficients from highest to lowest degree
        """
        self.numerator = numerator
        self.denominator = denominator
        
        # Create sympy polynomials for easier manipulation
        x = sp.Symbol('x')
        self.num_poly = sum(coeff * x**(len(numerator) - 1 - i) for i, coeff in enumerate(numerator))
        self.den_poly = sum(coeff * x**(len(denominator) - 1 - i) for i, coeff in enumerate(denominator))
        
        # Simplify by finding common factors
        self.simplified_num, self.simplified_den = self._simplify()
    
    def _simplify(self) -> Tuple[sp.Poly, sp.Poly]:
        """Simplify the rational function by canceling common factors"""
        x = sp.Symbol('x')
        
        # Factor numerator and denominator
        num_factored = sp.factor(self.num_poly)
        den_factored = sp.factor(self.den_poly)
        
        # Find GCD and simplify
        gcd = sp.gcd(self.num_poly, self.den_poly)
        simplified_num = sp.simplify(self.num_poly / gcd)
        simplified_den = sp.simplify(self.den_poly / gcd)
        
        return simplified_num, simplified_den
    
    def vertical_asymptotes(self) -> List[float]:
        """Find vertical asymptotes"""
        x = sp.Symbol('x')
        
        # Find zeros of simplified denominator
        den_zeros = sp.solve(self.simplified_den, x)
        
        # Filter out complex solutions and convert to float
        va = []
        for zero in den_zeros:
            if zero.is_real:
                va.append(float(zero))
        
        return sorted(va)
    
    def horizontal_asymptote(self) -> Optional[float]:
        """Find horizontal asymptote"""
        # Get degrees of numerator and denominator
        num_degree = sp.degree(self.simplified_num)
        den_degree = sp.degree(self.simplified_den)
        
        if num_degree < den_degree:
            return 0.0
        elif num_degree == den_degree:
            # Ratio of leading coefficients
            num_leading = float(sp.LC(self.simplified_num))
            den_leading = float(sp.LC(self.simplified_den))
            return num_leading / den_leading
        else:
            return None  # No horizontal asymptote
    
    def holes(self) -> List[Tuple[float, float]]:
        """Find holes (removable discontinuities)"""
        x = sp.Symbol('x')
        
        # Find common factors between original numerator and denominator
        gcd = sp.gcd(self.num_poly, self.den_poly)
        
        if gcd == 1:
            return []
        
        # Find zeros of the GCD
        hole_x_values = sp.solve(gcd, x)
        
        holes = []
        for x_val in hole_x_values:
            if x_val.is_real:
                x_float = float(x_val)
                # Calculate y-coordinate by substituting into simplified function
                try:
                    y_val = float(self.simplified_num.subs(x, x_val) / self.simplified_den.subs(x, x_val))
                    holes.append((x_float, y_val))
                except:
                    pass  # Skip if calculation fails
        
        return holes
    
    def x_intercepts(self) -> List[float]:
        """Find x-intercepts"""
        x = sp.Symbol('x')
        
        # Find zeros of simplified numerator
        num_zeros = sp.solve(self.simplified_num, x)
        
        x_ints = []
        for zero in num_zeros:
            if zero.is_real:
                x_ints.append(float(zero))
        
        return sorted(x_ints)
    
    def y_intercept(self) -> Optional[float]:
        """Find y-intercept"""
        x = sp.Symbol('x')
        
        # Check if x = 0 is in domain
        if self.simplified_den.subs(x, 0) == 0:
            return None
        
        try:
            y_int = float(self.simplified_num.subs(x, 0) / self.simplified_den.subs(x, 0))
            return y_int
        except:
            return None
    
    def end_behavior(self) -> str:
        """Determine end behavior"""
        ha = self.horizontal_asymptote()
        
        if ha is not None:
            if ha == 0:
                return "approaches 0"
            elif ha > 0:
                return f"approaches {ha}"
            else:
                return f"approaches {ha}"
        else:
            # Check if function goes to infinity or negative infinity
            num_degree = sp.degree(self.simplified_num)
            den_degree = sp.degree(self.simplified_den)
            
            if num_degree > den_degree:
                num_leading = float(sp.LC(self.simplified_num))
                den_leading = float(sp.LC(self.simplified_den))
                
                if (num_leading / den_leading) > 0:
                    return "approaches infinity"
                else:
                    return "approaches -infinity"
            else:
                return "approaches 0"
    
    def evaluate(self, x_val: float) -> float:
        """Evaluate the function at a given x value"""
        x = sp.Symbol('x')
        
        try:
            result = float(self.simplified_num.subs(x, x_val) / self.simplified_den.subs(x, x_val))
            return result
        except:
            return float('inf')  # Return infinity if undefined
    
    def plot(self, ax, x_range: Tuple[float, float] = (-10, 10), num_points: int = 300):
        """Plot the rational function"""
        x_vals = np.linspace(x_range[0], x_range[1], num_points)
        y_vals = []
        
        for x_val in x_vals:
            try:
                y_val = self.evaluate(x_val)
                if abs(y_val) > 50:  # Clip extreme values for better visualization
                    y_val = np.inf if y_val > 0 else -np.inf
                y_vals.append(y_val)
            except:
                y_vals.append(np.inf)
        
        y_vals = np.array(y_vals)
        
        # Plot the function
        ax.plot(x_vals, y_vals, 'b-', linewidth=1.5, label='f(x)')
        
        # Plot vertical asymptotes
        for va in self.vertical_asymptotes():
            if x_range[0] <= va <= x_range[1]:
                ax.axvline(x=va, color='r', linestyle='--', alpha=0.7, label='Vertical Asymptote')
        
        # Plot horizontal asymptote
        ha = self.horizontal_asymptote()
        if ha is not None:
            ax.axhline(y=ha, color='g', linestyle='--', alpha=0.7, label='Horizontal Asymptote')
        
        # Plot holes
        for hole_x, hole_y in self.holes():
            if x_range[0] <= hole_x <= x_range[1]:
                ax.plot(hole_x, hole_y, 'wo', markersize=6, markeredgecolor='red', markeredgewidth=1.5, label='Hole')
        
        # Plot intercepts
        for x_int in self.x_intercepts():
            if x_range[0] <= x_int <= x_range[1]:
                ax.plot(x_int, 0, 'ro', markersize=4, label='X-intercept')
        
        y_int = self.y_intercept()
        if y_int is not None:
            ax.plot(0, y_int, 'go', markersize=4, label='Y-intercept')
        
        # Set labels and grid
        ax.set_xlabel('x', fontsize=8)
        ax.set_ylabel('y', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-8, 8)  # Reasonable y-axis limits
        ax.tick_params(axis='both', which='major', labelsize=7)
        
        # Remove duplicate labels and make legend smaller
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), fontsize=6, loc='upper right')
    
    def to_latex(self) -> str:
        """Convert the function to LaTeX format"""
        x = sp.Symbol('x')
        
        # Convert coefficients to LaTeX
        num_latex = sp.latex(self.num_poly)
        den_latex = sp.latex(self.den_poly)
        
        return f"f(x) = \\frac{{{num_latex}}}{{{den_latex}}}"
    
    def __str__(self) -> str:
        """String representation of the function"""
        return f"f(x) = ({self.num_poly}) / ({self.den_poly})"
