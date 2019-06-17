# coding=utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph
from datetime import timedelta
from functools import reduce

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['JSON_AS_ASCII'] = False
graph = Graph("http://localhost:7474", username="neo4j", password="nihao1234")


def buildNodes(node_record):
    # print(node_record)
    data = {"id": str(node_record['id']),
            "name": str(node_record['name']).encode("utf-8").decode("utf-8"),
            "label": str(node_record['label'][0]).encode("utf-8").decode("utf-8")}
    # data.update(node_record.n.properties)
    return data


def buildEdges(relationRecord):
    data = {"id": str(relationRecord['id']),
            "source": str(relationRecord['start']),
            "target": str(relationRecord['end']),
            "type": relationRecord['type'],
            "relationship": relationRecord['relationship']}
    return data


def list_dict_duplicate_removal(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)

# 导航页
@app.route('/')
def navigation():
    return render_template('navigation_page.html')


# 业务类图谱展示页面
@app.route('/business.html')
def business():
    return render_template('business.html')



# 股权结构树展示页面
@app.route('/tree.html')
def tree():
    return render_template('tree.html')


# @app.route('/continue')# 数量太大，网页会崩
# def get_con():
#     name1 = str(request.args.get('name1'))
#     name2 = str(request.args.get('name2'))
#     print(name1, name2)
#     nodes = list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(c)-[d]-(e{name:\"" + name2 + "\"})-[f]-(g)-[h]-"
#                                                                                        "(i:公司) return distinct id(c) as id, c.name as name, labels(c) as label")))
#     nodes1 = list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(e)-[d]-(i{name:\"" + name2 + "\"})-[f]-(g)-[h]-(c:公司) return  distinct id(c) as id, c.name as name, labels(c) as label")))
#     nodes2 = (list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(g)-[d]-(e{name:\"" + name2 + "\"})-[f]-(c)-[h]-(i:公司) return  distinct id(c) as id, c.name as name, labels(c) as label"))))
#     nodes = nodes + nodes1 + nodes2
#     nodes.append((list(map(buildNodes,graph.run(
#         "match (c:公司{name:\"" + name1 + "\"}) return  id(c) as id, c.name as name, labels(c) as label"))))[0])
#     nodes.append((list(map(buildNodes,graph.run(
#         "match (c:公司{name:\"" + name2 + "\"}) return  id(c) as id, c.name as name, labels(c) as label"))))[0])
#     edges = list(
#         map(buildEdges, graph.run("match (a:公司{name:\"" + name1 + "\"})-[b]-(c)-[d]-(e:公司{name:\"" + name2 + "\"})"
#                                                                                                                  "-[f]-(g)-[h]-(i:公司) return  id(startnode(b)) as start, id(endnode(b)) as end,type(b) as type")))
#     edges1 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(c)-[d]-(e:公司{name:\"" + name2 + "\"})-[f]-(g)-[h]-(i:公司) return  id(startnode(d)) as start, id(endnode(d)) as end,type(d) as type, d.relationship as relationship"))))
#     edges2 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(c)-[d]-(e:公司{name:\"" + name2 + "\"})-[f]-(g)-[h]-(i:公司) return  id(startnode(f)) as start, id(endnode(f)) as end,type(f) as type, f.relationship as relationship"))))
#     edges3 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name1 + "\"})-[b]-(c)-[d]-(e:公司{name:\"" + name2 + "\"})-[f]-(g)-[h]-(i:公司) return  id(startnode(h)) as start, id(endnode(h)) as end,type(h) as typed, h.relationship as relationship"))))
#     edges = edges + edges1 + edges2 + edges3
#     print(nodes, edges)
#     return jsonify(nodes, edges)


