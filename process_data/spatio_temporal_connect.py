# -*- coding: utf8 -*-
import pandas as pd
import folium
import networkx as nx
import matplotlib.pyplot as plt
import datetime
from process_data.process_traffic_data import ProcessData
from process_data.road_info import RoadInfo


class SpatioTemporal():
    """
    结合时间和空间，构建拥堵模式graph
    """
    file_path = '../road_data/spatio_temporal_correlation.csv'
    html_path = '../roadmap_html/Roadmap.html'

    @staticmethod
    def spatio_temporal_correlation():
        """
        获得路径关联矩阵
        :return:
        """
        road = RoadInfo.open_road_distance(10)
        time = ProcessData.open_road_correlation()
        df = pd.DataFrame(columns=['lcode1', 'lcode2', 'dis'])
        count = 0
        for i in range(len(time)):
            count += 1
            lcode1 = time.iloc[i].at['lcode1']
            lcode2 = time.iloc[i].at['lcode2']
            s = road[(road.lcode1 == lcode1) & (road.lcode2 == lcode2)]
            q = road[(road.lcode1 == lcode2) & (road.lcode2 == lcode1)]
            if len(s):
                df.loc[count] = [lcode1, lcode2, s['min_dis'].values[0]]
                continue
            elif len(q):
                df.loc[count] = [lcode1, lcode2, q['min_dis'].values[0]]
        df = df.drop_duplicates(keep='first', inplace=False)
        df.to_csv(SpatioTemporal.file_path, mode='a', index=False, header=False)

    @staticmethod
    def open_correlation_csv():
        """
        打开文件
        :return:
        """
        df = pd.read_csv(SpatioTemporal.file_path)
        return df

    @staticmethod
    def draw_line_on_map(road, collection):
        """
        在地图上画点，线
        :param all_line:
        :return:
        """
        # colors = ['black', 'green', 'yellow', 'orange', 'red']
        x, y = 121.473658, 31.230378
        maps = folium.Map(
            location=[y, x],
            zoom_start=11,
            tiles=
            'http://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
            attr="高德地图")
        for i in collection:
            lcode1 = i[0]
            lcode2 = i[1]
            road1 = road[road['Lcode'] == str(lcode1)]['geometry'].values[0]
            road2 = road[road['Lcode'] == str(lcode2)]['geometry'].values[0]
            count1 = len(list(road1.coords)) // 2
            count2 = len(list(road2.coords)) // 2
            loc1 = [road1.coords[count1][1], road1.coords[count1][0]]
            loc2 = [road2.coords[count2][1], road2.coords[count2][0]]
            folium.CircleMarker(
                        location=loc1,
                        radius=10,
                        popup='popup',
                        color='red',  # 圈的颜色
                        fill=True,
                        fill_color='white'  # 填充颜色
                        ).add_to(maps)
            folium.CircleMarker(
                        location=loc2,
                        radius=10,
                        popup='popup',
                        color='red',  # 圈的颜色
                        fill=True,
                        fill_color='white'  # 填充颜色
                        ).add_to(maps)
            folium.PolyLine(
                [loc1, loc2],
                weight=4,  # 粗细
                opacity=0.8,  # 透明度
                color='black').add_to(maps)
        return maps

    @staticmethod
    def draw_graph():
        """
        画出图
        :return:
        """
        df = SpatioTemporal.open_correlation_csv()
        edge_list = df.values.tolist()
        # G = nx.DiGraph()
        # G.add_weighted_edges_from(edge_list)
        # nx.draw(G)
        # nx.draw(G, pos=nx.random_layout(G), node_color='b', edge_color='r', with_labels=True, font_size=18, node_size=20)
        # plt.show()
        # lcode_list = list(set(df.iloc[:, 0].tolist() + df.iloc[:, 1].tolist()))
        # lcode_list = [str(x) for x in lcode_list]
        road = RoadInfo.get_road_info()
        # roads = road[(road['Lcode'].isin(lcode_list))]['geometry']
        SpatioTemporal.draw_line_on_map(road, edge_list).save(SpatioTemporal.html_path)

    @staticmethod
    def create_graphs():
        """
        创建多个有向图
        :return:
        """
        df = SpatioTemporal.open_correlation_csv()
        edge_list = df.values.tolist()
        congestion_propagation_graph = list()
        for lcode1, lcode2, _ in edge_list:
            flag = 0
            for graph in congestion_propagation_graph:
                if flag == 1:
                    break
                for edge in graph:
                    if edge == lcode1:
                        graph.add(lcode2)
                        flag = 1
                        break
                    elif edge == lcode2:
                        graph.add(lcode1)
                        flag = 1
                        break
            if flag == 1:
                continue
            new_graph = set()
            new_graph.add(lcode1)
            new_graph.add(lcode2)
            congestion_propagation_graph.append(new_graph)
        congestion_propagation_graph_list = list()
        for i in congestion_propagation_graph:
            if len(i) > 2:
                congestion_propagation_graph_list.append(list(i))
        return congestion_propagation_graph_list

    @staticmethod
    def get_graph_congestion(road_code_list, data, time_interal=10):
        """
        根据拥堵图结构，获取对应的拥堵数据
        :return:
        """
        datas = data[data['Lcode'].isin(road_code_list)]
        # s = datas['2020-01-02 06:00:00':'2020-01-02 06:00:00']
        time_list = sorted(set(datas.index))
        congestion_time = list()
        end_time = time_list[0]
        for start_time in time_list:
            if start_time < end_time:
                continue
            tmp = datas[start_time:start_time]
            flag = 1
            if tmp['CongestionRate'].max() >= 3:
                propagation_time = start_time + datetime.timedelta(minutes=time_interal)
                while True:
                    s = datas[start_time:propagation_time]
                    q = s[s['CongestionRate'] >= 3]
                    if len(q) < 2:
                        flag = 0
                        break
                    tmp_time = q.index.max()
                    if tmp_time + datetime.timedelta(minutes=time_interal) == propagation_time:
                        end_time = propagation_time
                        break
                    propagation_time = tmp_time + datetime.timedelta(minutes=time_interal)
                if flag:
                    congestion_time.append((start_time, end_time))
        print(congestion_time)
        print(len(congestion_time))
        return congestion_time


if __name__ == '__main__':
    # SpatioTemporal.spatio_temporal_correlation()
    graph_list = SpatioTemporal.create_graphs()
    csv_lists = ProcessData.get_csv_path(ProcessData.file_name)
    for csv_file in csv_lists:
        data = ProcessData.open_road_csv(csv_file)
        congestion_time = SpatioTemporal.get_graph_congestion(graph_list[1], data, time_interal=8)
        # ProcessData.get_temporal_correlation(data)
        break