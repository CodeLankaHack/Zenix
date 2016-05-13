import MySQLdb
from Crypto.Cipher import AES
import base64
import os

# Open database connection (Database is on Google Cloud Platform)
db = MySQLdb.connect("173.194.105.40","amila","rajans12","zvote" )

# prepare a cursor object using cursor() method
cur = db.cursor()

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '}'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

# generate a random secret key
secret = os.urandom(BLOCK_SIZE)

# create a cipher object using the random secret
cipher = AES.new(secret)

nic = raw_input('Enter your NIC number: ')
pin = int(raw_input('Enter your PIN number: '))
vote = raw_input('Enter your vote: ')

cur.execute("SELECT nic, pin, voted FROM tbl_users")

row = cur.fetchone()
while row is not None:
	#print row[0], row[1]
	
	if (row[0] == nic and row[1] == pin and row[2] == 0):
		valid = 1
		cur.execute("UPDATE tbl_users SET voted=1 WHERE pin=%d"% pin)
		encoded = EncodeAES(cipher, nic)
		
		try:
   			# Execute the SQL command
   			cur.execute("INSERT INTO tbl_votes(authkey,vote) VALUES(%s,%s)", (encoded,vote))
   			# Commit your changes in the database
   			db.commit()
		except:
   			# Rollback in case there is any error
			db.rollback()

		break
	else:
		valid = 0
		
	row = cur.fetchone()

if valid == 1:
	print 'Valid user, Vote accepted'
elif valid == 0:
	print 'Invalid user, Vote rejected'
	 	
cur.close()
db.close()