# 查找金融业务(包括发行股票、债券、授信金额)
@app.route('/get_fan_business')
def get_business():
    name = str(request.args.get('name'))
    nodes = list(map(buildNodes, graph.run("match (a{name:\'" + name + "\'})-[b:发行债券|发行股票|总授信额度]-(c) return  "
                                                      " distinct id(c) as id, c.name as name, labels(c) as label")))
    if(len(nodes) == 0):
        nodes = []
        edges = []
    else:
        current_node = list(map(buildNodes, graph.run('match (a{name:\"' + name + '\"}) '
                                                'return distinct  id(a) as id,labels(a) as label ,a.name as name').data()))
        nodes.append(current_node[0])
        edges = list(map(buildEdges, graph.run(
            "match (a{name:\"" + name + "\"})-[b:发行债券|发行股票|总授信额度]-(c) return distinct id(startnode(b)) as start,id(endnode(b)) as end,type(b) as type, b.relationship as relationship, id(b) as id")))
        #print(nodes, edges)
    return jsonify({'nodes': nodes, 'relations': edges})


# 查找两个公司联系
@app.route('/get_connect')
def get_connect():
    name1 = str(request.args.get('name1'))
    name2 = str(request.args.get('name2'))
    #print(name1, name2)
    nodes = list(map(buildNodes, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                "(i{name:\'" + name2 + "\'}) return distinct  id(c) as id, c.name as name, labels(c) as label")))
    nodes1 = list(map(buildNodes, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                        "(i{name:\'" + name2 + "\'}) return distinct  id(e) as id, e.name as name, labels(e) as label")))
    nodes2 = list(map(buildNodes, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                 "(i{name:\'" + name2 + "\'}) return distinct  id(g) as id, g.name as name, labels(g) as label")))
    nodes = nodes + nodes1 + nodes2
    if (len(nodes) == 0):
        nodes = []
        edges = []
    else:
        current_node1 = list(map(buildNodes, graph.run("match (c{name:\'" + name1 + "\'})"
                                        "return  distinct id(c) as id, c.name as name, labels(c) as label").data()))
        nodes.append(current_node1[0])
        current_node2 = list(map(buildNodes, graph.run("match (c{name:\'" + name2 + "\'})"
                                                                                      "return distinct id(c) as id, c.name as name, labels(c) as label").data()))
        nodes.append(current_node2[0])
        edges = list(map(buildEdges, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                 "(i{name:\'" + name2 + "\'}) return distinct  id(startnode(b)) as start, id(endnode(b)) as end, type(b) as type, b.relationship as relationship,id(b) as id")))
        edges1 = list(map(buildEdges, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                 "(i{name:\'" + name2 + "\'}) return distinct  id(startnode(d)) as start, id(endnode(d)) as end, type(d) as type, d.relationship as relationship, id(d) as id")))
        edges2 = list(map(buildEdges, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                 "(i{name:\'" + name2 + "\'}) return distinct  id(startnode(f)) as start, id(endnode(f)) as end, type(f) as type, f.relationship as relationship, id(f) as id")))
        edges3 = list(map(buildEdges, graph.run("match (a{name:\'" + name1 + "\'})-[b:发行债券|发行股票|总授信额度]-(c)-" \
                                                        "[d:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(e)-"
                                                "[f:上市推荐人|保荐机构|债券主承销商|股票主承销商|合作银行]-(g)-[h:发行债券|发行股票|总授信额度]-"
                                                 "(i{name:\'" + name2 + "\'}) return distinct  id(startnode(h)) as start, id(endnode(h)) as end, type(h) as type, h.relationship as relationship, id(h) as id")))
        edges = edges + edges1 + edges2 + edges3
    print(nodes, edges)
    return jsonify({'nodes': nodes, 'relations': edges})

