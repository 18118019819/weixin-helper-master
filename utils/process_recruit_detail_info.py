# encoding:UTF-8
import regex as re

from extensions import lac, replace_dict, lac_city_data
from utils.constant import PATH_CITY_DATA


def getTypes(msg):
    text = msg
    lac_result = lac.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'types':
            res.append(item[0])

    return res


regex_number = ''
regex_place = ''
regex_money = ''
regex_time = ''
regex_content = ''
regex_title = ''
regex_acquire = ''
regex_city = ''
regex_type = ''
regex_contact = ''


def getORGName(str_content):
    text = str_content
    lac_result = lac.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'ORG':
            res.append(item[0])

    return res


def getTypesName(str_content):
    text = str_content
    lac_result = lac.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'types':
            res.append(item[0])
    return res

def getCityName(str_content):
    text = str_content
    lac_result = lac_city_data.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'city':
            res.append(item[0])
    return res

def getDistrictName(str_content):
    text = str_content
    lac_result = lac_city_data.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'district':
            res.append(item[0])
    return res


def getLOCName(str_content):
    text = str_content
    lac_result = lac.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'LOC':
            res.append(item[0])
    return res


def getMNumber(content):
    tel_rules = ["1[3-9]\\d{9}", "0\\d{2,3}-[1-9]\\d{6,8}"]
    phones = set()
    for rule in tel_rules:
        phone = re.findall(rule, content)
        if not phone:
            continue
        for p in phone:
            phones.add(p)
    return list(phones)


