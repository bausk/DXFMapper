
def GetPoints(Entity):
    #Points = []
    if Entity.dxftype == "LINE":
        return [Entity.start, Entity.end]
    elif Entity.dxftype == "CIRCLE":
        return [Entity.center]
    elif Entity.dxftype in ("LWPOLYLINE",):
        Points = []
        for point in list(Entity.points):
            Points.append(point + (0.0,))
        return Points
    elif Entity.dxftype in ("SOLID", "FACE"):
        Points = []
        for point in list(Entity.points):
            if len(point) == 2:
                Points.append(point + (0.0,))
        return Points
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in list(Entity.points):
            if len(point) == 2:
                Points.append(point + (0.0,))
        return Points
    