# 查找目标公司的关联公司(节点太多容易崩)
# @app.route('/all')
# def get_all():
#     name = str(request.args.get('name'))
#     nodes = list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(c)-[d]-(e)-[f]-(g)-[h]-(i:公司) return distinct id(c) as id, c.name as name, labels(c) as label")))
#     nodes1 = list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(e)-[d]-(c)-[f]-(g)-[h]-(i:公司) return  distinct id(c) as id, c.name as name, labels(c) as label")))
#     nodes2 = (list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(g)-[d]-(e)-[f]-(c)-[h]-(i:公司) return  distinct id(c) as id, c.name as name , labels(c) as label"))))
#     nodes3 = (list(map(buildNodes, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(g)-[d]-(e)-[f]-(i)-[h]-(c:公司) return distinct id(c) as id, c.name as name, labels(c) as label"))))
#     nodes = nodes + nodes1 + nodes2 + nodes3
#     if(len(nodes) == 0):
#         nodes = {}
#         edges = {}
#     else:
#         nodes.append((list(map(buildNodes,graph.run(
#         "match (c:公司{name:\"" + name + "\"}) return  id(c) as id, c.name as name, labels(c) as label"))))[0])
#         edges = list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(c)-[d]-(e)-[f]-(g)-[h]-(i:公司) return  id(startnode(b)) as start, id(endnode(b)) as end,type(b) as type, b.relationship as relationship")))
#         edges1 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(c)-[d]-(e)-[f]-(g)-[h]-(i:公司) return  id(startnode(d)) as start, id(endnode(d)) as end,type(d) as type, d.relationship as relationship"))))
#         edges2 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(c)-[d]-(e)-[f]-(g)-[h]-(i:公司) return  id(startnode(f)) as start, id(endnode(f)) as end,type(f) as type, f.relationship as relationship"))))
#         edges3 = (list(map(buildEdges, graph.run(
#         "match (a:公司{name:\"" + name + "\"})-[b]-(c)-[d]-(e)-[f]-(g)-[h]-(i:公司) return  id(startnode(h)) as start, id(endnode(h)) as end,type(h) as type, h.relationship as relationship"))))
#         edges = edges + edges1 + edges2 + edges3
#     print(nodes, edges)
#     return jsonify(nodes, edges)


# 查找企业关联图谱（返回高管和投资信息）
@app.route('/get_info')
def get_executive():
    name = str(request.args.get('name'))
    nodes = list(map(buildNodes, graph.run(
        "match (a{name:\'" + name + "\'})-[b:高管关系|投资占比]-(c) return distinct id(c) as id, c.name as name, labels(c) as label")))
    nodes = nodes
    if (len(nodes) == 0):
        nodes = []
        edges = []
    else:
        nodes.append((list(map(buildNodes, graph.run(
        "match (c{name:\'" + name + "\'}) return distinct  id(c) as id, c.name as name, labels(c) as label"))))[0])
        edges = list(map(buildEdges, graph.run(
        "match (a{name:\'" + name + "\'})-[b:高管关系|投资占比]-(c)  return distinct  id(startnode(b)) as start, id(endnode(b)) as end,type(b) as type, b.relationship as relationship, id(b) as id")))

        edges = edges
    print(nodes, edges)
    return jsonify({'nodes': nodes, 'relations': edges})

# 查找目标公司的关联金融机构
@app.route('/get_fin')
def get_fin():
    name = str(request.args.get('name'))
    nodes = list(map(buildNodes, graph.run(
        "match (a{name:\"" + name + "\"})-[b:发行债券|发行股票|总授信额度]-(c)-"
                                       "[d:合作银行|上市推荐人|股票主承销商|债券主承销商|保荐机构]-(e) return distinct id(c) as id, c.name as name, labels(c) as label")))
    nodes1 = list(map(buildNodes, graph.run(
        "match (a{name:\"" + name + "\"})-[b:发行债券|发行股票|总授信额度]-(e)-[d:合作银行|上市推荐人|股票主承销商|债券主承销商|保荐机构]-(c) return distinct id(c) as id, c.name as name, labels(c) as label")))
    nodes = nodes + nodes1
    if (len(nodes) == 0):
        nodes = []
        edges = []
    else:
        nodes.append((list(map(buildNodes, graph.run(
        "match (c{name:\"" + name + "\"}) return distinct  id(c) as id, c.name as name, labels(c) as label"))))[0])
        nodes = list_dict_duplicate_removal(nodes)
        edges = list(map(buildEdges, graph.run(
        "match (a{name:\"" + name + "\"})-[b:发行债券|发行股票|总授信额度]-(c)-[d:合作银行|上市推荐人|股票主承销商|债券主承销商|保荐机构]-(e) return distinct   id(startnode(b)) as start, id(endnode(b)) as end,type(b) as type, b.relationship as relationship, id(b) as id")))
        edges1 = (list(map(buildEdges, graph.run(
        "match (a{name:\"" + name + "\"})-[b:发行债券|发行股票|总授信额度]-(c)-[d:合作银行|上市推荐人|股票主承销商|债券主承销商|保荐机构]-(e) return distinct  id(startnode(d)) as start, id(endnode(d)) as end,type(d) as type, d.relationship as relationship, id(d) as id"))))
        edges = edges + edges1
    print(nodes, edges)
    return jsonify({'nodes': nodes, 'relations': edges})
    # return jsonify(nodes,  edges)


