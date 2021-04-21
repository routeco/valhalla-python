
__all__ = ['Route', 'Locate', 'OptimizedRoute', 'Matrix', 'Isochrone', 'TraceRoute', 'TraceAttributes' , 'Height', 'TransitAvailable', 'Expansion', 'Centroid']

import json
from typing import Union, Callable

try:
    from .python_valhalla import _Route, _Locate, _OptimizedRoute, _Matrix, _Isochrone, _TraceRoute, _TraceAttributes, _Height, _TransitAvailable, _Expansion, _Centroid
except ModuleNotFoundError:
    from python_valhalla import _Route, _Locate, _OptimizedRoute, _Matrix, _Isochrone, _TraceRoute, _TraceAttributes, _Height, _TransitAvailable, _Expansion, _Centroid


def _wrapper(func: Callable, req: Union[str, dict]) -> Union[str, dict]:
    # return the type being passed, str -> str, dict -> dict
    if isinstance(req, dict):
        return json.loads(func(json.dumps(req)))
    elif not isinstance(req, str):
        raise ValueError("Request must be either of type str or dict")

    return func(req)


def Route(req: Union[str, dict]) -> Union[str, dict]:
    """Calculates a route."""
    return _wrapper(_Route, req)

def Locate(req: Union[str, dict]) -> Union[str, dict]:
    """Provides information about nodes and edges."""
    return _wrapper(_Locate, req)

def OptimizedRoute(req: Union[str, dict]) -> Union[str, dict]:
    """Optimizes the order of a set of waypoints by time."""
    return _wrapper(_OptimizedRoute, req)

def Matrix(req: Union[str, dict]) -> Union[str, dict]:
    """Computes the time and distance between a set of locations and returns them as a matrix table."""
    return _wrapper(_Matrix, req)

def Isochrone(req: Union[str, dict]) -> Union[str, dict]:
    """Calculates isochrones and isodistances."""
    return _wrapper(_Isochrone, req)

def TraceRoute(req: Union[str, dict]) -> Union[str, dict]:
    """Map-matching for a set of input locations, e.g. from a GPS."""
    return _wrapper(_TraceRoute, req)

def TraceAttributes(req: Union[str, dict]) -> Union[str, dict]:
    """Returns detailed attribution along each portion of a route calculated from a set of input locations, e.g. from a GPS trace."""
    return _wrapper(_TraceAttributes, req)

def Height(req: Union[str, dict]) -> Union[str, dict]:
    """Provides elevation data for a set of input geometries."""
    return _wrapper(_Height, req)

def TransitAvailable(req: Union[str, dict]) -> Union[str, dict]:
    """Lookup if transit stops are available in a defined radius around a set of input locations."""
    return _wrapper(_TransitAvailable, req)

def Expansion(req: Union[str, dict]) -> Union[str, dict]:
    """Returns all road segments which were touched by the routing algorithm during the graph traversal."""
    return _wrapper(_Expansion, req)

def Centroid(req: Union[str, dict]) -> Union[str, dict]:
    """Determines the ideal meeting point (centroid) for a list of locations."""
    return _wrapper(_Centroid, req)
