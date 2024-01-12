# import fastf1
# import fastf1.core
# import fastf1._api
from driver.driver import Driver
from ff1.session import Session


from pathlib import Path
import logging
import math
import numpy as np
import datetime

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.express.colors import sample_colorscale
from sklearn.preprocessing import minmax_scale


logger = logging.getLogger(Path(__file__).name)
SESSION_CACHE = {

}

class Session_f1:
    def __init__(self, year=2023, circuit=1, stint='R'):
        self.session = None
        self.session_key = None

        self.set_session(year, circuit, stint)

        self.driver = Driver()
        self.driver_id = str()

    def print_vars(self):
        try:
            logger.info("session name: %s", self.session.name)
        except AttributeError:
            print("AttributeError: 'NoneType' object has no attribute 'name'")

        logger.info("f1: %s", self.driver.f1)
        logger.info("driver: %s", self.driver)
        logger.info("driver_id: %s", self.driver_id)

    def set_session(self, year, circuit, stint):
        self.session_key = f"{year}-{circuit}"
        self.session = SESSION_CACHE.get(self.session_key, None)

        if self.session is None:
            self.session = Session(year, circuit)
            SESSION_CACHE[self.session_key] = self.session
            logger.info('BRAND NEW SESSION SET: %s', self.session_key)
    def set_driver(self, driver_abb: str):
        '''set current session driver'''
        self.driver_id = driver_abb
        self.driver = Driver(Driver.get_driver_id(self.driver_id))
        self.print_vars()
        logger.info("set_driver: %s, %s", self.driver_id, self.driver)


    def get_driver(self):
        logger.info("get_driver: %s", self.driver_id)
        return self.session.get_driver(self.driver_id)

    def laps_participated(self) -> list:
        laps = self.session.laps_participated(self.driver_id)
        return laps

    def __rotate_point(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        # angle = angle/360*2*np.pi

        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    def __range(self, points):
        max_x = max(points[0])
        min_x = min(points[0])
        max_y = max(points[1])
        min_y = min(points[1])

        return max_x-min_x, max_y-min_y
    def __rotate_90(self, points, center_x, center_y):
        new_points = [[],[]]
        for index in range(len(points[0])):
            if points[0][index] is None:
                continue
            x, y = self.__rotate_point([center_x, center_y], [points[0][index], points[1][index]], np.pi/2)
            new_points[0].append(x)
            new_points[1].append(y)

        return new_points

    def __flip_v(self, points, center_x, center_y):
        for index in range(10,len(points[0])):

            x = points[0][index]
            points[0][index] = -1 * (x - center_x) + center_x

            y = points[1][index]
            points[1][index] = -1 * (y - center_y) + center_y

        return points

    def __get_brakepoints(self, tel_data):
        x_brakes = []
        y_brakes = []

        prev_is_none = False

        brake = 12
        x = 18
        y = 19

        for row in tel_data.itertuples():
            brake_status = row[brake]

            if brake_status:
                x_brakes.append(row[x])
                y_brakes.append(row[y])
                prev_is_none = False
            else:
                if not prev_is_none:
                    x_brakes.append(None)
                    y_brakes.append(None)
                    prev_is_none = True

        brakepoints = [x_brakes, y_brakes]

        return brakepoints

    def __get_max_speed_points(self, tel_data):
        max_speed = max(tel_data.Speed.tolist())

        x_co = []
        y_co = []

        x = 18
        y = 19
        speed = 9

        for row in tel_data.itertuples():
            if max_speed == row[speed]:
                x_co.append(row[x])
                y_co.append(row[y])

        max_speed_points = [x_co, y_co]

        return max_speed_points

    def __get_circuit_corners(self):
        corner_info = self.session.get_circuit_info('corners')
        corners = [corner_info.X, corner_info.Y]
        return corners, corner_info.Number

    def fastest_lap_num(self):
        tel_data = self.session.get_laps(self.driver_id).copy()
        tel_data['Seconds'] = tel_data.LapTime.map(lambda x: x / datetime.timedelta(seconds=1))
        tel_data = tel_data.sort_values(by='Seconds', ascending=True)
        return int(tel_data.LapNumber.iloc[0])

    def get_circuit_fig(self, screen_height, screen_width, show_legend, measure, lap):
        logger.info("get_circuit_fig: %s, %s, %s", show_legend, measure, lap)
        units = {
            'Speed': '[km/h]',
            'Throttle': '%',
            'RPM': '',
            'nGear': '',
            'Brake': "",
        }
        #TODO verify measure
        # if lap=='fastest':
        #     logger.info("GETTING FASTEST LAP CIRCUIT FIG")
        #     tel_data = self.session.laps.pick_driver(self.driver_id).pick_fastest().get_telemetry()
        #     points = [tel_data['X'].tolist(), tel_data['Y'].tolist()]
        #     # points = self.__rotate(points)
        #     metric = tel_data[measure]
        #     title = "Fastest Lap"
        #     subtitle = measure
        #     colorscale = 'hot'
        if lap in self.laps_participated():
            tel_data = self.session.get_tel(self.driver_id, [lap]).copy()
            print(tel_data.head())
            points = [tel_data['X'].tolist(), tel_data['Y'].tolist()]
            metric = tel_data[measure]
            title = f"Lap {lap}"
            subtitle = measure
            colorscale = 'hot'
            #TODO if lapnum out of bounds, print error
        else:
            logger.error("Lap # Out of Bounds.")
            return

        center_x = (max(points[0]) + min(points[0])) / 2
        center_y = (max(points[1]) + min(points[1])) / 2

        dim_x, dim_y = self.__range(points)
        logger.info("Dimensions: %s, %s", dim_x, dim_y)

        brakepoints = self.__get_brakepoints(tel_data).copy()
        max_speed_points = self.__get_max_speed_points(tel_data).copy()
        corners, corner_text = self.__get_circuit_corners()
        corners = corners.copy()
        # corners = self.__flip_v(corners, center_x, center_y)

        if dim_x < dim_y:
            logger.info("Rotate Circuit")
            logger.info("Rotate Points")
            points = self.__rotate_90(points, center_x, center_y)
            logger.info("Rotate BrakePoints")
            brakepoints = self.__rotate_90(brakepoints, center_x, center_y)
            logger.info("Rotate MaxSpeedPoints")
            max_speed_points = self.__rotate_90(max_speed_points, center_x, center_y)
            logger.info("Rotate Corners")
            corners = self.__rotate_90(corners, center_x, center_y)

        width = screen_width*2/3

        dim_x, dim_y = self.__range(points)
        dim_y = dim_y/dim_x * width
        dim_x = width

        size_metric = int(width*.0075)

        logger.info("SIZE METRIC: %s", size_metric)

        logger.info("Dimensions: %s, %s", dim_x, dim_y)

        tel_data['Lap_Time'] = tel_data.Time.map(lambda x: f"{int(x.seconds / 3600)}:{int(x.seconds)}:{x.seconds % 3600}.{str(x.microseconds).zfill(6)}")

        # create figure
        fig = px.scatter(tel_data, x=points[0], y=points[1],
                         color_continuous_scale=colorscale,
                         color=measure,
                         size=[1]*len(points[0]),
                         size_max=size_metric,
                         opacity=0.8,
                         # title=f"{title} by {subtitle}",
                         hover_data=['RPM', 'Speed', 'nGear', 'Throttle', 'Brake', 'DRS', 'Status', 'Lap_Time'],

                         )

        fig_brakes = go.Scatter(x=brakepoints[0], y=brakepoints[1],
                                mode='markers',
                                name='brake points',
                                opacity=0.25,
                                marker=dict(color="#FFA1F2",
                                            size=size_metric * 2.25),
                                hoverinfo='skip'
                                )
        fig_max_speed = go.Scatter(x=max_speed_points[0], y=max_speed_points[1],
                                   mode='markers',
                                   name='max speed',
                                   opacity=.9,
                                   marker=dict(color="#10F36C",
                                               size=size_metric * 1.5,
                                               ),
                                   hoverinfo='skip'
                                   )

        fig_corners = go.Scatter(x=corners[0], y=corners[1],
                                 mode='markers+text',
                                 name='corners',
                                 opacity=.85,
                                 marker=dict(color="rgb(245,245,245)",
                                             size=size_metric * 3,
                                             ),
                                 text=corner_text,
                                 hoverinfo='skip',
                                 textposition='middle center',
                                 textfont=dict(color='black', size=size_metric*1.5),
                                 )
        if show_legend:
            fig.add_trace(fig_brakes)
            fig.add_trace(fig_max_speed)
            fig.add_trace(fig_corners)

        # fig.update_xaxes(
        #     linecolor='red'
        # )

        fig.update_layout(
            xaxis_visible=False, yaxis_visible=False,
            # xaxis_showline=True, yaxis_showline=True,
            showlegend=show_legend,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1,
                xanchor="right",
                x=1,
                font=dict(
                    color="rgb(20,20,20)"
                ),
            ),
            plot_bgcolor='rgb(25,25,25)',
            autosize=False,
            height=dim_y, width=dim_x,
            margin=dict(
                l=15,
                r=15,
                b=15,
                t=15,
                pad=4
            ),
            paper_bgcolor="white",
        )

        fig.update_coloraxes(
            colorbar=dict(
                title=dict(
                    text=f"{measure} {units[measure]}",
                    font_color='rgb(20,20,20)',
                ),
                y=0.5,
                showticklabels=True,
                ticks='outside',
                tickfont_color='#141414',
                tickcolor='#141414',
                ticklabelstep=2,
                # dtick=10
            ),
        )

        fig.update_traces({'marker.opacity':1, 'marker.line.width':0})

        return fig

    def update_circuit_fig(self, fig, checklist):
        """lapNum, avg, fastest"""
        logger.info("UPDATE FIG: %s", checklist)

    def get_basic_stats_display(self, lap_numbers, metrics, dim_width, x_axis=' time'):
        if lap_numbers is None or len(lap_numbers)==0:
            fig = go.Figure()
            fig.update_layout(
                height=750, width=dim_width * 4 / 7, title_text="Statistics", showlegend=False,
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="rgba(25,25,25,0.9)",
                    font_size=10,
                    font_color='white'
                ),
                plot_bgcolor='#EAEAEA',
            )
            return fig

        lap_numbers.sort()
        rows = len(metrics)

        # get color palette
        colors_ = [i for i in range(0, int(len(lap_numbers)))]
        discrete_colors = sample_colorscale('Bluered', minmax_scale(colors_))
        discrete_colors.reverse()
        logger.info("BASIC STATS: discrete colors: %s", discrete_colors)

        fig = make_subplots(rows=rows, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.005
                            )

        for index, lap_n in enumerate(lap_numbers):
            lap_tel = self.session.get_tel(self.driver_id, [lap_n])
            # display(lap_tel.head())
            date = lap_tel.Date.iloc[0]

            lap_tel['time'] = lap_tel.Time.map(
                lambda x: x + datetime.datetime(date.year, date.month, date.day, 0, 0, 0, 0))

            color = discrete_colors[index]

            line_config = dict(color=f"{color[:-1]},0.8)", width=1.5, )

            time_template = '<br>%{x|%M:%S.%L}<br>'
            distance_template = '<br>%{x:d} m<br>'

            x_axis = x_axis.lower()
            if x_axis == ' time':
                x_data = lap_tel['time']
                x_template = time_template
            elif x_axis == ' distance':
                x_data = lap_tel["Distance"]
                x_template = distance_template
            else:
                logger.error("NO VALID X_AXIS")
                x_data = lap_tel['time']
                x_template = time_template

            fig_speed = go.Scatter(x=x_data, y=lap_tel.Speed,
                                   mode='lines',
                                   name=f'lap {lap_n}',
                                   opacity=1,
                                   line=line_config,
                                   hovertemplate=x_template + '%{y} km/h',
                                   )
            fig_ngear = go.Scatter(x=x_data, y=lap_tel.nGear,
                                   mode='lines',
                                   name=f'lap {lap_n}',
                                   opacity=1,
                                   line=line_config,
                                   hovertemplate=x_template + 'gear %{y}',
                                   )
            fig_throttle = go.Scatter(x=x_data, y=lap_tel.Throttle,
                                      mode='lines',
                                      name=f'lap {lap_n}',
                                      opacity=1,
                                      line=line_config,
                                      hovertemplate=x_template + 'throttle: %{y}%',
                                      )
            fig_rpm = go.Scatter(x=x_data, y=lap_tel.RPM,
                                 mode='lines',
                                 name=f'lap {lap_n}',
                                 opacity=1,
                                 line=line_config,
                                 hovertemplate=x_template + '%{y} RPM',
                                 )
            fig_brake = go.Scatter(x=x_data, y=lap_tel.Brake,
                                   mode='lines',
                                   name=f'lap {lap_n}',
                                   opacity=1,
                                   line=line_config,
                                   hovertemplate=x_template + 'braking: %{y}',
                                   )
            # fig_drs
            # fig_status
            i = 1
            y_axis_labels = []
            if 'speed' in metrics:
                fig.add_trace(fig_speed, row=i, col=1)
                y_axis_labels.append('Speed [km/h]')
                i+=1
            if 'gear' in metrics:
                fig.add_trace(fig_ngear, row=i, col=1)
                y_axis_labels.append('Gear')
                i+=1
            if 'throttle' in metrics:
                fig.add_trace(fig_throttle, row=i, col=1)
                y_axis_labels.append('Throttle %')
                i+=1
            if 'rpm' in metrics:
                fig.add_trace(fig_rpm, row=i, col=1)
                y_axis_labels.append('RPM')
                i+=1
            if 'brakes' in metrics:
                fig.add_trace(fig_brake, row=i, col=1)
                y_axis_labels.append('Brakes')

        fig['layout']['xaxis']['title'] = f'{x_axis}'

        for index in range(len(y_axis_labels)):
            label = y_axis_labels[index]
            # if index == 0: index = ''
            # else:
            index += 1
            print(f'yaxis{index}', label)
            fig['layout'][f'yaxis{index}']['title'] = label

        axes = ""
        if len(metrics) > 1:
            axes=len(metrics)
        fig.update_traces(
            xaxis=f"x{axes}",
        )

        x_axis_config = dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            mirror=True,
            showspikes=True,
            spikemode='toaxis+across',
            spikesnap='cursor',
        )

        fig['layout']['xaxis'] = x_axis_config

        fig.update_layout(
            height=750, width=dim_width*5/6, title_text="Statistics", showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="rgba(25,25,25,0.9)",
                font_size=10,
                font_color='white'
            ),
            plot_bgcolor='#EAEAEA',
        )
        fig.update_xaxes(
            spikecolor='#FF4D4D'
        )

        logger.info("RETURNING STATS FIG")

        fig.update_layout(height=750)

        return fig

# if __name__=="__main__":
    # race = initialize(2023, 'Canada', 'R')
    # set_driver("VER")

