# -*- coding: utf8 -*-
import geopandas
import pandas as pd
import time


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        ret = func(*args, **kw)
        info_str = 'Function [%s] run time is %.2f' % (func.__name__, time.time() - local_time)
        print(info_str)
        return ret
    return wrapper


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
    @print_run_time
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
            name = data[data['Lcode'] == lcode]['name']
        except:
            print('can not find lcode')
            name = -1
        del data
        return name

    @staticmethod
    def road_in_code(lcodes, road_info):
        """
        获取对应在时间内的lcodes信息
        :param lcodes:
        :param data:
        :return:
        """
        return road_info.loc[road_info['Lcode'].isin(lcodes)]


if __name__ == '__main__':
    # roads = RoadInfo.get_road_info()
    # RoadInfo.save_road_distance(roads)
    print(len(RoadInfo.open_road_distance(10)))