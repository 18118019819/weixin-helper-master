from regex import Regex
import re

from utils.extensions import lac

city = "北京"
content = "地址；北京市顺义区南法信（外地来的可以报销路费）。 1：岗位：快递分拣 装卸工（小件快递分拣装车卸车，女的都可以干轻松不累） 2：年龄：18-50岁。 3：薪资待遇底薪4500+800全勤+（1000～1500绩效）加班费一小时30元。综合工资(6800) 第二月转正：底薪6800+800全勤+（1000～1500绩效）加班费一小时30元。综合工资(9100) 4：包吃包住。 5:五险一金，不用公司上保险的给补助（1200） 注意：来时请带好个人的洗漱用品和被褥。（被褥宿舍旁边小超市也有。电话：18118019819 。5：提供男生女生宿舍，上铺27，下铺30。"

lac_result = lac.run(content)
loc_dict = list(zip(lac_result[0], lac_result[1]))
for item in loc_dict:
    print(item)


# # pos = content.find(city)
# # print(pos)
#
#
# p1 = re.compile(r"^")
#
# print(p1)
# # m = re.findall("(%s).*[，。！？]"%city[0], content)
# m = p1.match(content)
# print(m)
#
# # p2 = re.compile(r"")