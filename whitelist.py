import config
from sqlalchemy import Column, BigInteger, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class WhitelistEntry(Base):
	__tablename__ = 'whitelist_entries'
	userId = Column(BigInteger, primary_key=True)
	guildId = Column(BigInteger, primary_key=True)
	wallet = Column(String)

engine = create_engine(config.db_path, echo=False, future=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_entry(session: Session, user_id: int, wallet: str, guild_id: int):
	r = get_entry(session, user_id, guild_id)
	if r is not None:
		r.wallet = wallet
		session.add(r)
	else:
		e = WhitelistEntry(userId=user_id, guildId=guild_id, wallet=wallet)
		session.add(e)
	session.commit()

def delete_entry(session: Session, user_id: int, guild_id: int) -> bool:
	r = get_entry(session, user_id, guild_id)
	if r is not None:
		session.delete(r)
		session.commit()
		return True
	return False

def get_entries(session: Session, guild_id: int):
	return session \
		.query(WhitelistEntry) \
		.filter(WhitelistEntry.guildId == guild_id) \
		.all()

def get_entry(session: Session, user_id: int, guild_id: int):
	return session \
		.query(WhitelistEntry) \
		.filter(WhitelistEntry.userId == user_id and WhitelistEntry.guildId == guild_id) \
		.first()


class Whitelist(object):
	@staticmethod
	def add(user_id: int, wallet: str, guild_id: int) -> bool:
		with Session() as session:
			save_entry(session, user_id, wallet, guild_id)
			return True
		return False

	@staticmethod
	def remove(user_id: int, guild_id: int) -> bool:
		with Session() as session:
			return delete_entry(session, user_id, guild_id)
		return False
	
	@staticmethod
	def check(user_id: int, guild_id: int) -> str:
		with Session() as session:
			entry = get_entry(session, user_id, guild_id)
			if entry is not None:
				return entry.wallet

	@staticmethod
	def count(guild_id: int) -> int:
		with Session() as session:
			return len(get_entries(session, guild_id))
		return 0
