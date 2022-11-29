import sqlite3


db = sqlite3.connect('db.sqlite3')
cursor = db.cursor()
cursor.execute("delete from app1_document")
#cursor.execute("update login_logindetails set username='bhupendar' where id = 2")
#cursor.execute("update login_logindetails set username='' where id = 1")
#cursor.execute("update login_logindetails set username='' where id = 3")
# # cursor.execute("update login_logindetails set clientid='xyz' where id = 2")
# # cursor.execute("update login_logindetails set cipher_text='abc' where id = 1")
# # cursor.execute("update login_logindetails set cipher_text='pqr' where id = 3")
#cursor.execute("ALTER TABLE app1_accesslog ADD id int")
# cursor.execute("delete from app1_detectorupload where status = 'Not Viewed'")
db.commit() 

from Crypto.Cipher import AES
#from Crypto.Util.Padding import pad, unpad
import base64

# c = 'shreysciphertext'

# decryption_suite = AES.new('thisisorignalkey', AES.MODE_CBC, 'thisisinitvector')
# #c = pad(c.encode(), AES.block_size)
# plain = decryption_suite.encrypt(c)
# plain = base64.b64encode(plain).decode('utf-8')
# print(len(plain))
# print(AES.block_size)
# #plain = plain.decode('utf-8')
# cursor.execute(f"update login_logindetails set cipher_text= '{c}' where id = 1")
# db.commit()

# decryption_suite = AES.new('thisisorignalkey', AES.MODE_CBC, 'thisisinitvector')
# plaintext = decryption_suite.decrypt(base64.b64decode(plain)).decode('utf-8')

# print(plaintext)