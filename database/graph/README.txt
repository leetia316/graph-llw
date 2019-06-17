说明：
1.create_csv.py文件用来生成csv文件用于导入图数据库（已生成）
2.将生成的所有文件放在neo4j的import目录下
3.在neo4j的bin目录下执行以下命令：(graph.db为数据库名称)
neo4j-admin  import --database=graph.db --nodes company_name.csv --nodes bank.csv --nodes total_credit.csv --nodes bond_name.csv --nodes company_executive.csv --nodes shares.csv  --relationships bank_rel.csv --relationships com_bond_rel.csv --relationships s_lu_name_rel.csv --relationships shares_rel.csv --relationships lead_underwriter_rel.csv --relationships recommender_rel.csv  --relationships institution_rel.csv --relationships total_credit_rel.csv --relationships com_exec_rel.csv  --relationships com_rate_rel.csv
4.执行此命令之前要暂停数据库的服务,执行完成后再启动服务器即可正常使用
