# -*- coding: utf8 -*-
import pandas as pd
import os
import datetime
# x = ['0 Unknown','1 Unimpeded','2 Amble','3 Congestion','4 Heavy Congestion' ]


class ProcessData():
    file_name = '../traffic_data'

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
        # 获取时间在早6点到晚9点的数据
        data = data[start_time:end_time]
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
    def get_temporal_correlation(data):
        """
        根据拥堵信息，构建路段时间关联信息
        :return:
        """

        datas = data[data["CongestionRate"] >= 3]
        df = pd.DataFrame(columns=['lcode1', 'lcode2', 'correlation'])
        # df = pd.read_csv('../road_data/road_correlation.csv')
        number = len(datas)
        count = 0
        for i in range(number):
            count += 1

            current_time = datas.index[i]
            # 获取之后所有拥堵点的数据
            end_time = current_time + datetime.timedelta(minutes=10)
            # 或许之后10分钟之内的数据
            tmp = datas[current_time:end_time]
            lcode_lists = set(ProcessData.get_row_on_name(tmp, 'Lcode'))
            lcode = datas.iloc[i].at['Lcode']
            for l in lcode_lists:
                if l != lcode:
                    df.loc[count] = [lcode, l, 1]
            if i % 100 == 0:
                print(i)
                df = df.drop_duplicates(
                    keep='first',
                    inplace=False)
                df.to_csv('../road_data/road_correlation.csv', mode='a', index=False, header=False)
                df = pd.DataFrame(columns=['lcode1', 'lcode2', 'correlation'])

    @staticmethod
    def open_road_correlation():
        df = pd.read_csv('../road_data/road_correlation.csv')
        df = df.drop_duplicates(
            keep='first',
            inplace=False)
        df.columns = ['lcode1', 'lcode2', 'correlation']
        df.reset_index(drop=True)
        return df


if __name__ == '__main__':
    csv_lists = ProcessData.get_csv_path(ProcessData.file_name)
    for csv_file in csv_lists:
        data = ProcessData.open_road_csv(csv_file)
        ProcessData.get_temporal_correlation(data)
        break
