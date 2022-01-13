from sqlalchemy import Column, BigInteger, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WhitelistEntry(Base):
	__tablename__ = 'whitelist_entries'
	userId = Column(BigInteger, primary_key=True)
	guildId = Column(BigInteger, primary_key=True)
	wallet = Column(String)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dbpw = ""
db = "postgresql://postgres:{}@db.rkqrkdnzfukpkeasaezn.supabase.co:6543/postgres".format(dbpw)

engine = create_engine(db, echo=True, future=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_entry(user_id: int, wallet: str, guild_id: int):
	r = get_entry(user_id, guild_id)
	if r is not None:
		r.wallet = wallet
		session.add(r)
	else:
		e = WhitelistEntry(userId=user_id, guildId=guild_id, wallet=wallet)
		session.add(e)
	session.commit()

def delete_entry(user_id: int, guild_id: int):
	r = get_entry(user_id, guild_id)
	if r is not None:
		session.delete(r)
		session.commit()
		return True
	return False

def get_entries(guildId):
	return session.query(WhitelistEntry).filter(WhitelistEntry.guildId == guildId).all()

def get_entry(userId, guildId):
	return session.query(WhitelistEntry).filter(WhitelistEntry.userId == userId and WhitelistEntry.guildId == guildI).first()