# 查找目标公司的授信金额及银行
@app.route('/get_credit')
def get_credit():
    name = str(request.args.get('name'))
    nodes = list(map(buildNodes, graph.run("match (a{name:\"" + name + "\"})-[b]-(c:总授信额度)-[d]-(e) "
                                                                            "return distinct  id(c) as id, c.name as name, labels(c) as label")))
    nodes1 = list(map(buildNodes, graph.run(
        "match (a{name:\"" + name + "\"})-[b]-(e:总授信额度)-[d]-(c) return distinct  id(c) as id, c.name as name, labels(c) as label")))
    nodes = nodes + nodes1
    if (len(nodes) == 0):
        nodes = []
        edges = []
    else:
        nodes.append((list(map(buildNodes, graph.run(
        "match (c{name:\"" + name + "\"}) return  distinct id(c) as id, c.name as name, labels(c) as label"))))[0])
        edges = list(map(buildEdges, graph.run(
        "match (a{name:\"" + name + "\"})-[b]-(c:总授信额度)-[d]-(e) return distinct  id(startnode(b)) as start, id(endnode(b)) as end,type(b) as type, b.relationship as relationship,id(b) as id")))
        edges1 = (list(map(buildEdges, graph.run(
        "match (a{name:\"" + name + "\"})-[b]-(c:总授信额度)-[d]-(e) return distinct  id(startnode(d)) as start, id(endnode(d)) as end,type(d) as type, d.relationship as relationship, id(d) as id"))))
        edges = edges + edges1
    print(nodes, edges)
    return jsonify({'nodes': nodes, 'relations': edges})


@app.route('/get_child')
def get_child():
    name = str(request.args.get('name'))
    nodes = graph.run("match (a{name:\""+name+"\"})-[:投资占比]->(c) return distinct c.name as name").data()   #查询数据信息
    return jsonify({"data": nodes})


@app.route('/get_father')
def get_father():
    name = str(request.args.get('name'))
    nodes = graph.run("match (a{name:\""+name+"\"})<-[:投资占比]-(c) return distinct  c.name as name").data()
    return jsonify({"data": nodes})
# @app.route('/graph')
# def get_graph():
#     name = str(request.args.get('name'))
#     node1 = list(map(buildNodes, graph.run('match (a:公司{name:\"'+name+'\"})-[b]-(c) return distinct id(c) as id,'
#                                                                           'labels(c) as label,c.name as name').data()))
#     node2 = (list(map(buildNodes, graph.run('match (a:公司{name:\"'+name+'\"})-[b]-(c)-[d]-(e) return '
#                                                                            'distinct id(e) as id, labels(e) as label, e.name as name').data())))
#     nodes = node1 + node2
#     current_node = list(map(buildNodes, graph.run('match (a:公司{name:\"'+name+'\"}) '
#                                                                                  'return id(a) as id,labels(a) as label ,a.name as name').data()))
#     if (len(nodes) == 0):
#         nodes = {}
#         edges = {}
#     else:
#         nodes.append(current_node[0])
#         edge1 = list(map(buildEdges, graph.run('match (a:公司{name:\"'+name+'\"})-[b]-(c) return '
#                                                                           'id(startnode(b)) as start ,id(endnode(b)) as end, type(b) as type, b.relationship as relationship').data()))
#         edges = edge1 + (list(map(buildEdges, graph.run('match (a:公司{name:\"'+name+'\"})-[b]-(c)-[d]-(e) return '
#                                                                                    'id(startnode(d)) as start, id(endnode(d)) as end, type(d) as type, d.relationship as relationship').data())))
#     return jsonify(nodes, edges)  # 用Flask的jsonify函数把elements转成JSON格式返回给前端

if __name__ == '__main__':
    app.run(debug=True)
