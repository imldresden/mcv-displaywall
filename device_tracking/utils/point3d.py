#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python libaries imports
import math


class Point3D:
    """
    Class for representing a point in a 3D space.
    """
    def __init__(self, pos_x=0, pos_y=0, pos_z=0):
        """Initialize a point 3d object

        Args:
            posX: the x pos
            posY: the y pos
            posZ: the z pos
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z

    def __eq__(self, other):
        """Test if points equals"""
        if isinstance(other, Point3D):
            if self.pos_x == other.x and \
                    self.pos_y == other.y and \
                    self.pos_z == other.z:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __ne__(self, other):
        """Test if points negated"""
        if isinstance(other, Point3D):
            if self.pos_x != other.x or \
                    self.pos_y != other.y or \
                    self.pos_z != other.z:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __lt__(self, other):
        """Test if point one is lower point two"""
        if isinstance(other, Point3D):
            firstVector = (self.pos_x, self.pos_y, self.pos_z)
            firstVectorLength = math.sqrt(sum([i*i for i in firstVector]))
            secondVector = (other.x, other.y, other.z)
            secondVectorLength = math.sqrt(sum([i*i for i in secondVector]))
            if firstVectorLength < secondVectorLength:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __le__(self, other):
        """Test if point one is lower equal point two"""
        if isinstance(other, Point3D):
            firstVector = (self.pos_x, self.pos_y, self.pos_z)
            firstVectorLength = math.sqrt(sum([i*i for i in firstVector]))
            secondVector = (other.x, other.y, other.z)
            secondVectorLength = math.sqrt(sum([i*i for i in secondVector]))
            if firstVectorLength < secondVectorLength or \
                    firstVectorLength <= secondVectorLength:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __gt__(self, other):
        """Test if point one is larger point two"""
        if isinstance(other, Point3D):
            firstVector = (self.pos_x, self.pos_y, self.pos_z)
            firstVectorLength = math.sqrt(sum([i*i for i in firstVector]))
            secondVector = (other.x, other.y, other.z)
            secondVectorLength = math.sqrt(sum([i*i for i in secondVector]))
            if firstVectorLength > secondVectorLength:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __ge__(self, other):
        """Test if point one is larger equal point two"""
        if isinstance(other, Point3D):
            firstVector = (self.pos_x, self.pos_y, self.pos_z)
            firstVectorLength = math.sqrt(sum([i*i for i in firstVector]))
            secondVector = (other.x, other.y, other.z)
            secondVectorLength = math.sqrt(sum([i*i for i in secondVector]))
            if firstVectorLength > secondVectorLength or \
                    firstVectorLength >= secondVectorLength:
                return True
            else:
                return False
        else:
            return NotImplemented

    def __add__(self, other):
        """Add one point to another"""
        if isinstance(other, Point3D):
            self.pos_x += other.x
            self.pos_y += other.y
            self.pos_z += other.z
            return self
        else:
            return NotImplemented

    def __sub__(self, other):
        """Subtract one point from another"""
        if isinstance(other, Point3D):
            self.pos_x -= other.x
            self.pos_y -= other.y
            self.pos_z -= other.z
            return self
        else:
            return NotImplemented

    def __mul__(self, other):
        """Multiplicate one point from another"""
        if isinstance(other, (int, long, float, complex)):
            self.pos_x *= other
            self.pos_y *= other
            self.pos_z *= other
            return self
        else:
            return NotImplemented

    def __div__(self, other):
        """Dedvide one point from another"""
        if isinstance(other, (int, long, float, complex)):
            self.pos_x /= other
            self.pos_y /= other
            self.pos_z /= other
            return self
        else:
            return NotImplemented

    def __invert__(self):
        """Invert a point"""
        self.pos_x = -self.pos_x
        self.pos_y = -self.pos_y
        self.pos_z = -self.pos_z
        return self

    def __str__(self):
        """Return a good readable point 3d string"""
        return "Point3D(%.2f, %.2f, %.2f)" % (self.pos_x, self.pos_y, self.pos_z)

    def getLength(self):
        """
        Uses point to calculate the length of a vector

        Keyword arguments:
        self    --  the actual point which the function creates the vector and
        calc its length
        """
        vector = (self.pos_x, self.pos_y, self.pos_z)
        return math.sqrt(sum([i*i for i in vector]))

    def get_distance_vector(self, point=None):
        """
        Uses two points to calculate the a offset between them

        Keyword arguments:
        self, point    --  origin and destination points
        """
        return Point3D(point.x - self.pos_x, point.y - self.pos_y, point.z - self.pos_z)

    def get_distance(self, point=None):
        """
        Calculates the euler distance to the point
        :param point:
        :return: euler distance
        """
        return math.sqrt((point.pos_x - self.pos_x)*(point.pos_x - self.pos_x) +
                         (point.pos_y - self.pos_y)*(point.pos_y - self.pos_y) +
                         (point.pos_z - self.pos_z)*(point.pos_z - self.pos_z))

    def get_squared_distance(self, point=None):
        """
        Calculates the squared euler distance to the point
        :param point:
        :return: euler distance
        """
        return (point.pos_x - self.pos_x)*(point.pos_x - self.pos_x) + \
                (point.pos_y - self.pos_y)*(point.pos_y - self.pos_y) + \
                (point.pos_z - self.pos_z)*(point.pos_z - self.pos_z)