def getAllMsg(content, data_original):
    place = []
    if len(place) == 0:
        tmp = getORGName(data_original)
        res = []
        for i in range(0, len(tmp)):
            if tmp[i] != '微信' and tmp[i] != '微信电话' and tmp[i] not in res:
                res.append(tmp[i])
        place = res
    if (len(place) > 3):
        # place = place[0]
        place = get_special_content(regex_place, content)

    # 地点
    # city = get_special_content(regex_place, content)
    city = ''
    if len(city) == 0:
        tmp = getLOCName(content)
        res = []
        for i in range(0, len(tmp)):
            if tmp[i] not in res:
                res.append(tmp[i])
        city = res
    if len(city) == 0:
        # 按配置找城市
        city = re.findall(regex_city, content)
        city = list(set(city))
        city = ",".join(city)

    dict_city = []
    dict_district = []
    with open(PATH_CITY_DATA, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()
        for line in lines:
            temp = line.split("/")
            if temp[1] == "city":
                dict_city.append(temp[0])
            else:
                dict_district.append(temp[0])

    single_city = getCityName(content)
    district = getDistrictName(content)
    # 因为lac没有最细粒度划分，只要干预字典的字可以在分词中找到，就把相关分词也提取出来
    if len(single_city) == 0:
        lac_result = lac_city_data.run(content)
        loc_dict = list(zip(lac_result[0], lac_result[1]))
        for item in loc_dict:
            if item[1] == "city":
                for city in dict_city:
                    pattern = r"%s"%city
                    temp_city =re.findall(pattern, item[0])
                    if len(temp_city) != 0:
                        single_city.append(item[0])

    if len(single_city) == 0:
        lac_result = lac_city_data.run(content)
        loc_dict = list(zip(lac_result[0], lac_result[1]))
        for item in loc_dict:
            if item[1] == "district":
                for district in dict_district:
                    pattern = r"%s"%district
                    temp_district =re.findall(pattern, item[0])
                    if len(temp_district) != 0:
                        district.append(item[0])

    print(f"single_city:{single_city},district:{district}")


    # 人数
    number = re.findall(r'\d+人|\d+名|数名|大量|若干|\d+个|\d+人|多名|若干个|几个|\d+—\d+人|\d+到\d+人|\d+位|多人|\d+到\d+名|\d+组人', content)

    # 招聘类型
    types = getTypes(content)

    persons = getPERName(content)
    # print(persons)
    # 处理经理
    tmp1 = []
    for t in persons:
        # print(t)
        if type(types) == list:
            for i in range(0, len(types)):
                if types[i] == '经理' and content.index('经理') > content.index(t):
                    # print('qa=',types[i],t)
                    continue
                else:
                    tmp1.append(types[i])
    if len(tmp1) > 0:
        types = tmp1
    money = ''
    acquire = ''
    contact = getMNumber(content)
    if not contact:
        contact = getMNumber(data_original.replace('   ', ','))
    # print(contact)
    work_time = ''
    return types, money, acquire, number, contact, city, work_time, place, persons, single_city, district


def get_res(content, wxid, raw, time, data_original):
    """
    :param content:
    :return:
    """
    types, money, acquire, number, contact, city, work_time, place, persons, single_city, district = getAllMsg(content, data_original)

    return process_return(types, money, acquire, number, contact, city, work_time, place, persons, wxid, raw, time,
                          data_original, content, single_city, district)  # 此句新添加


def process_return(types, money, acquire, number, contact, city, work_time, place, persons, wxid, raw, time,
                   data_original, content, single_city, district):
    if type(types) == list:
        for i in range(0, len(types)):
            if '一开一' in types[i] and type(number) == list:
                number.insert(i, '1组')
                break
    if type(types) == list:
        for i in range(0, len(types)):
            if '一开一' in types[i] and "司机" in types:
                types.remove('司机')
                break
    if type(types) == list and len(types) > 1:
        tmp = []
        for i in range(0, len(types)):
            for j in range(0, len(types)):
                if i != j:
                    if types[i] in types[j] and types[j] not in tmp:
                        tmp.append(types[j])
                        types[i] = types[j]
                    elif types[j] in types[i] and types[i] not in tmp:
                        tmp.append(types[i])
                        types[j] = types[i]
                    if types[j] not in types[i] and types[i] not in types[j] and types[i] not in tmp and j == len(
                            types) - 1:
                        tmp.append(types[i])
            if types[i] not in tmp and i == len(types) - 1:
                tmp.append(types[i])
        types = tmp
    # 处理 不要小工
    if type(types) == list:
        tmp = []
        for t in types:
            if '不要' + t in content or t + '不要' in content or '不是' + t in content or t + '不是' in content or '双证' + t in content or t + '双证' in content:
                continue
            else:
                tmp.append(t)
    if tmp != [] and len(tmp) > 0:
        types = tmp
    all_info = []
    for i in range(0, len(types)):
        if len(types) > 1 and type(types) == list:
            one_types = types[i]
        else:
            one_types = types
        if len(money) > i and len(types) > 1 and type(types) == list:

            one_money = money[i]
        else:
            one_money = money
        if len(acquire) > i and len(types) > 1 and type(types) == list:
            one_acquire = acquire[i]
        else:
            one_acquire = acquire
        if len(number) > i and len(types) > 1 and type(types) == list:
            one_number = number[i]
        elif len(number) <= i and len(types) > 1 and type(types) == list:
            one_number = ''
        else:
            one_number = number
        if len(contact) >= len(types) and len(types) > 1 and type(types) == list:
            one_contact = contact[i]
        else:
            one_contact = contact
        one_contact = str(one_contact).replace(']', '').replace('[', '').replace(',', '').replace('\'', '')
        if len(place) >= len(types) and len(types) > 1 and type(types) == list:
            one_place = place[i]
        else:
            one_place = place
        if len(city) >= len(types) and type(city) != type("") and type(types) == list:
            one_city = city[i]
        else:
            one_city = city
        res = ''  # 地址
        if type(one_city) == list and type(types) == list:
            for item in one_city:
                if "市" in item:
                    res = item
                    break
            if res == '':
                one_city = one_city[0]
            else:
                one_city = res
        if len(work_time) >= len(types) and type(types) == list:
            one_time = work_time[i]
        else:
            one_time = work_time
        if type(one_acquire) == list:
            work_content = ",".join(one_acquire)
        else:
            work_content = one_acquire
        if type(one_money) == list:
            work_content = work_content + " " + ",".join(one_money)
        else:
            work_content = work_content + " " + one_money
        if type(persons) == list and len(persons) >= len(types):
            one_persons = persons[i]
        else:
            one_persons = persons
        # 处理地址
        if type(types) == list and len(types) > 1 and len(city) - 1 == len(types):
            one_city = city[i + 1]
        info = {"工种": one_types, "期望工作地点": one_city, "招工单位": one_place, "招工人数": one_number, "联系人": one_persons,
                "联系电话": one_contact}
        all_info.append(info)
        if type(types) != list:
            break
    print(city)
    res = {"期望工作地点": city, "招工单位": place, "招工信息": all_info, "联系人": "无",
           "联系电话": contact, "联系微信": "无", "项目内容": "无", "消息来源": "无", "个人昵称": "无"}
    return res, types, number, city, place, contact, single_city, district


def delBlank(obj):
    t = []
    if type(obj) == type(t):
        for i in range(0, len(obj)):
            obj[i] = str(obj[i]).strip(' ')
    else:
        obj = str(obj).strip(' ')
    return obj


def get_special_content(forward_text, content):
    """
    输入正则表达式匹配的开始的字符串，生成匹配的结尾字符串，返回匹配的结果
    :param forward_text:
    :param content:
    :return:
    """
    list_rg = [regex_place, regex_money, regex_time, regex_title, regex_content, regex_acquire, '<end>'
        , regex_number, regex_contact]  # 获取所有需要匹配的字符串
    list_rg.remove(forward_text)  # 移除开头字符串
    backward_text = "|".join(list_rg)  # 组合起来
    if (forward_text != regex_title and forward_text != regex_time and forward_text != regex_money):
        regex_concat = '(?<=' + forward_text + ').*?(?=\\n|' + backward_text + '|～～|！|其它：)'  # 组成完整表达式
    else:  # if (forward_text==regex_title):

        regex_concat = '(?<=' + forward_text + ').*?(?=，|。|：|！|' + backward_text + '|\\n)'
    return re.findall(regex_concat, content)


def extract_telephone(data):
    # 处理 电话号码
    tel_rules = ["1[3-9]\\d{9}", "0\\d{2,3} [1-9]\\d{3,4} [0-9]\\d{3,4}", "0\\d{2,3}-[1-9]\\d{6,8}",
                 "1[0-9]{2} [0-9]{4} [0-9]{4}"]
    all_phones = []
    for each_rule in tel_rules:
        phone = re.findall(each_rule, data)
        if not phone:
            continue
        all_phones.extend(phone)
    # 统一电话的格式
    res = []
    for ori_phone in all_phones:
        if " " not in ori_phone:
            res.append((ori_phone, " %s " % ori_phone))
        else:
            if ori_phone[0] == "0":
                seg_phone = ori_phone.split(" ")
                phone_str = " %s-%s " % (seg_phone[0], "".join(seg_phone[1:]))
                res.append((ori_phone, phone_str))
            else:
                phone_str = ori_phone.replace(" ", "")
                res.append((ori_phone, " %s " % phone_str))
    return res


def extract_info(data, wxid, raw, time):
    # globals().update(regex_config)
    data_original = data
    # 提取文本中的电话号码 or 座机号码
    phones = extract_telephone(data)
    for ori_phone, format_phone in phones:
        data = data.replace(ori_phone, format_phone)
        # print(f'ori_phone:{ori_phone},fomate_phone:{format_phone}')

    # 十人   30到50人 四个 五六个 8九个人 shi ming shiwu ming 一个工管住不管吃 一个礼拜 一个班
    # 算0.5个工 不要暑期工 暑假工不要 物流仓库 28个班 热水空调 汽车玻璃 服务费20 威特电梯 8个通层
    for origin_text, replace_text in replace_dict:
        # print(replace_text)

        data = data.replace(origin_text, replace_text)
    data = f"<start>{data}<end>"
    return get_res(data, wxid, raw, time, data_original)


def getPERName(text):
    lac_result = lac.run(text)
    resdict = dict(zip(lac_result[0], lac_result[1]))
    res = []
    for item in resdict.items():
        if str(item[1]) == 'PER':
            res.append(item[0])
    return res



