# -*- coding: utf8 -*-
import geopandas
import pandas as pd
import time


class RoadInfo():
    # 关于路网的信息
    road_file = '../information_of_road'
    road_info = '../road_data/road_distance.csv'

    @staticmethod
    def get_road_info():
        """
        获取所有的数据
        :return: roads数据
        """
        roads = geopandas.read_file(RoadInfo.road_file, encoding='utf-8')
        return roads

    @staticmethod
    def min_distance(lines_1, lines_2):
        return int(lines_1.distance(lines_2) * 1000)

    @staticmethod
    def save_road_distance(roads):
        """
        计算两个路网直接的距离信息，存储
        :return:
        """
        number = len(roads)
        count = 0
        for i in range(number):
            print(i)
            df = pd.DataFrame(columns=('lcode1', 'lcode2', 'min_dis'))
            for j in range(i, number):
                dis = RoadInfo.min_distance(roads.loc[i]['geometry'], roads.loc[j]['geometry'])
                df.loc[count] = [roads.loc[i]['Lcode'], roads.loc[j]['Lcode'], dis]
                count += 1
            df.to_csv("road_distance.csv",  mode='a', index=False, header=False)

    @staticmethod
    def open_road_distance(threshold=-1):
        """
        打开距离矩阵
        :return:
        """
        road_dis = pd.read_csv(RoadInfo.road_info)
        road_dis = road_dis.drop_duplicates(
            keep='first',
            inplace=False)
        road_dis = road_dis
        road_dis.columns = ['lcode1', 'lcode2', 'min_dis']
        if threshold != -1:
            road_dis = road_dis[road_dis['min_dis'] < threshold]
        return road_dis

    @staticmethod
    def get_road_name_from_lcode(lcode):
        """
        获取lcode，
        :param lcode:
        :return:
        """
        data = RoadInfo.get_road_info()
        try:
            name = data[data['Lcode'] == str(lcode)]['name'].values[0]
        except:
            print('can not find lcode')
            name = -1
        del data
        return name

    @staticmethod
    def get_lcode_in_area():
        roads = RoadInfo.get_road_info()

        def is_inBox(x, y):
            A = [121.357288, 31.10965]
            B = [121.672458, 31.155495]
            C = [121.620959, 31.386143]
            D = [121.324329, 31.34041]
            a = (B[0] - A[0]) * (y - A[1]) - (B[1] - A[1]) * (x - A[0])
            b = (C[0] - B[0]) * (y - B[1]) - (C[1] - B[1]) * (x - B[0])
            c = (D[0] - C[0]) * (y - C[1]) - (D[1] - C[1]) * (x - C[0])
            d = (A[0] - D[0]) * (y - D[1]) - (A[1] - D[1]) * (x - D[0])
            if (a > 0 and b > 0 and c > 0 and d > 0) or (a < 0 and b < 0 and c < 0 and d < 0):
                return 1
            else:
                return 0

        codes = []
        for item in range(0, len(roads)):
            s = roads.loc[item]
            q = list(s['geometry'].coords)
            for i in q:
                if is_inBox(i[0], i[1]) == 1:
                    codes.append(s['Lcode'])
                    break
        return codes

    @staticmethod
    def road_in_area_code(data):
        """
        获取对应在区域内的lcodes信息
        :param data:
        :return:
        """
        lcodes = RoadInfo.get_lcode_in_area()
        return data.loc[data['Lcode'].isin(lcodes)]

    @staticmethod
    def resave_road():
        """

        :return:
        """
        pass
        # roads.to_file("information_of_road", encoding='utf-8')


if __name__ == '__main__':
    RoadInfo.resave_road()
    # RoadInfo.save_road_distance(roads)
    # print(len(RoadInfo.open_road_distance(10)))
