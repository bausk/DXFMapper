
def GetPoints(Entity, Precision):
    #Points = []
    if Entity.dxftype == "LINE":
        point1 = Entity.start
        point1 = tuple([round(x, Precision) for x in point1])
        point2 = Entity.end
        point2 = tuple([round(x, Precision) for x in point2])
        return [point1, point2]
    elif Entity.dxftype == "CIRCLE":
        point = Entity.center
        point = tuple([round(x, Precision) for x in point])
        return [point]
    elif Entity.dxftype in ("LWPOLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point + (0.0,))
        return Points
    elif Entity.dxftype in ("SOLID", "FACE"):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        return Points
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        return Points
