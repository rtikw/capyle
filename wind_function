

# wind angle in degrees, from north, clockwise
wind_angle = 0
wind_speed = 10

def wind_strength_fn(angle):
    return wind_speed * math.cos((wind_angle + angle) * (2*math.pi/360))

# wind strength to match "neighborstates"
# in directions NE,N,NW,E,W,SE,S,SW
wind_strengths = [wind_strength_fn(a) for a in [-45,0,45,-90,90,-135,180,135]]

