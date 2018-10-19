class IpMapper(object):
    """
    Allows a mapping between the the ips from clients and the server.
    """
    __next_free_id = 0
    __ip_map = {}

    @classmethod
    def get_id_from_ip(cls, ip):
        """
        Gets or generates an id for the given id.

        :param ip: The ip that should get an id.
        :type ip: str
        :return: The id for the ip.
        :rtype: int
        """
        if ip not in cls.__ip_map:
            cls.__ip_map[ip] = cls.__next_free_id
            cls.__next_free_id += 1

        return cls.__ip_map[ip]

    @classmethod
    def remove_ip_id(cls, ip):
        """
        Removes an ip and its ip from this class.

        :param ip: The ip to remove.
        :type ip: str
        """
        if ip not in cls.__ip_map:
            return

        cls.__ip_map.pop(ip)

    @classmethod
    def is_ip_already_known(cls, ip):
        """
        Checks if an ip is already known to the mapper.

        :param ip: The ip to check for.
        :type ip: str
        :return: Is the ip already known?
        :rtype: bool
        """
        return ip in cls.__ip_map

    @classmethod
    def get_ip_from_id(cls, id):
        """
        Searches for an ip with the given id.

        :param id: The id of the ip.
        :type id: int
        :return: The ip for the given id. If non was found it will return None.
        :rtype: str
        """
        if id in cls.__ip_map.values():
            return cls.__ip_map.keys()[cls.__ip_map.values().index(id)]
        return None
