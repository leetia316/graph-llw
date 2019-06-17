import pymysql
import csv
import codecs
import time
import re
from decimal import *

# 说明：
# 此脚本文件主要用来生成债券类csv文件

# 主要用来生成node的唯一id
id = 0


# 连接mysql
def get_conn():
    conn = pymysql.connect(host='localhost', port=33061, user='rhb',
                           passwd='COYKK6dzu45EDsqI', db='rhb_db', charset='utf8')
    return conn


# 查询结果
def query_all(cur, sql, args):
    cur.execute(sql, args)
    return cur.fetchall()


# 创建节点和关系文件
def create_csv(node_filename, rel_filename):
    global id
    # 连接mysql数据库
    conn = get_conn()
    cur = conn.cursor()

    # 公司节点
    sql = """select distinct `name` from c_client where  `name` is not null and
       is_fin_institution is null or is_fin_institution  = 0 """
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[0], 'w', 'utf-8') as file:
        c_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['companyId:ID', 'name', ':LABEL'])
        for result in results:
            if notnull(result[0]):
                id += 1
                c_id[result[0]] = id
                data.append((id, result[0], "公司"))
        write.writerows(data)

    # 金融机构节点
    sql = """select distinct `name` from c_client where  `name` is not null and is_fin_institution = 1"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[6], 'w', 'utf-8') as file:
        institution_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['institutionId:ID', 'name', ':LABEL'])
        for result in results:
            if notnull(result[0]):
                id += 1
                institution_id[result[0]] = id
                data.append((id, result[0], "金融机构"))
        write.writerows(data)

    # 授信表中有客户表中没有的公司，因此需要把这部分公司拿出来，追加到''company_name.csv’中去。不然会报错
    # 追加新节点
    sql = """select distinct `name` from c_credit_2
           where `name` not  in (select distinct `name` from c_client)"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[0], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                c_id[result[0]] = id
                data.append((id, result[0], "公司"))
        write.writerows(data)

    # 债券信息表中发行人有金融机构中没有的公司，因此需要把这部分公司拿出来。
    # 追加新节点
    sql = """select distinct `B_INFO_ISSUER` from cbonddescription
           where `B_INFO_ISSUER` not  in (select distinct `name` from c_client)"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[6], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                institution_id[result[0]] = id
                data.append((id, result[0], "金融机构"))
        write.writerows(data)

    # 债券信息表中发行人有金融机构中没有的公司，因此需要把这部分公司拿出来。
    # 追加新节点
    sql = """select distinct `s_lu_name` from cbonddescription
           where `s_lu_name` not  in (select distinct `name` from c_client)"""
    results = query_all(cur, sql, None)
    s_lu_name_list = []
    for i in range(len(results)):
        s_lu_name_list.append(results[i][0])
    s_lu_name_list = format_lead_underwriter(s_lu_name_list)
    with codecs.open(node_filename[6], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for i in range(len(s_lu_name_list)):
            if notnull(s_lu_name_list[i]):
                id += 1
                institution_id[s_lu_name_list[i]] = id
                data.append((id, s_lu_name_list[i], "金融机构"))
        write.writerows(data)

    # 股票信息表中有主承销商有金融机构中没有的公司，因此需要把这部分公司拿出来。
    # 追加新节点
    sql = """ select distinct `lead_underwriter` from shares
           where `lead_underwriter` not in (select distinct name from c_client) """
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[6], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        underwriter_list = []
        for i in range(len(results)):
            underwriter_list.append(results[i][0])
        underwriter_list = format_lead_underwriter(underwriter_list)
        for i in range(len(underwriter_list)):
            if notnull(underwriter_list[i]):
                id += 1
                institution_id[underwriter_list[i]] = id
                data.append((id, underwriter_list[i], "金融机构"))
        write.writerows(data)

    # 股票信息表中有上市推荐人有金融机构没有的公司，因此需要把这部分公司拿出来。
    # 追加新节点
    sql = """select distinct `recommender` from shares
           where `recommender` not in (select distinct name from c_client) """
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[6], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                institution_id[result[0]] = id
                data.append((id, result[0], "金融机构"))
        write.writerows(data)

    # 股票信息表中有保荐机构有金融机构中没有的公司，因此需要把这部分公司拿出来。
    # 追加新节点
    sql = """select distinct `institution` from shares
            where `institution` not in (select distinct name from c_client) """
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[6], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                institution_id[result[0]] = id
                data.append((id, result[0], "金融机构"))
        write.writerows(data)

    # 合作银行节点
    sql = """select distinct bank from c_credit_2 where bank is not null"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[1], "w", 'utf-8') as file:
        bank_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['bankId:ID', 'name', ':LABEL'])
        for result in results:
            if notnull(result[0]):
                id += 1
                bank_id[str(result[0]).rstrip()] = id
                data.append((id, str(result[0]).rstrip(), "合作银行"))
        write.writerows(data)

    # 授信额度节点
    sql = """select distinct t1.name,t1.bank,t1.amount,t1.currency from c_credit_2 as t1
    inner join
    (
    select t2.name, max(t2.time) as maxtime,max(t2.end_date) as maxenddate
    from c_credit_2 as t2
    group by t2.name
    ) as t3 on t1.name = t3.name and t1.time = t3.maxtime and t1.end_date = t3.maxenddate and  t1.bank <> '综合'"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[2], "w", 'utf-8') as file:
        total_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['totalId:ID', 'name', ':LABEL'])
        for result in results:
            if notnull(result[2]):
                id += 1
                key = str(Decimal(result[2]).quantize(Decimal('0.0'))) + result[0]
                total_id[key] = id
                data.append((id, format_unit(result[2]), "总授信额度"))
        write.writerows(data)

    # 授信额度关系（公司--授信额度）
    with codecs.open(rel_filename[0], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[2]) and notnull(result[0]):
                key = str(Decimal(result[2]).quantize(Decimal('0.0'))) + result[0]
                try:
                    if notnull(result[3]):
                        data.append(
                            (c_id[str(result[0])], '总授信额度' + '(' + result[3] + ')', total_id[key], '总授信额度'))
                    else:
                        data.append((c_id[str(result[0])], '总授信额度', total_id[key], '总授信额度'))
                except KeyError:
                    if notnull(result[3]):
                        data.append((institution_id[str(result[0])], '总授信额度' + '(' + result[3] + ')',
                                     total_id[key], '总授信额度'))
                    else:
                        data.append((institution_id[str(result[0])], '总授信额度', total_id[key], '总授信额度'))
        write.writerows(data)

    # 公司合作银行关系(授信额度--合作银行）
    with codecs.open(rel_filename[1], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[2]) and notnull(result[1]):
                key = str(Decimal(result[2]).quantize(Decimal('0.0'))) + result[0]
                data.append((total_id[key], '合作银行', bank_id[str(result[1]).rstrip()], "合作银行"))
        write.writerows(data)

    # 债券名称节点
    sql = """SELECT distinct `S_INFO_NAME`, `B_INFO_ISSUER`,`s_lu_name` FROM cbonddescription"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[3], "w", 'utf-8') as file:
        bond_name_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['bond_nameId:ID', 'name', ':LABEL'])
        for result in results:
            if notnull(result[0]):
                id += 1
                bond_name_id[result[0]] = id
                data.append((id, result[0], "债券简称"))
        write.writerows(data)

    # # 特殊债券类型节点
    # with codecs.open(node_filename[4], "w", 'utf-8') as file:
    #     special_bond_type_id = {}
    #     data = []
    #     special_bond_type_list = []
    #     for i in range(len(results)):
    #         special_bond_type_list.append(results[i][2])
    #     special_bond_type_list = list(set(special_bond_type_list))
    #     write = csv.writer(file, dialect='excel')
    #     write.writerow(['special_bond_typeId:ID', 'special_bond_type', ':LABEL'])
    #     for i in range(len(special_bond_type_list)):
    #         if notnull(special_bond_type_list[i]):
    #             id += 1
    #             special_bond_type_id[special_bond_type_list[i]] = id
    #             data.append((id, special_bond_type_list[i], "特殊债券类型"))
    #     write.writerows(data)

    # 债券名称关系（公司--（发行债券）--债券名称）
    with codecs.open(rel_filename[2], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[1]) and notnull(result[0]):
                try:
                    data.append((c_id[result[1]], '发行债券', bond_name_id[result[0]], '发行债券'))
                except KeyError:
                    data.append((institution_id[result[1]], '发行债券', bond_name_id[result[0]], '发行债券'))
        write.writerows(data)

    # # 特殊债券类型关系（债券名称--（特殊债券类型）--特殊债券类型）
    # with codecs.open(rel_filename[3], 'w', 'utf-8') as file:
    #     data = []
    #     write = csv.writer(file, dialect='excel')
    #     write.writerow([':START_ID', ':END_ID', ':TYPE'])
    #     for result in results:
    #         if notnull(result[0]) and notnull(result[2]):
    #             data.append((bond_name_id[result[0]], special_bond_type_id[result[2]], '特殊债券类型'))
    #     write.writerows(data)

    # 债券主承销商关系（债券名称--（主承销商）--主承销商）
    with codecs.open(rel_filename[4], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[0]) and notnull(result[2]):
                underwriters = []
                underwriters.append(result[2])
                underwriters = format_lead_underwriter(underwriters)
                for i in range(len(underwriters)):
                    if notnull(underwriters[i]):
                        try:
                            data.append((bond_name_id[result[0]], '债券主承销商', institution_id[underwriters[i]], '债券主承销商'))
                        except KeyError:
                            data.append((bond_name_id[result[0]], '债券主承销商', c_id[underwriters[i]], '债券主承销商'))

        write.writerows(data)

    # 发行股票节点
    sql = """SELECT `name`, a_code,  h_code, b_code, a_name, h_name, b_name FROM c_client"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[5], "w", 'utf-8') as file:
        shares_id = {}
        data = []
        shares_list = []
        for i in range(len(results)):
            for j in range(3):
                if notnull(results[i][j + 1]):
                    shares_list.append(results[i][j + 1 + 3] + '(' + results[i][j + 1] + ')')
        shares_list = list(set(shares_list))
        write = csv.writer(file, dialect='excel')
        write.writerow(['shareId:ID', 'name', ':LABEL'])
        for i in range(len(shares_list)):
            if notnull(shares_list[i]):
                id += 1
                shares_id[shares_list[i]] = id
                data.append((id, shares_list[i], "股票"))
        write.writerows(data)

    # 发行股票关系（公司--（发行股票）--股票简称（股票代码））
    with codecs.open(rel_filename[5], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            try:
                if notnull(result[1]) and notnull(result[4]):
                    data.append((c_id[result[0]], '发行股票', shares_id[result[4] + '(' + result[1] + ')'], '发行股票'))
                    if notnull(result[2]) and notnull(result[5]):
                        data.append((c_id[result[0]], '发行股票', shares_id[result[5] + '(' + result[2] + ')'], '发行股票'))
                        if notnull(result[3]) and notnull(result[6]):
                            data.append((c_id[result[0]], '发行股票', shares_id[result[6] + '(' + result[3] + ')'], '发行股票'))
            except KeyError:
                if notnull(result[1]) and notnull(result[4]):
                    data.append(
                        (institution_id[result[0]], '发行股票', shares_id[result[4] + '(' + result[1] + ')'], '发行股票'))
                    if notnull(result[2]) and notnull(result[5]):
                        data.append(
                            (institution_id[result[0]], '发行股票', shares_id[result[5] + '(' + result[2] + ')'], '发行股票'))
                        if notnull(result[3]) and notnull(result[6]):
                            data.append((
                                        institution_id[result[0]], '发行股票', shares_id[result[6] + '(' + result[3] + ')'],
                                        '发行股票'))

        write.writerows(data)

    # 股票主承销商关系(股票--承销商）
    sql = """SELECT distinct `s_id`, `s_name`, `lead_underwriter`, `recommender`, `institution` FROM shares
    join c_client on s_name = c_client.a_name or s_name = c_client.b_name or s_name =c_client.h_name"""
    results = query_all(cur, sql, None)
    with codecs.open(rel_filename[6], "w", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[0]) and notnull(result[1]) and notnull(result[2]):
                share_underwriter = []
                share_underwriter.append(result[2])
                share_underwriter = format_lead_underwriter(share_underwriter)
                for i in range(len(share_underwriter)):
                    try:
                        data.append((shares_id[result[1] + '(' + result[0] + ')'], '股票主承销商',
                                     institution_id[share_underwriter[i]], '股票主承销商'))
                    except KeyError:
                        data.append((shares_id[result[1] + '(' + result[0] + ')'], '股票主承销商', c_id[share_underwriter[i]],
                                     '股票主承销商'))

        write.writerows(data)

    # 上市推荐人关系（股票--上市推荐人）
    with codecs.open(rel_filename[7], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[0]) and notnull(result[1]) and notnull(result[3]):
                data.append((shares_id[result[1] + '(' + result[0] + ')'], '上市推荐人', institution_id[result[3]], '上市推荐人'))
        write.writerows(data)

    # 保荐机构关系（股票--保荐机构）
    with codecs.open(rel_filename[8], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[0]) and notnull(result[1]) and notnull(result[4]):
                data.append((shares_id[result[1] + '(' + result[0] + ')'], '保荐机构', institution_id[result[4]], '保荐机构'))
        write.writerows(data)

    # 高管表中有客户表中没有的公司，因此需要把这部分公司拿出来，追加到'company_name.csv’中去。不然会报错
    # 追加新节点
    sql = """select distinct c_name from e_executive
         where `c_name` not in (select distinct `name` from c_client)"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[0], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                c_id[result[0]] = id
                data.append((id, result[0], "公司"))
        write.writerows(data)

    # 高管节点
    sql = """select distinct c_name, e_name, post from e_executive where e_name is not null and post is not null"""
    results = query_all(cur, sql, None)
    executive_list = []
    for i in range(len(results)):
        executive_list.append(results[i][1])
    executive_list = list(set(executive_list))
    with codecs.open(node_filename[7], "w", 'utf-8') as file:
        e_name_id = {}
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow(['e_nameId:ID', 'name', ':LABEL'])
        for i in range(len(executive_list)):
            if notnull(executive_list[i]):
                id += 1
                e_name_id[executive_list[i]] = id
                data.append((id, executive_list[i], "高管"))
        write.writerows(data)

    # 高管关系（高管--公司）
    with codecs.open(rel_filename[9], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            if notnull(result[1]) and notnull(result[2]):
                try:
                    data.append((e_name_id[result[1]], result[2], c_id[result[0]], "高管关系"))
                except KeyError:
                    data.append((e_name_id[result[1]], result[2], institution_id[result[0]], "高管关系"))
        write.writerows(data)

    # 对外投资表中有客户表中没有的公司，因此需要把这部分公司拿出来，追加到'company_name.csv’中去。不然会报错
    # 追加新节点
    sql = """select distinct  `name` from c_investment
         where `name` not in (select distinct `name` from c_client)"""
    results = query_all(cur, sql, None)
    with codecs.open(node_filename[0], "a+", 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        for result in results:
            if notnull(result[0]):
                id += 1
                c_id[result[0]] = id
                data.append((id, result[0], "公司"))
        write.writerows(data)

    # 投资占比关系
    sql = """select b.name, a.name,format(rate,2) from c_investment a join c_client b on
      a.c_id = b.c_id and rate is not null"""
    results = query_all(cur, sql, None)
    with codecs.open(rel_filename[10], 'w', 'utf-8') as file:
        data = []
        write = csv.writer(file, dialect='excel')
        write.writerow([':START_ID', 'relationship', ':END_ID', ':TYPE'])
        for result in results:
            try:
                if notnull(result[0]) and notnull(result[1]):
                    data.append((c_id[result[0]], '投资占比' + result[2] + '%', c_id[result[1]], "投资占比"))
            except KeyError:
                try:
                    if notnull(result[0]) and notnull(result[1]):
                        data.append((c_id[result[0]], '投资占比' + result[2] + '%', institution_id[result[1]], "投资占比"))
                except KeyError:
                    try:
                        if notnull(result[0]) and notnull(result[1]):
                            data.append((institution_id[result[0]], '投资占比' + result[2] + '%', institution_id[result[1]],
                                         "投资占比"))
                    except KeyError:
                        if notnull(result[0]) and notnull(result[1]):
                            data.append((institution_id[result[0]], '投资占比' + result[2] + '%', c_id[result[1]], "投资占比"))

        write.writerows(data)


# 空值字段不导入
def notnull(content):
    if content:
        if str(content) != "-" and str(content) != "--":
            return True
        else:
            return False
    else:
        return False


def format_unit(number):
    if notnull(number):
        return str(Decimal(number).quantize(Decimal('0.00'))) + '亿元'


def format_lead_underwriter(underwriters):
    new_underwriters = []
    for i in range(len(underwriters)):
        if notnull(underwriters[i]):
            row = underwriters[i].replace(' ', '')
            new_row_list = re.split(",|，|、", row)
            for j in range(len(new_row_list)):
                new_underwriters.append(new_row_list[j])
    return list(set(new_underwriters))


# # 解析高管职务
# def format_post(line):
#     post = []
#     row = line.replace(' ', '')
#     new_row_list = re.split(",|，|、", row)
#     for i in range(len(new_row_list)):
#         if new_row_list[i]:
#             if '兼' in new_row_list[i] and '兼职监事' not in new_row_list[i]:
#                 new_row_list[i] = new_row_list[i].split('兼')
#                 for j in range(len(new_row_list[i])):
#                     post_item = re.sub(u"\\（.*?）|\\(.*?\\)", "", new_row_list[i][j])
#                     post.append(post_item)
#             else:
#                 item = re.sub(u"\\（.*?）|\\(.*?\\)", "", new_row_list[i])  # 用正则表达式去掉分割后每一项的括号内容
#                 post.append(item)
#     return post


if __name__ == '__main__':
    starttime = time.clock()
    node_filename = ['company_name.csv', 'bank.csv', 'total_credit.csv', 'bond_name.csv', 'special_bond_type.csv',
                     'shares.csv', 'institution.csv', 'company_executive.csv'
                     ]
    rel_filename = ['total_credit_rel.csv', 'bank_rel.csv', 'com_bond_rel.csv', 'special_bond_type_rel.csv',
                    's_lu_name_rel.csv', 'shares_rel.csv', 'lead_underwriter_rel.csv', 'recommender_rel.csv',
                    'institution_rel.csv', 'com_exec_rel.csv', 'com_rate_rel.csv']
    create_csv(node_filename, rel_filename)
    endtime = time.clock()
    print(str(endtime - starttime))
