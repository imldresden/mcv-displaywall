import json
import os
import pickle
import time

from libavg import app, player, avg
from libavg.app.touchvisualization import TouchVisualizationOverlay

from configs import config_app
from data_models.sql_provider.sql_interface import SqlInterface
from divico_ctrl.translation import T
from examples.data.sql_crime_data import table_name_to_query
from examples.wall_divico import WallDivico
from libavg_charts.aid_lines.factory.aid_line_to_factory import add_aid_lines_to_factory
from libavg_charts.aid_lines.helper.data_point_snapping_methods import add_snapping_methods_to_method_holder
from libavg_charts.aid_lines.helper.intersection_methods import add_intersections_methods_to_method_holder
from libavg_charts.aid_lines.helper.selections_methods import add_selection_methods_to_method_holder
from logging_base.study_logging import StudyLog
from other_views.text_view_2 import TextView2
from other_views.touch_test_view import TouchTestView
from other_views.touch_visualization import TouchVisualization
from study.study_handler import StudyHandler


class Application(app.MainDiv):
    def onArgvParserCreated(self, parser):
        parser.add_option('--fake', '-f', default='False', dest='fake', help = 'Fake')
        parser.add_option('--session', '', default='-1', dest='session',
                          help='Session ID')

    def onArgvParsed(self, options, args, parser):
        self.argvoptions = options

    def onInit(self):
        if self.argvoptions.fake == 'True':
            config_app.fake_data_mode = True
            config_app.data_mode_string = 'fake'
        if self.argvoptions.session != '-1':
            config_app.SESSION = int(self.argvoptions.session)

        self.__key_messages = {}
        self._study_handler = None
        if config_app.study_mode:
            with open("assets/study_preparations/key_messages.json") as f:
                self.__key_messages = json.load(f)
            self._study_handler = StudyHandler(
                block_question_file=config_app.study_tasks_file,
                study_order_file=config_app.study_order_file,
                session_id=config_app.SESSION
            )

        add_aid_lines_to_factory()
        add_intersections_methods_to_method_holder()
        add_selection_methods_to_method_holder()
        add_snapping_methods_to_method_holder()

        self.__grid_groups = [
            [0, 1, 2, 3],
            [4, 5, 6, 7, 8, 9, 10],
            [11],
            [12],
            [13],
            [16],
            [17],
            [22],
            [23],
            [24],
            [25],
            [26],
            [27],
            [32],
            [33],
            [34],
            [35],
            [36],
            [37],
            [38],
            [39],
            [40],
            [41],
            [42],
            [43],
            [44, 45, 46, 47, 48],
            [49, 50, 51, 52, 53],
            [54],
        ]

        self.__grid_labels = {}
        sql = SqlInterface(
            sql_db_path=config_app.db_filename[config_app.data_mode_string],
            table_mapper_method=table_name_to_query,
            query_file="examples/data/crime_data.queries"
        )
        if len(self.__grid_labels) == 0:
            for grid_group in self.__grid_groups:
                for grid_id in grid_group:
                    self.__grid_labels[grid_id] = T.tl(msg=sql.get_query_label(str(grid_id)), lang=config_app.default_language)
                    self.__grid_labels[grid_id] += " [{}]".format(grid_id) if not config_app.study_mode else ""
            self.__grid_labels[21] = T.tl(msg="Weapons <--> Types", lang=config_app.default_language) + (" [21]" if not config_app.study_mode else "")
            self.__grid_labels[15] = T.tl(msg="Map of Crimes/Neighborhood", lang=config_app.default_language) + (" [15]" if not config_app.study_mode else "")

        if not os.path.exists(config_app.sql_result_dump_filename[config_app.data_mode_string]) or config_app.force_sql_reload:
            start_time = time.time()
            last_time = start_time

            sql_results = {}
            for grid_group in self.__grid_groups:
                for grid_id in grid_group:
                    sql_results[str(grid_id)] = sql.get_query_results(str(grid_id))

                    now = time.time()
                    print "Duration:", now - last_time, "| loaded chart for query ", self.__grid_labels[grid_id]
                    last_time = now

            for query_name in ["map data from neighborhoods", "districts per neighborhood", "crime types per neighborhood", "crime type names", "highest weapon usage per neighborhood"]:
                sql_results[query_name] = sql.get_query_results(query_name)

            now = time.time()
            print "Duration:", now - last_time, "| loaded chart for map"
            print "The complete creation needed ", time.time() - start_time

            # dumping sql results for later use
            try:
                if not os.path.exists("tmp"):
                    os.makedirs("tmp")
                with open(config_app.sql_result_dump_filename[config_app.data_mode_string], 'wb') as f:
                    pickle.dump(sql_results, f, 0)
                print 'Saved sql results locally!'
            except IOError:
                print 'Error: Failed to save sql results locally!'

        self.__wall_divico = None
        self.__touch_test_view = None
        self.__touch_visualization_overlay = None

        self.__task_text_view = None
        self.__task_text_view_canvas = None
        self.__task_text_view_image_bottom = None
        self.__task_text_view_image_top = None
        self.__phase_block_label = None
        self.__interaction_activation_label = None

        if config_app.show_test_touch_view and config_app.study_mode:
            self.__draw_pre_view()
        else:
            self.__draw_main_view()

        player.subscribe(player.KEY_DOWN, self.__on_key_down)

    def __draw_pre_view(self):
        """
        Draws the view to test the touches.
        """
        self.__touch_test_view = TouchTestView(
            parent=self,
            size=self.size
        )
        self.__touch_test_view.start_listening(all_nodes_clicked=self.__on_all_test_nodes_clicked)

    def __draw_main_view(self, fake=False):
        """
        Draws the main vis view.

        :param fake: Should the fake or the original data set be loaded?
        :type fake: bool
        """
        if self.__touch_test_view:
            self.__touch_test_view.unlink(True)
            self.__touch_test_view = None

        self.__wall_divico = WallDivico(
            parent=self,
            size=self.size,
            map_image_info=config_app.maps_images[config_app.map_image],
            data_file=config_app.sql_result_dump_filename[config_app.data_mode_string],
            grid_groups=self.__grid_groups,
            grid_labels=self.__grid_labels
        )

        self.__task_text_view_canvas = player.createCanvas(
            id="task_text_view",
            autorender=True,
            multisamplesamples=8,
            size=(self.size[0], self.size[1] / 12)
        )
        text = ["{} ({})".format(self._study_handler.current_block_name, self._study_handler.current_phase)] if self._study_handler else []
        self.__task_text_view = TextView2(
            text_elements=text,
            alignment="center",
            font_size=42,
            element_size=900,
            parent=self.__task_text_view_canvas.getRootNode(),
            size=(self.size[0], self.size[1] / 12),
            padding_top=20,
            padding_bottom=20,
            element_offset=50,
            # elementoutlinecolor="f00"
        )
        self.__task_text_view_image_top = avg.ImageNode(
            parent=self,
            size=(self.size[0], self.size[1] / 12),
            href="canvas:task_text_view"
        )
        self.__task_text_view_image_bottom = avg.ImageNode(
            parent=self,
            pos=(0, self.size[1] * 11 / 12),
            size=(self.size[0], self.size[1] / 12),
            href="canvas:task_text_view"
        )
        self.__phase_block_label = avg.WordsNode(
            parent=self,
            pos=(3, self.size[1] - 20),
            fontsize=15,
            color="555",
            alignment="left",
            variant="bold",
            rawtextmode=True,
            text="#{} - {}: {}".format(
                config_app.SESSION,
                self._study_handler.current_phase,
                self._study_handler.current_block_name
            ) if self._study_handler else ""
        )
        self.__interaction_activation_label = avg.WordsNode(
            parent=self,
            pos=(3, 3),
            fontsize=15,
            color="555",
            alignment="left",
            variant="bold",
            rawtextmode=True,
            text=""
        )

        self.__create_touch_vis_view()

        # initialize StudyLogging
        if config_app.study_mode:
            StudyLog.get_instance().write_event_log("initialized view and divico control")
            
            self.subscribe(avg.Node.CURSOR_DOWN, lambda event: self.__log_touch(event, event_type="CURSOR_DOWN"))
            self.subscribe(avg.Node.CURSOR_MOTION, lambda event: self.__log_touch(event, event_type="CURSOR_MOTION"))
            self.subscribe(avg.Node.CURSOR_UP, lambda event: self.__log_touch(event, event_type="CURSOR_UP"))

    @staticmethod
    def __log_touch(event, event_type="-1"):
        # print "event node: ", self.getElementByPos(event.pos)
        StudyLog.get_instance().write_touch(event.x, event.y, event.userid, event_type)

    def __on_all_test_nodes_clicked(self, sender):
        """
        Called when all nodes in the test touch view were touched.

        :type sender: TouchTestView
        """
        if not self.__touch_test_view:
            return

        self.__touch_test_view.active = False
        if sender is not None:
            StudyLog.get_instance().write_event_log('The touch test view was successfully passed.')
        player.setTimeout(1, lambda: self.__draw_main_view())

    def __on_key_down(self, event):
        """
        Called when a key input was recognized.
        """
        shift = event.modifiers & avg.KEYMOD_LSHIFT or event.modifiers & avg.KEYMOD_RSHIFT
        strg = event.modifiers & avg.KEYMOD_LCTRL or event.modifiers & avg.KEYMOD_RCTRL

        # For the normal interaction with the application.
        if event.keyname == 'A' and not strg and not shift:
            key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['A']]
            if len(key_message) != 0:
                StudyLog.get_instance().write_event_log(key_message[0])

            self.sensitive = True
            self.__interaction_activation_label.text = ""

        # For the normal interaction with the application.
        if event.keyname == 'D' and not strg and not shift:
            key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['D']]
            if len(key_message) != 0:
                StudyLog.get_instance().write_event_log(key_message[0])

            self.sensitive = False
            self.__interaction_activation_label.text = "Touch interactions deactivated"

        if event.keyname == 'V' and not strg and not shift:
            key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['V']]
            if len(key_message) != 0:
                StudyLog.get_instance().write_event_log(key_message[0])

            if self.__touch_visualization_overlay:
                self.__touch_visualization_overlay.active = not self.__touch_visualization_overlay.active
                if self.__touch_visualization_overlay.active:
                    self.reorderChild(self.__touch_visualization_overlay, self.getNumChildren() - 1)
            else:
                self.__create_touch_vis_view()

        if event.keyname == 'T' and not strg and not shift:
            if self.__touch_test_view and self.__touch_test_view.active:
                key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['T']]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0])

                self.__on_all_test_nodes_clicked(None)

        if event.keyname == 'R' and not strg and not shift:
            key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['R']]
            if len(key_message) != 0:
                StudyLog.get_instance().write_event_log(key_message[0])

            self.__wall_divico.divico_control.reset()

        # For the interaction with the application if study mode is true.
        if self._study_handler:
            if event.keyname == 'H' and not strg and not shift:
                key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['H']]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0])

            if event.keyname == 'Escape' and not strg and not shift:
                key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['Escape']]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0])

            # Change the phase
            if shift and event.keyname in ['1', '2', '3', '4'] and not strg:
                self._study_handler.go_to_phase(self._study_handler.phases[int(event.keyname) - 1])

                self.__task_text_view.text_alignment = "center"
                self.__task_text_view.font_colors = []
                text = self._study_handler.current_block_name
                text = text if "Training" not in self._study_handler.current_phase else text + " ({})".format(self._study_handler.current_phase)
                self.__task_text_view.text_elements = [text]
                self.__task_text_view.draw()

                self.__phase_block_label.text = "#{} - {}: {}".format(
                    config_app.SESSION,
                    self._study_handler.current_phase,
                    self._study_handler.current_block_name
                )

                key_message = [v['msg'] for v in self.__key_messages if event.keyname in v['keys'] and 'shift' in v['keys']]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0] + self.__phase_block_label.text)

            # Switch through the blocks of a phase.
            if event.keyname in ['Up', 'Down'] and not shift and not strg:
                self._study_handler.go_to_neighbor_block(-1 if event.keyname == 'Up' else 1)

                self.__task_text_view.text_alignment = "center"
                self.__task_text_view.font_colors = []
                self.__task_text_view.text_elements = [self._study_handler.current_block_name]
                self.__task_text_view.draw()

                self.__phase_block_label.text = "#{} - {}: {}".format(
                    config_app.SESSION,
                    self._study_handler.current_phase,
                    self._study_handler.current_block_name
                )

                key_message = [v['msg'] for v in self.__key_messages if v['keys'] == [event.keyname]]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0] + self._study_handler.current_block_name)

            # Check/uncheck a task in a block.
            if event.keyname in [str(i) for i in range(1, 10)] and not shift and not strg:
                if not (len(self.__task_text_view.text_elements) == 1 and
                        self._study_handler.current_block_name in self.__task_text_view.text_elements[0]):
                    index = int(event.keyname) - 1
                    if index < len(self.__task_text_view.text_elements):
                        current_color = self.__task_text_view.font_colors[index]
                        new_color = colors.GREY_DARKEN_3 if current_color != colors.GREY_DARKEN_3 else self.__task_text_view.default_font_color
                        self.__task_text_view.font_colors[index] = new_color

                    self.__task_text_view.draw()

                    if index < len(self._study_handler.current_tasks):
                        key_message = [v['msg'] for v in self.__key_messages if event.keyname in v['keys'] and 'strg' not in v['keys'] and 'shift' not in v['keys']]
                        if len(key_message) != 0:
                            StudyLog.get_instance().write_event_log("{}{} - {}".format(key_message[0], event.keyname, self._study_handler.current_tasks[index].encode('utf-8')))

            # Go inside a block and show its task.
            if event.keyname == 'Return' and not shift and not strg:
                self.__task_text_view.text_elements = self._study_handler.current_tasks
                if "Guided" in self._study_handler.current_phase:
                    self.__task_text_view.text_alignment = "left"
                elif "Free" in self._study_handler.current_phase:
                    self.__task_text_view.text_alignment = "center"
                elif "Training" in self._study_handler.current_phase:
                    self.__task_text_view.text_alignment = "left"
                    user = "N1" if self._study_handler.phases.index(self._study_handler.current_phase) == 0 else "N2"

                    tasks = self._study_handler.current_tasks if user == "N1" else list(reversed(self._study_handler.current_tasks))
                    colors = [(colors.AMBER if t.startswith(user) else colors.CYAN) for t in tasks]
                    tasks = [t[3:] for t in tasks]

                    self.__task_text_view.font_colors = colors + [colors.WHITE] + colors
                    self.__task_text_view.text_elements = tasks + [""] + tasks
                self.__task_text_view.draw()

                key_message = [v['msg'] for v in self.__key_messages if v['keys'] == ['Return']]
                if len(key_message) != 0:
                    StudyLog.get_instance().write_event_log(key_message[0] + self._study_handler.current_block_name)

    def __create_touch_vis_view(self):
        self.__touch_visualization_overlay = TouchVisualizationOverlay(
            isDebug=False,
            visClass=TouchVisualization,
            rootNode=self,
            parent=self,
            sensitive=False
        )

    def onFrame(self):
        if self.__wall_divico:
            self.__wall_divico.divico_control.on_frame()

        if config_app.study_mode:
            StudyLog.get_instance().on_frame()
