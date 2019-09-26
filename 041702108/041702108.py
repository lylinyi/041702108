"""


"""

import requests
import re
import json


class Address:
    def __init__(self, addr):
        self.level = 0
        self.rawAddr = ""
        self.tmpAddr = addr[:-1]

        self.name = ""
        self.phoneNum = 0
        self.addr = []
        self.json_file = json.load(open('./pcas.json', encoding='utf-8'))

        self.parse()

    def get_level(self):
        self.level = int(self.tmpAddr[:1])
        self.tmpAddr = self.tmpAddr[2:]

    def get_phone_num(self):

        reg = r"\d{11}"
        self.phoneNum = re.search(reg, self.tmpAddr).group()
        self.tmpAddr = self.tmpAddr.replace(self.phoneNum, "")

    def get_name(self):
        index = self.tmpAddr.find(',')

        self.name = self.tmpAddr[:index]
        self.tmpAddr = self.tmpAddr[index + 1:]
        self.rawAddr = self.tmpAddr

    def parse(self):
        self.get_level()
        self.get_phone_num()
        self.get_name()

        self.get_province()
        self.get_city()
        self.get_county()
        self.get_town()
        self.get_road()
        self.get_house_num()
        self.get_detail()
        if self.level == 3:
            self.call_api()

    def cut_string(self, full_addr, tmp_addr):
        i = 0
        while i < len(full_addr) and full_addr[i] == tmp_addr[i]:
            i += 1
        return tmp_addr[i:]

    def get_province(self):
        sub_addr = self.tmpAddr[:2]

        municipality = ["天津", "北京", "重庆", "上海"]
        for province in self.json_file:
            if province.find(sub_addr) != -1:
                self.addr.append(province)

                if self.tmpAddr.find(province) == 0:
                    if sub_addr in municipality:

                        if self.tmpAddr[2] == '市':
                            self.tmpAddr = self.tmpAddr.replace('市', '', 1)

                        self.addr.append(self.addr[0] + "市")
                    self.tmpAddr = self.tmpAddr.replace(province, '', 1)
                else:
                    self.tmpAddr = self.tmpAddr.replace(province[:-1], '', 1)

                return
        self.addr.append('')

    def get_city(self):
        if len(self.addr) != 2:
            sub_addr = self.tmpAddr[:2]  # 可能缺失,得到下一级地址

            cities = self.json_file[self.addr[0]]
            for city in cities:
                if city.find(sub_addr) != -1:
                    self.addr.append(city)

                    if self.tmpAddr.find(city) == 0:
                        self.tmpAddr = self.tmpAddr.replace(city, '', 1)
                    else:
                        self.tmpAddr = self.tmpAddr.replace(city[:-1], '', 1)

                    return
            self.addr.append('')

    def get_county(self):
        # print(self.tmpAddr)
        sub_addr = self.tmpAddr[:2]

        if self.addr[1] != '':
            counties = self.json_file[self.addr[0]][self.addr[1]]
            for county in counties:
                if county.find(sub_addr) == 0:
                    self.addr.append(county)
                    self.tmpAddr = self.cut_string(county, self.tmpAddr)

                    return
        else:
            cities = self.json_file[self.addr[0]]
            for city in cities:
                counties = self.json_file[self.addr[0]][city]
                for county in counties:
                    if county.find(sub_addr) != -1:
                        self.addr.append(county)
                        self.tmpAddr = self.cut_string(county, self.tmpAddr)
                        return

        self.addr.append('')

    def get_town(self):
        # print(self.tmpAddr)
        if self.addr.count("") is 0:
            sub_addr = self.tmpAddr[:2]
            towns=self.json_file[self.addr[0]][self.addr[1]][self.addr[2]]
            for town in towns:
                if town.find(sub_addr)!=-1:
                    self.addr.append(town)
                    self.tmpAddr = self.cut_string(town, self.tmpAddr)
                    return
        else:
            #res = re.search("(.*?街道)|(.*?[镇乡])", self.tmpAddr)
            res = re.search("(.*?街道)|(.*?[镇乡区])", self.tmpAddr)
            if res is None:
                self.addr.append('')
            else:
                self.addr.append(res.group(0))
                self.tmpAddr = self.tmpAddr.replace(res.group(0), '', 1)

    # 可以合并,将正则表达式作为参数传入
    def get_road(self):
        #   测试  .*?[路街巷道里区岛线桥梁]|.*国道|.*省道|.*乡道
        # print(self.tmpAddr)
        res = re.search("(.*[路巷道街里岛线桥梁])", self.tmpAddr)

        if res is None:
            self.addr.append('')
        else:
            self.addr.append(res.group(0))
            self.tmpAddr = self.tmpAddr.replace(res.group(0), '', 1)

    def get_house_num(self):
        # print(self.tmpAddr)

        res = re.search("(.*[号弄])", self.tmpAddr)
        if res is None:
            self.addr.append('')
        else:
            self.addr.append(res.group(0))
            self.tmpAddr = self.tmpAddr.replace(res.group(0), '', 1)

    def call_api(self):
        # print(self.rawAddr)
        url1 = 'https://restapi.amap.com/v3/geocode/geo?address=' + self.rawAddr + '&output=JSON&key=16e93d04ea8f153bf7b4f81042008954'
        resp1 = requests.get(url1).json()
        location = resp1['geocodes'][0]['location']

        url2 = 'https://restapi.amap.com/v3/geocode/regeo?output=JSON&location=' + location + '&key=16e93d04ea8f153bf7b4f81042008954&radius=5&extensions=all'
        resp2 = requests.get(url2).json()
        address_info = resp2['regeocode']['addressComponent']

        level_name = ["province", "city", "district", "township", "street", "street_number"]
        for i in range(4):
            if self.addr[i] == "":
                if address_info[level_name[i]]:
                    self.addr[i] = address_info[level_name[i]]
        # 处理直辖市
        if self.addr[0][-1] == "市":
            self.addr[1] = self.addr[0]
            self.addr[0] = self.addr[0][0:2]

    def get_detail(self):
        # print(self.tmpAddr)
        self.addr.append(self.tmpAddr)
        if self.level == 1:
            self.addr[4] += self.addr[5] + self.addr[6]
            self.addr = self.addr[:5]

    def show_info(self):
        data = {
            "姓名": self.name,
            "手机": self.phoneNum,
            "地址": self.addr
        }

        print(json.dumps(data, ensure_ascii=False))


def main():
    a = Address(input())
    a.show_info()


main()
