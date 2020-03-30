# -*- coding: utf8 -*-
import pandas as pd
import os
import datetime
from process_data.road_info import RoadInfo
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# x = ['0 Unknown','1 Unimpeded','2 Amble','3 Congestion','4 Heavy Congestion' ]


class ProcessData():
    file_name = '../traffic_data'
    correlation_path = '../road_data/road_correlation.csv'
    top_congestion_path = '../road_data/congestion_time.csv'

    @staticmethod
    def get_csv_path(root_path):
        """
        获取列表下所有的csv文件
        :param root_path:
        :return:
        """
        csv_lists = list()
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if os.path.splitext(file)[1] == '.csv':
                    csv_lists.append(os.path.join(root, file))
        return csv_lists

    @staticmethod
    def get_row_on_name(dataframe, name):
        """
        获取pandas的一行,转换为list
        :param dataframe:
        :param name:
        :return:
        """
        return dataframe[name].to_list()

    @staticmethod
    def open_road_csv(filename):
        """
        打开traffic_data
        :param filename:
        :return:
        """

        data = pd.read_csv(filename)[['Timestamp', 'Lcode', 'speed', 'CongestionRate']]
        data = data.drop_duplicates(
            keep='first',
            inplace=False)
        # 删除未知
        # data = data[data["CongestionRate"] >= 1]
        data = data.reset_index(drop=True)
        # 把时间进行变换
        date = pd.to_datetime(data.Timestamp, format='%Y_%m_%d %H:%M:%S')
        start_time = date.loc[0] + datetime.timedelta(days=1) - datetime.timedelta(minutes=50) - datetime.timedelta(hours=15)
        end_time = date.loc[0] + datetime.timedelta(days=1) - datetime.timedelta(minutes=50)
        data.Timestamp = date
        data = data.set_index('Timestamp')
        data = data[start_time:end_time]
        data = RoadInfo.road_in_area_code(data)
        # 获取时间在早6点到晚9点的数据
        del date
        return data

    @staticmethod
    def data_resample(data):
        """
        将数据进行对应平均值填补
        1. 缺失补零
        2. 缺失补平均
        3. 缺失补相同
        :param data:
        :return:
        """
        pass

    @staticmethod
    def get_top_congestion_lcode(data):
        """
        获取这段时间内拥堵发生最多的路段名
        :param data:
        :return:
        """

        datas = data[data["CongestionRate"] >= 3]
        df = datas.groupby(['Lcode']).count()['CongestionRate']
        df = pd.DataFrame(df)
        try:
            d = pd.read_csv(ProcessData.top_congestion_path)
            d = d.set_index('Lcode')
            df = df.add(d,  fill_value=0)
        except:
            pass
        df.to_csv(ProcessData.top_congestion_path, header=True, index=True)

    @staticmethod
    def get_temporal_correlation(data, time_interal=10):
        """
        根据拥堵信息，构建路段时间关联信息
        :return:
        """

        datas = data[data["CongestionRate"] >= 3]
        df = pd.DataFrame(columns=['lcode1', 'lcode2'])
        # df = pd.read_csv('../road_data/road_correlation.csv')
        number = len(datas)
        count = 0
        for i in range(number):
            current_time = datas.index[i]
            # 获取之后所有拥堵点的数据
            end_time = current_time + datetime.timedelta(minutes=time_interal)
            # 或许之后10分钟之内的数据
            tmp = datas[current_time:end_time]
            lcode_lists = set(ProcessData.get_row_on_name(tmp, 'Lcode'))
            lcode = datas.iloc[i].at['Lcode']
            for l in lcode_lists:
                if l != lcode:
                    count += 1
                    df.loc[count] = [lcode, l]
            if i % 100 == 0:
                print(i)
                df = df.drop_duplicates(
                    keep='first',
                    inplace=False)
                df.to_csv(ProcessData.correlation_path, mode='a', index=False, header=False)
                df = pd.DataFrame(columns=['lcode1', 'lcode2'])

    @staticmethod
    def open_road_correlation():
        """

        :return:
        """
        df = pd.read_csv(ProcessData.correlation_path)
        df = df.drop_duplicates(
            keep='first',
            inplace=False)
        df.columns = ['lcode1', 'lcode2']
        df.reset_index(drop=True)
        return df

    @staticmethod
    def draw_top_congestion():
        df = pd.read_csv(ProcessData.top_congestion_path)
        sort_df = df.sort_values(by='CongestionRate', ascending=False)
        sort_df = sort_df.reset_index(drop=True)
        time_list, name_list = [], []
        avg = sort_df['CongestionRate'].mean()
        N = 10
        for i in range(N):
            code = int(sort_df.loc[i]['Lcode'])
            time = int(sort_df.loc[i]['CongestionRate'])
            time_list.append(time)
            name = RoadInfo.get_road_name_from_lcode(code)
            name_list.append(name)
        plt.figure(figsize=(8, 6), dpi=160)
        # 再创建一个规格为 1 x 1 的子图
        plt.subplot(1, 1, 1)
        # 柱子总数
        # 包含每个柱子对应值的序列
        values = time_list
        # 包含每个柱子下标的序列
        index = name_list
        # 柱子的宽度
        width = 0.35
        # 绘制柱状图, 每根柱子的颜色为紫罗兰色
        plt.bar(index, values, width, label="拥堵次数", color="#87CEFA")
        # 设置横轴标签
        plt.xlabel('路名')
        # 设置纵轴标签
        plt.ylabel('堵塞次数')
        # 添加标题
        plt.title('Top路段堵塞次数一览图')
        # # 添加纵横轴的刻度
        # plt.xticks(index, name_list)
        # plt.yticks(np.arange(0, 81, 10))
        # 画直线
        plt.axhline(y=avg, color='r', linestyle='-.', label='平均拥堵次数')
        # 添加图例
        plt.legend(loc="upper right")
        plt.show()

    @staticmethod
    def draw_speed_of_lcode(lcode, data):
        """
        画出lcode之间的
        :param lcode:
        :param data:
        :return:
        """
        one_lcode_data = data[data['Lcode'] == lcode]
        speed = one_lcode_data['speed'].tolist()
        # congestion_rate = one_lcode_data['CongestionRate']
        avg = sum(speed) / len(speed)
        plt.figure(figsize=(8, 6), dpi=160)
        # 再创建一个规格为 1 x 1 的子图
        plt.subplot(1, 1, 1)
        # 柱子总数
        # 包含每个柱子对应值的序列
        time = np.arange(len(speed))
        plt.plot(time, speed, label='速度')
        # 画直线
        plt.axhline(y=avg, color='r', linestyle='-.', label='平均速度')
        plt.axhline(y=avg*0.6, color='b', linestyle='--', label='0.6 平均速度')
        # 添加图例
        # 设置横轴标签
        plt.xlabel('时间(秒)')
        # 设置纵轴标签
        plt.ylabel('速度(km/h)')
        # 添加标题
        plt.title('路段速度曲线图')
        plt.legend(loc="upper right")
        plt.show()


if __name__ == '__main__':
    csv_lists = ProcessData.get_csv_path(ProcessData.file_name)
    for csv_file in csv_lists:
        data = ProcessData.open_road_csv(csv_file)
        ProcessData.draw_speed_of_lcode(2073, data)
        # ProcessData.get_temporal_correlation(data)
        break
    # ProcessData.get_top_congestion_lcode(data)
    # ProcessData.draw_top_congestion()
