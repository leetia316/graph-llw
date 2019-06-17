说明：
1.create_csv.py文件用来生成csv文件用于导入图数据库（已生成）
2.将生成的所有文件放在neo4j的import目录下
3.在neo4j的bin目录下执行以下命令：(graph.db为数据库名称)
neo4j-admin  import --database=graph.db --nodes D:\neo4j-community-3.5.3\import\company_name.csv --nodes D:\neo4j-community-3.5.3\import\bank.csv --nodes D:\neo4j-community-3.5.3\import\total_credit.csv --nodes D:\neo4j-community-3.5.3\import\bond_name.csv --nodes D:\neo4j-community-3.5.3\import\company_executive.csv --nodes D:\neo4j-community-3.5.3\import\shares.csv  --relationships D:\neo4j-community-3.5.3\import\bank_rel.csv --relationships D:\neo4j-community-3.5.3\import\com_bond_rel.csv --relationships D:\neo4j-community-3.5.3\import\s_lu_name_rel.csv --relationships D:\neo4j-community-3.5.3\import\shares_rel.csv --relationships D:\neo4j-community-3.5.3\import\lead_underwriter_rel.csv --relationships D:\neo4j-community-3.5.3\import\recommender_rel.csv  --relationships D:\neo4j-community-3.5.3\import\institution_rel.csv --relationships D:\neo4j-community-3.5.3\import\total_credit_rel.csv --relationships D:\neo4j-community-3.5.3\import\com_exec_rel.csv  --relationships D:\neo4j-community-3.5.3\import\com_rate_rel.csv
4.执行此命令之前要暂停数据库的服务,执行完成后再启动服务器即可正常使用
