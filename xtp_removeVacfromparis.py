import sqlite3
import sys
import numpy as np
if len(sys.argv)==2:
        filesql=sys.argv[1]
else:
        print "just enter .sql file from which the vac has to be removed. Exiting.."
        sys.exit()

def remove(sqlname):
        sqlstatement = "DELETE FROM pairs WHERE pairs.id IN (SELECT pairs.id FROM pairs JOIN segments seg1 ON seg1._id =pairs.seg1 JOIN segments seg2 ON seg2._id =pairs.seg2 WHERE (seg1.name=\'vac\' OR seg2.name=\'vac\'));"
        sqlstatement2= "UPDATE sqlite_sequence SET seq=(SELECT COUNT(_id) FROM pairs) WHERE name=\'pairs\';"
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                cur.execute(sqlstatement2)


remove(filesql)


