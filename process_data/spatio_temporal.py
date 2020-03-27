# -*- coding: utf8 -*-
import pandas as pd
import folium
import networkx as nx
import matplotlib.pyplot as plt
from process_data.process_traffic_data import ProcessData
from process_data.road_info import RoadInfo


class SpatioTemporal():
    """
    结合时间和空间，构建拥堵模式graph
    """
    file_path = '../road_data/spatio_temporal_correlation.csv'

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
        df.to_csv('../road_data/spatio_temporal_correlation.csv', mode='a', index=False, header=False)

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
    def create_correlation_graph():
        """
        创建有向图
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
        SpatioTemporal.draw_line_on_map(road, edge_list).save("../roadmap_html/Roadmap.html")


if __name__ == '__main__':
    # SpatioTemporal.spatio_temporal_correlation()
    SpatioTemporal.create_correlation_graph()