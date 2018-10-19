from libavg_charts.charts.chart_basis.chart_base import ChartBase


class AidLineControllerFactory(object):
    __aid_line_methods = {}

    @staticmethod
    def add_aid_line_method(aid_line_type, creation_method):
        """
        Adds an aid line controller type with a method to this factory.

        :param aid_line_type: The type for the given method.
        :type aid_line_type: AidLineType
        :param creation_method: The method that should be called with the given type.
        :type creation_method: function(chart:ChartBase, aid_line_area:tuple]
        """
        if aid_line_type in AidLineControllerFactory.__aid_line_methods:
            return
        AidLineControllerFactory.__aid_line_methods[aid_line_type] = creation_method

    @staticmethod
    def create_aid_line_controller(aid_line_type, chart, aid_line_area, **kwargs):
        """
        Creates a new aid line controller with the given type and the other parameters.

        :param aid_line_type: The aid line controller type to create.
        :type aid_line_type: AidLineType
        :param chart: The chart that should be watched through the created controller.
        :type chart: ChartBase
        :param aid_line_area: The area the aid line can lie in. Always the same order: left, top, right, bottom.
        :type aid_line_area: tuple[int, int, int, int]
        :param kwargs: Other parameter for the aid line controller.
        :return: The newly created aid line controller.
        :rtype: object
        """
        if aid_line_type not in AidLineControllerFactory.__aid_line_methods:
            return
        return AidLineControllerFactory.__aid_line_methods[aid_line_type](chart=chart, aid_line_area=aid_line_area, **kwargs)
