import math

def map_range(value, from_min, from_max, to_min, to_max):
    """Performs a linear interpolation of a value within the range of [from_min, 
        from_max] to another range of [to_min, to_max].
    """
    from_range = from_max - from_min
    to_range = to_max - to_min
    value_scaled = (value - from_min)/float(from_range)
    return to_min + (value_scaled * to_range)

def clamp(value, vmin, vmax):
    """Clamp value between vmin and vmax.
    """
    return max([min([value, vmax]), vmin])

def arange(start, stop, step):
    """Returns evenly spaced values within a given interval.
    
    The function is similar to NumPy's *arange* function.
    """
    if math.fabs(stop - (start + step)) > math.fabs(stop - start):
        raise ValueError("Please check the sign of step.")
    
    len = int(math.ceil((stop - start)/float(step)))
    return [start + i*step for i in range(len)]


def allclose(l1, l2, tol = 1e-05):
    """Returns True if two lists are element-wise equal within a tolerance.
    
    The function is similar to NumPy's *allclose* function.
    """
    for a, b in zip(l1, l2):
        if math.fabs(a - b) > tol:
            return False
    return True


def range_geometric_row(number, d, r=1.1):
    """Returns a list of numbers with a certain relation to each other.

    The function divides a number into d numbers [n0, n1, ...] such that 
    their sum is number and the relation between the numbers is defined with 
    n1 = n0 / r, n2 = n1 / r, n3 = n2 / r, ...
    """
    if r <= 0:
        raise ValueError("r must be > 0")
        
    n0 = number/((1 - (1/r)**d)/(1 - 1/r))
    
    numbers = [n0]
    for i in range(d - 1):
        numbers.append(numbers[-1] / r)

    return numbers
    
if __name__ == "__main__":
    print(map_range(2, 0, 10, 0, 100))
    print(arange(3, -4, -0.2))
