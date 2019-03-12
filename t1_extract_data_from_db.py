from pandas import DataFrame
import mysql.connector as mc
from properties import user, password, host, port, database, data_path

cnx = mc.connect(user=user, password=password, host=host, port=port, database=database)
cursor = cnx.cursor()

# Find answer(with code block which has changed at least once) ids
sql1 = """CREATE OR REPLACE VIEW sotorrent18_09.edits AS
SELECT DISTINCT PH.Id,PH.Comment
FROM sotorrent18_09.posts AS P
INNER JOIN sotorrent18_09.posthistory AS PH ON PH.PostId=P.Id
INNER JOIN sotorrent18_09.postblockversion AS PBV ON PBV.PostHistoryId=PH.Id
WHERE P.PostTypeId=2 AND  PBV.PostBlockTypeId=2 AND PBV.PredSimilarity<1 AND PH.Comment IS NOT NULL;
"""
cursor.execute(sql1)

# Find text content from mentioned ids
sql2 = """CREATE OR REPLACE VIEW sotorrent18_09.text AS 
SELECT PostHistoryId AS Id,PredPostHistoryId,Content AS Text
FROM sotorrent18_09.postblockversion 
WHERE PostBlockTypeId=1 AND LocalId=1 AND PostHistoryId IN (SELECT Id FROM sotorrent18_09.edits);
"""
cursor.execute(sql2)

# Find code content from mentioned ids
sql3 = """CREATE OR REPLACE VIEW sotorrent18_09.code AS 
SELECT PostHistoryId AS Id,PredPostHistoryId,Content AS Code
FROM sotorrent18_09.postblockversion 
WHERE PostBlockTypeId=2 AND LocalId=2 AND PostHistoryId IN (SELECT Id FROM sotorrent18_09.edits);
"""
cursor.execute(sql3)

# Create a view (fin_edits)  with all previous data (id,predid,comment,text,code)
sql4 = """CREATE OR REPLACE VIEW sotorrent18_09.fin_edits AS 
SELECT E.Id,T.PredPostHistoryId,E.Comment,T.Text,C.Code
FROM sotorrent18_09.edits AS E
INNER JOIN sotorrent18_09.text AS T ON T.Id=E.Id
INNER JOIN sotorrent18_09.code AS C ON C.Id=E.Id
ORDER BY E.Id;
"""
cursor.execute(sql4)

# Find text content from original anwser ids
sql5 = """CREATE OR REPLACE VIEW sotorrent18_09.roots1 AS
SELECT PostHistoryId AS Id,Content AS Text
FROM sotorrent18_09.postblockversion 
WHERE PostBlockTypeId=1 AND LocalId=1 AND PostHistoryId IN (SELECT PredPostHistoryId FROM sotorrent18_09.fin_edits) AND PostHistoryId NOT IN (SELECT Id FROM sotorrent18_09.fin_edits);
"""
cursor.execute(sql5)

# Find code content from original anwser ids
sql6 = """CREATE OR REPLACE VIEW sotorrent18_09.roots2 AS
SELECT PostHistoryId AS Id,Content AS Code
FROM sotorrent18_09.postblockversion 
WHERE PostBlockTypeId=2 AND LocalId=2 AND PostHistoryId IN (SELECT PredPostHistoryId FROM sotorrent18_09.fin_edits) AND PostHistoryId NOT IN (SELECT Id FROM sotorrent18_09.fin_edits);
"""
cursor.execute(sql6)

# Create a view (fin_roots) with data (id,text,code) from original answers
sql7 = """CREATE OR REPLACE VIEW sotorrent18_09.fin_roots AS 
SELECT R1.Id,NULL,NULL,Text,Code
FROM sotorrent18_09.roots1 AS R1 
INNER JOIN sotorrent18_09.roots2 AS R2 ON R1.Id=R2.Id
ORDER BY R1.Id;
"""
cursor.execute(sql7)

sql8 = """(SELECT * FROM sotorrent18_09.fin_edits)
UNION ALL
(SELECT * FROM sotorrent18_09.fin_roots)
ORDER BY Id;
"""
cursor.execute(sql8)

df = DataFrame(cursor.fetchall())
df.columns = cursor.column_names
df.to_csv(data_path + 'answer_posts_with_edits.csv', sep='\t', encoding='utf-8')

